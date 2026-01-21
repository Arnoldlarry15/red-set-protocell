"""
Red Set ProtoCell Backend - Main Server Entry Point

This file serves as the main entry point for running the backend server.
It can be run:
- Locally: python main.py
- With uvicorn: uvicorn app.api_server:app --host 0.0.0.0 --port 8000
- With gunicorn: gunicorn -b 0.0.0.0:8000 app.api_server:app
- In Docker containers
- On cloud platforms (Render, Railway, Fly.io)
"""

from app.api_server import app

# Export app for WSGI servers (gunicorn) and ASGI servers (uvicorn)
__all__ = ['app']

if __name__ == "__main__":
    import uvicorn
    
    # Run the server directly
    # For production, use gunicorn or uvicorn via command line
    uvicorn.run(
        "app.api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Set to True for development
        log_level="info"
    )
