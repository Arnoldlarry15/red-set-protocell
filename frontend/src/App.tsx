import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Analytics } from '@vercel/analytics/react';
import LandingPage from './pages/LandingPage';
import EarlyAccessPage from './pages/EarlyAccessPage';
import AboutPage from './pages/AboutPage';
import LoginPage from './pages/LoginPage';
import Dashboard from './pages/Dashboard';
import AdminDashboard from './pages/AdminDashboard';
import AdminEarlyAccessPage from './pages/AdminEarlyAccessPage';
import PRManagement from './pages/PRManagement';
import Navigation from './components/Navigation';
import { User } from './types';
import './styles/globals.css';

function App() {
  // NOTE: Auth state is intentionally in-memory only for now.
  // TODO(production-auth): Add persistent token lifecycle (access + refresh,
  // expiry tracking, and refresh-on-401) when multi-user production auth is introduced.
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
        {/* Public Routes */}
        <Route 
          path="/" 
          element={
            authenticated ? 
              <Navigate to="/dashboard" replace /> : 
              <LandingPage />
          } 
        />
        <Route 
          path="/early-access" 
          element={<EarlyAccessPage />}
        />
        <Route 
          path="/about" 
          element={<AboutPage />}
        />
        <Route 
          path="/login" 
          element={
            authenticated ? 
              <Navigate to="/dashboard" replace /> : 
              <LoginPage onAuth={handleAuth} />
          } 
        />

        {/* Protected Routes */}
        <Route 
          path="/dashboard" 
          element={
            authenticated ? 
              <Dashboard apiKey={apiKey} backend={backend} /> : 
              <Navigate to="/login" replace />
          } 
        />
        <Route 
          path="/admin" 
          element={
            authenticated && user ? 
              <AdminDashboard user={user} apiKey={apiKey} /> : 
              <Navigate to="/login" replace />
          } 
        />
        <Route
          path="/admin/early-access"
          element={
            authenticated && user?.role === 'admin' ?
              <AdminEarlyAccessPage user={user} /> :
              <Navigate to="/login" replace />
          }
        />
        <Route
          path="/pull-requests"
          element={
            authenticated ?
              <PRManagement /> :
              <Navigate to="/login" replace />
          }
        />

        <Route
          path="/pull-requests"
          element={
            authenticated ?
              <PRManagement /> :
              <Navigate to="/login" replace />
          }
        />

        {/* Catch-all redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <Analytics />
    </Router>
  );
}

export default App;
