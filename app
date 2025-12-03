import React, { useState, useEffect, useRef, useCallback } from 'react';
import Header from './components/Header.jsx';
import Footer from './components/Footer';
import Menu from './components/Menu';
import Dashboard from './components/Dashboard';
import Chatbot from './components/ChatBot';
import Login from './components/Login';
import './App.css';
import { 
  fetchLatestAnnouncement, 
  validateSession, 
  hasSessionData, 
  clearAllStorage,
  setLogoutHandler,
  checkSession 
} from './api/PostApi';

// Function to conditionally disable inspect element
function useDisableInspectElement(enabled) {
  useEffect(() => {
    if (!enabled) return;

    document.oncontextmenu = function() {
      return false;
    };

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
      document.removeEventListener('contextmenu', document.oncontextmenu);
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('dragstart', handleDragStart);
      document.removeEventListener('keydown', handleSelectStart);
    };
  }, [enabled]);
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
  const [appLoading, setAppLoading] = useState(true);
  const [sessionExpired, setSessionExpired] = useState(false);
  const inactivityTimer = useRef(null);
  const sessionCheckTimer = useRef(null);
  const heartbeatTimer = useRef(null);

  // Inactivity time limit in ms (60 minutes)
  const INACTIVITY_LIMIT = 60 * 60 * 1000;
  // Session check interval (5 minutes)
  const SESSION_CHECK_INTERVAL = 5 * 60 * 1000;

  // Define allowed user levels for Chatbot access
  const CHATBOT_ALLOWED_LEVELS = ['ADMIN', 'L2', 'Banker','L1'];
  const CHATBOT_BLOCKED_LEVELS = ['Support'];

  // Check if current user has access to chatbot
  const hasChatbotAccess = CHATBOT_ALLOWED_LEVELS.includes(userLevel) &&
    !CHATBOT_BLOCKED_LEVELS.includes(userLevel);

  // Only disable inspect for users other than ADMIN
  useDisableInspectElement(userLevel && userLevel !== 'ADMIN');

  // Function to perform logout with cleanup
  const performLogout = useCallback(async (showAlert = true, reason = 'Session expired') => {
    console.log(`Performing logout: ${reason}`);
    
    // Prevent multiple logout calls
    if (sessionExpired) return;
    
    setSessionExpired(true);
    
    if (showAlert && reason === 'Session expired') {
      alert('Your session has expired. Please log in again.');
    }
    
    setIsLoggedIn(false);
    setUsername('');
    setUserLevel('');
    setAnnouncement('');
    
    // Clear all storage
    clearAllStorage();
    
    // Clear all timers
    if (inactivityTimer.current) clearTimeout(inactivityTimer.current);
    if (sessionCheckTimer.current) clearInterval(sessionCheckTimer.current);
    if (heartbeatTimer.current) clearInterval(heartbeatTimer.current);
    
    console.log('Logout complete');
  }, [sessionExpired]);

  // Setup logout handler for API interceptor
  useEffect(() => {
    setLogoutHandler((reason) => performLogout(true, reason));
  }, [performLogout]);

  // Check for existing login session on app load with validation
  useEffect(() => {
    const checkAndRestoreSession = async () => {
      // First check if session data exists
      if (!hasSessionData()) {
        console.log('App.js - No session data found');
        setAppLoading(false);
        return;
      }

      const storedUsername = localStorage.getItem('username');
      const storedUserLevel = localStorage.getItem('userlevel');
      const storedSessionId = localStorage.getItem('sessionid');

      console.log('App.js - Validating stored session:', {
        storedUsername,
        storedUserLevel,
        hasSessionId: !!storedSessionId
      });

      // Validate the session before restoring
      try {
        const sessionCheck = await validateSession();
        
        if (sessionCheck.isValid) {
          console.log('App.js - Session valid, restoring...');
          setUsername(storedUsername);
          setUserLevel(storedUserLevel);
          setIsLoggedIn(true);

          // Set login time if not already set
          if (!localStorage.getItem('loginTime')) {
            localStorage.setItem('loginTime', Date.now().toString());
          }

          console.log('App.js - Session restored successfully');
        } else {
          console.log('App.js - Session invalid:', sessionCheck.reason);
          await performLogout(false, 'Invalid session on load');
        }
      } catch (error) {
        console.error('App.js - Session validation error:', error);
        await performLogout(false, 'Session validation failed');
      }

      setAppLoading(false);
    };

    checkAndRestoreSession();
  }, [performLogout]);

  // On login from persisted session, fetch announcement
  useEffect(() => {
    if (isLoggedIn && !announcement) {
      (async () => {
        try {
          const ann = await fetchLatestAnnouncement();
          setAnnouncement(ann);
          if (ann) setShowAnnouncementPopup(true);
        } catch (err) {
          console.error('Error fetching announcement:', err);
        }
      })();
    }
  }, [isLoggedIn, announcement]);

  // Start session validation timer
  useEffect(() => {
    if (!isLoggedIn) return;

    const startSessionCheck = () => {
      // Clear any existing timer
      if (sessionCheckTimer.current) clearInterval(sessionCheckTimer.current);
      
      // Set up new interval to check session validity
      sessionCheckTimer.current = setInterval(async () => {
        try {
          // First check if session data still exists
          if (!hasSessionData()) {
            console.log('Session data missing during check');
            await performLogout(true, 'Session data missing');
            return;
          }

          const sessionCheck = await checkSession();
          if (!sessionCheck.isValid) {
            console.log('Session check failed:', sessionCheck.reason);
            await performLogout(true, 'Session validation failed');
          } else {
            console.log('Session check passed');
          }
        } catch (error) {
          console.error('Session check error:', error);
          await performLogout(true, 'Session check error');
        }
      }, SESSION_CHECK_INTERVAL);
    };

    startSessionCheck();

    return () => {
      if (sessionCheckTimer.current) clearInterval(sessionCheckTimer.current);
    };
  }, [isLoggedIn, performLogout]);

  // Handle login from Login component
  const handleLogin = async (user, loginData = {}) => {
    try {
      console.log('App.js - handleLogin called with:', { user, loginData });

      const now = Date.now();
      const level = loginData.userLevel || localStorage.getItem('userlevel') || '';

      // Store all data to localStorage
      localStorage.setItem('username', user);
      localStorage.setItem('userlevel', level);
      localStorage.setItem('loginTime', now.toString());

      if (loginData.sessionid) {
        localStorage.setItem('sessionid', loginData.sessionid);
      }
      if (loginData.uid) {
        localStorage.setItem('uidd', loginData.uid);
      }

      // Set local state
      setUsername(user);
      setUserLevel(level);
      setIsLoggedIn(true);
      setSessionExpired(false);

      console.log('App.js - Login successful');

    } catch (err) {
      console.error('App.js - Login error:', err);
      alert('Login failed: ' + err.message);
    }
  };

  // Updated logout handler
  const handleLogout = async () => {
    console.log('App.js - Manual logout initiated for user:', username);
    await performLogout(false, 'User manually logged out');
  };

  // Auto logout after 60 min of inactivity
  useEffect(() => {
    if (!isLoggedIn) return;

    const resetInactivityTimer = () => {
      if (inactivityTimer.current) clearTimeout(inactivityTimer.current);
      inactivityTimer.current = setTimeout(() => {
        alert('You have been logged out due to 60 minutes of inactivity.');
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

  // Heartbeat check for session data
  useEffect(() => {
    if (!isLoggedIn) return;

    const checkSessionData = () => {
      if (!hasSessionData()) {
        console.log('Heartbeat check: Session data missing');
        performLogout(true, 'Session data lost');
      }
    };

    heartbeatTimer.current = setInterval(checkSessionData, 30000);

    return () => {
      if (heartbeatTimer.current) clearInterval(heartbeatTimer.current);
    };
  }, [isLoggedIn, performLogout]);

  // Show loading state while checking for existing session
  if (appLoading) {
    return (
      <div>
        <Header darkMode={darkMode} setDarkMode={setDarkMode} />
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <p>Loading...</p>
        </div>
        <Footer />
      </div>
    );
  }

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
        {/* Conditionally render Chatbot only for specific user levels */}
        {hasChatbotAccess && (
          <Chatbot setChatbotMinimized={setChatbotMinimized} username={username} />
        )}
      </div>
      <Footer />
    </div>
  );
}

export default App;
