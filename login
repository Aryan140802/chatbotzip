import React, { useState } from 'react';
import '../styles/Login.css';
import Header from './Header';
import Footer from './Footer';
import { postLogin } from "../api/loginApi";
import { postGetSecurityQuestion, postForgotPassword } from "../api/postNewApi";

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [darkMode, setDarkMode] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [errorType, setErrorType] = useState('');
  const [showForgotPwd, setShowForgotPwd] = useState(false);

  // Forgot password popup states
  const [showEmpIdModal, setShowEmpIdModal] = useState(false);
  const [empId, setEmpId] = useState('');
  const [secQLoading, setSecQLoading] = useState(false);
  const [securityQ, setSecurityQ] = useState('');
  const [showSecQModal, setShowSecQModal] = useState(false);
  const [securityAnswer, setSecurityAnswer] = useState('');
  const [newPwd, setNewPwd] = useState('');
  const [forgotPwdMsg, setForgotPwdMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setErrorType('');
    setShowForgotPwd(false);

    try {
      const response = await postLogin(username, password);
      // You should adjust this block based on your backend's actual response structure!
      if (response.data.status === 302) {
        onLogin(response.data.username);
      } else if (response.data.status === 401) {
        setError('Wrong ID');
        setErrorType('id');
      } else if (response.data.status === 402) {
        setError('Wrong password');
        setErrorType('password');
        setShowForgotPwd(true);
      } else {
        setError('Invalid credentials');
        setErrorType('');
      }
    } catch (error) {
      if (error.response && error.response.data) {
        if (error.response.data.message === "wrong id") {
          setError('Wrong ID');
          setErrorType('id');
        } else if (error.response.data.message === "wrong password") {
          setError('Wrong password');
          setErrorType('password');
          setShowForgotPwd(true);
        } else {
          setError(error.response.data.message || 'Login failed');
          setErrorType('');
        }
      } else {
        setError('Unable to connect to server');
        setErrorType('');
      }
    } finally {
      setLoading(false);
    }
  };

  // --- Forgot Password Flow ---

  // Open Modal 1 (enter Employee ID)
  const openForgotPwdModal = () => {
    setShowEmpIdModal(true);
    setEmpId('');
    setForgotPwdMsg('');
  };

  // Submit Employee ID, get security question
  const handleEmpIdSubmit = async (e) => {
    e.preventDefault();
    setSecQLoading(true);
    setForgotPwdMsg('');
    try {
      const res = await postGetSecurityQuestion(empId);
      if (res.data.securtiyQuestion) {
        setSecurityQ(res.data.securtiyQuestion);
        setShowEmpIdModal(false);
        setShowSecQModal(true);
        setSecurityAnswer('');
        setNewPwd('');
      } else {
        setForgotPwdMsg(res.data.msg || 'Invalid employee ID. Please try again.');
      }
    } catch (err) {
      setForgotPwdMsg('Invalid employee ID. Please try again.');
    } finally {
      setSecQLoading(false);
    }
  };

  // Submit Security Answer, New Password
  const handleSecQSubmit = async (e) => {
    e.preventDefault();
    setSecQLoading(true);
    setForgotPwdMsg('');
    try {
      const res = await postForgotPassword({
        uid: empId,
        SecQ: securityQ,
        password: newPwd,
        answer: securityAnswer
      });
      if (res.data.msg && res.data.msg.toLowerCase().includes('success')) {
        setForgotPwdMsg('Password updated successfully. You can now login.');
        setShowSecQModal(false);
      } else {
        setForgotPwdMsg(res.data.msg || 'Failed to reset password. Please check your answer.');
      }
    } catch (err) {
      setForgotPwdMsg('Failed to reset password. Please check your answer.');
    } finally {
      setSecQLoading(false);
    }
  };

  // Close all modals
  const closeModals = () => {
    setShowEmpIdModal(false);
    setShowSecQModal(false);
    setForgotPwdMsg('');
  };

  const handleRegisterRedirect = () => {
    window.location.href = 'https://10.191.171.12:5443/EISInfra/EIS/EIS/Registration.php';
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
          <button type="button" onClick={handleRegisterRedirect}>
            Register
          </button>
          {errorType === 'password' && showForgotPwd && (
            <button type="button" onClick={openForgotPwdModal}>Forgot Password?</button>
          )}
        </form>
        {forgotPwdMsg && <div className="info-message">{forgotPwdMsg}</div>}
      </div>
      <Footer />

      {/* Employee ID Modal */}
      {showEmpIdModal && (
        <div className="modal-overlay">
          <div className="modal-box">
            <h3>Forgot Password</h3>
            <form onSubmit={handleEmpIdSubmit}>
              <label>Enter your Employee ID:</label>
              <input
                type="text"
                value={empId}
                onChange={(e) => setEmpId(e.target.value)}
                required
                autoFocus
              />
              <div className="modal-actions">
                <button type="submit" disabled={secQLoading}>Next</button>
                <button type="button" onClick={closeModals}>Cancel</button>
              </div>
            </form>
            {forgotPwdMsg && <div className="error-message">{forgotPwdMsg}</div>}
          </div>
        </div>
      )}

      {/* Security Question Modal */}
      {showSecQModal && (
        <div className="modal-overlay">
          <div className="modal-box">
            <h3>Reset Password</h3>
            <form onSubmit={handleSecQSubmit}>
              <label>Employee ID:</label>
              <input type="text" value={empId} readOnly />
              <label>Security Question:</label>
              <input type="text" value={securityQ} readOnly />
              <label>Your Answer:</label>
              <input
                type="text"
                value={securityAnswer}
                onChange={(e) => setSecurityAnswer(e.target.value)}
                required
              />
              <label>New Password:</label>
              <input
                type="password"
                value={newPwd}
                onChange={(e) => setNewPwd(e.target.value)}
                required
              />
              <div className="modal-actions">
                <button type="submit" disabled={secQLoading}>Submit</button>
                <button type="button" onClick={closeModals}>Cancel</button>
              </div>
            </form>
            {forgotPwdMsg && <div className="error-message">{forgotPwdMsg}</div>}
          </div>
        </div>
      )}

      {/* Modal styling (you can move to your CSS file) */}
      <style>{`
        .modal-overlay {
          position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
          background: rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; z-index: 1000;
        }
        .modal-box {
          background: #fff; padding: 2em; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.2); min-width: 320px;
        }
        .modal-actions { margin-top: 1em; display: flex; gap: 1em; }
        .info-message { color: green; margin-top: 1em; }
        .error-message { color: red; margin-top: 1em; }
      `}</style>
    </div>
  );
}

export default Login;
