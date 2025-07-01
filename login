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
      // Accept both possible keys due to typo
      const secQ = res.data.securityQuestion ?? res.data.securtiyQuestion;
      // If the key is present (even if empty), allow to proceed to next modal
      if (typeof secQ !== 'undefined') {
        setSecurityQ(secQ);
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
          <div className="modal-box modal-fade">
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
                <button className="modal-btn" type="submit" disabled={secQLoading}>Next</button>
                <button className="modal-btn cancel" type="button" onClick={closeModals}>Cancel</button>
              </div>
            </form>
            {forgotPwdMsg && <div className="error-message">{forgotPwdMsg}</div>}
          </div>
        </div>
      )}

      {/* Security Question Modal (styled as login form) */}
      {showSecQModal && (
        <div className="modal-overlay">
          <div className="modal-box modal-fade" style={{ padding: 0, background: 'none', boxShadow: 'none', minWidth: 'unset' }}>
            <div className="login-container" style={{ minHeight: 'unset', background: 'none', boxShadow: 'none', position: 'static' }}>
              <form className="login-form" style={{ margin: 0, width: '350px', zIndex: 2 }} onSubmit={handleSecQSubmit}>
                <h2>Reset Password</h2>
                {forgotPwdMsg && <div className="error-message">{forgotPwdMsg}</div>}
                <input
                  type="text"
                  value={empId}
                  readOnly
                  placeholder="Employee ID"
                  style={{ background: "rgba(255,255,255,0.08)", cursor: "not-allowed" }}
                />
                <input
                  type="text"
                  value={securityQ || ''}
                  readOnly
                  placeholder="Security Question"
                  style={{ background: "rgba(255,255,255,0.08)", cursor: "not-allowed" }}
                />
                {securityQ === "" && (
                  <div className="info-message" style={{ color: "orange" }}>
                    No security question set for this user. Please contact admin if you cannot reset your password.
                  </div>
                )}
                <input
                  type="text"
                  placeholder="Your Answer"
                  value={securityAnswer}
                  onChange={e => setSecurityAnswer(e.target.value)}
                  required={securityQ !== ""}
                  disabled={securityQ === ""}
                />
                <input
                  type="password"
                  placeholder="New Password"
                  value={newPwd}
                  onChange={e => setNewPwd(e.target.value)}
                  required
                />
                <button type="submit" disabled={secQLoading || !securityQ}>
                  {secQLoading ? 'Submitting...' : 'Submit'}
                </button>
                <button
                  type="button"
                  style={{
                    background: '#e74c3c',
                    color: '#fff',
                    marginTop: '0.5rem'
                  }}
                  onClick={closeModals}
                >
                  Cancel
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Modal styling (move to Login.css if preferred) */}
      <style>{`
        .modal-overlay {
          position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
          background: rgba(0,0,0,0.5); display: flex; align-items: center; justify-content: center; z-index: 2000;
          animation: modal-bg-fade 0.2s;
        }
        .modal-box {
          background: #fff;
          padding: 2em 2.2em 1.5em 2.2em;
          border-radius: 14px;
          box-shadow: 0 4px 24px rgba(0,0,0,0.22);
          min-width: 330px;
          max-width: 90vw;
          animation: modal-fadein 0.24s;
          position: relative;
        }
        .modal-box h3 {
          margin-top: 0;
          margin-bottom: 1.1em;
          font-size: 1.33em;
          text-align: center;
        }
        .modal-input {
          width: 100%;
          padding: 0.60em 0.9em;
          border: 1.1px solid #c6c7d4;
          border-radius: 5px;
          margin-bottom: 0.9em;
          font-size: 1em;
          background: #f7f8fa;
          transition: border 0.18s;
        }
        .modal-input:focus {
          border: 1.2px solid #1976d2;
          outline: none;
          background: #fff;
        }
        .modal-actions {
          margin-top: 0.8em;
          display: flex;
          gap: 0.9em;
          justify-content: flex-end;
        }
        .modal-btn {
          background: #1976d2;
          color: #fff;
          border: none;
          padding: 0.52em 1.18em;
          border-radius: 4px;
          font-size: 0.98em;
          cursor: pointer;
          transition: background 0.18s;
        }
        .modal-btn:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }
        .modal-btn.cancel {
          background: #e74c3c;
        }
        .info-message {
          color: #1976d2;
          margin-top: 1em;
          font-size: 1em;
          text-align: center;
        }
        .error-message {
          color: #e74c3c;
          margin-top: 1em;
          font-size: 1em;
          text-align: center;
        }
        @keyframes modal-fadein {
          from { transform: translateY(-22px) scale(0.98); opacity: 0; }
          to   { transform: translateY(0) scale(1); opacity: 1; }
        }
        @keyframes modal-bg-fade {
          from { background: rgba(0,0,0,0.0);}
          to   { background: rgba(0,0,0,0.5);}
        }
      `}</style>
    </div>
  );
}

export default Login;
