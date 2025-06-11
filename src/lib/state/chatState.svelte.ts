/**
 * Clara Chat Application State Management
 * 
 * This module manages the global chat state using Svelte 5 runes.
 * Provides real-time WebSocket communication with instant UI feedback.
 */

export interface ChatMessage {
  id: number;
  content: string;
  from: 'user' | 'model';
  ok: boolean;
  err?: string; 
  created_at: string;
  isLoading?: boolean; // Used for loading states like "Clara is thinking..."
}

export interface ChatSession {
  id: string;
  title: string;
  context_summary?: string;
  started_at: string;
  payloads?: ChatMessage[];
}

interface ChatState {
  currentSession: ChatSession | null;
  sessions: ChatSession[];
  messages: ChatMessage[];
  isLoading: boolean;
  error: string | null;
  inputValue: string;
}

// Initialize chat state
export const chatState = $state<ChatState>({
  currentSession: null,
  sessions: [],
  messages: [],
  isLoading: false,
  error: null,
  inputValue: ''
});

// API base URL - uses Vite proxy
const API_BASE = '/api';

// API functions
export async function createSession(title: string, contextSummary?: string): Promise<ChatSession | null> {
  try {
    chatState.isLoading = true;
    chatState.error = null;

    const response = await fetch(`${API_BASE}/interaction-sessions/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        title,
        context_summary: contextSummary
      })
    });

    if (!response.ok) {
      throw new Error('Failed to create session');
    }

    const session = await response.json();
    chatState.currentSession = session;
    chatState.sessions.unshift(session);
    chatState.messages = [];
    
    return session;
  } catch (error) {
    chatState.error = error instanceof Error ? error.message : 'Failed to create session';
    return null;
  } finally {
    chatState.isLoading = false;
  }
}

/**
 * Send a message via WebSocket with instant UI feedback.
 * 
 * Flow:
 * 1. Show user message immediately (temporary)
 * 2. Show "Clara is thinking..." (temporary)  
 * 3. Send via WebSocket
 * 4. WebSocket handlers replace temporary messages with real data
 */
export async function sendMessage(content: string): Promise<void> {
  if (!chatState.currentSession) return;

  try {
    chatState.error = null;

    // Import wsState here to avoid circular dependencies
    const { wsState } = await import('./wsState.svelte.js');
    
    // Only use WebSocket - no HTTP fallback
    if (!wsState.isConnected) {
      chatState.error = 'Not connected to chat server. Please refresh the page.';
      return;
    }

    // Clear input immediately for responsive feel
    chatState.inputValue = '';

    // Add user message immediately to UI (with temporary negative ID)
    const tempUserMessage = {
      id: -Date.now(), // Negative ID to avoid conflicts with real database IDs
      content: content,
      from: 'user' as const,
      ok: true,
      created_at: new Date().toISOString()
    };
    chatState.messages.push(tempUserMessage);

    // Add Clara loading message immediately
    const tempLoadingMessage = {
      id: -Date.now() - 1, // Negative ID to avoid conflicts
      content: 'Clara is thinking...',
      from: 'model' as const,
      ok: true,
      isLoading: true,
      created_at: new Date().toISOString()
    };
    chatState.messages.push(tempLoadingMessage);

    // Send via WebSocket - responses will update the UI via handlers
    const success = wsState.sendMessage(content);
    if (!success) {
      // Remove loading message and show error on user message
      const loadingIndex = chatState.messages.findIndex(m => m.id === tempLoadingMessage.id);
      if (loadingIndex !== -1) {
        chatState.messages.splice(loadingIndex, 1);
      }
      
      const userIndex = chatState.messages.findIndex(m => m.id === tempUserMessage.id);
      if (userIndex !== -1) {
        chatState.messages[userIndex] = {
          ...chatState.messages[userIndex],
          ok: false,
          err: 'Failed to send message'
        };
      }
    }

  } catch (error) {
    chatState.error = error instanceof Error ? error.message : 'Failed to send message';
  }
}



export async function loadSession(sessionId: string): Promise<void> {
  try {
    chatState.isLoading = true;
    chatState.error = null;

    // FIRST: Disconnect any existing WebSocket to prevent cross-session interference
    await disconnectWebSocket();

    // Load session details
    const sessionResponse = await fetch(`${API_BASE}/interaction-sessions/${sessionId}`);
    if (!sessionResponse.ok) {
      throw new Error('Failed to load session');
    }

    const session = await sessionResponse.json();
    chatState.currentSession = session;

    // Load messages for this session
    const messagesResponse = await fetch(`${API_BASE}/interaction-payloads/by-session/${sessionId}`);
    if (!messagesResponse.ok) {
      throw new Error('Failed to load messages');
    }

    const payloads = await messagesResponse.json();
    chatState.messages = payloads.map((payload: any) => ({
      id: payload.id,
      content: payload.content,
      from: payload.from,
      ok: payload.ok,
      err: payload.err,
      created_at: payload.created_at
    }));

    // THEN: Connect to WebSocket for real-time communication
    // Add a small delay to ensure clean disconnection
    await new Promise(resolve => setTimeout(resolve, 100));
    await connectWebSocket(sessionId);

  } catch (error) {
    chatState.error = error instanceof Error ? error.message : 'Failed to load session';
  } finally {
    chatState.isLoading = false;
  }
}

export async function loadRecentSessions(): Promise<void> {
  try {
    chatState.isLoading = true;
    chatState.error = null;

    const response = await fetch(`${API_BASE}/interaction-sessions/recent?limit=10`);
    if (!response.ok) {
      throw new Error('Failed to load recent sessions');
    }

    const sessions = await response.json();
    chatState.sessions = sessions;

  } catch (error) {
    chatState.error = error instanceof Error ? error.message : 'Failed to load recent sessions';
  } finally {
    chatState.isLoading = false;
  }
}

export function startNewSession(): void {
  chatState.currentSession = null;
  chatState.messages = [];
  chatState.inputValue = '';
  chatState.error = null;
  
  // Disconnect WebSocket when starting new session
  import('./wsState.svelte.js').then(({ wsState }) => {
    wsState.disconnect();
  });
}

// WebSocket integration functions
export async function connectWebSocket(sessionId: string): Promise<void> {
  const { wsState } = await import('./wsState.svelte.js');
  
  // Connect to session FIRST
  wsState.connect(sessionId);
  
  // THEN set up WebSocket handlers (after connection to avoid them being cleared)
  wsState.setHandlers({
    onUserMessage: (message) => {
      // Find and replace temporary user message with real one
      const tempUserIndex = chatState.messages.findIndex(m => m.id < 0 && m.from === 'user' && m.content === message.content);
      if (tempUserIndex !== -1) {
        chatState.messages[tempUserIndex] = {
          id: message.id,
          content: message.content,
          from: message.from,
          ok: message.ok,
          err: message.err,
          created_at: message.created_at
        };
      } else {
        // If no temp message found, just add it (shouldn't happen normally)
        chatState.messages.push(message);
      }
    },
    onAiResponse: (message) => {
      // Find and replace the loading message with Clara's real response
      const loadingIndex = chatState.messages.findIndex(m => m.isLoading === true);
      
      if (loadingIndex !== -1) {
        chatState.messages[loadingIndex] = {
          id: message.id,
          content: message.content,
          from: message.from,
          ok: message.ok,
          err: message.err,
          created_at: message.created_at
        };
      } else {
        // If no loading message found, just add it (fallback)
        chatState.messages.push(message);
      }
      
      chatState.isLoading = false;
    },
    onError: (error) => {
      // Remove any loading messages
      const loadingIndex = chatState.messages.findIndex(m => m.isLoading === true);
      if (loadingIndex !== -1) {
        chatState.messages.splice(loadingIndex, 1);
      }
      
      chatState.error = error;
      chatState.isLoading = false;
    }
  });
}

export async function disconnectWebSocket(): Promise<void> {
  const { wsState } = await import('./wsState.svelte.js');
  wsState.disconnect();
} 