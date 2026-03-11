import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { FiUploadCloud, FiFileText, FiCheckCircle, FiXCircle, FiLoader } from 'react-icons/fi';
import axios from 'axios';

const UploadPDF = ({ onUploadSuccess }) => {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState(null); // 'idle', 'success', 'error'
  const [statusMessage, setStatusMessage] = useState('');

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const onDrop = useCallback(async (acceptedFiles) => {
    if (!acceptedFiles || acceptedFiles.length === 0) return;

    let hasInvalidFiles = false;
    acceptedFiles.forEach(file => {
      if (file.type !== 'application/pdf') hasInvalidFiles = true;
    });

    if (hasInvalidFiles) {
      setUploadStatus('error');
      setStatusMessage('Please upload valid PDF files only.');
      return;
    }

    setIsUploading(true);
    setUploadStatus(null);

    const formData = new FormData();
    acceptedFiles.forEach(file => {
        formData.append('files', file);
    });

    try {
      const response = await axios.post(`${API_URL}/upload-pdfs`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setUploadStatus('success');
      setStatusMessage(response.data.message || `Successfully processed ${acceptedFiles.length} file(s)`);
      if (onUploadSuccess) {
        onUploadSuccess({
          filename: response.data.filename,
          chunks: response.data.chunks_processed,
          total: response.data.total_documents
        });
      }
    } catch (error) {
      console.error('Upload failed:', error);
      setUploadStatus('error');
      setStatusMessage(error.response?.data?.detail || 'Failed to upload document.');
    } finally {
      setIsUploading(false);

      // Reset status after 5 seconds if success
      if (uploadStatus !== 'error') {
        setTimeout(() => {
          setUploadStatus(null);
          setStatusMessage('');
        }, 5000);
      }
    }
  }, [onUploadSuccess, uploadStatus, API_URL]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    multiple: true,
    disabled: isUploading
  });

  return (
    <div className="w-full flex justify-center animate-fade-in">
      <div
        {...getRootProps()}
        className={`w-full max-w-2xl glass-panel rounded-2xl p-8 transition-all duration-300 ease-in-out border-2 border-dashed
          ${isDragActive ? 'border-primary-light bg-primary/5 scale-[1.02]' : 'border-white/10 hover:border-white/20 hover:bg-white/[0.02]'}
          ${isUploading ? 'opacity-70 cursor-not-allowed' : 'cursor-pointer'}
        `}
      >
        <input {...getInputProps()} />
        <div className="flex flex-col items-center justify-center space-y-4 text-center">

          <div className={`p-4 rounded-full transition-colors duration-300 shadow-lg ${isDragActive ? 'bg-primary/20 text-primary-light' : 'bg-surfaceHighlight text-text-secondary'}`}>
            {isUploading ? (
              <FiLoader className="w-8 h-8 animate-spin text-primary" />
            ) : uploadStatus === 'success' ? (
              <FiCheckCircle className="w-8 h-8 text-green-400" />
            ) : uploadStatus === 'error' ? (
              <FiXCircle className="w-8 h-8 text-red-400" />
            ) : (
              <FiUploadCloud className={`w-8 h-8 ${isDragActive ? 'animate-bounce' : ''}`} />
            )}
          </div>

          <div className="space-y-1">
            <h3 className="text-xl font-semibold text-text-primary tracking-tight">
              {isUploading ? 'Processing Document...' : 'Upload Knowledge Base'}
            </h3>
            <p className="text-sm text-text-secondary">
              {isDragActive
                ? "Drop the PDFs here..."
                : "Drag & drop PDF files here, or click to select"}
            </p>
          </div>

          {/* Status Messages */}
          {statusMessage && (
            <div className={`mt-4 flex items-center gap-2 text-sm px-4 py-2 rounded-full animate-slide-up bg-surfaceHighlight border
              ${uploadStatus === 'success' ? 'text-green-300 border-green-500/20' : 'text-red-300 border-red-500/20'}`}>
              {uploadStatus === 'success' ? <FiCheckCircle /> : <FiXCircle />}
              <span>{statusMessage}</span>
            </div>
          )}

          <div className="mt-8 flex items-center justify-center gap-6 text-xs text-text-secondary/60">
            <div className="flex items-center gap-1.5 backdrop-blur-sm bg-black/20 px-3 py-1.5 rounded-full">
              <FiFileText />
              <span>PDF Only</span>
            </div>
            <div className="flex items-center gap-1.5 backdrop-blur-sm bg-black/20 px-3 py-1.5 rounded-full border border-white/5">
              <span>Up to 20MB</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UploadPDF;
