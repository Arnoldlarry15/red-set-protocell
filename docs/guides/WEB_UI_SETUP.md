# Red Set ProtoCell - Web UI Setup Guide

## Overview

The Red Set ProtoCell now includes a modern web interface for real-time red teaming operations. The UI features:

- **Glassmorphism Design**: Modern bento box style with black, red, and white color scheme
- **Live Attack Feed**: Real-time stream of attacks with detailed metrics
- **Interactive Dashboard**: Comprehensive charts and graphs
- **Configuration Controls**: Select attack strategies, vectors, and payloads
- **Cost Management**: Track API costs and auto-halt when limits are reached
- **Security Features**: Auto-halt on critical vulnerabilities

## Quick Start

### 1. Install Backend Dependencies

```bash
cd rsp-core/backend
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd ../../rsp-ui
npm install
```

### 3. Start the Backend API Server

```bash
cd ../rsp-core/backend
python -m app.api_server
```

The API server will start on `http://localhost:8000`

### 4. Start the Frontend Development Server

In a new terminal:

```bash
cd rsp-ui
npm run dev
```

The UI will be available at `http://localhost:3000`

## Adding Your Logo

The UI has placeholders for your Red Set ProtoCell logo. To add your custom logo:

1. **Prepare your logo**: Save as PNG or SVG format
2. **Place in public folder**: Copy to `rsp-ui/public/logo.png` (or `logo.svg`)
3. **Update components**: Replace the Shield icon placeholders

### Auth Page Logo

Edit `rsp-ui/src/pages/AuthPage.tsx`:

```tsx
// Replace this:
<div className="logo-placeholder">
  <Shield size={64} className="logo-icon" />
</div>

// With this:
<div className="logo-placeholder">
  <img src="/logo.png" alt="Red Set ProtoCell" style={{ width: '80px', height: '80px' }} />
</div>
```

### Dashboard Header Logo

Edit `rsp-ui/src/pages/Dashboard.tsx`:

```tsx
// Replace this:
<div className="header-logo">
  <Shield size={32} className="header-logo-icon" />
</div>

// With this:
<div className="header-logo">
  <img src="/logo.png" alt="Red Set ProtoCell" style={{ width: '48px', height: '48px' }} />
</div>
```

## Architecture

### Backend (FastAPI)

- **REST API**: Session management, configuration
- **WebSocket**: Real-time attack stream
- **Integration**: Connects to existing RSP core system

### Frontend (React + TypeScript)

- **Authentication**: API key validation
- **Dashboard**: Real-time monitoring
- **Charts**: Recharts for data visualization
- **State Management**: React hooks

### Communication Flow

```
┌─────────────┐         ┌──────────────┐         ┌────────────┐
│   Browser   │ ◄─────► │ FastAPI      │ ◄─────► │ RSP Core   │
│  (React UI) │         │ API Server   │         │ System     │
└─────────────┘         └──────────────┘         └────────────┘
     │                        │
     │   WebSocket            │
     │   (Real-time)          │
     └────────────────────────┘
```

## Features

### 1. Authentication Page

- API key input with secure storage
- Backend selection (OpenAI/Anthropic)
- Logo display
- Security notices

### 2. Dashboard

#### Live Attack Feed
- Real-time attack stream
- Attack details (prompt, response, scores)
- Severity indicators
- EGG blocking status

#### Metrics Panel
- Session statistics cards
- Score history chart
- Severity distribution pie chart
- Attack domain bar chart

#### Cost Tracker
- Real-time API cost monitoring
- Visual progress bar
- Warning alerts at 80%
- Auto-halt at limit

#### Attack Configuration
- Attack domain selection (7 domains)
- Mutation strategy selection (6 strategies)
- Session parameters (rounds, cost limit, mutation rate)
- Halt on critical toggle

#### User Input
- Custom prompt testing
- Execute button with validation
- Character counter

### 3. Auto-Halt Features

The system automatically halts when:
- **Critical vulnerability detected** (if enabled)
- **Max API cost reached**
- **Max rounds completed**

## Development

### Project Structure

```
rsp-core/backend/
└── app/
    └── api_server.py        # FastAPI server

rsp-ui/
├── src/
│   ├── components/          # React components
│   ├── pages/              # Page components
│   ├── styles/             # CSS files
│   ├── types/              # TypeScript types
│   └── services/           # API/WebSocket services
├── public/                 # Static assets (logo)
└── package.json
```

### Available Scripts

#### Backend
```bash
# Start API server
python -m app.api_server

# With auto-reload
uvicorn app.api_server:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend
```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## Production Deployment

### Build Frontend

```bash
cd rsp-ui
npm run build
```

This creates a `dist/` folder with optimized static files.

### Serve Frontend with Backend

Update `api_server.py` to serve static files:

```python
# Mount static files
app.mount("/", StaticFiles(directory="../../../rsp-ui/dist", html=True), name="static")
```

### Deploy

1. **Build frontend**: `npm run build`
2. **Copy dist to backend**: Configure static file serving
3. **Run backend**: `python -m app.api_server`
4. **Access**: Navigate to `http://localhost:8000`

## API Endpoints

### REST API

- `GET /` - API info
- `GET /api/health` - Health check
- `POST /api/session/start` - Start new session
- `POST /api/session/{id}/execute` - Execute session
- `POST /api/session/{id}/stop` - Stop session
- `POST /api/prompt/execute` - Execute custom prompt
- `GET /api/session/{id}/stats` - Get session stats

### WebSocket

- `WS /ws` - Real-time attack stream

## Troubleshooting

### Port Already in Use

Backend (8000):
```bash
lsof -ti:8000 | xargs kill -9
```

Frontend (3000):
```bash
lsof -ti:3000 | xargs kill -9
```

### CORS Issues

The API server includes CORS middleware. In production, restrict origins:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    ...
)
```

### WebSocket Connection Failed

1. Ensure backend is running
2. Check browser console for errors
3. Verify WebSocket URL in frontend code

## Security Considerations

1. **API Keys**: Stored in browser localStorage - use HTTPS in production
2. **CORS**: Restrict origins in production
3. **Rate Limiting**: Add rate limiting to API endpoints
4. **Authentication**: Add proper auth layer for production
5. **HTTPS**: Use SSL/TLS certificates in production

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## License

MIT - See main project LICENSE
