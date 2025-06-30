import React, { useState } from 'react';
import '../styles/Login.css';
import Header from './Header';
import Footer from './Footer';
import { postLogin } from "../api/loginApi";

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [darkMode, setDarkMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [responseMessage, setResponseMessage] = useState('');
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');


    try {
      const response = await postLogin(username, password);
      console.log('Login response:', response);

      // Check the response status from your Django backen
      if (response.data.status === 302) {
        // Call parent component's onLogin function with username
        onLogin(response.data.username);
      } else {
        setError('Invalid credentials');
      }
    } catch (error) {
      console.error('Login error:', error);
      if (error.response && error.response.data) {
        setError(error.response.data.Response || 'Login failed');
      } else {
        setError('Unable to connect to server');
      }
    } finally {
      setLoading(false);
    }
  };
   const handleRegisterRedirect = () => {
        window.location.href = 'https://10.191.171.12:5443/EISInfra/EIS/EIS/Registration.php';
      };

  const uid = localStorage.getItem('uidd');

    const handleReset = async () => {



 try {
      const response = await fetch('https://10.191.171.12:5443/EISInfra/EIS/EIS/ResetPassword.php', { // Replace with your API endpoint
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ Uid : 'uid' }), // Data to send
      });
  }
   catch (error) {
      setResponseMessage(`Error: ${error.message}`);
    }
  };

  return (
    <div className={darkMode ? 'dark-mode' : ''}>
      <Header darkMode={darkMode} setDarkMode={setDarkMode} />
      <div className="login-container">
        <div className="bubble"></div>
        <div className="bubble"></div>
        <form className="login-form" onSubmit={handleSubmit}>
          <h2>Login</h2>
          {error && <div className="error-message">{error}</div>}
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit" disabled={loading}>
            {loading ? 'Logging in...' : 'Login'}
          </button>
           <button onClick={handleRegisterRedirect}>Register</button>
           <button onClick={handleReset}>Forgot Password</button>
        </form>
      </div>
      <Footer />
    </div>
  );
}

export default Login;
