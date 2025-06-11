import type { ChatMessage } from './chatState.svelte.js';

interface WebSocketMessage {
  type: 'user_message' | 'ai_response' | 'error' | 'ping' | 'pong';
  content?: string;
  payload_id?: number;
  timestamp?: string;
  message?: string;
}

class WebSocketState {
  private ws: WebSocket | null = $state(null);
  private currentSessionId: string | null = $state(null);
  private reconnectAttempts = $state(0);
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  
  isConnected = $state(false);
  isConnecting = $state(false);
  error = $state<string | null>(null);
  
  // Callbacks for handling different message types
  private onUserMessage?: (message: ChatMessage) => void;
  private onAiResponse?: (message: ChatMessage) => void;
  private onError?: (error: string) => void;

  connect(sessionId: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN && this.currentSessionId === sessionId) {
      return; // Already connected to this session
    }

    this.disconnect(); // Close existing connection
    
    // Clear any existing handlers to prevent cross-session messages
    this.onUserMessage = undefined;
    this.onAiResponse = undefined;
    this.onError = undefined;
    
    this.currentSessionId = sessionId;
    this.isConnecting = true;
    this.error = null;

    const wsUrl = `ws://localhost:8000/api/chat/ws/${sessionId}`;
    
    try {
      this.ws = new WebSocket(wsUrl);
      this.setupEventHandlers();
    } catch (err) {
      this.handleConnectionError(`Failed to create WebSocket: ${err}`);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isConnected = false;
    this.isConnecting = false;
    this.currentSessionId = null;
    this.reconnectAttempts = 0;
    
    // Clear handlers to prevent any lingering callbacks
    this.onUserMessage = undefined;
    this.onAiResponse = undefined;
    this.onError = undefined;
  }

  sendMessage(content: string) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      this.error = 'WebSocket is not connected';
      return false;
    }

    try {
      this.ws.send(JSON.stringify({
        type: 'message',
        content
      }));
      return true;
    } catch (err) {
      this.error = `Failed to send message: ${err}`;
      return false;
    }
  }

  ping() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type: 'ping' }));
    }
  }

  // Set callback handlers
  setHandlers(handlers: {
    onUserMessage?: (message: ChatMessage) => void;
    onAiResponse?: (message: ChatMessage) => void;
    onError?: (error: string) => void;
  }) {
    this.onUserMessage = handlers.onUserMessage;
    this.onAiResponse = handlers.onAiResponse;
    this.onError = handlers.onError;
  }

  private setupEventHandlers() {
    if (!this.ws) return;

    this.ws.onopen = () => {
      console.log(`WebSocket connected to session ${this.currentSessionId}`);
      this.isConnected = true;
      this.isConnecting = false;
      this.error = null;
      this.reconnectAttempts = 0;
    };

    this.ws.onclose = (event) => {
      console.log('WebSocket closed:', event.code, event.reason);
      this.isConnected = false;
      this.isConnecting = false;
      
      // Attempt to reconnect if it wasn't a manual disconnect
      if (event.code !== 1000 && this.currentSessionId && this.reconnectAttempts < this.maxReconnectAttempts) {
        this.attemptReconnect();
      }
    };

    this.ws.onerror = (event) => {
      console.error('WebSocket error:', event);
      this.handleConnectionError('WebSocket connection error');
    };

    this.ws.onmessage = (event) => {
      try {
        const message: WebSocketMessage = JSON.parse(event.data);
        this.handleMessage(message);
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
        this.error = 'Received invalid message from server';
      }
    };
  }

  private handleMessage(message: WebSocketMessage) {
    switch (message.type) {
      case 'user_message':
        if (message.content && message.timestamp && this.onUserMessage) {
          // Only process if we have a valid payload_id from the server
          if (message.payload_id) {
            this.onUserMessage({
              id: message.payload_id,
              content: message.content,
              from: 'user',
              ok: true,
              created_at: message.timestamp
            });
          } else {
            console.warn('Received user message without payload_id, ignoring:', message.content);
          }
        }
        break;

      case 'ai_response':
        if (message.content && message.timestamp && this.onAiResponse) {
          // Only process if we have a valid payload_id from the server
          if (message.payload_id) {
            this.onAiResponse({
              id: message.payload_id,
              content: message.content,
              from: 'model',
              ok: true,
              created_at: message.timestamp
            });
          } else {
            console.warn('Received AI response without payload_id, ignoring:', message.content);
          }
        }
        break;

      case 'error':
        const errorMsg = message.message || 'Unknown error occurred';
        console.error('Server error:', errorMsg);
        this.error = errorMsg;
        if (this.onError) {
          this.onError(errorMsg);
        }
        break;

      case 'pong':
        // Handle ping response - connection is alive
        break;

      default:
        console.warn('Unknown message type:', message.type);
    }
  }

  private handleConnectionError(errorMessage: string) {
    console.error(errorMessage);
    this.error = errorMessage;
    this.isConnected = false;
    this.isConnecting = false;
    
    if (this.onError) {
      this.onError(errorMessage);
    }
  }

  private attemptReconnect() {
    if (!this.currentSessionId) return;

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1); // Exponential backoff
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      if (this.currentSessionId) {
        this.connect(this.currentSessionId);
      }
    }, delay);
  }
}

// Export singleton instance
export const wsState = new WebSocketState(); 