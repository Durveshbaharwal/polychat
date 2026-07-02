// PolyChat — App Component
import React from 'react';
import ChatWidget from '@/components/ChatWidget';
import LandingPage from '@/components/landing/LandingPage';

const App: React.FC = () => {
  return (
    <>
      <LandingPage />
      <ChatWidget />
    </>
  );
};

export default App;
