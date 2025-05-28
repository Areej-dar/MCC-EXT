#Tested locally.
import os
import re
import json
import pandas as pd
import pdfplumber
import requests
from dotenv import load_dotenv
import openai
from xlsxwriter.utility import xl_col_to_name
import time

file_path = "DeclinedTransactionDetails-16-May-2025.xlsx" 

# skipping the first 10 rows
df_main = pd.read_excel(file_path, header=10)
print("Main Sheet Column Names:", df_main.columns)

whitelist_file_path = "Whitelist 2.0.xlsx" 
# Load
df_whitelist = pd.read_excel(whitelist_file_path)
print("Whitelist Sheet Column Names:", df_whitelist.columns)

#Filter DE39 AUTH RESP to keep only blank or "85"
filtered_df = df_main[(df_main['DE39 AUTH RESP '].isnull()) | (df_main['DE39 AUTH RESP '] == 85)]
print("Filtered DataFrame shape:", filtered_df.shape)

#Inspect and clean the DE6 CDHLDR AMT column
print("Raw DE6 CDHLDR AMT values:", filtered_df['DE6 CDHLDR AMT '].head(20))
filtered_df.loc[:, 'DE6 CDHLDR AMT '] = filtered_df['DE6 CDHLDR AMT '].replace('[^0-9.]', '', regex=True)
filtered_df.loc[:, 'DE6 CDHLDR AMT '] = pd.to_numeric(filtered_df['DE6 CDHLDR AMT '], errors='coerce')
print("Cleaned DE6 CDHLDR AMT values:", filtered_df['DE6 CDHLDR AMT '].head(20))

#Group by DE43 ACCEPTOR and sum DE6 CDHLDR AMT
grouped_df = filtered_df.groupby(['DE43 ACCEPTOR ', 'DE18 MCC '])['DE6 CDHLDR AMT '].sum().reset_index()
print("Grouped DataFrame shape:", grouped_df.shape)
print("Sample grouped data:", grouped_df.head())

#Remove duplicates in DE43 ACCEPTOR while keeping the summed values
final_df = grouped_df.drop_duplicates(subset=['DE43 ACCEPTOR '])
print("Final DataFrame shape:", final_df.shape)
print("Sample final data:", final_df.head())

#Rename columns for clarity
final_df.columns = ['DE43', 'DE18', 'DE6(SUMMED)']

#Filter the whitelist DataFrame for rows where 'Merchant Name' matches 'DE43'
matched_rows = df_whitelist[df_whitelist['Merchant Name'].isin(final_df['DE43'])]

#Merge the result DataFrame with the matched rows from the whitelist DataFrame
result_df = pd.merge(final_df, matched_rows, how='left', left_on='DE43', right_on='Merchant Name')

#Fill missing values in 'Status' column with 'Not found'
result_df['Status'] = result_df['Status'].fillna('Not found')

#Select and reorder columns
result_df = result_df[['DE43', 'DE6(SUMMED)', 'DE18', 'Status']]

result_df = result_df.drop_duplicates(subset=['DE43'])

#Filter out rows where DE6(SUMMED) is <= 5000 OR Status is 'Whitelist'
result_df = result_df[
    (result_df['DE6(SUMMED)'] > 5000) & 
    (result_df['Status'].str.strip().str.lower() != 'whitelist')
]
# Normalize function
def normalize_text(text):
    if pd.isna(text):
        return ""
    text = re.sub(r'\W+', '', text)  # remove all non-alphanumerics
    return text.lower()

# Normalize base merchants once
base_merchants = [
    "airbnb", "uber", "envato", "namecheap", "name-cheap", "namecheapcom", "primark", "2c2p", "godaddy", "wl steam purchase",
    "ebay", "upwork", "shopify", "aliexpress", "zara", "zoom", "indeed", "steam purchase", "cursor", "grammarly", "slack",
    "etsy", "tiktok", "spaceship", "google", "microsoft", "watiio", "tommy hilfiger", "chuffedor", "canva", "stable",
    "facebook", "facebk", "a2webhosting", "adobe", "agoda", "ai humanizeio", "humanize ai", "bolt", "bolteu", "wordpress",
    "stealth ai", "stealthwriterai", "dubai duty free", "openai chatgpt subscr", "pubg", "elevenlabs", "pagopa", "playtomicio", "promptchan",
    "tesco", "contabo", "paddlenet", "fidelity", "dynadot", "decathlon", "copyleaks", "bookingcom", "driffle", "nuvei payments", "sistic",
    "istanbulepass", "nimvideo", "ideogramai", "amboss", "otpmobl", "myprotein", "smtp2go", "suno", "smyths toys", "taobaocom", "worldtaobaocom",
    "kitopi", "12go nicosia cyp",
]
normalized_base_merchants = [normalize_text(bm) for bm in base_merchants]

# Apply normalization to result_df['DE43']
result_df['normalized_de43'] = result_df['DE43'].apply(normalize_text)

# Matching function
def is_base_merchant(name):
    return any(base in name for base in normalized_base_merchants)

# Save removed merchants
removed_base = result_df[result_df['normalized_de43'].apply(is_base_merchant)]
if not removed_base.empty:
    print("Removed due to base match:")
    print(removed_base[['DE43', 'DE6(SUMMED)', 'Status']])
    removed_base.to_excel('removed_base_merchants.xlsx', index=False)
else:
    print("No base merchants matched.")

# Remove base merchants
result_df = result_df[~result_df['normalized_de43'].apply(is_base_merchant)]
result_df = result_df.drop(columns=['normalized_de43'])

output_file_path = '16-may-2025.xlsx'
result_df.to_excel(output_file_path, index=False)
print(f"Final cleaned data saved to {output_file_path}")


#------------------
# Whitelist of MCCs
WHITELISTED_MCC = {
    '3690','5311','5411','5462','5499','5531','5621','5631','5641','5651',
    '5655','5661','5691','5722','5733','5811','5812','5814','5815',
    '5912','5931','5932','5933','5941','5942','5943','5944','5945',
    '5946','5947','5948','5949','5950','5970','5971','5992','5994',
    '5995','6011','7210','7211','7216','7217','7221','7230','7251',
    '7298','7542','7933','8062','8071'
}

SENSITIVE_KEYWORDS = [
    "adult content", "gambling", "illegal substances", "regulated substances",
    "weapons", "hacking", "illegal software", "scams", "phishing",
    "unregulated financial services"
]

#Red-flags, social patterns, etc.
RED_FLAG_TERMS = ["Get Rich Quick","No Risk Guarantee","Limited Time Offer","Act Now","Make Money Fast","Zero Investment"]
SOCIAL_PATTERNS = ["facebook.com","twitter.com","linkedin.com","instagram.com","t.me","youtube.com"]
PAGE_KEYWORDS   = ["About Us","Contact Us","Privacy Policy","Terms and Conditions","Refund Policy"]
PROHIBITED_CATEGORIES = ["weapons","illicit","drugs","adult","gambling","counterfeit"]

#Extract all MCC codes from PDF
def extract_all_codes(pdf_file):
    pattern = re.compile(r'^(?P<code>(?:MCC\s*\d{4}|[A-Z]{1,5}\d{1,4}))\b')
    extracted = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.splitlines():
                m = pattern.match(line.strip())
                if m:
                    code = m.group("code").replace("MCC","").strip()
                    desc = line[m.end():].strip(" -–—")
                    extracted.append({"Code":code,"Description":desc})
    return extracted

# Merchant-string heuristics
def extract_domains(text):
    return re.findall(r'\b(?:[\w-]+\.)+[A-Za-z]{2,}\b', text)

def extract_website_name_heuristic(s):
    tokens = s.split()
    groups, cur = [], []
    for t in tokens:
        c = t.strip(" ,.;()")
        if re.search(r'\d',c) or not re.match(r'^[A-Za-z-]+$',c):
            if cur:
                groups.append(" ".join(cur))
                cur=[]
            continue
        cur.append(c)
    if cur: groups.append(" ".join(cur))
    return max(groups, key=len) if groups else ""

def extract_merchant_name_field(s):
    parts = re.split(r'\s{2,}', s.strip())
    name = parts[0] if len(parts)>1 else s.strip()
    for p in ["PM *","PM ","www*","WWW.","WWW/"]:
        if name.upper().startswith(p):
            name = name[len(p):].strip()
    return name

def combine_extractions(s):
    res = set()
    d = extract_domains(s)
    if d: res.add(d[0])
    h = extract_website_name_heuristic(s)
    if h: res.add(h)
    f = extract_merchant_name_field(s)
    if f: res.add(f)
    return " ".join(res)

# Parse mobile, country, name
def parse_merchant_details(s):
    m = re.search(r'\+?\d{7,}', s)
    mobile = m.group() if m else None
    c = re.search(r'\b[A-Z]{2,3}\b$', s)
    country = c.group() if c else ""
    n = re.match(r'([A-Za-z\s]+)', s)
    name = n.group(1).strip() if n else s
    return {"merchant_name":name,"mobile":mobile,"country":country}

# GPT-4o for structured JSON (now returns website+confidence)
def generate_risk_assessment_gpt4o(prompt):
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("OPENAI_API_KEY not set")
    openai.api_key = key

    system = """
You are a risk-analysis assistant for SadaPay.
Input: merchant name, country code.
Output *only* this JSON:
{
  "risk_level":"Low|Medium|High",
  "risk_score":0-100,
  "website":"<inferred or provided domain or null>",
  "summary":"one-sentence findings",
  "business_nature":"Briefly explain what the merchant does or offers",
  "reason":"brief rationale for the level",
  "confidence":0-100
}
Rules:
1. If “domain” is empty, try to infer the merchant’s website and put it in `website`.
2. Blacklist if business involves: weapons, arms, adult content, gambling, scam, phishing, hacking, forex, crypto, trading, fundraising, charity, donations.
3. Base your score on:
  • domain validity
  • presence of pages: About Us, Contact Us, Privacy Policy, T&C, Refund Policy
  • social links (Facebook, Twitter, LinkedIn, Instagram, YouTube)
  • red-flag marketing terms
4. If you can’t infer a domain, set `"website": null` and say so in `summary`.
5. Tell the merchant category (e.g. “e-commerce”, “gaming”) in `summary`.
""".strip()

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
              {"role":"system","content":system},
              {"role":"user","content":prompt}
            ],
            temperature=0.0
        )
        text = resp.choices[0].message.content
        m = re.search(r'\{.*\}', text, re.DOTALL)
        if not m:
            return None, None, None, text, None
        obj = json.loads(m.group())
        return (
            obj.get("risk_level"),
            obj.get("risk_score"),
            obj.get("website"),
            obj.get("summary"),
            obj.get("business_nature"),
            obj.get("reason"), 
            obj.get("confidence")
        )
    except Exception as e:
        return None, None, None, None, None, f"GPT-4o error: {e}"

# Google Custom Search fallback
def generate_risk_assessment_google(name, country):
    key = os.getenv("GOOGLE_API_KEY")
    cx  = os.getenv("GOOGLE_CX")
    if not key or not cx:
        raise ValueError("Google API creds not set")

    query = f"{name} {country}"
    response = requests.get(
        "https://www.googleapis.com/customsearch/v1",
        params={"key": key, "cx": cx, "q": query}
    )
    items = response.json().get("items", [])[:3]

    # No results → treat as High
    if not items:
        summary = f"No Google results for “{name} {country}.”"
        return "High", 90, None, summary, 0

    # Build snippet+links
    lines, all_links = ["Top Google results:"], []
    for it in items:
        title   = it.get("title","").strip()
        link    = it.get("link","").strip()
        snippet = it.get("snippet","").replace("\n"," ").strip()
        lines.append(f"• {title}\n  {link}\n  {snippet}\n")
        all_links.append(link.lower())
    summary = "\n".join(lines)
    website = items[0].get("link").strip()
    text_blob = summary.lower()

    # 1) Sensitive content?
    detected = [kw for kw in SENSITIVE_KEYWORDS if kw in text_blob]
    if detected:
        print(f"[Sensitive content detected]: {', '.join(detected)}")
        return "Critical", 100, website, summary, int(len(items)/3*100)

    # 2) Safe indicators in snippet or URLs?
    safe_patterns = [
        "about us", "privacy policy", "contact us", "terms & conditions",
        "/about", "/about-us", "/ueber-uns", "/privacy", "/contact"
    ]
    found_safe = (
        any(patt in text_blob for patt in safe_patterns) or
        any(patt in link for link in all_links for patt in safe_patterns)
    )
    if found_safe:
        return "Low", 20, website, summary, int(len(items)/3*100)

    # 3) Otherwise Medium
    return "Medium", 50, website, summary, int(len(items)/3*100)

# Combined get_risk → GPT or fallback
def get_risk_assessment(prompt, name, country):
    level, score, website, summary, business_nature, reason, confidence = generate_risk_assessment_gpt4o(prompt)
    if level is not None and score is not None:
        return level, score, website, summary, business_nature, reason, confidence

    # GPT failed, fall back to Google using the merchant name + country
    return generate_risk_assessment_google(name, country)

def main():
    # Extract MCC codes
    #codes = extract_all_codes("quick-reference-booklet-merchant-edition (1).pdf")
    # pd.DataFrame(codes).to_excel("extracted_mcc_codes.xlsx", index=False)

    # Load transactions
    df = pd.read_excel("16-May-2025.xlsx")
    assert 'DE43' in df and 'DE18' in df and 'DE6(SUMMED)' in df

    final_results = []
    chunk_size = 10

    processed_count = 0
    skipped_count = 0

    for start_idx in range(0, len(df), chunk_size):
        end_idx = min(start_idx + chunk_size, len(df))
        chunk = df.iloc[start_idx:end_idx]
        print(f"\n🔄 Processing merchants {start_idx+1} to {end_idx}...\n")

        for idx, row in chunk.iterrows():
            status = str(row.get("Status", "")).strip().lower()
            if "to be blacklisted" in status:
                print(f"⏭️ Row {idx} skipped — already blacklisted.")
                skipped_count += 1
                continue

            raw = str(row['DE43'])
            summed = row['DE6(SUMMED)']
            mcc = str(row['DE18']).replace("MCC", "").strip()
            name = combine_extractions(raw)
            det = parse_merchant_details(raw)
            country = det['country']
            domain = (extract_domains(raw) or [""])[0]

            print(f"\nRow {idx}: Merchant={name}  MCC={mcc}")
            if mcc in WHITELISTED_MCC:
                print(" → Whitelisted, skipping detailed risk check.\n")
                lvl, sc, web, summ_txt, nature, reason, conf = "Whitelisted", None, None, "", "", "", None
            else:
                prompt = f"Merchant Name: {name}\nCountry: {country}\nDomain: {domain}"
                print("Prompt:\n" + prompt + "\n")
                lvl, sc, web, summ_txt, nature, reason, conf = get_risk_assessment(prompt, name, country)
                print(f"Website   : {web}")
                print(f"Risk Level: {lvl} | Score: {sc} | Confidence: {conf}")
                print(f"Summary   : {summ_txt}")
                print(f"Reason    : {reason}\n")
                print(f"Nature    : {nature}\n")

            status = "blacklisted" if lvl == "High" else "whitelisted"

            final_results.append({
                "DE43":        raw,
                "DE6(SUMMED)": summed,
                "DE18":        row['DE18'],
                "Risk Level":  lvl,
                "Risk Score":  sc,
                "Summary":     summ_txt,
                "Confidence":  conf,
                "Status":      status
            })

            processed_count += 1
            time.sleep(1)

        time.sleep(5)

    # Save to single Excel file
    out = pd.DataFrame(final_results)
    report_file = "risk_report.xlsx"
    with pd.ExcelWriter(report_file, engine="xlsxwriter") as writer:
        out.to_excel(writer, index=False, sheet_name="Report")
        wb = writer.book
        ws = writer.sheets["Report"]

        # Auto-adjust column widths
        for i, col in enumerate(out.columns):
            max_len = max(out[col].astype(str).map(len).max(), len(col)) + 2
            ws.set_column(i, i, min(max_len, 50))

        # Conditional formatting
        fmt_g = wb.add_format({"bg_color": "#C6EFCE"})
        fmt_y = wb.add_format({"bg_color": "#FFEB9C"})
        fmt_r = wb.add_format({"bg_color": "#FFC7CE"})

        cols = out.columns.tolist()
        idx_map = {c: i for i, c in enumerate(cols)}
        start, end = 2, len(out) + 1

        c = idx_map["Risk Level"]
        col_letter = xl_col_to_name(c)
        rng = f"{col_letter}{start}:{col_letter}{end}"
        ws.conditional_format(rng, {"type": "text", "criteria": "containing", "value": "Low", "format": fmt_g})
        ws.conditional_format(rng, {"type": "text", "criteria": "containing", "value": "Medium", "format": fmt_y})
        ws.conditional_format(rng, {"type": "text", "criteria": "containing", "value": "High", "format": fmt_r})

        cs = idx_map["Risk Score"]
        rng_s = f"{xl_col_to_name(cs)}{start}:{xl_col_to_name(cs)}{end}"
        ws.conditional_format(rng_s, {
            "type": "3_color_scale",
            "min_type": "num", "min_value": 0,
            "mid_type": "percentile", "mid_value": 50,
            "max_type": "num", "max_value": 100
        })

        cc = idx_map["Confidence"]
        rng_c = f"{xl_col_to_name(cc)}{start}:{xl_col_to_name(cc)}{end}"
        ws.conditional_format(rng_c, {"type": "data_bar"})

    # Final log summary
    print(f"\nReport written to: {report_file}")
    print(f"Processed merchants: {processed_count}")
    print(f"Skipped merchants  : {skipped_count}")
    
if __name__=="__main__":
    main()