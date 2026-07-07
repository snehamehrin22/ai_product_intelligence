import React, { useState, useRef, useEffect } from 'react';
import './AgentChat.css';
import { sendAgentMessage } from '../services/api';
import eventEmitter from '../services/eventEmitter';

function AgentChat({ userId, onTaskCreated }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const userMessage = inputValue.trim();
    if (!userMessage || isLoading) return;

    // Add user message to chat
    const userMsg = {
      id: Date.now(),
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMsg]);
    setInputValue('');
    setIsLoading(true);

    // Emit agent_message_sent event
    eventEmitter.emit('agent_message_sent', userId, {
      message_text: userMessage,
      message_length: userMessage.length,
      timestamp: userMsg.timestamp
    });

    try {
      // Send to agent
      const response = await sendAgentMessage(userMessage, userId);

      // Add agent response to chat
      const agentMsg = {
        id: Date.now() + 1,
        role: 'agent',
        content: response.message,
        taskCreated: response.task_created,
        taskId: response.task_id,
        needsClarification: response.needs_clarification,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, agentMsg]);

      // Emit agent_message_received event
      eventEmitter.emit('agent_message_received', userId, {
        message_text: response.message,
        message_length: response.message.length,
        task_created: response.task_created || false,
        task_id: response.task_id || null,
        needs_clarification: response.needs_clarification || false,
        timestamp: agentMsg.timestamp
      });

      // Notify parent if task was created
      if (response.task_created && onTaskCreated) {
        onTaskCreated();
      }
    } catch (error) {
      // Add error message
      const errorMsg = {
        id: Date.now() + 1,
        role: 'agent',
        content: `❌ Error: ${error.message}`,
        isError: true,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={`agent-chat-container ${isOpen ? 'open' : 'closed'}`}>
      {/* Toggle Button */}
      <button
        className="agent-toggle-btn"
        onClick={() => setIsOpen(!isOpen)}
        aria-label={isOpen ? 'Close AI Assistant' : 'Open AI Assistant'}
      >
        {isOpen ? '✕' : '🤖'}
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div className="agent-chat-panel">
          <div className="chat-header">
            <h3>AI Assistant</h3>
            <p className="chat-subtitle">Create tasks naturally</p>
          </div>

          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="empty-chat">
                <p>👋 Hi! I can help you create tasks.</p>
                <p className="hint">Try: "Remind me to buy milk tomorrow at 3pm"</p>
              </div>
            )}

            {messages.map(msg => (
              <div
                key={msg.id}
                className={`message ${msg.role} ${msg.isError ? 'error' : ''}`}
              >
                <div className="message-content">
                  <div className="message-text">{msg.content}</div>
                  {msg.taskCreated && (
                    <div className="task-created-badge">
                      ✓ Task created
                    </div>
                  )}
                </div>
                <div className="message-time">{formatTime(msg.timestamp)}</div>
              </div>
            ))}

            {isLoading && (
              <div className="message agent">
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="chat-input-form">
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Type a message..."
              disabled={isLoading}
              className="chat-input"
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              className="send-btn"
              aria-label="Send message"
            >
              {isLoading ? '...' : '→'}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}

export default AgentChat;
