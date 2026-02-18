import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Analytics } from '@vercel/analytics/react';
import AuthPage from './pages/AuthPage';
import Dashboard from './pages/Dashboard';
import AdminDashboard from './pages/AdminDashboard';
import Navigation from './components/Navigation';
import { User } from './types';
import './styles/globals.css';

function App() {
  const [authenticated, setAuthenticated] = useState(false);
  const [apiKey, setApiKey] = useState('');
  const [backend, setBackend] = useState('openai');
  const [user, setUser] = useState<User | null>(null);

  const handleAuth = (key: string, backendType: string, userData?: User) => {
    setApiKey(key);
    setBackend(backendType);
    setAuthenticated(true);
    if (userData) {
      setUser(userData);
    }
  };

  const handleLogout = () => {
    setAuthenticated(false);
    setApiKey('');
    setBackend('openai');
    setUser(null);
  };

  return (
    <Router>
      {authenticated && <Navigation user={user} onLogout={handleLogout} />}
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
        <Route 
          path="/admin" 
          element={
            authenticated && user ? 
              <AdminDashboard user={user} apiKey={apiKey} /> : 
              <Navigate to="/" replace />
          } 
        />
      </Routes>
      <Analytics />
    </Router>
  );
}

export default App;
