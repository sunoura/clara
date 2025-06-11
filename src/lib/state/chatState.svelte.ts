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

    // Add user message
    const userPayloadResponse = await fetch(`${API_BASE}/interaction-payloads/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: chatState.currentSession.id,
        content,
        from: 'user',
        ok: true
      })
    });

    if (!userPayloadResponse.ok) {
      throw new Error('Failed to send message');
    }

    const userPayload = await userPayloadResponse.json();
    
    // Add user message to local state
    chatState.messages.push({
      id: userPayload.id,
      content: userPayload.content,
      from: 'user',
      ok: userPayload.ok,
      err: userPayload.err,
      created_at: userPayload.created_at
    });

    // Clear input
    chatState.inputValue = '';

    // Simulate AI response (replace with actual AI integration later)
    const aiResponse = `This is a simulated response to: "${content}"`;
    
    const aiPayloadResponse = await fetch(`${API_BASE}/interaction-payloads/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: chatState.currentSession.id,
        content: aiResponse,
        from: 'model',
        ok: true
      })
    });

    if (!aiPayloadResponse.ok) {
      throw new Error('Failed to get AI response');
    }

    const aiPayload = await aiPayloadResponse.json();
    
    // Add AI message to local state
    chatState.messages.push({
      id: aiPayload.id,
      content: aiPayload.content,
      from: 'model',
      ok: aiPayload.ok,
      err: aiPayload.err,
      created_at: aiPayload.created_at
    });

  } catch (error) {
    chatState.error = error instanceof Error ? error.message : 'Failed to send message';
  } finally {
    chatState.isLoading = false;
  }
}

export async function loadSession(sessionId: string): Promise<void> {
  try {
    chatState.isLoading = true;
    chatState.error = null;

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
} 