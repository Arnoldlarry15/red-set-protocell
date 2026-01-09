import React, { useState } from 'react';
import { Database, BarChart, Users, Settings } from 'lucide-react';
import InfraDashboard from '../components/InfraDashboard';
import ModelVersionComparison from '../components/ModelVersionComparison';
import UserManagement from '../components/UserManagement';
import RemoteControl from '../components/RemoteControl';
import { User } from '../types';
import '../styles/NewComponents.css';

interface AdminDashboardProps {
  user: User;
  apiKey: string;
}

const AdminDashboard: React.FC<AdminDashboardProps> = ({ user, apiKey }) => {
  const [activeTab, setActiveTab] = useState<'infra' | 'comparison' | 'users' | 'remote'>('infra');

  return (
    <div className="admin-dashboard">
      <div className="admin-nav">
        <button
          className={`nav-button ${activeTab === 'infra' ? 'active' : ''}`}
          onClick={() => setActiveTab('infra')}
        >
          <Database size={20} />
          Infrastructure
        </button>
        <button
          className={`nav-button ${activeTab === 'comparison' ? 'active' : ''}`}
          onClick={() => setActiveTab('comparison')}
        >
          <BarChart size={20} />
          Model Comparison
        </button>
        <button
          className={`nav-button ${activeTab === 'users' ? 'active' : ''}`}
          onClick={() => setActiveTab('users')}
        >
          <Users size={20} />
          User Management
        </button>
        <button
          className={`nav-button ${activeTab === 'remote' ? 'active' : ''}`}
          onClick={() => setActiveTab('remote')}
        >
          <Settings size={20} />
          Remote Control
        </button>
      </div>

      <div className="admin-content">
        {activeTab === 'infra' && <InfraDashboard />}
        {activeTab === 'comparison' && <ModelVersionComparison />}
        {activeTab === 'users' && <UserManagement currentUser={user} />}
        {activeTab === 'remote' && <RemoteControl apiKey={apiKey} userRole={user.role} />}
      </div>
    </div>
  );
};

export default AdminDashboard;
