/**
 * TypeScript types for the frontend.
 */

export interface User {
  id: number;
  name: string;
  email: string;
}

export interface Apod {
  title: string;
  explanation: string;
  url: string;
  hdurl?: string;
  media_type: string;
  date: string;
  copyright?: string;
}

export interface MarsPhoto {
  id: number;
  sol: number;
  img_src: string;
  earth_date: string;
  camera: {
    name: string;
    full_name: string;
  };
  rover: {
    name: string;
    status: string;
  };
}

export interface Asteroid {
  id: string;
  name: string;
  nasa_jpl_url: string;
  estimated_diameter: {
    kilometers: {
      estimated_diameter_min: number;
      estimated_diameter_max: number;
    };
  };
  is_potentially_hazardous_asteroid: boolean;
  close_approach_data: Array<{
    close_approach_date: string;
    miss_distance: {
      kilometers: string;
    };
    relative_velocity: {
      kilometers_per_hour: string;
    };
  }>;
}

export interface EonetEvent {
  id: string;
  title: string;
  description?: string;
  categories: Array<{ id: string; title: string }>;
  geometry: Array<{ date: string; type: string; coordinates: number[] }>;
}

export interface DashboardData {
  apod: Apod | { error: string };
  mars_photos: { photos: MarsPhoto[] } | { error: string };
  asteroids: { near_earth_objects: Record<string, Asteroid[]>; element_count: number } | { error: string };
  earth_events: { events: EonetEvent[] } | { error: string };
}

export interface Favorite {
  id: number;
  item_type: string;
  item_payload: Record<string, unknown>;
  saved_at: string;
}
