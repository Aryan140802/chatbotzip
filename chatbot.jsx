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
    const pattern = /(?:<b>(.*?)<\/b>:\s*(.*?))/gs;
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
  // Detect "server config" style messages by number of colons
  const isServerConfig = (text.match(/:/g) || []).length > 2;
  if (isServerConfig) {
    const lines = text.split('\n').map(line => `<div>${line.trim()}</div>`);
    return `<div class="formatted-card">${lines.join('')}</div>`;
  }
  // Always convert newlines to <br/> in default case
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
          sentences.push(``);
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
        sentences.push(``);
      } else {
        sentences.push(`${formattedLabel}: "${value}"`);
      }
    });
  }
  return sentences.length > 0 ? sentences.join(' ') : "no values given ";
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
    return 'text';
  }
  return 'text';
};

const determineFormType = (fields) => {
  const hasServiceField = fields.some(field => field.name.toLowerCase().includes('service'));
  const hasExpiryOrCreatedField = fields.some(field =>
    field.name.toLowerCase().includes('expiry') ||
    field.name.toLowerCase().includes('created')
  );

  // Check if this is a filter form
  const isFilterForm = fields.some(field =>
    field.name.toLowerCase().includes('filter') &&
    Array.isArray(field.options)
  );

  if (hasServiceField) return 'workload';
  if (isFilterForm) return 'filter';
  if (hasExpiryOrCreatedField) return 'multiple';
  return 'default';
};

const filterNonEmptyFields = (obj) =>
  Object.fromEntries(
    Object.entries(obj).filter(
      ([, value]) =>
        value !== null &&
        value !== undefined &&
        value !== "date" &&
        !(typeof value === "string" && value.trim() === "") &&
        !(Array.isArray(value) && value.length === 0)
    )
  );

const extractFormFields = (response, currentValues = {}) => {
  if (!hasFormFields(response)) return null;
  return Object.entries(response.message).map(([name, value]) => {
    const isService = name === 'service';
    let displayLabel = name.charAt(0).toUpperCase() + name.slice(1).replace(/_/g, ' ');
    displayLabel = isService ? `* ${displayLabel}` : displayLabel;
    const options = Array.isArray(value) ? value : [];
    const fieldType = options.length > 0
      ? 'select'
      : isService
        ? 'text'
        : determineFieldType(name, value);

    let initialValue;
    if (typeof currentValues[name] !== "undefined") {
      initialValue = currentValues[name];
    } else if (fieldType === "date" && value === "date") {
      initialValue = "";
    } else if (Array.isArray(value)) {
      initialValue = "";
    } else {
      initialValue = value;
    }

    return {
      name,
      label: displayLabel,
      required: isService,
      value: initialValue,
      type: fieldType,
      options,
    };
  });
};

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
  const [selectedFilter, setSelectedFilter] = useState(null);
  const allFieldsFilled = fieldDefs.every(f => !!formData[f.name]);
  useEffect(() => {
    setFieldDefs(fields);
    setFormData(current => {
      const merged = {};
      fields.forEach(f => {
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

  useEffect(() => {
    if (formType === 'filter' && formData.filter) {
      const newSelectedFilter = formData.filter.toLowerCase();
      if (newSelectedFilter !== selectedFilter) {
        setSelectedFilter(newSelectedFilter);

        setFieldDefs(prevFields =>
          prevFields.map(field => {
            if (field.name.toLowerCase() === 'expires') {
              return {
                ...field,
                required: newSelectedFilter.includes('filterexpired')
              };
            }
            if (field.name.toLowerCase() === 'created') {
              return {
                ...field,
                required: newSelectedFilter.includes('filtercreated')
              };
            }
            return field;
          })
        );
      }
    }
  }, [formData.filter, formType, selectedFilter]);

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

    if (formType === 'filter' && name.toLowerCase() === 'filter') {
      updated = applyCascadingLogic(updated, name);
      setSelectedFilter(value.toLowerCase());
    } else {
      updated = applyCascadingLogic(updated, name);
    }

    setFormData(updated);
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: null }));

    if (onFieldChange) {
      const filtered = filterNonEmptyFields(updated);
      await onFieldChange(filtered, name);
    }
  };

  const handleSubmit = async e => {
    e.preventDefault();

    const missing = fieldDefs.filter(f => {
      if (formType === 'filter' && selectedFilter) {
        if (selectedFilter.includes('filterexpired')) {
          return f.required && f.name.toLowerCase() === 'expires' && !formData[f.name];
        }
        if (selectedFilter.includes('filtercreated')) {
          return f.required && f.name.toLowerCase() === 'created' && !formData[f.name];
        }
      }
      return f.required && !formData[f.name];
    });

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

  const allRequiredFilled = fieldDefs
    .filter(f => {
      if (formType === 'filter' && selectedFilter) {
        if (selectedFilter.includes('filterexpired')) {
          return f.required && f.name.toLowerCase() === 'expires';
        }
        if (selectedFilter.includes('filtercreated')) {
          return f.required && f.name.toLowerCase() === 'created';
        }
        return false;
      }
      return f.required;
    })
    .every(f => !!formData[f.name]);

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
    const isRequiredField = field.required;

    switch (type) {
      case "select":
        return (
          <div key={name} className="form-field">
            <label className="form-label">
              {isRequiredField && <span style={{ color: "red" }}>* </span>}
              {label.replace('* ', '')}
            </label>
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
            <label className="form-label">
              {isRequiredField && <span style={{ color: "red" }}>* </span>}
              {label.replace('* ', '')}
            </label>
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
            <label className="form-label">
              {isRequiredField && <span style={{ color: "red" }}>* </span>}
              {label.replace('* ', '')}
            </label>
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
            <label className="form-label">
              {isRequiredField && <span style={{ color: "red" }}>* </span>}
              {label.replace('* ', '')}
            </label>
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
          <button
            type="submit"
            className="submit-button"
            disabled={
              isSubmitting ||
              isSubmittingFromParent ||
              (formType === "workload" && !allFieldsFilled) ||
              (formType === "filter" && !allRequiredFilled)
            }
          >
            {isSubmitting || isSubmittingFromParent ? "Processing..." : "Submit"}
          </button>
        </div>
      </form>
    </div>
  );
};

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
  const API_TIMEOUT = 200000;

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

  const handleFormSubmit = async (formData, originalFields) => {
    setActiveForm(null);
    setCurrentFormType(null);

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
                             displayText.includes("please select from following options")||
                            displayText === "DO YOU WANT MORE DETAILS?:" ||
                            displayText === "do you want more details?" ||
                            displayText === "do you want more details" ||
                            displayText === "do you want more details?:" ;

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





import axios from 'axios';

// Create axios instance with custom configuration
const api = axios.create({
  baseURL: 'https://10.191.171.12:5443/EISHOME_TEST/',
 // baseURL: 'https://10.191.171.12:5443/EISHOME/'
  timeout: 100000,
  headers: {
    'Content-Type': 'application/json',
  }
});

// Modified postMessage to always send data under "message"
export const postMessage = (data) => {
  if (typeof data === 'string') {
    return api.post('EIS-GINI/', { "message": data }, { timeout: 100000 });
  }
  if (Array.isArray(data)) {
    return api.post('EIS-GINI/', { "message": data }, { timeout: 100000 });
  }
  if (typeof data === 'object' && data !== null) {
    if (data.hasOwnProperty('message')) {
      return api.post('EIS-GINI/', data, { timeout: 100000 });
    }
    return api.post('EIS-GINI/', { "message": data }, { timeout: 100000 });
  }
  return api.post('EIS-GINI/', { "message": data }, { timeout: 100000 });
};

// All other API functions remain unchanged
export const getPost = () => {
  return api.get('EIS-GINI/', { timeout: 100000 });
};

export const getServiceSys = () => {
  return api.get('EISHome/servicewise_sys/');
};

export const getServiceExp = () => {
  return api.get('EISHome/servicewise_exp/');
};

export const getIpwiseSys = () => {
  return api.get('EISHome/ipwise_sys/');
};

export const getIpwiseExp = () => {
  return api.get('EISHome/ipwise_exp/');
};

export const getPortwiseSys = () => {
  return api.get('EISHome/portwise_sys/');
};

export const getPortwiseExp = () => {
  return api.get('EISHome/portwise_exp/');
};

export const getServiceWiseExp5 = () => {
  return api.get('EISHome/servicewise_top5_exp/');
};

export const getServiceWiseSys5 = () => {
  return api.get('EISHome/servicewise_top5_sys/');
};

export const getIpWiseExp5 = () => {
  return api.get('EISHome/ipwise_exp_top5/');
};

export const getIpWiseSys5 = () => {
  return api.get('EISHome/ipwise_sys_top5/');
};

export const getPortWiseExp5 = () => {
  return api.get('EISHome/portwise_top5_exp/');
};

export const getPortWiseSys5 = () => {
  return api.get('EISHome/portwise_top5_sys/');
};

export const getFARExpires = () => {
  return api.get('EISHome/farExpiresNext5M/');
};

// NEW: Add the FAR details specific API function
export const getFARDetailsSpecific = async (dataFilter) => {
  try {
    const userId = localStorage.getItem('uidd');
    const password = localStorage.getItem('password');

    const response = await api.post('EISHome/farSpecificAll/', {
      "data_filter": dataFilter,
      "userId": userId,
      "password": password
    });
    return response;
  } catch (error) {
    console.error('Could not fetch FAR details:', error);
    throw error;
  }
};

export const postGraphDownload = async ({ path, time }) => {
  try {
    const uid = localStorage.getItem('uidd');
    const password = localStorage.getItem('password');
    const payload = {
      uid,
      password,
      time,
      download: true
    };
    const response = await api.post(path, payload);
    return response;
  } catch (error) {
    console.error("Error in postGraphDownload:", error);
    throw error;
  }
};

// Time-based post functions remain unchanged
export const postServiceWiseExp5 = async (time) => {
  try {
    const uid = localStorage.getItem('uidd');
    const password = localStorage.getItem('password');
    const response = await api.post('EISHome/servicewise_top5_FiveM/EXP/', {
      "time": time,
      "uid": uid,
      "password": password
    });
    return response;
  } catch (error) {
    console.error('Could not fetch error:', error);
    throw error;
  }
};

export const postServiceWiseSys5 = async (time) => {
  try {
    const uid = localStorage.getItem('uidd');
    const password = localStorage.getItem('password');
    const response = await api.post('EISHome/servicewise_top5_FiveM/SYS/', {
      "time": time,
      "uid": uid,
      "password": password
    });
    return response;
  } catch (error) {
    console.error('Could not fetch error:', error);
    throw error;
  }
};

export const postIpWiseExp5 = async (time) => {
  try {
    const uid = localStorage.getItem('uidd');
    const password = localStorage.getItem('password');
    const response = await api.post('EISHome/ipwise_top5_FiveM/EXP/', {
      "time": time,
      "uid": uid,
      "password": password
    });
    return response;
  } catch (error) {
    console.error('Could not fetch error:', error);
    throw error;
  }
};

export const postIpWiseSys5 = async (time) => {
  try {
    const uid = localStorage.getItem('uidd');
    const password = localStorage.getItem('password');
    const response = await api.post('EISHome/ipwise_top5_FiveM/SYS/', {
      "time": time,
      "uid": uid,
      "password": password
    });
    return response;
  } catch (error) {
    console.error('Could not fetch error:', error);
    throw error;
  }
};

export const postPortWiseExp5 = async (time) => {
  try {
    const uid = localStorage.getItem('uidd');
    const password = localStorage.getItem('password');
    const response = await api.post('EISHome/portwise_top5_FiveM/EXP/', {
      "time": time,
      "uid": uid,
      "password": password
    });
    return response;
  } catch (error) {
    console.error('Could not fetch error:', error);
    throw error;
  }
};

export const postPortWiseSys5 = async (time) => {
  try {
    const uid = localStorage.getItem('uidd');
    const password = localStorage.getItem('password');
    const response = await api.post('EISHome/portwise_top5_FiveM/SYS/', {
      "time": time,
      "uid": uid,
      "password": password
    });
    return response;
  } catch (error) {
    console.error('Could not fetch error:', error);
    throw error;
  }
};

// === UPDATED MQ API FUNCTIONS BELOW ===

// POST to EISHome/mqOverall/<layer>/ with { username, password }
export const postMqOverall = async (layer) => {
  try {
    const uid = localStorage.getItem('uidd');
    const password = localStorage.getItem('password');
    const response = await api.post(`EISHome/mqOverall/${layer}/`, {
      uid,
      password,
    });
    return response;
  } catch (error) {
    console.error('Could not fetch mqOverall:', error);
    throw error;
  }
};

// POST to EISHome/mqSource/<layer>/ with { username, password }
export const postMqSource = async (layer) => {
  try {
    const uid = localStorage.getItem('uidd');
    const password = localStorage.getItem('password');
    const response = await api.post(`EISHome/mqSource/${layer}/`, {
      uid,
      password,
    });
    return response;
  } catch (error) {
    console.error('Could not fetch mqSource:', error);
    throw error;
  }
};

// POST to EISHome/mqHourly/<layer>/ with { username, password, hour }
export const postMqHourly = async (layer, hour) => {
  try {
    const uid = localStorage.getItem('uidd');
    const password = localStorage.getItem('password');
    const response = await api.post(`EISHome/mqHourly/${layer}/`, {
      uid,
      password,
      hour,
    });
    return response;
  } catch (error) {
    console.error('Could not fetch mqHourly:', error);
    throw error;
  }
};

// Download mqgraph (source or overall) given a path ending with /layer/
export const downloadMqGraph = async (path) => {
  try {
    const uid = localStorage.getItem('uidd');
    const password = localStorage.getItem('password');
    // Ensure the path ends with a slash
    if (!path.endsWith('/')) {
      path += '/';
    }
    const payload = {
      uid,
      password,
      download: true
    };
    // If the API returns a file, use responseType: 'blob'
    const response = await api.post(path, payload, { responseType: 'blob' });
    return response;
  } catch (error) {
    console.error('Could not download mqgraph:', error);
    throw error;
  }
};

// Download mqHourly given a path ending with /layer/ and an hour
export const downloadMqHourly = async (path, hour) => {
  try {
    const uid = localStorage.getItem('uidd');
    const password = localStorage.getItem('password');
    // Ensure the path ends with a slash
    if (!path.endsWith('/')) {
      path += '/';
    }
    const payload = {
      uid,
      password,
      hour,
      download: true
    };
    // If the API returns a file, use responseType: 'blob'
    const response = await api.post(path, payload, { responseType: 'blob' });
    return response;
  } catch (error) {
    console.error('Could not download mqHourly:', error);
    throw error;
  }
};

// === ANNOUNCEMENT API ===
export const postAnnouncement = async (announcement, time) => {
  try {
    const uid = localStorage.getItem('uidd');
    const password = localStorage.getItem('password');
    const payload = {
      announcement,
      time: time && !isNaN(Number(time)) ? Number(time) : 24,
      uid,
      password,
    };
    const response = await api.post('EISHome/announcement/', payload, {
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      }
    });
    return response;
  } catch (error) {
    console.error('Could not post announcement:', error);
    throw error;
  }
};

export const fetchLatestAnnouncement = async () => {
  try {
    const uid = localStorage.getItem('uidd');
    const password = localStorage.getItem('password');
    const res = await api.post('EISHome/announcement/', { uid, password });
    // Assuming the response is { announcement: "..." }
    return res.data.announcement || "";
  } catch (error) {
    console.error('Could not fetch announcement:', error);
    return "";
  }
};

// === ALERT MODAL API ===
export const fetchPortalAlerts = async () => {
  try {
    const uid = localStorage.getItem('uidd');
    const password = localStorage.getItem('password');
    const response = await api.post('EISHome/getPortalAlerts/', {
      uid,
      password
    });
    return response;
  } catch (error) {
    console.error('Could not fetch portal alerts:', error);
    throw error;
  }
};

// Add API for getting security question
export const postGetSecurityQuestion = async (uid) => {
  try {
    const response = await axios.post(
      'https://10.191.171.12:5443/EISHOME_TEST/EISHome/getSecurityQuestion/',
    // const response = await axios.post(
    //  'https://10.191.171.12:5443/EISHOME/EISHome/getSecurityQuestion/',

      { uid },
      { headers: { 'Content-Type': 'application/json' } }
    );
    return response;
  } catch (error) {
    throw error;
  }
};

// Add API for forgot password
export const postForgotPassword = async ({ uid, securityQuestion, password,answer }) => {
  try {
    const response = await axios.post(
      'https://10.191.171.12:5443/EISHOME_TEST/EISHome/forgotPassword/',
     // 'https://10.191.171.12:5443/EISHOME/EISHome/forgotPassword/',
      { uid, securityQuestion, password ,answer },
      { headers: { 'Content-Type': 'application/json' } }
    );
    return response;
  } catch (error) {
    throw error;
  }
};





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

// Login API call to get userLevel and other details
async function loginApi(username, password) {
  const response = await fetch('https://10.191.171.12:5443/EISHOME_TEST/EISHome/newLogin/',
 // const response = await fetch('https://10.191.171.12:5443/EISHOME/EISHome/newLogin/',
          {
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
    const response = await fetch('https://10.191.171.12:5443/EISHOME_TEST/EISHome/newLogout/',
   // const response = await fetch('https://10.191.171.12:5443/EISHOME/EISHome/newLogout/',
            {
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

  // Inactivity time limit in ms (60 minutes)
  const INACTIVITY_LIMIT = 60 * 60 * 1000;

  // Only disable inspect for users other than ADMIN
  useDisableInspectElement(userLevel && userLevel !== 'ADMIN');

  // Check for existing login session on app load
  useEffect(() => {
    const storedUsername = localStorage.getItem('username');
    const storedLoginTime = localStorage.getItem('loginTime');
    const storedUserLevel = localStorage.getItem('userlevel');
    if (storedUsername && storedLoginTime && storedUserLevel) {
      setUsername(storedUsername);
      setUserLevel(storedUserLevel); // <- ensure userLevel is set!
      setIsLoggedIn(true);
    }
  }, []);

  // Set login timestamp and userLevel on login
  const handleLogin = async (user, password) => {
    try {
      const loginData = await loginApi(user, password);
      const now = Date.now();
      setUsername(user);

      // Set userLevel from response!
      setUserLevel(loginData.userLevel);

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
    setUserLevel('');

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
