import React, { useState, useEffect, useRef } from 'react';
import Header from './components/Header.jsx';
import Footer from './components/Footer';
import Menu from './components/Menu';
import Dashboard from './components/Dashboard';
import Chatbot from './components/ChatBot';
import Login from './components/Login';
import './App.css';
import { fetchLatestAnnouncement } from './api/PostApi';

// Robust function to clear all cookies (within JS limitations)
function clearAllCookies() {
  const cookies = document.cookie.split(";");
  for (const cookie of cookies) {
    const eqPos = cookie.indexOf("=");
    const name = eqPos > -1 ? cookie.substr(0, eqPos).trim() : cookie.trim();
    document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
    const pathSegments = window.location.pathname.split('/');
    let path = '';
    for (let i = 0; i < pathSegments.length; i++) {
      path += (path.endsWith('/') ? '' : '/') + pathSegments[i];
      document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=${path};`;
    }
  }
}

// -- Disable Inspect Element Feature --
function useDisableInspectElement(enabled) {
  useEffect(() => {
    if (!enabled) return;

    const handleContextMenu = (e) => e.preventDefault();
    document.addEventListener('contextmenu', handleContextMenu);

    const handleKeyDown = (e) => {
      if (e.keyCode === 123) { e.preventDefault(); e.stopPropagation(); }
      if (
        (e.ctrlKey && e.shiftKey && ['I', 'J', 'C', 'U'].includes(e.key.toUpperCase())) ||
        (e.ctrlKey && e.key.toUpperCase() === 'U') ||
        (e.metaKey && e.altKey && e.key.toUpperCase() === 'I')
      ) {
        e.preventDefault();
        e.stopPropagation();
      }
    };
    document.addEventListener('keydown', handleKeyDown);

    const handleDragStart = (e) => e.preventDefault();
    document.addEventListener('dragstart', handleDragStart);

    const handleSelectStart = (e) => {
      if (e.ctrlKey && e.key === 'a') {
        e.preventDefault();
        e.stopPropagation();
      }
    };
    document.addEventListener('keydown', handleSelectStart);

    return () => {
      document.removeEventListener('contextmenu', handleContextMenu);
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('dragstart', handleDragStart);
      document.removeEventListener('keydown', handleSelectStart);
    };
  }, [enabled]);
}

// NEW: API call for login that returns userLevel, etc.
async function loginApi(username, password) {
  const response = await fetch('https://10.191.171.12:5443/PyPortal/EISHome/newLogin/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ username, password })
  });
  if (!response.ok) throw new Error('Login failed');
  return response.json(); // should contain userLevel etc.
}

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [chatbotMinimized, setChatbotMinimized] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [username, setUsername] = useState('');
  const [announcement, setAnnouncement] = useState('');
  const [showAnnouncementPopup, setShowAnnouncementPopup] = useState(false);
  const [userLevel, setUserLevel] = useState(''); // NEW
  const inactivityTimer = useRef(null);

  const INACTIVITY_LIMIT = 30 * 60 * 1000;

  // Conditionally enable disable-inspect based on userLevel
  useDisableInspectElement(userLevel && userLevel !== 'L1');

  // Check for existing login session on app load
  useEffect(() => {
    const storedUsername = localStorage.getItem('username');
    const storedLoginTime = localStorage.getItem('loginTime');
    const storedUserLevel = localStorage.getItem('userLevel');
    if (storedUsername && storedLoginTime && storedUserLevel) {
      setUsername(storedUsername);
      setUserLevel(storedUserLevel);
      setIsLoggedIn(true);
    }
  }, []);

  // Set login timestamp on login
  const handleLogin = async (user, password) => {
    try {
      // Use your login API
      const loginData = await loginApi(user, password);
      const now = Date.now();
      setUsername(user);
      setUserLevel(loginData.userLevel); // Set userLevel from API payload
      setIsLoggedIn(true);
      localStorage.setItem('username', user);
      localStorage.setItem('userLevel', loginData.userLevel);
      localStorage.setItem('loginTime', now.toString());
      sessionStorage.setItem('loginTime', now.toString());

      // Fetch announcement and show popup
      const ann = await fetchLatestAnnouncement();
      setAnnouncement(ann);
      if (ann) setShowAnnouncementPopup(true);
    } catch (err) {
      alert('Login failed: ' + err.message);
    }
  };

  useEffect(() => {
    if (isLoggedIn && !announcement) {
      (async () => {
        const ann = await fetchLatestAnnouncement();
        setAnnouncement(ann);
        if (ann) setShowAnnouncementPopup(true);
      })();
    }
  }, [isLoggedIn]);

  // ...rest of your code remains the same...

  // --- Pass handleLogin with new signature to Login component ---
  if (!isLoggedIn) {
    return <Login onLogin={handleLogin} />;
  }

  return (
    <div>
      <Header
        darkMode={darkMode}
        setDarkMode={setDarkMode}
        username={username}
        onLogout={handleLogout}
      />
      {/* Announcement Popup */}
      {showAnnouncementPopup && announcement &&
        <div className="announcement-popup-overlay">
          <div className="announcement-popup">
            <button
              className="announcement-popup-close"
              onClick={() => setShowAnnouncementPopup(false)}
              aria-label="Close announcement"
            >
              ×
            </button>
            <div className="announcement-popup-content">
              <h3>Announcement</h3>
              <div>{announcement}</div>
            </div>
          </div>
        </div>
      }
      {!chatbotMinimized && <div className="app-background" />}
      <div className={`main ${isSidebarOpen ? "sidebar-open" : "sidebar-collapsed"}`}>
        <Menu
          isSidebarOpen={isSidebarOpen}
          setIsSidebarOpen={setIsSidebarOpen}
        />
        <Dashboard isSidebarOpen={isSidebarOpen} />
        <Chatbot setChatbotMinimized={setChatbotMinimized} username={username} />
      </div>
      <Footer />
    </div>
  );
}

export default App;
