import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Home, Shield, GitPullRequest, LogOut } from 'lucide-react';
import { User } from '../types';

interface NavigationProps {
  user: User | null;
  onLogout: () => void;
}

const Navigation: React.FC<NavigationProps> = ({ user, onLogout }) => {
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="navigation glass-panel">
      <div className="nav-brand">
        <img 
          src="/logo.png" 
          alt="Red Set ProtoCell logo" 
          style={{ width: '32px', height: '32px', objectFit: 'contain' }}
        />
        <span className="nav-title">RED SET PROTOCELL</span>
      </div>

      <div className="nav-links">
        <button
          className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}
          onClick={() => navigate('/dashboard')}
          aria-label="Dashboard"
        >
          <Home size={20} />
          <span>Dashboard</span>
        </button>

        {user && (user.role === 'admin' || user.role === 'researcher') && (
          <button
            className={`nav-link ${isActive('/admin') ? 'active' : ''}`}
            onClick={() => navigate('/admin')}
            aria-label="Admin Panel"
          >
            <Shield size={20} />
            <span>Admin</span>
          </button>
        )}

        <button
          className={`nav-link ${isActive('/pull-requests') ? 'active' : ''}`}
          onClick={() => navigate('/pull-requests')}
          aria-label="Pull Requests"
        >
          <GitPullRequest size={20} />
          <span>Pull Requests</span>
        </button>
      </div>

      <div className="nav-user">
        {user && (
          <div className="user-info">
            <span className="user-name">{user.username}</span>
            <span className="user-role">{user.role}</span>
          </div>
        )}
        <button
          className="nav-link logout"
          onClick={onLogout}
          aria-label="Logout"
        >
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </div>
    </nav>
  );
};

export default Navigation;
