import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../services/api';
import { Heart } from 'lucide-react';
import type { Apod } from '../types';

const STALE_TIME = 60 * 60 * 1000;

export default function ApodPage() {
  const [date, setDate] = useState('');

  const { data, isLoading, error } = useQuery<Apod>({
    queryKey: ['apod', date],
    queryFn: () => api.get('/space/apod', { params: date ? { date } : {} }).then((r) => r.data),
    staleTime: STALE_TIME,
    gcTime: STALE_TIME,
  });

  const saveFavorite = async () => {
    if (!data) return;
    await api.post('/favorites/', {
      item_type: 'apod',
      item_payload: data,
    });
    alert('Added to favorites!');
  };

  return (
    <div>
      <div className="page-header">
        <h1>Astronomy Picture of the Day</h1>
        <p>Daily cosmic images from NASA</p>
      </div>

      <div style={{ marginBottom: 24, display: 'flex', gap: 12, alignItems: 'center' }}>
        <input
          type="date"
          className="input"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          max={new Date().toISOString().split('T')[0]}
          id="apod-date-picker"
        />
        {date && (
          <button className="btn btn-ghost btn-sm" onClick={() => setDate('')}>
            Today
          </button>
        )}
      </div>

      {isLoading && (
        <div className="loading-container">
          <div className="spinner" />
          <p>Loading APOD...</p>
        </div>
      )}

      {error && <div className="error-box">Failed to load APOD.</div>}

      {data && (
        <div className="card" style={{ overflow: 'hidden' }}>
          {data.media_type === 'image' ? (
            <img
              src={data.hdurl || data.url}
              alt={data.title}
              style={{ width: '100%', maxHeight: 600, objectFit: 'contain', borderRadius: 'var(--radius-md)', marginBottom: 20 }}
            />
          ) : (
            <iframe
              src={data.url}
              title={data.title}
              style={{ width: '100%', height: 400, border: 'none', borderRadius: 'var(--radius-md)', marginBottom: 20 }}
              allowFullScreen
            />
          )}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 16, flexWrap: 'wrap' }}>
            <div>
              <h2 style={{ fontSize: '1.4rem', marginBottom: 4 }}>{data.title}</h2>
              <p style={{ color: 'var(--accent-secondary)', fontSize: '0.85rem', fontWeight: 600 }}>
                {data.date} {data.copyright && `| © ${data.copyright}`}
              </p>
            </div>
            <button className="btn btn-primary btn-sm" onClick={saveFavorite} id="save-apod">
              <Heart size={14} /> Save
            </button>
          </div>
          <p style={{ marginTop: 16, color: 'var(--text-secondary)', lineHeight: 1.8 }}>{data.explanation}</p>
        </div>
      )}
    </div>
  );
}
