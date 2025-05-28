import React, { useState, useRef } from 'react';
import { Upload, FileText, AlertCircle, Loader2 } from 'lucide-react';

interface FileUploadSectionProps {
  uploadedFile: File | null;
  onFileUpload: (file: File | null) => void;
  isProcessing: boolean;
  onBackendResponse: (res: { risk_report: string; clean_file: string }) => void;
  onTerminalOutput: (line: string) => void;
}

export const FileUploadSection: React.FC<FileUploadSectionProps> = ({
  uploadedFile,
  onFileUpload,
  isProcessing,
  onBackendResponse,
  onTerminalOutput,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => setIsDragging(false);

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      validateAndUploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      validateAndUploadFile(e.target.files[0]);
    }
  };

  const validateAndUploadFile = (file: File) => {
    setUploadError(null);
    const validExtensions = ['.xlsx', '.xls', '.csv'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

    if (!validExtensions.includes(fileExtension)) {
      setUploadError('Please upload an Excel file (.xlsx, .xls) or CSV file.');
      return;
    }

    const maxSize = 50 * 1024 * 1024;
    if (file.size > maxSize) {
      setUploadError('File size exceeds 50MB limit.');
      return;
    }

    onFileUpload(file);
  };

  const handleProcessFile = async () => {
    if (!uploadedFile) return;

    setUploadError(null);
    onTerminalOutput('⏳ Uploading file...');

    const formData = new FormData();
    formData.append('file', uploadedFile);

    try {
      const res = await fetch('http://localhost:8000/risk-assessment/', {
        method: 'POST',
        body: formData,
      });

      const json = await res.json();
      if (!res.ok) throw new Error(json?.error || 'Unknown error');

      onTerminalOutput('✅ File processed successfully.');
      onBackendResponse({
        risk_report: json.risk_report,
        clean_file: json.clean_file,
      });
    } catch (err: unknown) {
      const message =
        typeof err === 'object' && err !== null && 'message' in err
          ? String((err as { message?: unknown }).message)
          : 'Upload failed';
      setUploadError(message);
      onTerminalOutput('❌ ' + message);
    }
  };

  const handleReplaceFile = () => {
    onFileUpload(null);
    fileInputRef.current?.click();
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' bytes';
    else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
    else return (bytes / 1048576).toFixed(1) + ' MB';
  };

  return (
    <section className="bg-white rounded-xl shadow-md overflow-hidden">
      <div className="p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">Upload Excel for MCC Analysis</h2>

        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-all duration-300 ${
            isDragging
              ? 'border-red-500 bg-red-50'
              : uploadedFile
              ? 'border-green-500 bg-green-50'
              : 'border-gray-300 hover:border-red-300'
          }`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {!uploadedFile ? (
            <div className="space-y-4">
              <div className="flex justify-center">
                <Upload className="h-12 w-12 text-gray-400" />
              </div>
              <p className="text-lg font-medium text-gray-700">
                Drag and drop your Excel file here
              </p>
              <p className="text-sm text-gray-500 mt-1">Or click to browse your files</p>
              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-500 hover:bg-red-600 focus:outline-none"
              >
                Browse Files
              </button>
              <input
                type="file"
                ref={fileInputRef}
                className="hidden"
                accept=".xlsx,.xls,.csv"
                onChange={handleFileInputChange}
              />
              <p className="text-xs text-gray-500">
                Supported formats: .xlsx, .xls, .csv (Max 50MB)
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex justify-center">
                <FileText className="h-12 w-12 text-green-500" />
              </div>
              <div>
                <p className="text-lg font-medium text-gray-700">{uploadedFile.name}</p>
                <p className="text-sm text-gray-500 mt-1">{formatFileSize(uploadedFile.size)}</p>
              </div>
              <div className="flex justify-center space-x-3">
                <button
                  type="button"
                  onClick={handleReplaceFile}
                  className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none"
                >
                  Replace
                </button>
                <button
                  type="button"
                  onClick={handleProcessFile}
                  disabled={isProcessing}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-500 hover:bg-red-600 focus:outline-none disabled:bg-red-300"
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="animate-spin h-4 w-4 mr-2" />
                      Processing...
                    </>
                  ) : (
                    'Process File'
                  )}
                </button>
              </div>
            </div>
          )}
        </div>

        {uploadError && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md flex items-start">
            <AlertCircle className="h-5 w-5 text-red-500 mr-2 flex-shrink-0 mt-0.5" />
            <p className="text-sm text-red-600">{uploadError}</p>
          </div>
        )}

        <div className="mt-6">
          <h3 className="text-sm font-medium text-gray-500 mb-2">What happens next?</h3>
          <ol className="list-decimal list-inside text-sm text-gray-600 space-y-1 ml-2">
            <li>Upload your Excel file containing merchant transaction data</li>
            <li>Our system analyzes the MCC codes and transaction patterns</li>
            <li>A comprehensive report is generated indicating merchant risk levels</li>
            <li>Download and review the analysis report</li>
          </ol>
        </div>
      </div>
    </section>
  );
};