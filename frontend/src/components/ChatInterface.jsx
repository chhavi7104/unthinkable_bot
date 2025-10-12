import React, { useState, useRef, useEffect } from 'react';
import './ChatInterface.css';

const ChatInterface = () => {
    const [messages, setMessages] = useState([]);
    const [inputMessage, setInputMessage] = useState('');
    const [sessionId, setSessionId] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        // Initialize session
        const initializeSession = async () => {
            try {
                const response = await fetch('http://localhost:8000/sessions/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                const data = await response.json();
                setSessionId(data.session_id);
                
                // Add welcome message
                setMessages([{
                    id: 1,
                    text: "Hello! I'm your AI customer support assistant. How can I help you today?",
                    isUser: false,
                    timestamp: new Date()
                }]);
            } catch (error) {
                console.error('Error initializing session:', error);
            }
        };

        initializeSession();
    }, []);

    const handleSendMessage = async () => {
        if (!inputMessage.trim() || !sessionId || isLoading) return;

        const userMessage = {
            id: Date.now(),
            text: inputMessage,
            isUser: true,
            timestamp: new Date()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputMessage('');
        setIsLoading(true);

        try {
            const response = await fetch(`http://localhost:8000/sessions/${sessionId}/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: inputMessage }),
            });

            const data = await response.json();

            const botMessage = {
                id: Date.now() + 1,
                text: data.response,
                isUser: false,
                timestamp: new Date(),
                requiresEscalation: data.requires_escalation
            };

            setMessages(prev => [...prev, botMessage]);

            if (data.requires_escalation) {
                // Auto-escalate if needed
                await handleEscalate();
            }

        } catch (error) {
            console.error('Error sending message:', error);
            const errorMessage = {
                id: Date.now() + 1,
                text: "Sorry, I'm having trouble connecting. Please try again.",
                isUser: false,
                timestamp: new Date()
            };
            setMessages(prev => [...prev, errorMessage]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleEscalate = async () => {
        if (!sessionId) return;

        try {
            const response = await fetch(`http://localhost:8000/sessions/${sessionId}/escalate`, {
                method: 'POST',
            });
            const data = await response.json();

            const escalationMessage = {
                id: Date.now(),
                text: "🚨 This conversation has been escalated to a human agent. They will be with you shortly.",
                isUser: false,
                timestamp: new Date(),
                isSystem: true
            };

            setMessages(prev => [...prev, escalationMessage]);
        } catch (error) {
            console.error('Error escalating conversation:', error);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    return (
        <div className="chat-container">
            <div className="chat-header">
                <h2>AI Customer Support</h2>
                <div className="session-info">
                    Session: {sessionId ? sessionId.substring(0, 8) + '...' : 'Loading...'}
                </div>
            </div>

            <div className="messages-container">
                {messages.map((message) => (
                    <div
                        key={message.id}
                        className={`message ${message.isUser ? 'user-message' : 'bot-message'} ${message.isSystem ? 'system-message' : ''}`}
                    >
                        <div className="message-content">
                            {message.text}
                            {message.requiresEscalation && (
                                <div className="escalation-warning">
                                    ⚠️ I recommend escalating this to a human agent
                                </div>
                            )}
                        </div>
                        <div className="message-timestamp">
                            {message.timestamp.toLocaleTimeString()}
                        </div>
                    </div>
                ))}
                {isLoading && (
                    <div className="message bot-message">
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

            <div className="input-container">
                <textarea
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Type your message here..."
                    disabled={isLoading}
                    rows={2}
                />
                <button 
                    onClick={handleSendMessage} 
                    disabled={!inputMessage.trim() || isLoading}
                >
                    Send
                </button>
                <button 
                    onClick={handleEscalate}
                    className="escalate-btn"
                    title="Escalate to human agent"
                >
                    🚨 Escalate
                </button>
            </div>
        </div>
    );
};

export default ChatInterface;