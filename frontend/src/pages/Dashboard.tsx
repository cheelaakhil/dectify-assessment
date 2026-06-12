import { useQuery } from '@tanstack/react-query';
import api from '../services/api';
import type { DashboardData, Apod, MarsPhoto, Asteroid } from '../types';
import { Sun, Globe2, Target, Flame, AlertTriangle } from 'lucide-react';
import './Dashboard.css';

const STALE_TIME = 60 * 60 * 1000; // 1 hour

export default function Dashboard() {
  const { data, isLoading, error } = useQuery<DashboardData>({
    queryKey: ['dashboard'],
    queryFn: () => api.get('/space/dashboard').then((r) => r.data),
    staleTime: STALE_TIME,
    gcTime: STALE_TIME,
  });

  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="spinner" />
        <p>Fetching data from NASA...</p>
      </div>
    );
  }

  if (error) {
    return <div className="error-box">Failed to load dashboard data.</div>;
  }

  if (!data) return null;

  const apod = 'error' in data.apod ? null : (data.apod as Apod);
  const hasApodError = 'error' in data.apod;

  const marsPhotos =
    'error' in data.mars_photos ? [] : (data.mars_photos as { photos: MarsPhoto[] }).photos?.slice(0, 4) ?? [];
  const hasMarsError = 'error' in data.mars_photos;

  const asteroidEntries = 'error' in data.asteroids ? [] : Object.values(
    (data.asteroids as { near_earth_objects: Record<string, Asteroid[]> }).near_earth_objects ?? {}
  ).flat().slice(0, 4);
  const hasAsteroidError = 'error' in data.asteroids;

  const events =
    'error' in data.earth_events ? [] : ((data.earth_events as { events: { id: string; title: string; categories?: { id: string; title: string }[] }[] }).events ?? []).slice(0, 4);
  const hasEventError = 'error' in data.earth_events;

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1>Mission Control</h1>
        <p>Your daily space intelligence briefing</p>
      </div>

      {/* APOD Hero */}
      <section className="dash-section">
        <h2 className="dash-section-title"><Sun size={18} /> Astronomy Picture of the Day</h2>
        {hasApodError ? (
          <div className="error-box"><AlertTriangle size={16} /> APOD service unavailable</div>
        ) : apod && (
          <div className="apod-hero card">
            {apod.media_type === 'image' ? (
              <img src={apod.url} alt={apod.title} className="apod-img" />
            ) : (
              <iframe src={apod.url} title={apod.title} className="apod-img" allowFullScreen />
            )}
            <div className="apod-info">
              <h3>{apod.title}</h3>
              <p className="apod-date">{apod.date}</p>
              <p className="apod-desc">{apod.explanation.slice(0, 300)}...</p>
            </div>
          </div>
        )}
      </section>

      {/* Mars Photos */}
      <section className="dash-section">
        <h2 className="dash-section-title"><Globe2 size={18} /> Mars Rover Photos</h2>
        {hasMarsError ? (
          <div className="error-box"><AlertTriangle size={16} /> Mars photos service unavailable</div>
        ) : (
          <div className="grid grid-4">
            {marsPhotos.map((p) => (
              <div key={p.id} className="card mars-card">
                <img src={p.img_src} alt={`Mars ${p.camera.name}`} />
                <div className="mars-card-info">
                  <span className="badge badge-primary">{p.camera.name}</span>
                  <span className="text-sm">{p.earth_date}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>

      {/* Asteroids */}
      <section className="dash-section">
        <h2 className="dash-section-title"><Target size={18} /> Near-Earth Asteroids</h2>
        {hasAsteroidError ? (
          <div className="error-box"><AlertTriangle size={16} /> Asteroid service unavailable</div>
        ) : (
          <div className="grid grid-2">
            {asteroidEntries.map((a: Asteroid, i: number) => {
              const images = ['/asteroid-placeholder.png', '/asteroid-placeholder-2.png', '/asteroid-placeholder-3.png'];
              const imgSrc = images[i % images.length];
              return (
              <div key={a.id} className="card asteroid-card" style={{ padding: 0, overflow: 'hidden' }}>
                <img src={imgSrc} alt="Asteroid" style={{ width: '100%', height: 100, objectFit: 'cover', opacity: 0.8 }} />
                <div style={{ padding: '16px' }}>
                  <div className="asteroid-header" style={{ marginBottom: 12 }}>
                    <h4 style={{ margin: 0 }}>{a.name}</h4>
                    {a.is_potentially_hazardous_asteroid && (
                      <span className="badge badge-danger">Hazardous</span>
                    )}
                  </div>
                <div className="asteroid-stats">
                  <div>
                    <span className="stat-label">Diameter</span>
                    <span className="stat-value">
                      {a.estimated_diameter?.kilometers?.estimated_diameter_min?.toFixed(2)} –{' '}
                      {a.estimated_diameter?.kilometers?.estimated_diameter_max?.toFixed(2)} km
                    </span>
                  </div>
                  {a.close_approach_data?.[0] && (
                    <div>
                      <span className="stat-label">Miss Distance</span>
                      <span className="stat-value">
                        {Number(a.close_approach_data[0].miss_distance?.kilometers).toLocaleString()} km
                      </span>
                    </div>
                  )}
                </div>
              </div>
              </div>
              );
            })}
          </div>
        )}
      </section>

      {/* Earth Events */}
      <section className="dash-section">
        <h2 className="dash-section-title"><Flame size={18} /> Earth Events (EONET)</h2>
        {hasEventError ? (
          <div className="error-box"><AlertTriangle size={16} /> Earth events service unavailable</div>
        ) : (
          <div className="grid grid-2">
            {events.map((e: { id: string; title: string; categories?: { id: string; title: string }[] }, i: number) => {
              const images = ['/event-placeholder.png', '/event-placeholder-2.png', '/event-placeholder-3.png'];
              const imgSrc = images[i % images.length];
              return (
              <div key={e.id} className="card event-card" style={{ padding: 0, overflow: 'hidden' }}>
                <img src={imgSrc} alt="Earth Event" style={{ width: '100%', height: 100, objectFit: 'cover', opacity: 0.8 }} />
                <div style={{ padding: '16px' }}>
                  <h4 style={{ margin: '0 0 8px 0' }}>{e.title}</h4>
                  <div className="event-meta">
                    {e.categories?.map((c: { id: string; title: string }) => (
                      <span key={c.id} className="badge badge-warning">{c.title}</span>
                    ))}
                  </div>
                </div>
              </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
