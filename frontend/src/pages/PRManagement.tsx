import React, { useState } from 'react';
import { GitPullRequest, GitMerge, X, RefreshCw, ChevronDown } from 'lucide-react';
import axios from 'axios';
import { API_BASE_URL } from '../utils/config';
import { getUserFriendlyApiError } from '../utils/apiErrors';

interface PullRequest {
  number: number;
  title: string;
  state: string;
  draft: boolean;
  merged: boolean;
  html_url: string;
  body: string;
  user: string | null;
  head: string | null;
  base: string | null;
  created_at: string | null;
  updated_at: string | null;
  mergeable: boolean | null;
}

const MERGE_METHODS = ['merge', 'squash', 'rebase'] as const;
type MergeMethod = (typeof MERGE_METHODS)[number];

const badgeBase: React.CSSProperties = {
  display: 'inline-block',
  padding: '0.1rem 0.5rem',
  borderRadius: '9999px',
  fontSize: '0.7rem',
  fontWeight: 700,
  letterSpacing: '0.03em',
  textTransform: 'uppercase',
};

const badgeStyles: Record<string, React.CSSProperties> = {
  open:   { ...badgeBase, background: 'rgba(74,222,128,0.15)',  color: '#4ade80' },
  closed: { ...badgeBase, background: 'rgba(248,113,113,0.15)', color: '#f87171' },
  merged: { ...badgeBase, background: 'rgba(168,85,247,0.2)',   color: '#c084fc' },
  draft:  { ...badgeBase, background: 'rgba(156,163,175,0.2)',  color: '#9ca3af' },
};

function StatusBadge({ pr }: { pr: PullRequest }) {
  if (pr.merged) return <span style={badgeStyles.merged}>Merged</span>;
  if (pr.state === 'closed') return <span style={badgeStyles.closed}>Closed</span>;
  if (pr.draft) return <span style={badgeStyles.draft}>Draft</span>;
  return <span style={badgeStyles.open}>Open</span>;
}

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '0.5rem 0.75rem',
  borderRadius: '6px',
  border: '1px solid rgba(255,255,255,0.15)',
  background: 'rgba(255,255,255,0.05)',
  color: 'inherit',
  fontSize: '0.9rem',
  outline: 'none',
};

const selectStyle: React.CSSProperties = {
  padding: '0.45rem 2rem 0.45rem 0.6rem',
  borderRadius: '6px',
  border: '1px solid rgba(255,255,255,0.15)',
  background: 'rgba(255,255,255,0.05)',
  color: 'inherit',
  fontSize: '0.875rem',
  appearance: 'none',
  cursor: 'pointer',
  outline: 'none',
};

const primaryButtonStyle: React.CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  padding: '0.5rem 1rem',
  borderRadius: '6px',
  border: '1px solid rgba(99,102,241,0.5)',
  background: 'rgba(99,102,241,0.2)',
  color: '#a5b4fc',
  fontSize: '0.875rem',
  cursor: 'pointer',
};

const actionButtonBase: React.CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: '0.3rem',
  padding: '0.4rem 0.75rem',
  borderRadius: '6px',
  border: '1px solid',
  fontSize: '0.8rem',
  cursor: 'pointer',
};

const PRManagement: React.FC = () => {
  const [owner, setOwner] = useState('');
  const [repo, setRepo] = useState('');
  const [githubToken, setGithubToken] = useState('');
  const [prState, setPrState] = useState<'open' | 'closed' | 'all'>('open');
  const [mergeMethod, setMergeMethod] = useState<MergeMethod>('merge');

  const [prs, setPrs] = useState<PullRequest[]>([]);
  const [loading, setLoading] = useState(false);
  const [fetchError, setFetchError] = useState<string | null>(null);
  const [actionStatus, setActionStatus] = useState<Record<number, string>>({});

  const fetchPRs = async () => {
    if (!owner || !repo || !githubToken) {
      setFetchError('Owner, repository, and GitHub token are required.');
      return;
    }
    setFetchError(null);
    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/github/prs`, {
        owner,
        repo,
        github_token: githubToken,
        state: prState,
      });
      setPrs(response.data.pull_requests);
      setActionStatus({});
    } catch (err) {
      setFetchError(getUserFriendlyApiError(err));
    } finally {
      setLoading(false);
    }
  };

  const closePR = async (prNumber: number) => {
    setActionStatus((prev) => ({ ...prev, [prNumber]: 'closing' }));
    try {
      await axios.post(`${API_BASE_URL}/github/prs/${prNumber}/close`, {
        owner,
        repo,
        github_token: githubToken,
      });
      setActionStatus((prev) => ({ ...prev, [prNumber]: 'closed' }));
      setPrs((prev) =>
        prev.map((pr) => (pr.number === prNumber ? { ...pr, state: 'closed' } : pr))
      );
    } catch (err) {
      setActionStatus((prev) => ({
        ...prev,
        [prNumber]: `error: ${getUserFriendlyApiError(err)}`,
      }));
    }
  };

  const mergePR = async (prNumber: number) => {
    setActionStatus((prev) => ({ ...prev, [prNumber]: 'merging' }));
    try {
      await axios.post(`${API_BASE_URL}/github/prs/${prNumber}/merge`, {
        owner,
        repo,
        github_token: githubToken,
        merge_method: mergeMethod,
      });
      setActionStatus((prev) => ({ ...prev, [prNumber]: 'merged' }));
      setPrs((prev) =>
        prev.map((pr) =>
          pr.number === prNumber ? { ...pr, state: 'closed', merged: true } : pr
        )
      );
    } catch (err) {
      setActionStatus((prev) => ({
        ...prev,
        [prNumber]: `error: ${getUserFriendlyApiError(err)}`,
      }));
    }
  };

  return (
    <div style={{ padding: '2rem', maxWidth: '1100px', margin: '0 auto' }}>
      <h1 style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1.5rem' }}>
        <GitPullRequest size={28} />
        Pull Request Management
      </h1>

      {/* Configuration form */}
      <div className="glass-panel" style={{ padding: '1.5rem', marginBottom: '1.5rem', borderRadius: '8px' }}>
        <h2 style={{ marginBottom: '1rem', fontSize: '1.1rem' }}>Repository Settings</h2>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.25rem', fontSize: '0.875rem', opacity: 0.8 }}>
              Owner / Organization
            </label>
            <input
              type="text"
              value={owner}
              onChange={(e) => setOwner(e.target.value)}
              placeholder="e.g. Arnoldlarry15"
              style={inputStyle}
            />
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.25rem', fontSize: '0.875rem', opacity: 0.8 }}>
              Repository
            </label>
            <input
              type="text"
              value={repo}
              onChange={(e) => setRepo(e.target.value)}
              placeholder="e.g. red-set-protocell"
              style={inputStyle}
            />
          </div>
        </div>

        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.25rem', fontSize: '0.875rem', opacity: 0.8 }}>
            GitHub Personal Access Token
          </label>
          <input
            type="password"
            value={githubToken}
            onChange={(e) => setGithubToken(e.target.value)}
            placeholder="ghp_…"
            style={{ ...inputStyle, width: '100%' }}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.875rem', opacity: 0.8 }}>State:</label>
            <div style={{ position: 'relative' }}>
              <select
                value={prState}
                onChange={(e) => setPrState(e.target.value as 'open' | 'closed' | 'all')}
                style={selectStyle}
              >
                <option value="open">Open</option>
                <option value="closed">Closed</option>
                <option value="all">All</option>
              </select>
              <ChevronDown
                size={14}
                style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', opacity: 0.6 }}
              />
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <label style={{ fontSize: '0.875rem', opacity: 0.8 }}>Merge method:</label>
            <div style={{ position: 'relative' }}>
              <select
                value={mergeMethod}
                onChange={(e) => setMergeMethod(e.target.value as MergeMethod)}
                style={selectStyle}
              >
                {MERGE_METHODS.map((m) => (
                  <option key={m} value={m}>
                    {m.charAt(0).toUpperCase() + m.slice(1)}
                  </option>
                ))}
              </select>
              <ChevronDown
                size={14}
                style={{ position: 'absolute', right: '8px', top: '50%', transform: 'translateY(-50%)', pointerEvents: 'none', opacity: 0.6 }}
              />
            </div>
          </div>

          <button onClick={fetchPRs} disabled={loading} style={primaryButtonStyle}>
            <RefreshCw size={16} style={{ marginRight: '0.4rem' }} />
            {loading ? 'Loading…' : 'Load Pull Requests'}
          </button>
        </div>
      </div>

      {fetchError && (
        <div
          style={{
            color: '#f87171',
            background: 'rgba(239,68,68,0.1)',
            border: '1px solid rgba(239,68,68,0.3)',
            borderRadius: '6px',
            padding: '0.75rem 1rem',
            marginBottom: '1rem',
          }}
        >
          {fetchError}
        </div>
      )}

      {/* PR list */}
      {prs.length > 0 && (
        <div>
          <h2 style={{ marginBottom: '0.75rem', fontSize: '1rem', opacity: 0.8 }}>
            {prs.length} Pull Request{prs.length !== 1 ? 's' : ''}
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {prs.map((pr) => {
              const status = actionStatus[pr.number];
              const isPending = status === 'closing' || status === 'merging';
              const isDone = status === 'closed' || status === 'merged';
              const isErr = status?.startsWith('error:');

              return (
                <div
                  key={pr.number}
                  className="glass-panel"
                  style={{ padding: '1rem 1.25rem', borderRadius: '8px', opacity: isDone ? 0.6 : 1 }}
                >
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      justifyContent: 'space-between',
                      gap: '1rem',
                      flexWrap: 'wrap',
                    }}
                  >
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.3rem', flexWrap: 'wrap' }}>
                        <StatusBadge pr={pr} />
                        <a
                          href={pr.html_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ fontWeight: 600, color: '#93c5fd', textDecoration: 'none', wordBreak: 'break-word' }}
                        >
                          #{pr.number} {pr.title}
                        </a>
                      </div>
                      <div style={{ fontSize: '0.8rem', opacity: 0.6 }}>
                        {pr.user && <span>by {pr.user}</span>}
                        {pr.head && pr.base && <span> · {pr.head} → {pr.base}</span>}
                        {pr.updated_at && (
                          <span> · updated {new Date(pr.updated_at).toLocaleDateString()}</span>
                        )}
                      </div>
                      {isErr && (
                        <div style={{ color: '#f87171', fontSize: '0.8rem', marginTop: '0.3rem' }}>
                          {status.replace('error: ', '')}
                        </div>
                      )}
                      {isDone && (
                        <div style={{ color: '#4ade80', fontSize: '0.8rem', marginTop: '0.3rem', fontWeight: 600 }}>
                          ✓ {status.charAt(0).toUpperCase() + status.slice(1)}
                        </div>
                      )}
                    </div>

                    {!isDone && pr.state === 'open' && (
                      <div style={{ display: 'flex', gap: '0.5rem', flexShrink: 0 }}>
                        <button
                          onClick={() => mergePR(pr.number)}
                          disabled={isPending || pr.draft}
                          title={pr.draft ? 'Cannot merge a draft PR' : 'Merge this pull request'}
                          style={{
                            ...actionButtonBase,
                            background: 'rgba(74,222,128,0.15)',
                            borderColor: 'rgba(74,222,128,0.4)',
                            color: '#4ade80',
                            opacity: pr.draft ? 0.4 : 1,
                            cursor: pr.draft ? 'not-allowed' : 'pointer',
                          }}
                        >
                          <GitMerge size={15} />
                          {status === 'merging' ? 'Merging…' : 'Merge'}
                        </button>
                        <button
                          onClick={() => closePR(pr.number)}
                          disabled={isPending}
                          title="Close this pull request"
                          style={{
                            ...actionButtonBase,
                            background: 'rgba(248,113,113,0.15)',
                            borderColor: 'rgba(248,113,113,0.4)',
                            color: '#f87171',
                            cursor: isPending ? 'not-allowed' : 'pointer',
                          }}
                        >
                          <X size={15} />
                          {status === 'closing' ? 'Closing…' : 'Close'}
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {!loading && prs.length === 0 && !fetchError && (
        <div style={{ textAlign: 'center', opacity: 0.5, marginTop: '3rem' }}>
          <GitPullRequest size={48} style={{ marginBottom: '1rem', opacity: 0.3 }} />
          <p>Enter repository details above and click &ldquo;Load Pull Requests&rdquo;.</p>
        </div>
      )}
    </div>
  );
};

export default PRManagement;
