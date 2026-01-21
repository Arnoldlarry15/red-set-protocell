import React, { useState, useEffect } from 'react';
import { Users, UserPlus, Shield, Eye, Wrench } from 'lucide-react';
import axios from 'axios';
import { User } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

interface UserManagementProps {
  currentUser: User;
}

const UserManagement: React.FC<UserManagementProps> = ({ currentUser }) => {
  const [users, setUsers] = useState<User[]>([]);
  const [showAddUser, setShowAddUser] = useState(false);
  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    role: 'observer' as 'admin' | 'researcher' | 'observer',
    password: '',
  });

  const isAdmin = currentUser.role === 'admin';

  useEffect(() => {
    if (isAdmin) {
      fetchUsers();
    }
  }, [isAdmin]);

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/auth/users`);
      setUsers(response.data.users);
    } catch (error) {
      console.error('Error fetching users:', error);
    }
  };

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post(`${API_BASE_URL}/api/auth/register`, newUser);
      alert('User created successfully');
      setShowAddUser(false);
      setNewUser({ username: '', email: '', role: 'observer', password: '' });
      fetchUsers();
    } catch (error) {
      console.error('Error creating user:', error);
      alert('Error creating user');
    }
  };

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'admin':
        return <Shield size={18} className="role-icon admin" />;
      case 'researcher':
        return <Wrench size={18} className="role-icon researcher" />;
      case 'observer':
        return <Eye size={18} className="role-icon observer" />;
      default:
        return null;
    }
  };

  const getRoleDescription = (role: string) => {
    switch (role) {
      case 'admin':
        return 'Full system access, user management';
      case 'researcher':
        return 'Start runs, configure experiments, view results';
      case 'observer':
        return 'View-only access to dashboards and results';
      default:
        return '';
    }
  };

  if (!isAdmin) {
    return (
      <div className="user-management">
        <div className="access-denied glass-panel">
          <Shield size={48} />
          <h3>Admin Access Required</h3>
          <p>You need administrator privileges to access user management.</p>
          <p className="current-role">Your role: <strong>{currentUser.role}</strong></p>
        </div>
      </div>
    );
  }

  return (
    <div className="user-management">
      <div className="management-header">
        <h2 className="section-title">
          <Users size={24} />
          User Management
        </h2>
        <button onClick={() => setShowAddUser(!showAddUser)} className="btn btn-primary">
          <UserPlus size={18} />
          Add User
        </button>
      </div>

      {showAddUser && (
        <div className="add-user-form glass-panel">
          <h3>Add New User</h3>
          <form onSubmit={handleAddUser}>
            <div className="form-group">
              <label>Username</label>
              <input
                type="text"
                value={newUser.username}
                onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                required
                className="form-control"
              />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input
                type="email"
                value={newUser.email}
                onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                required
                className="form-control"
              />
            </div>
            <div className="form-group">
              <label>Role</label>
              <select
                value={newUser.role}
                onChange={(e) => setNewUser({ ...newUser, role: e.target.value as 'admin' | 'researcher' | 'observer' })}
                className="form-control"
              >
                <option value="observer">Observer</option>
                <option value="researcher">Researcher</option>
                <option value="admin">Admin</option>
              </select>
              <small className="form-help">{getRoleDescription(newUser.role)}</small>
            </div>
            <div className="form-group">
              <label>Password</label>
              <input
                type="password"
                value={newUser.password}
                onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                required
                className="form-control"
              />
            </div>
            <div className="form-actions">
              <button type="submit" className="btn btn-primary">Create User</button>
              <button type="button" onClick={() => setShowAddUser(false)} className="btn btn-secondary">
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="users-list">
        <h3>Current Users</h3>
        <div className="users-grid">
          {users.map((user) => (
            <div key={user.username} className="user-card glass-panel">
              <div className="user-header">
                <h4>{user.username}</h4>
                <div className="user-role">
                  {getRoleIcon(user.role)}
                  <span>{user.role}</span>
                </div>
              </div>
              <div className="user-details">
                <p className="user-email">{user.email}</p>
                <p className="user-permissions">{getRoleDescription(user.role)}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="role-info glass-panel">
        <h3>Role Permissions</h3>
        <div className="roles-grid">
          <div className="role-card">
            <div className="role-header">
              {getRoleIcon('admin')}
              <h4>Admin</h4>
            </div>
            <ul>
              <li>Manage users and permissions</li>
              <li>Configure system settings</li>
              <li>Start and stop runs</li>
              <li>Access all dashboards</li>
              <li>Export all data</li>
            </ul>
          </div>
          <div className="role-card">
            <div className="role-header">
              {getRoleIcon('researcher')}
              <h4>Researcher</h4>
            </div>
            <ul>
              <li>Start and configure runs</li>
              <li>Save experiment configs</li>
              <li>Access all dashboards</li>
              <li>Export session data</li>
              <li>View historical comparisons</li>
            </ul>
          </div>
          <div className="role-card">
            <div className="role-header">
              {getRoleIcon('observer')}
              <h4>Observer</h4>
            </div>
            <ul>
              <li>View live sessions</li>
              <li>View historical data</li>
              <li>Access read-only dashboards</li>
              <li>Export limited data</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default UserManagement;
