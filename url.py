/* Dynamic Form Styles */
.dynamic-form-container {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.dynamic-form {
  background: white;
  padding: 20px;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  max-height: 70vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.form-field {
  margin-bottom: 15px;
}

.form-label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
  color: #333;
}

.required {
  color: #e74c3c;
}

.form-input, .form-textarea, .form-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.form-input:focus, .form-textarea:focus, .form-select:focus {
  border-color: #007bff;
  outline: none;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.form-input.error, .form-textarea.error, .form-select.error {
  border-color: #e74c3c;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.checkbox-field {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: normal;
}

.form-checkbox {
  margin-right: 8px;
  width: auto;
}

.error-message {
  color: #e74c3c;
  font-size: 12px;
  margin-top: 4px;
  display: block;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #eee;
}

.submit-button, .cancel-button {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.submit-button {
  background-color: #007bff;
  color: white;
}

.submit-button:hover {
  background-color: #0056b3;
}

.cancel-button {
  background-color: #6c757d;
  color: white;
}

.cancel-button:hover {
  background-color: #545b62;
}

.form-button {
  background: #007bff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
  font-size: 14px;
  transition: background-color 0.3s ease;
}

.form-button:hover {
  background-color: #0056b3;
}

.form-trigger {
  margin-top: 10px;
}

/* Responsive adjustments */
@media (max-width: 600px) {
  .dynamic-form {
    width: 95%;
    max-height: 80vh;
    padding: 15px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .submit-button, .cancel-button {
    width: 100%;
  }
}
