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
    try {
      const response = await postLogin(username, password);
      if (response.data.status === 302) {
        onLogin(response.data.username);
      } else {
        setError('Invalid credentials');
      }
    } catch (error) {
      setError('Unable to connect to server');
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
      console.log('Security Question Response:', res.data); // Debug log
      
      // Accept typo key first, then correct key
      const secQ = res.data.securtiyQuestion ?? res.data.securityQuestion;
      
      // Check if we got a valid response and security question
      if (res.data && (secQ !== undefined && secQ !== null && secQ !== '')) {
        setSecurityQ(secQ);
        setShowEmpIdModal(false);
        setShowSecQModal(true);
        setSecurityAnswer('');
        setNewPwd('');
        setForgotPwdMsg(''); // Clear any previous messages
      } else {
        // Handle case where employee ID is valid but no security question is set
        if (res.data && (secQ === '' || secQ === null)) {
          setSecurityQ(''); // Set empty security question
          setShowEmpIdModal(false);
          setShowSecQModal(true);
          setSecurityAnswer('');
          setNewPwd('');
          setForgotPwdMsg('');
        } else {
          setForgotPwdMsg(res.data?.msg || 'Invalid employee ID. Please try again.');
        }
      }
    } catch (err) {
      console.error('Error fetching security question:', err);
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
          {/* Forgot Password link always visible */}
          <div style={{ marginTop: "10px" }}>
            <a
              href="#"
              onClick={e => { e.preventDefault(); openForgotPwdModal(); }}
              style={{
                color: '#007bff',
                cursor: 'pointer',
                textDecoration: 'underline',
                fontSize: '0.95em',
                display: 'inline-block'
              }}
            >
              Forgot Password?
            </a>
          </div>
        </form>
        {forgotPwdMsg && !showEmpIdModal && !showSecQModal && (
          <div className="info-message">{forgotPwdMsg}</div>
        )}
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
                className="modal-input"
              />
              <div className="modal-actions">
                <button className="modal-btn" type="submit" disabled={secQLoading}>
                  {secQLoading ? 'Loading...' : 'Next'}
                </button>
                <button className="modal-btn cancel" type="button" onClick={closeModals}>Cancel</button>
              </div>
            </form>
            {forgotPwdMsg && <div className="modal-error-message">{forgotPwdMsg}</div>}
          </div>
        </div>
      )}

      {/* Security Question Modal */}
      {showSecQModal && (
        <div className="modal-overlay">
          <div className="modal-box security-modal">
            <h3>Reset Password</h3>
            <form onSubmit={handleSecQSubmit}>
              {forgotPwdMsg && <div className="modal-error-message">{forgotPwdMsg}</div>}
              
              <label>Employee ID:</label>
              <input
                type="text"
                value={empId}
                readOnly
                className="modal-input readonly"
              />
              
              <label>Security Question:</label>
              <input
                type="text"
                value={securityQ || 'No security question set'}
                readOnly
                className="modal-input readonly"
              />
              
              {securityQ === "" && (
                <div className="modal-info-message">
                  No security question set for this user. Please contact admin if you cannot reset your password.
                </div>
              )}
              
              <label>Your Answer:</label>
              <input
                type="text"
                placeholder="Enter your answer"
                value={securityAnswer}
                onChange={e => setSecurityAnswer(e.target.value)}
                required={securityQ !== ""}
                disabled={securityQ === ""}
                className="modal-input"
              />
              
              <label>New Password:</label>
              <input
                type="password"
                placeholder="Enter new password"
                value={newPwd}
                onChange={e => setNewPwd(e.target.value)}
                required
                className="modal-input"
              />
              
              <div className="modal-actions">
                <button className="modal-btn" type="submit" disabled={secQLoading || !securityQ}>
                  {secQLoading ? 'Submitting...' : 'Submit'}
                </button>
                <button className="modal-btn cancel" type="button" onClick={closeModals}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Enhanced Modal Styling */}
      <style>{`
        .modal-overlay {
          position: fixed; 
          top: 0; 
          left: 0; 
          width: 100vw; 
          height: 100vh;
          background: rgba(0,0,0,0.6); 
          display: flex; 
          align-items: center; 
          justify-content: center; 
          z-index: 2000;
          animation: modal-bg-fade 0.3s ease-out;
        }
        
        .modal-box {
          background: #fff;
          padding: 2em 2.5em 2em 2.5em;
          border-radius: 12px;
          box-shadow: 0 8px 32px rgba(0,0,0,0.3);
          min-width: 380px;
          max-width: 90vw;
          animation: modal-fadein 0.3s ease-out;
          position: relative;
          max-height: 90vh;
          overflow-y: auto;
        }
        
        .modal-box.security-modal {
          min-width: 420px;
        }
        
        .modal-box h3 {
          margin-top: 0;
          margin-bottom: 1.5em;
          font-size: 1.4em;
          text-align: center;
          color: #333;
          font-weight: 600;
        }
        
        .modal-box label {
          display: block;
          margin-bottom: 0.5em;
          font-weight: 500;
          color: #555;
          font-size: 0.95em;
        }
        
        .modal-input {
          width: 100%;
          padding: 0.75em 1em;
          border: 1.5px solid #ddd;
          border-radius: 6px;
          margin-bottom: 1.2em;
          font-size: 1em;
          background: #fff;
          transition: all 0.2s ease;
          box-sizing: border-box;
        }
        
        .modal-input:focus {
          border-color: #1976d2;
          outline: none;
          box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.1);
        }
        
        .modal-input.readonly {
          background: #f8f9fa;
          color: #666;
          cursor: not-allowed;
          border-color: #e9ecef;
        }
        
        .modal-actions {
          margin-top: 1.5em;
          display: flex;
          gap: 1em;
          justify-content: flex-end;
        }
        
        .modal-btn {
          background: #1976d2;
          color: #fff;
          border: none;
          padding: 0.7em 1.5em;
          border-radius: 6px;
          font-size: 1em;
          cursor: pointer;
          transition: all 0.2s ease;
          font-weight: 500;
          min-width: 80px;
        }
        
        .modal-btn:hover:not(:disabled) {
          background: #1565c0;
          transform: translateY(-1px);
        }
        
        .modal-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
          transform: none;
        }
        
        .modal-btn.cancel {
          background: #dc3545;
        }
        
        .modal-btn.cancel:hover:not(:disabled) {
          background: #c82333;
        }
        
        .modal-info-message {
          color: #ff9800;
          margin: 1em 0;
          font-size: 0.9em;
          text-align: center;
          padding: 0.8em;
          background: #fff3cd;
          border: 1px solid #ffeaa7;
          border-radius: 6px;
        }
        
        .modal-error-message {
          color: #dc3545;
          margin: 1em 0;
          font-size: 0.9em;
          text-align: center;
          padding: 0.8em;
          background: #f8d7da;
          border: 1px solid #f5c6cb;
          border-radius: 6px;
        }
        
        .info-message {
          color: #1976d2;
          margin-top: 1em;
          font-size: 1em;
          text-align: center;
          padding: 1em;
          background: #e3f2fd;
          border-radius: 6px;
          border: 1px solid #bbdefb;
        }
        
        .error-message {
          color: #dc3545;
          margin-top: 1em;
          font-size: 1em;
          text-align: center;
          padding: 1em;
          background: #f8d7da;
          border-radius: 6px;
          border: 1px solid #f5c6cb;
        }
        
        @keyframes modal-fadein {
          from { 
            transform: translateY(-30px) scale(0.95); 
            opacity: 0; 
          }
          to { 
            transform: translateY(0) scale(1); 
            opacity: 1; 
          }
        }
        
        @keyframes modal-bg-fade {
          from { 
            background: rgba(0,0,0,0); 
          }
          to { 
            background: rgba(0,0,0,0.6); 
          }
        }
        
        /* Dark Mode Support */
        .dark-mode .modal-box {
          background: #2d3748;
          color: #e2e8f0;
        }
        
        .dark-mode .modal-box h3 {
          color: #e2e8f0;
        }
        
        .dark-mode .modal-box label {
          color: #cbd5e0;
        }
        
        .dark-mode .modal-input {
          background: #4a5568;
          border-color: #718096;
          color: #e2e8f0;
        }
        
        .dark-mode .modal-input.readonly {
          background: #2d3748;
          color: #a0aec0;
          border-color: #4a5568;
        }
        
        .dark-mode .modal-input:focus {
          border-color: #4299e1;
          box-shadow: 0 0 0 3px rgba(66, 153, 225, 0.1);
        }
      `}</style>
    </div>
  );
}

export default Login;
