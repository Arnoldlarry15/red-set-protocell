#!/bin/bash

# Red Set ProtoCell - Start Script
# This script starts both the backend API server and the frontend dev server

set -e

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                                                           ║"
echo "║         RED SET PROTOCELL (RSP)                           ║"
echo "║         Web UI Startup Script                             ║"
echo "║                                                           ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/rsp-core/backend"
FRONTEND_DIR="$SCRIPT_DIR/rsp-ui"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16 or higher."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo "✓ Node.js found: $(node --version)"
echo "✓ npm found: $(npm --version)"
echo ""

# Install backend dependencies
echo "📦 Checking backend dependencies..."
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -q -r requirements.txt

echo "✓ Backend dependencies installed"
echo ""

# Install frontend dependencies
echo "📦 Checking frontend dependencies..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install --silent
else
    echo "✓ Frontend dependencies already installed"
fi
echo ""

# Start backend in background
echo "🚀 Starting backend API server..."
cd "$BACKEND_DIR"
source venv/bin/activate
python -m app.api_server > /tmp/rsp-backend.log 2>&1 &
BACKEND_PID=$!
echo "✓ Backend started (PID: $BACKEND_PID)"
echo "   API available at: http://localhost:8000"
echo "   WebSocket at: ws://localhost:8000/ws"
echo "   Logs: /tmp/rsp-backend.log"
echo ""

# Wait for backend to start
echo "⏳ Waiting for backend to be ready..."
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start. Check logs at /tmp/rsp-backend.log"
    exit 1
fi

# Start frontend
echo "🚀 Starting frontend development server..."
cd "$FRONTEND_DIR"
npm run dev > /tmp/rsp-frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✓ Frontend started (PID: $FRONTEND_PID)"
echo "   UI available at: http://localhost:3000"
echo "   Logs: /tmp/rsp-frontend.log"
echo ""

# Save PIDs for cleanup
echo $BACKEND_PID > /tmp/rsp-backend.pid
echo $FRONTEND_PID > /tmp/rsp-frontend.pid

echo "═══════════════════════════════════════════════════════════"
echo "✅ Red Set ProtoCell is now running!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "🌐 Open your browser to: http://localhost:3000"
echo ""
echo "To stop the servers, run:"
echo "   kill $(cat /tmp/rsp-backend.pid) $(cat /tmp/rsp-frontend.pid)"
echo ""
echo "Or press Ctrl+C in this terminal."
echo ""

# Wait for user interrupt
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f /tmp/rsp-backend.pid /tmp/rsp-frontend.pid; echo '✓ Servers stopped'; exit 0" INT TERM

# Keep script running
wait
