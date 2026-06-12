import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import api from '../services/api';
import { Heart } from 'lucide-react';
import type { MarsPhoto } from '../types';

const STALE_TIME = 60 * 60 * 1000;

export default function MarsPhotos() {
  const [rover, setRover] = useState('curiosity');
  const [camera, setCamera] = useState('');
  const [sol, setSol] = useState(1000);
  const [page, setPage] = useState(1);
  const [selectedPhoto, setSelectedPhoto] = useState<MarsPhoto | null>(null);

  const { data, isLoading, error } = useQuery<{ photos: MarsPhoto[] }>({
    queryKey: ['mars', rover, camera, sol, page],
    queryFn: () =>
      api.get('/space/mars-photos', { params: { rover, camera: camera || undefined, sol, page } }).then((r) => r.data),
    staleTime: STALE_TIME,
    gcTime: STALE_TIME,
  });

  const saveFavorite = async (photo: MarsPhoto) => {
    await api.post('/favorites/', {
      item_type: 'mars',
      item_payload: photo,
    });
    alert('Mars photo saved to favorites!');
  };

  const photos = data?.photos ?? [];

  return (
    <div>
      <div className="page-header">
        <h1>Mars Rover Photos</h1>
        <p>Images captured by NASA's Mars rovers</p>
      </div>

      <div style={{ display: 'flex', gap: 12, marginBottom: 24, flexWrap: 'wrap', alignItems: 'center' }}>
        <select className="input" value={rover} onChange={(e) => { setRover(e.target.value); setPage(1); }} id="mars-rover-select">
          <option value="curiosity">Curiosity</option>
          <option value="opportunity">Opportunity</option>
          <option value="spirit">Spirit</option>
        </select>
        <select className="input" value={camera} onChange={(e) => { setCamera(e.target.value); setPage(1); }} id="mars-camera-select">
          <option value="">All Cameras</option>
          <option value="FHAZ">FHAZ</option>
          <option value="RHAZ">RHAZ</option>
          <option value="MAST">MAST</option>
          <option value="CHEMCAM">CHEMCAM</option>
          <option value="MAHLI">MAHLI</option>
          <option value="MARDI">MARDI</option>
          <option value="NAVCAM">NAVCAM</option>
          <option value="PANCAM">PANCAM</option>
          <option value="MINITES">MINITES</option>
        </select>
        <div className="input-group" style={{ width: 120 }}>
          <label htmlFor="mars-sol" style={{ display: 'none' }}>Sol</label>
          <input id="mars-sol" type="number" className="input" placeholder="Sol" value={sol} onChange={(e) => { setSol(Number(e.target.value)); setPage(1); }} min={0} />
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center', marginLeft: 'auto' }}>
          <button className="btn btn-ghost btn-sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Prev</button>
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>Page {page}</span>
          <button className="btn btn-ghost btn-sm" onClick={() => setPage((p) => p + 1)}>Next</button>
        </div>
      </div>

      {isLoading && (
        <div className="loading-container"><div className="spinner" /><p>Loading Mars photos...</p></div>
      )}
      {error && <div className="error-box">Failed to load Mars photos.</div>}

      {!isLoading && photos.length === 0 && (
        <div className="card" style={{ textAlign: 'center', padding: 40 }}>
          <p style={{ color: 'var(--text-muted)' }}>No photos found for Sol {sol}. Try a different sol value.</p>
        </div>
      )}

      <div className="grid grid-4">
        {photos.map((p) => (
          <div key={p.id} className="card hover-scale" style={{ padding: 0, overflow: 'hidden', cursor: 'pointer', transition: 'transform 0.2s' }} onClick={() => setSelectedPhoto(p)}>
            <img src={p.img_src} alt={`Mars ${p.camera.name}`} style={{ width: '100%', height: 200, objectFit: 'cover' }} />
            <div style={{ padding: '12px 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span className="badge badge-primary" style={{ marginBottom: 4 }}>{p.camera.name}</span>
                <p className="text-sm" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{p.earth_date}</p>
              </div>
              <button className="btn btn-ghost btn-sm" onClick={(e) => { e.stopPropagation(); saveFavorite(p); }} title="Save"><Heart size={14} /></button>
            </div>
          </div>
        ))}
      </div>

      {selectedPhoto && (
        <div className="modal-overlay" onClick={() => setSelectedPhoto(null)} style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0,0,0,0.85)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 20, animation: 'fadeIn 0.2s' }}>
          <div className="modal-content card" onClick={(e) => e.stopPropagation()} style={{ maxWidth: 800, width: '100%', maxHeight: '90vh', overflowY: 'auto', position: 'relative', padding: 24 }}>
            <button className="btn btn-ghost" onClick={() => setSelectedPhoto(null)} style={{ position: 'absolute', top: 16, right: 16, zIndex: 10 }}>Close</button>
            <img src={selectedPhoto.img_src} alt={`Mars ${selectedPhoto.camera.name}`} style={{ width: '100%', maxHeight: '50vh', objectFit: 'contain', backgroundColor: '#000', borderRadius: '8px' }} />
            <div style={{ padding: '20px 0 0' }}>
              <h2 style={{ marginBottom: 16 }}>Mars Rover: {selectedPhoto.rover.name}</h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16, borderTop: '1px solid var(--border-color)', paddingTop: 16 }}>
                <div>
                  <p style={{ margin: '4px 0', color: 'var(--text-secondary)' }}><strong style={{ color: 'var(--text-color)' }}>Camera:</strong> {selectedPhoto.camera.full_name} ({selectedPhoto.camera.name})</p>
                  <p style={{ margin: '4px 0', color: 'var(--text-secondary)' }}><strong style={{ color: 'var(--text-color)' }}>Earth Date:</strong> {selectedPhoto.earth_date}</p>
                  <p style={{ margin: '4px 0', color: 'var(--text-secondary)' }}><strong style={{ color: 'var(--text-color)' }}>Martian Sol:</strong> {selectedPhoto.sol}</p>
                </div>
                <div>
                  <p style={{ margin: '4px 0', color: 'var(--text-secondary)' }}><strong style={{ color: 'var(--text-color)' }}>Rover Status:</strong> <span style={{ textTransform: 'capitalize', color: selectedPhoto.rover.status === 'active' ? 'var(--success-color)' : 'var(--text-secondary)' }}>{selectedPhoto.rover.status}</span></p>
                  <button className="btn btn-primary" onClick={() => saveFavorite(selectedPhoto)} style={{ marginTop: 12 }}>
                    <Heart size={16} style={{ marginRight: 8 }} /> Save to Favorites
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
