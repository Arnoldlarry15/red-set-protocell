# Red Set ProtoCell - Web UI

A modern, glassmorphism-styled web interface for the Red Set ProtoCell AI red teaming system.

## Features

- **Authentication Page**: Secure login with API key validation and logo display
- **Live Attack Feed**: Real-time stream of red teaming attacks with detailed information
- **Metrics Dashboard**: Comprehensive charts and statistics
  - Score history graphs
  - Severity distribution
  - Attack domain analysis
- **Attack Configuration**: Interactive controls for:
  - Attack domains selection
  - Mutation strategies selection
  - Session parameters
- **User Input**: Custom adversarial prompt testing
- **Cost Tracker**: Real-time API cost monitoring with automatic halt
- **Vulnerability Detection**: Automatic session halt on critical findings

## Design

- **Style**: Bento box glassmorphism
- **Color Scheme**: Black (#0a0a0a), Red (#ef4444), White (#ffffff)
- **Responsive**: Mobile-friendly design
- **Animations**: Smooth transitions and micro-interactions

## Setup

### Prerequisites

- Node.js 16+ and npm

### Installation

```bash
cd rsp-ui
npm install
```

### Development

```bash
npm run dev
```

The UI will be available at `http://localhost:3000`

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
rsp-ui/
├── src/
│   ├── components/         # React components
│   │   ├── AttackConfig.tsx
│   │   ├── CostTracker.tsx
│   │   ├── LiveFeed.tsx
│   │   ├── MetricsPanel.tsx
│   │   └── UserInput.tsx
│   ├── pages/             # Page components
│   │   ├── AuthPage.tsx
│   │   └── Dashboard.tsx
│   ├── styles/            # CSS files
│   │   ├── globals.css
│   │   ├── Auth.css
│   │   ├── Dashboard.css
│   │   └── Components.css
│   ├── types/             # TypeScript types
│   │   └── index.ts
│   ├── App.tsx            # Main app component
│   └── main.tsx           # Entry point
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Logo Integration

To add your logo:

1. Place your logo image in `rsp-ui/public/` as `logo.png`
2. Update the authentication page to use the logo image instead of the Shield icon
3. Update the dashboard header to use the logo image

Example code changes:

```tsx
// In AuthPage.tsx, replace the Shield icon:
<div className="logo-placeholder">
  <img src="/logo.png" alt="RSP Logo" className="logo-image" />
</div>

// In Dashboard.tsx, replace the Shield icon:
<div className="header-logo">
  <img src="/logo.png" alt="RSP Logo" className="header-logo-image" />
</div>
```

## Backend Integration

The UI is designed to connect to a WebSocket backend for real-time updates. To integrate:

1. Set up WebSocket server in the Python backend
2. Implement WebSocket client in `src/services/websocket.ts`
3. Connect the Dashboard to receive real-time attack data

## Technologies

- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool
- **Recharts**: Data visualization
- **React Router**: Navigation
- **Framer Motion**: Animations (optional)
- **Lucide React**: Icons

## License

MIT License - See main project LICENSE file
