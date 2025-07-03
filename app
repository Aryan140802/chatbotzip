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
    // Remove cookie for root path
    document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`;
    // Attempt to remove cookie for every path segment
    const pathSegments = window.location.pathname.split('/');
    let path = '';
    for (let i = 0; i < pathSegments.length; i++) {
      path += (path.endsWith('/') ? '' : '/') + pathSegments[i];
      document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=${path};`;
    }
  }
}

// Function to conditionally disable inspect element
function useDisableInspectElement(enabled) {
  useEffect(() => {
    if (!enabled) return;

    document.oncontextmenu = function() {
    return false;
}

    const handleKeyDown = (e) => {
      // F12
      if (e.keyCode === 123) {
        e.preventDefault();
        e.stopPropagation();
      }
      // Ctrl+Shift+I/J/C/U, Ctrl+U (view source), Cmd+Opt+I (Mac)
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
      document.removeEventListener('contextmenu',oncontextmenu );
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('dragstart', handleDragStart);
      document.removeEventListener('keydown', handleSelectStart);
    };
  }, [enabled]);
}

// Login API call to get userLevel and other details
async function loginApi(username, password) {
  const response = await fetch('https://10.191.171.12:5443/PyPortal/EISHome/newLogin/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ username, password })
  });

  return response.json(); // should contain userLevel and other info
}

// Logout API call
async function callLogoutAPI(username) {
  try {
    const response = await fetch('https://10.191.171.12:5443/PyPortal/EISHome/newLogout/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({
        username: username,
        timestamp: new Date().toISOString()
      })
    });

    if (!response.ok) {
      console.warn('Logout API call failed:', response.status, response.statusText);
    } else {
      console.log('Logout API call successful');
    }
  } catch (error) {
    console.error('Error calling logout API:', error);
    // Don't prevent logout even if API call fails
  }
}

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [chatbotMinimized, setChatbotMinimized] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [username, setUsername] = useState('');
  const [announcement, setAnnouncement] = useState('');
  const [showAnnouncementPopup, setShowAnnouncementPopup] = useState(false);
  const [userLevel, setUserLevel] = useState('');
  const inactivityTimer = useRef(null);

  // Inactivity time limit in ms (30 minutes)
  const INACTIVITY_LIMIT = 30 * 60 * 1000;

  // Only disable inspect for users other than L1
  useDisableInspectElement(userLevel && userLevel !== 'ADMIN');

  // Check for existing login session on app load
  useEffect(() => {
    const storedUsername = localStorage.getItem('username');
    const storedLoginTime = localStorage.getItem('loginTime');
    const storedUserLevel = localStorage.getItem('userlevel');
    if (storedUsername && storedLoginTime && storedUserLevel) {
      setUsername(storedUsername);
      setUserLevel(storedUserLevel);
      setIsLoggedIn(true);
    }
  }, []);

  // Set login timestamp and userLevel on login
  const handleLogin = async (user, password) => {
    try {
      const loginData = await loginApi(user, password);
      const now = Date.now();
      setUsername(user);

      setIsLoggedIn(true);
      localStorage.setItem('username', user);

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

  // On login from persisted session, fetch announcement
  useEffect(() => {
    if (isLoggedIn && !announcement) {
      (async () => {
        const ann = await fetchLatestAnnouncement();
        setAnnouncement(ann);
        if (ann) setShowAnnouncementPopup(true);
      })();
    }
    // eslint-disable-next-line
  }, [isLoggedIn]);

  // Logout and flush session storage, local storage, cookies, and caches
  const handleLogout = async () => {
    await callLogoutAPI(username);

    setIsLoggedIn(false);
    setUsername('');

    localStorage.clear();
    sessionStorage.clear();
    clearAllCookies();

    if ('caches' in window) {
      caches.keys().then((names) => {
        for (let name of names) {
          caches.delete(name);
        }
      });
    }
    // Optionally, redirect or show a message here
  };

  // Auto logout after 30 min of inactivity
  useEffect(() => {
    if (!isLoggedIn) return;

    const resetInactivityTimer = () => {
      if (inactivityTimer.current) clearTimeout(inactivityTimer.current);
      inactivityTimer.current = setTimeout(() => {
        alert('You have been logged out due to 30 minutes of inactivity.');
        handleLogout();
      }, INACTIVITY_LIMIT);
    };

    // List of events indicating user activity
    const events = ['mousemove', 'keydown', 'mousedown', 'touchstart', 'scroll'];

    // Add event listeners
    events.forEach(event =>
      window.addEventListener(event, resetInactivityTimer, true)
    );

    // Start timer initially
    resetInactivityTimer();

    // Cleanup event listeners and timer on unmount or logout
    return () => {
      events.forEach(event =>
        window.removeEventListener(event, resetInactivityTimer, true)
      );
      if (inactivityTimer.current) clearTimeout(inactivityTimer.current);
    };
  }, [isLoggedIn]);

  if (!isLoggedIn) {
    // Login component must now provide both username and password to handleLogin
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
