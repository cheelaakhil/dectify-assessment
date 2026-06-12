import { useQuery } from '@tanstack/react-query';
import api from '../services/api';
import type { EonetEvent } from '../types';
import { Heart } from 'lucide-react';

const STALE_TIME = 60 * 60 * 1000;

export default function EarthEvents() {
  const { data, isLoading, error } = useQuery<{ events: EonetEvent[] }>({
    queryKey: ['eonet'],
    queryFn: () => api.get('/space/earth-events').then((r) => r.data),
    staleTime: STALE_TIME,
    gcTime: STALE_TIME,
  });

  const saveFavorite = async (event: EonetEvent) => {
    await api.post('/favorites/', { item_type: 'eonet', item_payload: event });
    alert('Event saved to favorites!');
  };

  const events = data?.events ?? [];

  return (
    <div>
      <div className="page-header">
        <h1>Earth Events</h1>
        <p>Natural events tracked by NASA's EONET</p>
      </div>

      {isLoading && (
        <div className="loading-container"><div className="spinner" /><p>Loading earth events...</p></div>
      )}
      {error && <div className="error-box">Failed to load earth events.</div>}

      <div className="grid grid-2">
        {events.map((e, i) => {
          const images = ['/event-placeholder.png', '/event-placeholder-2.png', '/event-placeholder-3.png'];
          const imgSrc = images[i % images.length];
          return (
          <div key={e.id} className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <img src={imgSrc} alt="Earth Event" style={{ width: '100%', height: 160, objectFit: 'cover', opacity: 0.8 }} />
            <div style={{ padding: 20 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
              <div>
                <h3 style={{ fontSize: '1rem', marginBottom: 8 }}>{e.title}</h3>
                <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 8 }}>
                  {e.categories.map((c) => (
                    <span key={c.id} className="badge badge-warning">{c.title}</span>
                  ))}
                </div>
                {e.geometry?.[0] && (
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Last reported: {new Date(e.geometry[0].date).toLocaleDateString()} &middot;
                    Coords: [{e.geometry[0].coordinates.join(', ')}]
                  </p>
                )}
              </div>
              <button className="btn btn-ghost btn-sm" onClick={() => saveFavorite(e)}><Heart size={14} /></button>
              </div>
            </div>
          </div>
          );
        })}
      </div>
    </div>
  );
}
