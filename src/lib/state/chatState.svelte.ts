// Global chat state using Svelte 5 runes
export interface ChatMessage {
  id: number;
  content: string;
  from: 'user' | 'model';
  ok: boolean;
  err?: string;
  created_at: string;
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

export async function sendMessage(content: string): Promise<void> {
  if (!chatState.currentSession) return;

  try {
    chatState.isLoading = true;
    chatState.error = null;

    // Import wsState here to avoid circular dependencies
    const { wsState } = await import('./wsState.svelte.js');
    
    // Send message via WebSocket if connected
    if (wsState.isConnected) {
      const success = wsState.sendMessage(content);
      if (success) {
        chatState.inputValue = ''; // Clear input on successful send
        return;
      }
    }

    // Fallback to HTTP if WebSocket is not available
    await sendMessageHTTP(content);

  } catch (error) {
    chatState.error = error instanceof Error ? error.message : 'Failed to send message';
  } finally {
    chatState.isLoading = false;
  }
}

// HTTP fallback for sending messages
async function sendMessageHTTP(content: string): Promise<void> {
  if (!chatState.currentSession) return;

  // Clear input immediately
  chatState.inputValue = '';

  // Use chat endpoint which handles both user message creation and AI response
  const response = await fetch(`${API_BASE}/chat/${chatState.currentSession.id}/message`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      content
    })
  });

  if (!response.ok) {
    throw new Error('Failed to send message');
  }

  const data = await response.json();
  
  // Add user message to local state
  chatState.messages.push({
    id: data.user_message.id,
    content: data.user_message.content,
    from: 'user',
    ok: true,
    created_at: data.user_message.created_at
  });
  
  // Add AI message to local state  
  chatState.messages.push({
    id: data.ai_response.id,
    content: data.ai_response.content,
    from: 'model',
    ok: true,
    created_at: data.ai_response.created_at
  });
}

export async function loadSession(sessionId: string): Promise<void> {
  try {
    console.log($state.snapshot(chatState));
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
  
  // Set up WebSocket handlers
  wsState.setHandlers({
    onUserMessage: (message) => {
      console.log('Received user message via WebSocket:', message);
      chatState.messages.push(message);
    },
    onAiResponse: (message) => {
      console.log('Received AI message via WebSocket:', message);
      chatState.messages.push(message);
      chatState.isLoading = false;
    },
    onError: (error) => {
      chatState.error = error;
      chatState.isLoading = false;
    }
  });
  
  // Connect to session
  wsState.connect(sessionId);
}

export async function disconnectWebSocket(): Promise<void> {
  const { wsState } = await import('./wsState.svelte.js');
  wsState.disconnect();
} 