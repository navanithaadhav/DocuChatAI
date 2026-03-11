import React from 'react';
import ReactMarkdown from 'react-markdown';
import { FiUser, FiCpu, FiAlertCircle } from 'react-icons/fi';

const MessageBubble = ({ message }) => {
  const isUser = message.role === 'user';
  const isError = message.role === 'error';

  return (
    <div className={`flex w-full ${isUser ? 'justify-end' : 'justify-start'} mb-6 px-4 animate-slide-up`}>
      <div className={`flex max-w-[85%] ${isUser ? 'flex-row-reverse' : 'flex-row'} gap-4`}>
        
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-lg
          ${isUser 
            ? 'bg-gradient-to-tr from-purple-500 to-indigo-500' 
            : isError
              ? 'bg-red-500/20 text-red-400'
              : 'bg-surfaceHighlight border border-white/10 text-primary-light'
          }`}
        >
          {isUser ? <FiUser size={14} /> : isError ? <FiAlertCircle size={14} /> : <FiCpu size={14} />}
        </div>

        {/* Message Content */}
        <div className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
          <div className={`px-5 py-3.5 rounded-2xl shadow-sm text-sm/relaxed
            ${isUser 
              ? 'bg-primary text-white rounded-tr-none' 
              : isError
                ? 'bg-red-500/10 text-red-200 border border-red-500/20 rounded-tl-none'
                : 'bg-surfaceHighlight border border-white/5 text-text-primary rounded-tl-none glass-panel'
            }`}
          >
            {isUser ? (
              <p>{message.content}</p>
            ) : (
              <div className="prose prose-invert max-w-none prose-sm prose-p:leading-relaxed prose-pre:bg-black/40 prose-pre:border prose-pre:border-white/10">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            )}
          </div>
          
          {/* Sources Chips */}
          {!isUser && message.sources && message.sources.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              <span className="text-xs text-text-secondary/60 py-1 mr-1">Sources:</span>
              {message.sources.map((source, idx) => (
                <div key={idx} className="group relative">
                  <span className="px-2 py-1 bg-surface border border-white/5 rounded-full text-[10px] text-text-secondary hover:text-white hover:border-primary/50 transition-colors cursor-help truncate max-w-[150px] inline-block">
                    {source.source} {source.page !== 'N/A' && `(p. ${source.page})`}
                  </span>
                  {/* Tooltip */}
                  <div className="absolute bottom-full left-0 mb-2 w-64 p-3 bg-surface border border-white/10 rounded-xl shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                    <p className="text-xs text-text-primary line-clamp-4 leading-relaxed tracking-wide">
                      "{source.content}"
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MessageBubble;
