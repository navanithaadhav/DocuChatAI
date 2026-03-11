import React from 'react';
import ChatPage from './pages/ChatPage';

function App() {
  return (
    <div className="min-h-screen bg-background text-text-primary selection:bg-primary/30">
      <div className="fixed inset-0 z-[-1] bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(120,119,198,0.15),rgba(255,255,255,0))]"></div>
      <ChatPage />
    </div>
  );
}

export default App;
