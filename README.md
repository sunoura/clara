# Clara Chat

A modern real-time chat application powered by AI. Clara is your intelligent personal assistant that provides thoughtful responses through a beautiful, responsive interface.

## ✨ Features

- **Real-time Communication** - WebSocket-powered instant messaging
- **AI-Powered Responses** - Powered by Google Gemini for intelligent conversations
- **Instant UI Feedback** - Messages appear immediately with loading states
- **Session Management** - Persistent conversation history
- **Modern UI** - Built with Svelte 5 and TailwindCSS
- **Responsive Design** - Works seamlessly on desktop and mobile

## 🛠 Tech Stack

### Frontend
- **Svelte 5** - Modern reactive framework with runes
- **SvelteKit** - Full-stack framework for routing and SSR
- **TailwindCSS 4** - Utility-first CSS framework
- **TypeScript** - Type-safe development
- **Vite** - Fast build tool and dev server

### Backend
- **FastAPI** - Modern Python web framework
- **SQLModel** - SQL database ORM with Pydantic integration
- **WebSockets** - Real-time bidirectional communication
- **Google Gemini** - AI language model integration
- **SQLite** - Database storage

## 🚀 Quick Start

### Prerequisites
- **Node.js** 18+ 
- **Python** 3.9+
- **pnpm** (recommended) or npm

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd copen-1
   ```

2. **Backend Setup**
   ```bash
   cd src-py
   
   # Create virtual environment
   python -m venv .venv
   
   # Activate virtual environment
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   # From project root
   pnpm install
   # or
   npm install
   ```

4. **Environment Configuration**
   ```bash
   # In src-py directory, create .env file
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

5. **Run the Application**
   
   **Terminal 1 - Backend:**
   ```bash
   cd src-py
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```
   
   **Terminal 2 - Frontend:**
   ```bash
   pnpm dev
   # or
   npm run dev
   ```

6. **Open your browser**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 📁 Project Structure

```
├── src/                          # Frontend (SvelteKit)
│   ├── lib/
│   │   ├── components/           # Reusable UI components
│   │   │   ├── chat/            # Chat-specific components
│   │   │   └── ui/              # Base UI components
│   │   └── state/               # Global state management
│   │       ├── chatState.svelte.ts    # Chat state & API calls
│   │       └── wsState.svelte.ts      # WebSocket management
│   ├── routes/                   # SvelteKit routes
│   └── app.html                  # Main app template
│
├── src-py/                       # Backend (FastAPI)
│   ├── api/                      # API route handlers
│   │   ├── chat_routes.py       # Chat WebSocket & endpoints
│   │   ├── interaction_*.py     # Session & payload endpoints
│   │   └── __init__.py
│   ├── services/                 # Business logic layer
│   │   ├── chat_service.py      # Message processing & AI
│   │   └── interaction_service.py # Database operations
│   ├── data/                     # Data models & database
│   │   ├── models.py            # SQLModel definitions
│   │   └── database.db          # SQLite database
│   ├── lib/                      # External integrations
│   │   └── gemini.py            # Google Gemini client
│   ├── tests/                    # Test suite
│   └── main.py                   # FastAPI application
│
├── static/                       # Static assets
├── package.json                  # Node.js dependencies
└── requirements.txt              # Python dependencies
```

## 🔧 Development

### Frontend Commands
```bash
pnpm dev          # Start development server
pnpm build        # Build for production
pnpm preview      # Preview production build
pnpm test         # Run tests
pnpm check        # Type checking
```

### Backend Commands
```bash
# From src-py directory
uvicorn main:app --reload                    # Development server
pytest                                       # Run tests
pytest tests/ -v                            # Verbose test output
```

## 📡 API Reference

### WebSocket Endpoints

#### `ws://localhost:8000/api/chat/ws/{session_id}`
Real-time chat communication

**Message Types:**
- `message` - Send user message
- `ping` - Keep connection alive

**Response Types:**
- `user_message` - User message confirmation
- `ai_response` - Clara's AI response
- `error` - Error notification
- `pong` - Ping response

### HTTP Endpoints

#### Sessions
- `GET /api/interaction-sessions/recent` - Get recent sessions
- `POST /api/interaction-sessions/` - Create new session
- `GET /api/interaction-sessions/{id}` - Get session details
- `DELETE /api/interaction-sessions/{id}` - Delete session

#### Messages
- `GET /api/interaction-payloads/by-session/{session_id}` - Get session messages
- `POST /api/interaction-payloads/` - Create message (internal use)

## 🎯 Architecture Highlights

### Real-time Communication Flow
1. **User types message** → Input cleared immediately
2. **Temporary messages shown** → User message + "Clara is thinking..."
3. **WebSocket transmission** → Message sent to backend
4. **AI processing** → Gemini generates response
5. **Real data replacement** → Temporary messages replaced with real database records

### State Management
- **Svelte 5 Runes** - Reactive state management
- **WebSocket State** - Connection management with auto-reconnection
- **Chat State** - Message history and session management

### Database Design
- **Sessions** - Conversation containers with metadata
- **Payloads** - Individual messages with timestamps and status
- **Relationships** - Proper foreign key constraints

## 🧪 Testing

### Backend Tests
```bash
cd src-py
pytest tests/ -v
```

**Test Coverage:**
- ✅ Database operations (CRUD)
- ✅ API endpoints (HTTP + WebSocket)
- ✅ Service layer logic
- ✅ Model validation
- ✅ AI integration

### Frontend Tests
```bash
pnpm test
```

## 🚀 Production Deployment

### Backend
```bash
cd src-py
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
pnpm build
pnpm preview
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

---

**Built with ❤️ using modern web technologies**
