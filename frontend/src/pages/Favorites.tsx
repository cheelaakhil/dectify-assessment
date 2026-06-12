import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';
import type { Favorite } from '../types';
import { Trash2, Star } from 'lucide-react';

export default function Favorites() {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery<Favorite[]>({
    queryKey: ['favorites'],
    queryFn: () => api.get('/favorites/').then((r) => r.data),
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => api.delete(`/favorites/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['favorites'] }),
  });

  const favorites = data ?? [];

  const typeLabels: Record<string, string> = {
    apod: 'APOD',
    mars: 'Mars Photo',
    asteroid: 'Asteroid',
    eonet: 'Earth Event',
  };

  const typeBadgeClass: Record<string, string> = {
    apod: 'badge-primary',
    mars: 'badge-success',
    asteroid: 'badge-danger',
    eonet: 'badge-warning',
  };

  return (
    <div>
      <div className="page-header">
        <h1>My Favorites</h1>
        <p>{favorites.length} saved items</p>
      </div>

      {isLoading && (
        <div className="loading-container"><div className="spinner" /><p>Loading favorites...</p></div>
      )}
      {error && <div className="error-box">Failed to load favorites.</div>}

      {!isLoading && favorites.length === 0 && (
        <div className="card" style={{ textAlign: 'center', padding: 60 }}>
          <Star size={40} style={{ color: 'var(--text-muted)', marginBottom: 16 }} />
          <h3 style={{ color: 'var(--text-secondary)', marginBottom: 8 }}>No favorites yet</h3>
          <p style={{ color: 'var(--text-muted)' }}>Save items from any NASA page to see them here.</p>
        </div>
      )}

      <div className="grid grid-2">
        {favorites.map((fav) => {
          const payload = fav.item_payload as { title?: string; name?: string };
          return (
            <div key={fav.id} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 12 }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <span className={`badge ${typeBadgeClass[fav.item_type] ?? 'badge-primary'}`} style={{ marginBottom: 8 }}>
                    {typeLabels[fav.item_type] ?? fav.item_type}
                  </span>
                  <h3 style={{ fontSize: '1rem', marginBottom: 4, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {payload.title || payload.name || `${fav.item_type} item`}
                  </h3>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    Saved {new Date(fav.saved_at).toLocaleDateString()}
                  </p>
                </div>
                <button
                  className="btn btn-danger btn-sm"
                  onClick={() => deleteMutation.mutate(fav.id)}
                  disabled={deleteMutation.isPending}
                  title="Remove"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
