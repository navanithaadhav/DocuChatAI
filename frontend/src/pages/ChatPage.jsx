import React, { useState } from 'react';
import UploadPDF from '../components/UploadPDF';
import ChatBox from '../components/ChatBox';

const ChatPage = () => {
  const [docStats, setDocStats] = useState({ totalFiles: 0, totalChunks: 0 });
  const [showUpload, setShowUpload] = useState(true);

  const handleUploadSuccess = (stats) => {
    setDocStats({
       totalFiles: docStats.totalFiles + 1,
       totalChunks: stats.total
    });
    // Auto collapse upload area after successful upload to focus on chat
    setTimeout(() => {
        setShowUpload(false);
    }, 1500);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-start p-6 pt-12 max-w-7xl mx-auto space-y-8 animate-fade-in relative z-10">
      
      {/* Header */}
      <header className="text-center space-y-4 w-full max-w-3xl">
        <div className="inline-flex items-center justify-center space-x-2 bg-primary/10 px-4 py-1.5 rounded-full border border-primary/20 mb-2 shadow-[0_0_20px_rgba(103,58,183,0.15)]">
          <span className="w-2 h-2 rounded-full bg-primary animate-pulse"></span>
          <span className="text-xs font-semibold text-primary-light uppercase tracking-wider">RAG Pipeline Active</span>
        </div>
        <h1 className="text-5xl md:text-6xl font-bold tracking-tight">
          <span className="text-white">Docu</span>
          <span className="text-gradient">Chat</span>
          <span className="text-white"> AI</span>
        </h1>
        <p className="text-text-secondary text-lg max-w-xl mx-auto leading-relaxed">
          Upload any PDF document and instantly get intelligent answers with source references.
        </p>
      </header>

      {/* Main Content Area */}
      <main className="w-full flex-1 flex flex-col gap-6 max-w-5xl h-[calc(100vh-16rem)]">
        
        {/* Upload Section (Collapsible) */}
        <div className={`transition-all duration-500 origin-top overflow-hidden w-full flex justify-center ${showUpload ? 'max-h-96 opacity-100 mb-6' : 'max-h-0 opacity-0 mb-0'}`}>
           <UploadPDF onUploadSuccess={handleUploadSuccess} />
        </div>

        {/* Status Bar & Toggle */}
        <div className="w-full max-w-4xl mx-auto flex justify-between items-end px-2">
           <div className="text-sm flex gap-4">
              <div className="bg-surfaceHighlight border border-white/5 py-1.5 px-3 rounded-lg shadow-sm">
                 <span className="text-text-secondary">Documents: </span>
                 <span className="text-white font-medium">{docStats.totalFiles}</span>
              </div>
              <div className="bg-surfaceHighlight border border-white/5 py-1.5 px-3 rounded-lg shadow-sm hidden md:block">
                 <span className="text-text-secondary">Embeddings: </span>
                 <span className="text-white font-medium">{docStats.totalChunks} Chunks</span>
              </div>
           </div>

           <button 
             onClick={() => setShowUpload(!showUpload)}
             className="text-sm text-primary-light hover:text-white transition-colors underline underline-offset-4 decoration-primary/30"
           >
             {showUpload ? 'Hide Upload Area' : 'Upload Another Document'}
           </button>
        </div>

        {/* Chat Interface */}
        <div className="w-full flex-1 min-h-0 relative shadow-2xl rounded-3xl pb-6">
           {/* Decorative blurred blobs behind chatbox */}
           <div className="absolute top-1/2 left-10 w-64 h-64 bg-primary/20 rounded-full blur-[100px] -z-10 pointer-events-none transform -translate-y-1/2"></div>
           <div className="absolute bottom-10 right-10 w-64 h-64 bg-pink-500/10 rounded-full blur-[100px] -z-10 pointer-events-none"></div>
           
           <ChatBox hasDocuments={docStats.totalFiles > 0} />
        </div>

      </main>
    </div>
  );
};

export default ChatPage;
