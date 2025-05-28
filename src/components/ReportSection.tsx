import React from 'react';
import { FileDown, CheckCircle, Loader2, FileSpreadsheet } from 'lucide-react';

interface ReportSectionProps {
  generatedReport: {
    riskReport: string | null;
    cleanedFile: string | null;
  } | null;
  isProcessing: boolean;
}

export const ReportSection: React.FC<ReportSectionProps> = ({
  generatedReport,
  isProcessing
}) => {
  if (!generatedReport && !isProcessing) {
    return null;
  }

  return (
    <section className="bg-white rounded-xl shadow-md overflow-hidden">
      <div className="p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Analysis Reports</h2>
        
        {isProcessing ? (
          <div className="bg-blue-50 border border-blue-100 rounded-lg p-6 text-center">
            <div className="flex justify-center mb-4">
              <div className="relative">
                <div className="w-16 h-16 border-4 border-blue-200 rounded-full"></div>
                <div className="absolute top-0 right-0 bottom-0 left-0 flex items-center justify-center">
                  <Loader2 className="h-8 w-8 text-blue-500 animate-spin" />
                </div>
              </div>
            </div>
            <h3 className="text-lg font-medium text-blue-800">Processing Your Data</h3>
            <p className="text-sm text-blue-600 mt-1">
              We're analyzing the merchant data and generating your reports...
            </p>
          </div>
        ) : generatedReport ? (
          <div className="space-y-6">
            <div className="bg-green-50 border border-green-100 rounded-lg p-6">
              <div className="flex items-start">
                <CheckCircle className="h-6 w-6 text-green-500 mr-3 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="text-lg font-medium text-green-800">Reports Ready</h3>
                  <p className="text-sm text-green-600 mt-1">
                    Your cleaned data file and risk analysis report have been generated successfully.
                  </p>
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Cleaned Data File */}
              <div className="bg-white p-6 rounded-lg border border-gray-200">
                <div className="flex items-center mb-4">
                  <FileSpreadsheet className="h-6 w-6 text-blue-500 mr-2" />
                  <h3 className="text-lg font-medium text-gray-800">Cleaned Data</h3>
                </div>
                <p className="text-sm text-gray-600 mb-4">
                  Processed and cleaned transaction data ready for analysis.
                </p>
                {/* <button
                  onClick={() => {
                    // Handle cleaned file download
                    alert('Downloading cleaned file: ' + generatedReport.cleanedFile);
                  }}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  <FileDown className="h-4 w-4 mr-2" />
                  Download Cleaned Data
                </button> */}
                <a
                  href={generatedReport.cleanedFile || '#'}
                  download
                  className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
                >
                  <FileDown className="h-4 w-4 mr-2" />
                  Download Cleaned Data
                </a>
              </div>

              {/* Risk Analysis Report */}
              <div className="bg-white p-6 rounded-lg border border-gray-200">
                <div className="flex items-center mb-4">
                  <FileSpreadsheet className="h-6 w-6 text-red-500 mr-2" />
                  <h3 className="text-lg font-medium text-gray-800">Risk Report</h3>
                </div>
                <p className="text-sm text-gray-600 mb-4">
                  Detailed risk analysis with merchant categorization and recommendations.
                </p>
                {/* <button
                  onClick={() => {
                    // Handle risk report download
                    alert('Downloading risk report: ' + generatedReport.riskReport);
                  }}
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-red-500 hover:bg-red-600"
                >
                  <FileDown className="h-4 w-4 mr-2" />
                  Download Risk Report
                </button> */}
                <a
                  href={generatedReport.riskReport || '#'}
                  download
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-md text-sm font-medium text-white bg-red-500 hover:bg-red-600"
                >
                  <FileDown className="h-4 w-4 mr-2" />
                  Download Risk Report
                </a>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-200">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Report Summary</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white p-4 rounded-md border border-gray-200">
                  <p className="text-xs uppercase text-gray-500 font-medium">Merchants Analyzed</p>
                  <p className="text-2xl font-semibold text-gray-800 mt-1">248</p>
                </div>
                <div className="bg-white p-4 rounded-md border border-gray-200">
                  <p className="text-xs uppercase text-gray-500 font-medium">Whitelist Candidates</p>
                  <p className="text-2xl font-semibold text-green-600 mt-1">195</p>
                </div>
                <div className="bg-white p-4 rounded-md border border-gray-200">
                  <p className="text-xs uppercase text-gray-500 font-medium">Blacklist Candidates</p>
                  <p className="text-2xl font-semibold text-red-600 mt-1">53</p>
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </section>
  );
};