import { useAuth } from '../context/AuthContext';
import { User, Mail, Calendar } from 'lucide-react';

export default function Profile() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <div>
      <div className="page-header">
        <h1>Profile</h1>
        <p>Your account information</p>
      </div>

      <div className="card" style={{ maxWidth: 500 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 20, marginBottom: 24 }}>
          <div
            style={{
              width: 72,
              height: 72,
              borderRadius: 'var(--radius-lg)',
              background: 'var(--gradient-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '1.5rem',
              fontWeight: 700,
              color: 'white',
            }}
          >
            {user.name.charAt(0).toUpperCase()}
          </div>
          <div>
            <h2 style={{ fontSize: '1.3rem' }}>{user.name}</h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>SpaceToday Explorer</p>
          </div>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px', background: 'var(--bg-glass)', borderRadius: 'var(--radius-md)' }}>
            <User size={18} style={{ color: 'var(--accent-primary)' }} />
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Name</span>
              <p style={{ fontWeight: 500 }}>{user.name}</p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px', background: 'var(--bg-glass)', borderRadius: 'var(--radius-md)' }}>
            <Mail size={18} style={{ color: 'var(--accent-primary)' }} />
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Email</span>
              <p style={{ fontWeight: 500 }}>{user.email}</p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12, padding: '12px 16px', background: 'var(--bg-glass)', borderRadius: 'var(--radius-md)' }}>
            <Calendar size={18} style={{ color: 'var(--accent-primary)' }} />
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>User ID</span>
              <p style={{ fontWeight: 500 }}>#{user.id}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
