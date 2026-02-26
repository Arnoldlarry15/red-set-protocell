# Quick Start Guide: New Dashboard Features

This guide will help you quickly get started with the new Unified Infrastructure Dashboard, User Management, and Remote Control features.

## Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI or Anthropic API key

## 1. Backend Setup

### Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Configure Demo Password (Optional)

The demo admin account uses a password from the environment variable. Set it before starting the server:

```bash
export RSP_DEMO_PASSWORD="your_secure_password_here"
```

If not set, the default is `changeme`.

### Start the API Server

```bash
python -m uvicorn app.api_server:app --host 0.0.0.0 --port 8000 --reload
```

The API server will be available at `http://localhost:8000`.

**Demo Credentials:**
- Username: `admin`
- Password: Value of `RSP_DEMO_PASSWORD` environment variable (default: `changeme`)

### Verify Installation

```bash
curl http://localhost:8000/api/health
```

Expected output:
```json
{
  "status": "healthy",
  "timestamp": "2026-01-09T...",
  "active_sessions": 0,
  "websocket_connections": 0
}
```

## 2. Frontend Setup

### Install Dependencies

```bash
cd rsp-ui
npm install
```

### Start the Development Server

```bash
npm run dev
```

The UI will be available at `http://localhost:5173`.

## 3. First Login

1. Open `http://localhost:5173` in your browser
2. Select backend: **OpenAI** or **Anthropic**
3. Enter your API key
4. Click **Begin Red Teaming**

You will be logged in as the demo admin user and redirected to the Admin Dashboard.

## 4. Exploring the Features

### Infrastructure Dashboard

**View Live Sessions:**
1. Click the **Infrastructure** tab
2. Select **Live Sessions**
3. See all currently running sessions
4. Auto-refreshes every 5 seconds

**View Historical Data:**
1. Click **Historical Sessions**
2. Browse past sessions
3. Click **JSON** or **CSV** to export data

**Compare Models:**
1. Navigate to the **Model Comparison** tab
2. Enter two model version identifiers (e.g., "gpt-4-v1.0", "gpt-4-v2.0")
3. Click **Compare**
4. Review metrics and trends

### User Management

**Add a New User:**
1. Click the **User Management** tab
2. Click **Add User**
3. Fill in details:
   - Username: `researcher1`
   - Email: `researcher@example.com`
   - Role: `Researcher`
   - Password: `secure123`
4. Click **Create User**

**View Users:**
- All users are displayed with their roles and permissions
- Role badges show access level

### Remote Control

**Create a Configuration:**
1. Click the **Remote Control** tab
2. Click **New Config**
3. Fill in configuration:
   - Name: "High Mutation Test"
   - Backend: OpenAI
   - Model: gpt-3.5-turbo
   - Max Rounds: 50
   - Mutation Rate: 0.9
4. Adjust mutation weights (optional)
5. Click **Save Configuration**

**Start a Run:**
1. Select a configuration from the dropdown
2. Review the run summary
3. Click **Start Run**
4. Note the session ID
5. Navigate to **Infrastructure → Live Sessions** to monitor

## 5. API Usage Examples

### Get Live Sessions

```bash
curl http://localhost:8000/api/dashboard/live-sessions
```

### Compare Models

```bash
curl "http://localhost:8000/api/dashboard/compare-models?model_v1=gpt-4-v1&model_v2=gpt-4-v2"
```

### Export Session Data

```bash
curl "http://localhost:8000/api/dashboard/export/rsp_20260109_123456?format=json"
```

### Login

```bash
# Use the password set in RSP_DEMO_PASSWORD environment variable
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "changeme"}'
```

**Note:** Replace `changeme` with the value you set in `RSP_DEMO_PASSWORD`.

### Save Configuration

```bash
curl -X POST http://localhost:8000/api/remote/config/save \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Config",
    "backend": "openai",
    "model": "gpt-3.5-turbo",
    "max_rounds": 50,
    "mutation_rate": 0.7,
    "selected_domains": ["injection"],
    "selected_strategies": ["lexical"]
  }'
```

### Start Remote Run

```bash
curl -X POST http://localhost:8000/api/remote/start-run \
  -H "Content-Type: application/json" \
  -d '{
    "backend": "openai",
    "api_key": "sk-...",
    "model": "gpt-3.5-turbo",
    "max_rounds": 10,
    "max_api_cost": 5.0,
    "halt_on_critical": true,
    "mutation_rate": 0.7,
    "selected_domains": ["injection"],
    "selected_strategies": ["lexical"]
  }'
```

## 6. Testing

Run the test suite to verify everything works:

```bash
cd backend
python -m pytest tests/test_api_endpoints.py -v
```

Expected: **16 tests passed**

## 7. Common Workflows

### Workflow 1: Compare Two Model Versions

**Goal:** Evaluate if a new model version improved safety.

1. Run 5 sessions with model v1
2. Run 5 sessions with model v2
3. Go to **Model Comparison**
4. Enter both version identifiers
5. Click **Compare**
6. Analyze the score difference

### Workflow 2: Team Collaboration

**Goal:** Set up researchers with appropriate access.

1. Admin creates researcher accounts
2. Researchers log in
3. Researchers create and save experiment configs
4. Researchers start runs
5. All team members can view results
6. Admin manages users and system

### Workflow 3: Automated Benchmarking

**Goal:** Run regular benchmarks on a model.

1. Create a standard benchmark config
2. Save the configuration with a descriptive name
3. Use the API to start runs programmatically:
   ```bash
   # Load config
   CONFIG_ID=$(curl http://localhost:8000/api/remote/config/list | jq -r '.configs[0].config_id')
   
   # Get config details
   CONFIG=$(curl http://localhost:8000/api/remote/config/$CONFIG_ID | jq '.config')
   
   # Start run (add API key)
   curl -X POST http://localhost:8000/api/remote/start-run \
     -H "Content-Type: application/json" \
     -d "$CONFIG"
   ```
4. Export results for analysis

## 8. Troubleshooting

### Backend won't start

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
pip install fastapi uvicorn websockets pydantic
```

### Frontend won't start

**Error:** `Cannot find module 'react'`

**Solution:**
```bash
cd rsp-ui
rm -rf node_modules package-lock.json
npm install
```

### CORS errors in browser

**Error:** `Access to XMLHttpRequest blocked by CORS policy`

**Solution:** Verify the API server is running on port 8000 and the UI is accessing `http://localhost:8000`.

### Can't create users

**Error:** "Admin Access Required"

**Solution:** Make sure you're logged in with the admin account (username: `admin`, password: value from `RSP_DEMO_PASSWORD` environment variable).

### Session not found

**Error:** "Session not found" when exporting

**Solution:** 
- Verify the session ID is correct
- Check if the database file exists
- Ensure at least one round was completed

## 9. Production Considerations

Before deploying to production:

### Security

1. **Hash passwords:**
   ```python
   from passlib.hash import bcrypt
   hashed = bcrypt.hash(password)
   ```

2. **Use JWT tokens:**
   ```python
   from jose import jwt
   token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
   ```

3. **Restrict CORS:**
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],  # Not "*"
       ...
   )
   ```

4. **Secure API keys:**
   - Use environment variables
   - Never commit to version control
   - Rotate regularly

### Scaling

1. **Database:** Migrate from SQLite to PostgreSQL
2. **Load balancing:** Use nginx or similar
3. **Session storage:** Use Redis for session data
4. **Background tasks:** Use Celery for long-running operations

### Monitoring

1. Set up logging with structured logs
2. Use monitoring tools (Prometheus, Grafana)
3. Set up alerts for critical events
4. Track API usage and costs

## 10. Next Steps

- Read the full documentation: [Dashboard Features (archive)](../archive/DASHBOARD_FEATURES.md)
- Explore the API reference
- Set up automated benchmarking
- Configure custom mutation strategies
- Integrate with CI/CD pipeline

## Support

- Documentation: [Project README](../../README.md)
- API Reference: [Dashboard Features (archive)](../archive/DASHBOARD_FEATURES.md)
- Issues: [GitHub Issues](https://github.com/Arnoldlarry15/red-set-protocell/issues)

---

**Happy Red Teaming! 🔴🛡️**
