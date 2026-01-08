import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import AuthPage from './pages/AuthPage';
import Dashboard from './pages/Dashboard';
import './styles/globals.css';

function App() {
  const [authenticated, setAuthenticated] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [backend, setBackend] = useState('openai');

  const handleAuth = (key: string, backendType: string) => {
    setApiKey(key);
    setBackend(backendType);
    setAuthenticated(true);
  };

  return (
    <Router>
      <Routes>
        <Route 
          path="/" 
          element={
            authenticated ? 
              <Navigate to="/dashboard" replace /> : 
              <AuthPage onAuth={handleAuth} />
          } 
        />
        <Route 
          path="/dashboard" 
          element={
            authenticated ? 
              <Dashboard apiKey={apiKey} backend={backend} /> : 
              <Navigate to="/" replace />
          } 
        />
      </Routes>
    </Router>
  );
}

export default App;
