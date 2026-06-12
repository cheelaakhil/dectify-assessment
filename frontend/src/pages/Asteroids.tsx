import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../services/api';
import type { Asteroid } from '../types';
import { Heart, AlertTriangle } from 'lucide-react';

const STALE_TIME = 60 * 60 * 1000;

export default function Asteroids() {
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');

  const { data, isLoading, error } = useQuery<{
    element_count: number;
    near_earth_objects: Record<string, Asteroid[]>;
  }>({
    queryKey: ['asteroids', startDate, endDate],
    queryFn: () => api.get('/space/asteroids', { params: { start_date: startDate || undefined, end_date: endDate || undefined } }).then((r) => r.data),
    staleTime: STALE_TIME,
    gcTime: STALE_TIME,
  });

  const saveFavorite = async (a: Asteroid) => {
    await api.post('/favorites/', { item_type: 'asteroid', item_payload: a });
    alert('Asteroid saved to favorites!');
  };

  const allAsteroids = data
    ? Object.values(data.near_earth_objects).flat()
    : [];

  return (
    <div>
      <div className="page-header">
        <h1>Near-Earth Asteroids</h1>
        <p>
          Today's asteroid feed &middot;{' '}
          {data ? `${data.element_count} objects detected` : 'Loading...'}
        </p>
      </div>

      <div style={{ marginBottom: 24, display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
        <div className="input-group">
          <label htmlFor="start-date" style={{ display: 'none' }}>Start Date</label>
          <input type="date" id="start-date" className="input" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
        </div>
        <span style={{ color: 'var(--text-muted)' }}>to</span>
        <div className="input-group">
          <label htmlFor="end-date" style={{ display: 'none' }}>End Date</label>
          <input type="date" id="end-date" className="input" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
        </div>
        {(startDate || endDate) && (
          <button className="btn btn-ghost btn-sm" onClick={() => { setStartDate(''); setEndDate(''); }}>
            Clear Filters
          </button>
        )}
      </div>

      {isLoading && (
        <div className="loading-container"><div className="spinner" /><p>Scanning for asteroids...</p></div>
      )}
      {error && <div className="error-box">Failed to load asteroid data.</div>}

      {!isLoading && !error && allAsteroids.length === 0 && (
        <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
          <AlertTriangle size={32} style={{ margin: '0 auto 16px', opacity: 0.5 }} />
          <h3>No Asteroids Found</h3>
          <p>Try selecting a different date range.</p>
        </div>
      )}

      <div className="grid grid-2">
        {allAsteroids.map((a, i) => {
          const images = ['/asteroid-placeholder.png', '/asteroid-placeholder-2.png', '/asteroid-placeholder-3.png'];
          const imgSrc = images[i % images.length];
          return (
          <div key={a.id} className="card" style={{ padding: 0, overflow: 'hidden' }}>
            <img src={imgSrc} alt="Asteroid" style={{ width: '100%', height: 160, objectFit: 'cover', opacity: 0.8 }} />
            <div style={{ padding: 20 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
              <div>
                <h3 style={{ fontSize: '1rem', marginBottom: 4 }}>{a.name}</h3>
                {a.is_potentially_hazardous_asteroid && (
                  <span className="badge badge-danger"><AlertTriangle size={10} /> Hazardous</span>
                )}
              </div>
              <button className="btn btn-ghost btn-sm" onClick={() => saveFavorite(a)}><Heart size={14} /></button>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              <div>
                <span className="stat-label">Diameter</span>
                <span className="stat-value">
                  {a.estimated_diameter.kilometers.estimated_diameter_min.toFixed(3)} –{' '}
                  {a.estimated_diameter.kilometers.estimated_diameter_max.toFixed(3)} km
                </span>
              </div>
              {a.close_approach_data[0] && (
                <>
                  <div>
                    <span className="stat-label">Miss Distance</span>
                    <span className="stat-value">
                      {Number(a.close_approach_data[0].miss_distance.kilometers).toLocaleString()} km
                    </span>
                  </div>
                  <div>
                    <span className="stat-label">Velocity</span>
                    <span className="stat-value">
                      {Number(a.close_approach_data[0].relative_velocity.kilometers_per_hour).toLocaleString()} km/h
                    </span>
                  </div>
                  <div>
                    <span className="stat-label">Close Approach</span>
                    <span className="stat-value">{a.close_approach_data[0].close_approach_date}</span>
                  </div>
                </>
              )}
              </div>
            </div>
          </div>
          );
        })}
      </div>
    </div>
  );
}
