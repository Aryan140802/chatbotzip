import { useState, useEffect, useRef } from "react";
import ProfileIcon from "./ProfileIcon";
import TypingIndicator from "./TypingIndicator";
import "../styles/Chatbot.css";
import send from "../assets/Send.png";
import logo from "../assets/logobot.jpg";
import { getPost, postMessage } from "../api/PostApi";

// Utility: Format dynamic bot message (safe HTML for <b> etc.)
const formatDynamicMessage = (text) => {
  if (!text || typeof text !== "string") return text;

  // If the message contains <b> tags, try to format them in a readable way
  if (text.includes("<b>")) {
    const hasHeaderAndFields = text.includes("Here is the information for") &&
      text.includes("<b>Name</b>:") &&
      text.includes("<b>Email</b>:");
    if (hasHeaderAndFields) {
      const lines = text.split('\n').filter(line => line.trim());
      const formattedLines = [];
      lines.forEach(line => {
        const trimmedLine = line.trim();
        if (trimmedLine.includes("Here is the information for")) {
          formattedLines.push(`<div class="info-header">${trimmedLine}</div>`);
        }
        else if (trimmedLine.includes("<b>") && trimmedLine.includes("</b>:")) {
          const fieldMatch = trimmedLine.match(/<b>(.*?)<\/b>:\s*(.*)/);
          if (fieldMatch) {
            const fieldName = fieldMatch[1].trim();
            const fieldValue = fieldMatch[2].trim() || "Not provided";
            formattedLines.push(`<div class="info-field"><strong>${fieldName}:</strong> ${fieldValue}</div>`);
          }
        }
        else if (trimmedLine && !trimmedLine.match(/^\s*$/)) {
          formattedLines.push(`<div>${trimmedLine}</div>`);
        }
      });
      return `<div class="formatted-card employee-info">${formattedLines.join('')}</div>`;
    }
    // Generic bold field formatting
    const pattern = /(?:<b>(.*?)<\/b>:\s*(.*?))|(?:(.*?)\s*:\s*<b>(.*?)<\/b>)/gs;
    const lines = [];
    let match;
    while ((match = pattern.exec(text)) !== null) {
      const key = (match[1] || match[3] || "").trim();
      const value = (match[2] || match[4] || "").trim().replace(/\n/g, "<br/>");
      lines.push(`<div><strong>${key}:</strong> ${value}</div>`);
    }
    if (lines.length === 0) {
      return `<div class="formatted-card">${text.replace(/\n/g, "<br/>")}</div>`;
    }
    return `<div class="formatted-card">${lines.join("")}</div>`;
  }

  // Detect "server config" or log-style messages by number of colons
  const isServerConfig = (text.match(/:/g) || []).length > 2;
  if (isServerConfig) {
    // Split on newlines and wrap each line in a div for clarity
    const lines = text.split('\n').map(line => `<div>${line.trim()}</div>`);
    return `<div class="formatted-card">${lines.join('')}</div>`;
  }

  // Default: Replace all newlines with <br/> so nothing is lost
  return text.replace(/\n/g, "<br/>");
};
const formatFormDataToSentence = (formData, originalFields, formType = null) => {
  if (!formData || Object.keys(formData).length === 0) {
    return "No form data provided";
  }
  const sentences = [];
  const fieldLabelsMap = {};
  if (originalFields) {
    originalFields.forEach(field => {
      fieldLabelsMap[field.name] = field.label || field.name;
    });
  }
  if (formType === 'workload') {
    Object.entries(formData).forEach(([key, value]) => {
      if (key.toLowerCase().includes('service')) {
        const fieldLabel = fieldLabelsMap[key] || key;
        const formattedLabel = fieldLabel.charAt(0).toUpperCase() + fieldLabel.slice(1);
        if (value === null || value === undefined || value === '') {
          sentences.push(`${formattedLabel}: No value given`);
        } else {
          sentences.push(`${formattedLabel}: "${value}"`);
        }
      }
    });
  } else {
    Object.entries(formData).forEach(([key, value]) => {
      const fieldLabel = fieldLabelsMap[key] || key;
      const formattedLabel = fieldLabel.charAt(0).toUpperCase() + fieldLabel.slice(1);
      if (value === null || value === undefined || value === '') {
        sentences.push(`${formattedLabel}: No value given`);
      } else {
        sentences.push(`${formattedLabel}: "${value}"`);
      }
    });
  }
  return sentences.length > 0 ? sentences.join(', ') : "No values provided";
};

const hasFormFields = (response) => {
  if (!response || !response.message) return false;
  return typeof response.message === 'object' &&
    !Array.isArray(response.message) &&
    Object.keys(response.message).length > 0;
};

const determineFieldType = (fieldName, fieldValue) => {
  const lowerName = fieldName.toLowerCase();
  if (
    lowerName.includes('date') ||
    lowerName.includes('expiry') ||
    lowerName.includes('created') ||
    lowerName.includes('expire') ||
    lowerName.includes('start') ||
    lowerName.includes('end') ||
    fieldValue === 'date'
  ) {
    return 'date';
  }
  if (Array.isArray(fieldValue) && fieldValue.length > 0) {
    return 'select';
  }
  if (typeof fieldValue === 'string' && fieldValue.trim() !== '' && fieldValue !== 'date') {
    return 'textarea';
  }
  return 'text';
};

const determineFormType = (fields) => {
  const hasServiceField = fields.some(field => field.name.toLowerCase().includes('service'));
  const hasExpiryOrCreatedField = fields.some(field => field.name.toLowerCase().includes('expiry') || field.name.toLowerCase().includes('created'));
  if (hasServiceField) return 'workload';
  if (hasExpiryOrCreatedField) return 'multiple';
  return 'default';
};

const filterNonEmptyFields = (obj) =>
  Object.fromEntries(
    Object.entries(obj).filter(
      ([, value]) =>
        value !== null &&
        value !== undefined &&
        !(typeof value === "string" && value.trim() === "") &&
        !(Array.isArray(value) && value.length === 0)
    )
  );

// Always merges in currentValues for option selection retention and ensures new fields are present
const extractFormFields = (response, currentValues = {}) => {
  if (!hasFormFields(response)) return null;
  // Always add all fields present in backend response, using user's value if available
  return Object.entries(response.message).map(([name, value]) => {
    const isService = name === 'service';
    let displayLabel = name.charAt(0).toUpperCase() + name.slice(1).replace(/_/g, ' ');
    displayLabel = isService ? `* ${displayLabel}` : displayLabel;
    return {
      name,
      label: displayLabel,
      required: isService,
      value: (typeof currentValues[name] !== "undefined")
        ? currentValues[name]
        : (Array.isArray(value) ? "" : value),
      type: Array.isArray(value)
        ? 'select'
        : isService
        ? 'text'
        : determineFieldType(name, value),
      options: Array.isArray(value) ? value : [],
    };
  });
};

// --- DynamicForm Subcomponent ---
const DynamicForm = ({
  fields,
  onSubmit,
  onCancel,
  formType,
  onFieldChange,
  isSubmittingFromParent,
}) => {
  const [fieldDefs, setFieldDefs] = useState(fields);
  const [formData, setFormData] = useState(() =>
    Object.fromEntries(fields.map(f => [f.name, f.value || ""]))
  );
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // --- ROBUST MERGING LOGIC FIX ---
  useEffect(() => {
    setFieldDefs(fields);
    setFormData(current => {
      const merged = {};
      fields.forEach(f => {
        // Always prefer user input (current), unless backend gives a new, non-empty value
        if (
          typeof current[f.name] !== "undefined" &&
          current[f.name] !== "" &&
          (typeof f.value === "undefined" || f.value === null || f.value === "")
        ) {
          merged[f.name] = current[f.name];
        } else if (typeof f.value !== "undefined" && f.value !== null) {
          merged[f.name] = f.value;
        } else {
          merged[f.name] = "";
        }
      });
      return merged;
    });
  }, [fields]);

  const applyCascadingLogic = (updated, name) => {
    if (formType === "workload") {
      if (name === "service") {
        updated.layer = "";
        updated.server = "";
        updated.eg = "";
      } else if (name === "layer") {
        updated.server = "";
        updated.eg = "";
      } else if (name === "server") {
        updated.eg = "";
      }
    }
    return updated;
  };

  const handleInputChange = (name, value) => {
    let updated = { ...formData, [name]: value };
    updated = applyCascadingLogic(updated, name);
    setFormData(updated);
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: null }));
  };

  const handleBlur = async (name) => {
    if (onFieldChange) {
      const filtered = filterNonEmptyFields(formData);
      await onFieldChange(filtered, name);
    }
  };

  const handleSelectChange = async (name, value) => {
    let updated = { ...formData, [name]: value };
    updated = applyCascadingLogic(updated, name);
    setFormData(updated); // update immediately so UI reflects the change!
    if (onFieldChange) {
      const filtered = filterNonEmptyFields(updated);
      await onFieldChange(filtered, name);
    }
  };

  const handleSubmit = async e => {
    e.preventDefault();
    const missing = fieldDefs.filter(f => f.required && !formData[f.name]);
    if (missing.length > 0) {
      setErrors(prev => ({
        ...prev,
        ...Object.fromEntries(missing.map(f => [f.name, "This field is required."]))
      }));
      return;
    }
    setIsSubmitting(true);
    await onSubmit(formData, fieldDefs);
    setIsSubmitting(false);
  };

  const renderField = (field) => {
    const {
      name,
      label,
      type,
      options = [],
      placeholder,
    } = field;
    const value = formData[name] || "";
    const error = errors[name];
    const isService = name === "service";
    switch (type) {
      case "select":
        return (
          <div key={name} className="form-field">
            <label className="form-label">{isService && <span style={{ color: "red" }}>* </span>}{label.replace('* ', '')}</label>
            <select
              value={value}
              onChange={e => handleSelectChange(name, e.target.value)}
              className={`form-select${error ? " error" : ""}`}
              disabled={isSubmitting || isSubmittingFromParent || options.length === 0}
            >
              <option value="">Select {label.replace('* ', '').toLowerCase()}</option>
              {options.map((opt, idx) => (
                <option key={idx} value={opt.value || opt}>
                  {opt.label || opt}
                </option>
              ))}
            </select>
            {error && <span className="error-message">{error}</span>}
          </div>
        );
      case "date":
        return (
          <div key={name} className="form-field">
            <label className="form-label">{isService && <span style={{ color: "red" }}>* </span>}{label.replace('* ', '')}</label>
            <input
              type="date"
              value={value}
              onChange={e => handleInputChange(name, e.target.value)}
              className={`form-input${error ? " error" : ""}`}
              disabled={isSubmitting || isSubmittingFromParent}
            />
            {error && <span className="error-message">{error}</span>}
          </div>
        );
      case "textarea":
        return (
          <div key={name} className="form-field">
            <label className="form-label">{isService && <span style={{ color: "red" }}>* </span>}{label.replace('* ', '')}</label>
            <textarea
              value={value}
              onChange={e => handleInputChange(name, e.target.value)}
              placeholder={placeholder || ""}
              className={`form-textarea${error ? " error" : ""}`}
              rows={3}
              disabled={isSubmitting || isSubmittingFromParent}
            />
            {error && <span className="error-message">{error}</span>}
          </div>
        );
      default:
        return (
          <div key={name} className="form-field">
            <label className="form-label">{isService && <span style={{ color: "red" }}>* </span>}{label.replace('* ', '')}</label>
            <input
              type="text"
              value={value}
              onChange={e => handleInputChange(name, e.target.value)}
              onBlur={() => handleBlur(name)}
              placeholder={placeholder || ""}
              className={`form-input${error ? " error" : ""}`}
              disabled={isSubmitting || isSubmittingFromParent}
            />
            {error && <span className="error-message">{error}</span>}
          </div>
        );
    }
  };

  return (
    <div className="dynamic-form-container">
      <form onSubmit={handleSubmit} className="dynamic-form">
        {fieldDefs.map(renderField)}
        <div className="form-actions">
          <button type="button" onClick={onCancel} className="cancel-button" disabled={isSubmitting}>
            Cancel
          </button>
          <button type="submit" className="submit-button" disabled={isSubmitting || isSubmittingFromParent}>
            {isSubmitting || isSubmittingFromParent ? "Processing..." : "Submit"}
          </button>
        </div>
      </form>
    </div>
  );
};

// --- Main Chatbot Component ---
const Chatbot = ({ setChatbotMinimized }) => {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [formDisabled, setFormDisabled] = useState(true);
  const [activeForm, setActiveForm] = useState(null);
  const [currentFormType, setCurrentFormType] = useState(null);
  const [currentFormFields, setCurrentFormFields] = useState(null);

  const messagesEndRef = useRef(null);
  const timeoutRef = useRef(null);
  const API_TIMEOUT = 20000;

  const clearCurrentTimeout = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  };

  const setApiTimeout = (errorHandler) => {
    clearCurrentTimeout();
    timeoutRef.current = setTimeout(() => {
      setIsTyping(false);
      errorHandler();
    }, API_TIMEOUT);
  };

  const getCurrentTime = () => {
    const now = new Date();
    return `${now.getHours().toString().padStart(2, "0")}:${now.getMinutes().toString().padStart(2, "0")}`;
  };

  const checkEnableForm = (text) => {
    const lowerText = text.toLowerCase();
    return lowerText.includes("enter") || lowerText.includes("provide");
  };

  const getPostData = async () => {
    try {
      setIsTyping(true);
      setApiTimeout(() => {
        setMessages([{
          id: Date.now(),
          text: "Unable to load messages. Please try again later.",
          sender: "bot",
          time: getCurrentTime(),
        }]);
      });

      const res = await getPost();
      clearCurrentTimeout();

      const formattedMessages = res.data.chat_history.map((item, index) => {
        const message = {
          id: Date.now() + index,
          text: typeof item.message === 'string' ? item.message : "",
          sender: item.sender.toLowerCase() === "you" ? "user" : "bot",
          time: getCurrentTime(),
          options: item.options || [],
        };

        if (hasFormFields(item)) {
          message.formFields = extractFormFields(item, {});
          message.isFormMessage = true;
        }

        return message;
      });

      setMessages(formattedMessages);
      setFormDisabled(true);
      setIsTyping(false);
    } catch {
      clearCurrentTimeout();
      setIsTyping(false);
      setMessages([{
        id: Date.now(),
        text: "An error occurred while loading messages.",
        sender: "bot",
        time: getCurrentTime(),
      }]);
    }
  };

  useEffect(() => {
    getPostData();
    return () => clearCurrentTimeout();
    // eslint-disable-next-line
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, activeForm]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (newMessage.trim() === "") return;

    const userMsg = {
      id: Date.now(),
      text: newMessage,
      sender: "user",
      time: getCurrentTime(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setNewMessage("");
    setIsTyping(true);
    setFormDisabled(true);

    try {
      setApiTimeout(() => { });
      const res = await postMessage(newMessage);
      clearCurrentTimeout();

      const latest = res.data.chat_history?.slice(-1)[0];
      if (latest) {
        const botResponse = {
          id: Date.now(),
          text: latest.message || "",
          sender: "bot",
          time: getCurrentTime(),
          options: latest.options || [],
        };

        if (hasFormFields(latest)) {
          botResponse.formFields = extractFormFields(latest, {});
          botResponse.isFormMessage = true;
        }

        setMessages((prev) => [...prev, botResponse]);
        setFormDisabled(!checkEnableForm(botResponse.text));
      }
    } catch {
      clearCurrentTimeout();
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          text: "An error occurred. Please try again.",
          sender: "bot",
          time: getCurrentTime(),
        },
      ]);
    }

    setIsTyping(false);
  };

  const handleOptionClick = async (optionText) => {
    const cleanedOpt = optionText.replace(/^\d+\.|[a-zA-Z]\.\s*/, "").trim();

    const userMessage = {
      id: Date.now(),
      text: cleanedOpt,
      sender: "user",
      time: getCurrentTime(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setFormDisabled(true);
    setIsTyping(true);

    try {
      setApiTimeout(() => { });
      const res = await postMessage(cleanedOpt);
      clearCurrentTimeout();

      const latest = res.data.chat_history?.slice(-1)[0];
      if (latest) {
        const botResponse = {
          id: Date.now(),
          text: latest.message || "",
          sender: "bot",
          time: getCurrentTime(),
          options: latest.options || [],
        };

        if (hasFormFields(latest)) {
          botResponse.formFields = extractFormFields(latest, {});
          botResponse.isFormMessage = true;
        }

        setMessages((prev) => [...prev, botResponse]);
        setFormDisabled(!checkEnableForm(botResponse.text));
      }
    } catch {
      clearCurrentTimeout();
    }

    setIsTyping(false);
  };

  // Handle cascading field changes for forms
  const handleFieldChange = async (fieldData, changedFieldName) => {
    try {
      setIsTyping(true);
      setApiTimeout(() => {});

      const filteredData = filterNonEmptyFields(fieldData);
      if (Object.keys(filteredData).length === 0) {
        setIsTyping(false);
        return;
      }
      const payload = { message: filteredData };
      const res = await postMessage(payload);
      clearCurrentTimeout();

      const latest = res.data.chat_history?.slice(-1)[0];
      if (latest && hasFormFields(latest)) {
        // critical: always use fieldData, not just filteredData, so all user-selected values are preserved
        const updatedFields = extractFormFields(latest, fieldData);
        setActiveForm(updatedFields);
        setCurrentFormFields(updatedFields);
      }
    } catch (error) {
      clearCurrentTimeout();
    } finally {
      setIsTyping(false);
    }
  };

  // Form submit handler for forms
  const handleFormSubmit = async (formData, originalFields) => {
    setActiveForm(null);
    setCurrentFormType(null);

    // Only send non-empty fields
    const completeFormData = filterNonEmptyFields(formData);

    const formattedText = formatFormDataToSentence(formData, originalFields, currentFormType);

    const userMessage = {
      id: Date.now(),
      text: formattedText,
      sender: "user",
      time: getCurrentTime(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);
    setFormDisabled(true);

    try {
      setApiTimeout(() => { });
      const payload = { message: completeFormData };
      const res = await postMessage(payload);
      clearCurrentTimeout();

      const latest = res.data.chat_history?.slice(-1)[0];
      if (latest) {
        const botResponse = {
          id: Date.now(),
          text: typeof latest.message === 'string' ? latest.message : "",
          sender: "bot",
          time: getCurrentTime(),
          options: latest.options || [],
        };

        if (hasFormFields(latest)) {
          botResponse.formFields = extractFormFields(latest, completeFormData);
          botResponse.isFormMessage = true;
        }

        setMessages((prev) => [...prev, botResponse]);
        setFormDisabled(!checkEnableForm(botResponse.text));
      }
    } catch (error) {
      clearCurrentTimeout();
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          text: "An error occurred while submitting the form. Please try again.",
          sender: "bot",
          time: getCurrentTime(),
        },
      ]);
    }
    setIsTyping(false);
  };

  const handleFormCancel = () => {
    setActiveForm(null);
    setCurrentFormType(null);
    setCurrentFormFields(null);
  };

  const handleFormButtonClick = (fields) => {
    const formType = determineFormType(fields);
    setCurrentFormType(formType);
    setCurrentFormFields(fields);
    setActiveForm(fields);
  };

  const handleMinimize = () => {
    setIsMinimized(true);
    setChatbotMinimized(true);
  };

  const handleRestore = () => {
    setIsMinimized(false);
    setChatbotMinimized(false);
  };

  return (
    <div className={`chat-container ${isMinimized ? "minimized" : ""}`}>
      <div className="chat-header">
        <img src={logo} alt="Logo" className="chat-logo" onClick={handleRestore} />
        {!isMinimized && (
          <>
            <div className="chat-title">
              <h1>EIS GINI</h1>
              <h5>(Generative Interactive Neural Interface)</h5>
            </div>
            <button className="minimize-button" onClick={handleMinimize}>
              &#x2212;
            </button>
          </>
        )}
      </div>
      {!isMinimized && (
        <>
          <div className="messages-container">
            {messages.map((item, index) => (
              <div
                key={index}
                className={`message-wrapper ${item.sender.toLowerCase()}`}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: item.sender === "user" ? "flex-end" : "flex-start",
                  marginBottom: "12px",
                }}
              >
                <div style={{ display: "flex", alignItems: "flex-end", gap: "5px" }}>
                  {item.sender === "bot" && <ProfileIcon sender={item.sender} />}
                  <div className={`message ${item.sender === "user" ? "user-message" : "bot-message"}`}>
                    {item.sender === "bot" && !item.isFormMessage ? (
                      <div
                        className="message-content"
                        dangerouslySetInnerHTML={{ __html: formatDynamicMessage(item.text) }}
                      />
                    ) : item.sender === "bot" && item.isFormMessage ? (
                      <div className="message-content">
                        <p>Please fill out the form with the required information:</p>
                      </div>
                    ) : (
                      <div className="message-content">{item.text}</div>
                    )}

                    {item.formFields && (
                      <div className="form-trigger">
                        <button
                          className="form-button"
                          onClick={() => handleFormButtonClick(item.formFields)}
                        >
                          Fill Form
                        </button>
                      </div>
                    )}

                    {item.options?.length > 0 && (
                      <div className="options-list">
                        {item.options.map((opt, i) => {
                          const displayText = opt.replace(/^\d+\.\s*|^[a-zA-Z]\.\s*/, "").trim().toLowerCase();
                          const isPlainText =
                            displayText.includes("please select one by name") ||
                            displayText.includes("please select from the following options");

                          if (isPlainText) {
                            return (
                              <div key={i} className="plain-text-option">
                                {displayText}
                              </div>
                            );
                          }

                          return (
                            <button key={i} className="option-button" onClick={() => handleOptionClick(opt)}>
                              {displayText}
                            </button>
                          );
                        })}
                      </div>
                    )}
                    <div className="message-time">{item.time}</div>
                  </div>
                  {item.sender === "user" && <ProfileIcon sender={item.sender} />}
                </div>
              </div>
            ))}
            {isTyping && (
              <div style={{ display: "flex", alignItems: "flex-end", gap: "5px" }}>
                <ProfileIcon sender="bot" />
                <div className="message bot-message">
                  <TypingIndicator />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
          {activeForm && (
            <DynamicForm
              fields={activeForm}
              onSubmit={handleFormSubmit}
              onCancel={handleFormCancel}
              formType={currentFormType}
              onFieldChange={handleFieldChange}
              isSubmittingFromParent={isTyping}
            />
          )}
          <form className="message-form" onSubmit={handleSendMessage}>
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder={formDisabled ? "Select a relevant option or wait for prompt..." : "Type a message..."}
              className="message-input"
              disabled={formDisabled}
            />
            <button type="submit" className="send-button" disabled={formDisabled}>
              <img className="logo" src={send} alt="Send" style={{ height: "20px", opacity: formDisabled ? 0.5 : 1 }} />
            </button>
          </form>
        </>
      )}
    </div>
  );
};

export default Chatbot;
