import React, { useCallback, useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import { CheckCircle2, Download, Eye, Mail, Trash2 } from 'lucide-react';
import { API_BASE_URL } from '../utils/config';
import { User } from '../types';
import '../styles/NewComponents.css';

type SignupStatus = 'pending' | 'verified';

interface EarlyAccessSignup {
  id: number;
  email: string;
  role: string | null;
  status: SignupStatus;
  submitted_at: string;
  created_at: string;
  updated_at: string;
  verified_at: string | null;
}

interface AdminEarlyAccessPageProps {
  user: User;
}

const PAGE_SIZE = 20;

const downloadBlob = (content: string, mimeType: string, filename: string) => {
  const blob = new Blob([content], { type: mimeType });
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  window.URL.revokeObjectURL(url);
};

const AdminEarlyAccessPage: React.FC<AdminEarlyAccessPageProps> = ({ user }) => {
  const [signups, setSignups] = useState<EarlyAccessSignup[]>([]);
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set());
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [role, setRole] = useState('');
  const [status, setStatus] = useState('');
  const [search, setSearch] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const headers = useMemo(() => (user.token ? { 'X-User-Token': user.token } : undefined), [user.token]);

  const fetchSignups = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const response = await axios.get(`${API_BASE_URL}/admin/early-access-signups`, {
        params: {
          page,
          page_size: PAGE_SIZE,
          role: role || undefined,
          status: status || undefined,
          email_query: search || undefined,
          start_date: startDate ? new Date(startDate).toISOString() : undefined,
          end_date: endDate ? new Date(endDate).toISOString() : undefined,
        },
        headers,
      });
      setSignups(response.data.signups ?? []);
      setTotal(response.data.count ?? 0);
      setSelectedIds(new Set());
    } catch {
      setError('Unable to load early-access signups.');
    } finally {
      setLoading(false);
    }
  }, [endDate, headers, page, role, search, startDate, status]);

  useEffect(() => {
    fetchSignups();
  }, [fetchSignups]);

  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const toggleSelection = (id: number) => {
    setSelectedIds((previous) => {
      const next = new Set(previous);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const selectedRows = signups.filter((signup) => selectedIds.has(signup.id));

  const exportAll = async (format: 'csv' | 'json') => {
    if (format === 'json') {
      const response = await axios.get(`${API_BASE_URL}/admin/early-access-signups/export`, {
        params: { format },
        headers,
      });
      downloadBlob(JSON.stringify(response.data.signups ?? [], null, 2), 'application/json', 'early-access-signups.json');
      return;
    }
    const response = await axios.get(`${API_BASE_URL}/admin/early-access-signups/export`, {
      params: { format },
      headers,
      responseType: 'text',
    });
    downloadBlob(response.data as string, 'text/csv', 'early-access-signups.csv');
  };

  const exportSelected = (format: 'csv' | 'json') => {
    if (!selectedRows.length) {
      return;
    }
    if (format === 'json') {
      downloadBlob(JSON.stringify(selectedRows, null, 2), 'application/json', 'early-access-selected.json');
      return;
    }
    const header = ['id', 'email', 'role', 'status', 'submitted_at', 'verified_at'];
    const body = selectedRows.map((row) =>
      [row.id, row.email, row.role ?? '', row.status, row.submitted_at, row.verified_at ?? '']
        .map((value) => `"${String(value).replace(/"/g, '""')}"`)
        .join(',')
    );
    downloadBlob([header.join(','), ...body].join('\n'), 'text/csv', 'early-access-selected.csv');
  };

  const markVerified = async (id: number) => {
    await axios.post(`${API_BASE_URL}/admin/early-access-signups/${id}/verify`, undefined, { headers });
    fetchSignups();
  };

  const removeSignup = async (id: number) => {
    await axios.delete(`${API_BASE_URL}/admin/early-access-signups/${id}`, { headers });
    fetchSignups();
  };

  const viewDetails = (signup: EarlyAccessSignup) => {
    window.alert(JSON.stringify(signup, null, 2));
  };

  return (
    <div className="infra-dashboard early-access-admin">
      <div className="dashboard-header">
        <h2 className="dashboard-title">
          <Mail size={24} />
          Early Access Signups ({user.username})
        </h2>
        <div className="export-controls">
          <button className="btn btn-secondary" onClick={() => exportSelected('csv')} disabled={!selectedRows.length}>
            Export Selected CSV
          </button>
          <button className="btn btn-secondary" onClick={() => exportSelected('json')} disabled={!selectedRows.length}>
            Export Selected JSON
          </button>
          <button className="btn btn-primary" onClick={() => exportAll('csv')}>
            <Download size={16} /> Export All CSV
          </button>
          <button className="btn btn-primary" onClick={() => exportAll('json')}>
            <Download size={16} /> Export All JSON
          </button>
        </div>
      </div>

      <div className="glass-panel filter-grid">
        <input
          className="form-control"
          placeholder="Search by email"
          value={search}
          onChange={(event) => {
            setSearch(event.target.value);
            setPage(1);
          }}
        />
        <select className="form-control" value={role} onChange={(event) => setRole(event.target.value)}>
          <option value="">All roles</option>
          <option value="developer">Developer</option>
          <option value="researcher">Researcher</option>
          <option value="security">Security</option>
          <option value="investor">Investor</option>
          <option value="other">Other</option>
        </select>
        <select className="form-control" value={status} onChange={(event) => setStatus(event.target.value)}>
          <option value="">All statuses</option>
          <option value="pending">Pending</option>
          <option value="verified">Verified</option>
        </select>
        <input className="form-control" type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} />
        <input className="form-control" type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} />
        <button className="btn btn-primary" onClick={fetchSignups}>
          Apply Filters
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}
      {loading ? (
        <div className="loading-state">Loading signups...</div>
      ) : (
        <table className="sessions-table">
          <thead>
            <tr>
              <th></th>
              <th>Email</th>
              <th>Role</th>
              <th>Submitted At</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {signups.map((signup) => (
              <tr key={signup.id}>
                <td>
                  <input type="checkbox" checked={selectedIds.has(signup.id)} onChange={() => toggleSelection(signup.id)} />
                </td>
                <td>{signup.email}</td>
                <td>{signup.role || 'N/A'}</td>
                <td>{new Date(signup.submitted_at).toLocaleString()}</td>
                <td>{signup.status}</td>
                <td>
                  <button className="btn btn-sm btn-secondary" onClick={() => viewDetails(signup)}>
                    <Eye size={14} /> View Details
                  </button>
                  <button
                    className="btn btn-sm btn-secondary"
                    onClick={() => markVerified(signup.id)}
                    disabled={signup.status === 'verified'}
                  >
                    <CheckCircle2 size={14} /> Mark Verified
                  </button>
                  <button className="btn btn-sm btn-secondary" onClick={() => removeSignup(signup.id)}>
                    <Trash2 size={14} /> Delete
                  </button>
                </td>
              </tr>
            ))}
            {!signups.length && (
              <tr>
                <td colSpan={6} className="empty-state">
                  No signups found for the selected filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      )}

      <div className="pagination-controls">
        <button className="btn btn-secondary" onClick={() => setPage((value) => Math.max(1, value - 1))} disabled={page === 1}>
          Previous
        </button>
        <span>
          Page {page} of {totalPages}
        </span>
        <button
          className="btn btn-secondary"
          onClick={() => setPage((value) => Math.min(totalPages, value + 1))}
          disabled={page >= totalPages}
        >
          Next
        </button>
      </div>
    </div>
  );
};

export default AdminEarlyAccessPage;
