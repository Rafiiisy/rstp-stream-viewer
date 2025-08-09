import React, { useState, useEffect } from 'react';
import './Notification.css';

const Notification = ({ message, type, onClose, duration = 4000 }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isHiding, setIsHiding] = useState(false);

  useEffect(() => {
    // Show notification after a brief delay
    const showTimer = setTimeout(() => {
      setIsVisible(true);
    }, 100);

    // Auto-hide notification
    const hideTimer = setTimeout(() => {
      handleClose();
    }, duration);

    return () => {
      clearTimeout(showTimer);
      clearTimeout(hideTimer);
    };
  }, [duration]);

  const handleClose = () => {
    setIsHiding(true);
    setTimeout(() => {
      onClose();
    }, 300); // Match CSS transition duration
  };

  return (
    <div className={`notification ${type} ${isVisible ? 'show' : ''} ${isHiding ? 'hide' : ''}`}>
      <div className="notification-content">
        <span className="notification-message">{message}</span>
      </div>
      <button className="notification-close" onClick={handleClose}>
        ✕
      </button>
    </div>
  );
};

export default Notification;
