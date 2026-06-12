import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Rocket, LayoutDashboard, Sun, Globe2, Target, Flame,
  Heart, User, LogOut
} from 'lucide-react';
import './Navbar.css';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <nav className="navbar">
      <div className="navbar-inner container">
        <NavLink to="/dashboard" className="navbar-brand">
          <Rocket size={22} />
          <span>SpaceToday</span>
        </NavLink>

        <div className="navbar-links">
          <NavLink to="/dashboard" className="nav-link">
            <LayoutDashboard size={16} /> Dashboard
          </NavLink>
          <NavLink to="/apod" className="nav-link">
            <Sun size={16} /> APOD
          </NavLink>
          <NavLink to="/mars-photos" className="nav-link">
            <Globe2 size={16} /> Mars
          </NavLink>
          <NavLink to="/asteroids" className="nav-link">
            <Target size={16} /> Asteroids
          </NavLink>
          <NavLink to="/earth-events" className="nav-link">
            <Flame size={16} /> Events
          </NavLink>
          <NavLink to="/favorites" className="nav-link">
            <Heart size={16} /> Favorites
          </NavLink>
        </div>

        <div className="navbar-user">
          <NavLink to="/profile" className="nav-link user-link">
            <User size={16} />
            <span>{user?.name}</span>
          </NavLink>
          <button onClick={handleLogout} className="btn btn-ghost btn-sm" id="logout-btn">
            <LogOut size={14} /> Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
