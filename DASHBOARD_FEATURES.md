# Unified Infrastructure Dashboard, User Management, and Remote Control

This document describes the new features added to Red Set ProtoCell for enhanced monitoring, access control, and remote operation.

## Table of Contents

1. [Unified Infrastructure Dashboard](#unified-infrastructure-dashboard)
2. [User Roles & Permissions](#user-roles--permissions)
3. [Remote Triggering](#remote-triggering)
4. [API Reference](#api-reference)
5. [UI Components](#ui-components)

---

## Unified Infrastructure Dashboard

The Unified Infrastructure Dashboard provides comprehensive monitoring and analysis capabilities for RSP sessions.

### Features

#### Live Session Monitoring
- Real-time view of all active sessions
- Monitor session status, progress, and costs
- Auto-refresh every 5 seconds

#### Historical Session Analysis
- View past sessions with summary metrics
- Filter by model version
- Sort and search capabilities

#### Model Version Comparison
- Compare performance between two model versions
- Statistical analysis of average scores
- Visual indicators for performance trends
- Identify regressions or improvements

#### Export Capabilities
- Export session data in CSV or JSON format
- Programmatic data access for external analysis
- Support for JSON Lines (JSONL) format for streaming

### Usage

#### Accessing the Dashboard

Navigate to the Admin Dashboard and select the "Infrastructure" tab.

#### Live Sessions

The live sessions view shows all currently running or recently active sessions:
- Session ID and status
- Backend and model configuration
- Current API cost vs. budget
- Start time

#### Historical Sessions

View historical data in a table format:
- Filter by date range
- Sort by any column
- Export individual sessions

#### Model Comparison

1. Enter two model version identifiers (e.g., "gpt-4-v1.0", "gpt-4-v2.0")
2. Click "Compare"
3. Review metrics:
   - Average vulnerability score
   - Total blocked attempts
   - Number of sessions analyzed
   - Statistical significance

---

## User Roles & Permissions

RSP now supports role-based access control (RBAC) with three distinct roles.

### Role Definitions

#### Admin
**Full system access**
- Manage users and permissions
- Configure system settings
- Start and stop runs
- Access all dashboards
- Export all data
- Save and load experiment configurations

#### Researcher
**Operational access**
- Start and configure runs
- Save experiment configurations
- Access all dashboards
- Export session data
- View historical comparisons
- Cannot manage users

#### Observer
**Read-only access**
- View live sessions
- View historical data
- Access read-only dashboards
- Export limited data
- Cannot start runs or manage users

### User Management

#### Creating Users (Admin Only)

1. Navigate to Admin Dashboard → User Management
2. Click "Add User"
3. Fill in user details:
   - Username
   - Email
   - Role (Admin/Researcher/Observer)
   - Password
4. Click "Create User"

#### Viewing Users

All current users are displayed with:
- Username and email
- Role badge with icon
- Permission description

#### Role Permissions Matrix

| Permission | Admin | Researcher | Observer |
|------------|-------|------------|----------|
| View dashboards | ✓ | ✓ | ✓ |
| View live sessions | ✓ | ✓ | ✓ |
| View historical data | ✓ | ✓ | ✓ |
| Start runs | ✓ | ✓ | ✗ |
| Save configurations | ✓ | ✓ | ✗ |
| Export data | ✓ | ✓ | Limited |
| Manage users | ✓ | ✗ | ✗ |
| System configuration | ✓ | ✗ | ✗ |

### Authentication

#### Login Process

1. Navigate to the authentication page
2. Select backend (OpenAI or Anthropic)
3. Enter API key
4. System authenticates and assigns role
5. Redirected to appropriate dashboard

**Note:** In production, API keys should be validated against the provider before authentication. The current implementation uses a simplified demo authentication.

---

## Remote Triggering

Remote triggering allows authorized users to start red teaming runs with custom configurations from the UI.

### Features

#### Start Runs from UI
- Configure and launch runs remotely
- No command-line access required
- Real-time feedback on run status

#### Parameter Configuration
- Mutation weights for each strategy
- Severity thresholds
- Domain selection
- Strategy selection
- Model and backend selection

#### Experiment Configurations
- Save configurations for reuse
- Load previously saved configurations
- Share configurations between team members
- Version control for experiments

### Usage

#### Saving a Configuration

1. Navigate to Admin Dashboard → Remote Control
2. Click "New Config"
3. Fill in configuration details:
   - Name and description
   - Backend and model
   - Max rounds and mutation rate
   - Mutation weights (fine-tune each strategy)
   - Severity thresholds
4. Click "Save Configuration"

#### Loading a Configuration

1. Select from the dropdown menu
2. Configuration populates all fields
3. Modify if needed
4. Click "Start Run"

#### Starting a Remote Run

1. Configure or load an experiment
2. Review the run summary
3. Click "Start Run"
4. System returns session ID
5. Monitor in Live Sessions view

#### Mutation Weights

Fine-tune the relative importance of each mutation strategy:
- **Lexical** (default: 1.0): Synonym substitution
- **Encoding** (default: 1.0): Character encoding tricks
- **Structural** (default: 1.0): Syntax manipulation
- **Roleplay** (default: 1.0): Character injection
- **Context** (default: 1.0): Context manipulation
- **Obfuscation** (default: 1.0): Pattern obfuscation

Higher weights = more likely to be selected.

#### Severity Thresholds

Customize score thresholds for severity classification:
- **Critical** (default: 0.8): Severe safety violations
- **High** (default: 0.6): Significant concerns
- **Medium** (default: 0.4): Moderate issues
- **Low** (default: 0.2): Minor deviations

---

## API Reference

### Infrastructure Dashboard Endpoints

#### GET /api/dashboard/live-sessions
Get all currently active sessions.

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "rsp_20260109_123456",
      "status": "running",
      "start_time": "2026-01-09T12:34:56Z",
      "current_cost": 2.50,
      "max_cost": 10.00,
      "config": {
        "backend": "openai",
        "model": "gpt-3.5-turbo",
        "max_rounds": 100
      }
    }
  ]
}
```

#### GET /api/dashboard/historical-sessions
Get historical session data.

**Query Parameters:**
- `db_path` (optional): Path to database file

**Response:**
```json
{
  "sessions": [
    {
      "session_id": "rsp_20260109_123456",
      "start_time": "2026-01-09T12:34:56Z",
      "end_time": "2026-01-09T13:45:12Z",
      "total_rounds": 100,
      "average_score": 0.456,
      "blocked_count": 5,
      "model_version": "gpt-4-v1.0"
    }
  ]
}
```

#### GET /api/dashboard/compare-models
Compare two model versions.

**Query Parameters:**
- `model_v1` (required): First model version
- `model_v2` (required): Second model version
- `db_path` (optional): Path to database file

**Response:**
```json
{
  "model_v1": "gpt-4-v1.0",
  "model_v1_metrics": {
    "avg_score": 0.456,
    "blocked_count": 10,
    "total_rounds": 500,
    "session_count": 5
  },
  "model_v2": "gpt-4-v2.0",
  "model_v2_metrics": {
    "avg_score": 0.389,
    "blocked_count": 8,
    "total_rounds": 500,
    "session_count": 5
  }
}
```

#### GET /api/dashboard/export/{session_id}
Export session data in various formats.

**Query Parameters:**
- `format`: "json", "csv", or "jsonl"
- `db_path` (optional): Path to database file

**Response:**
```json
{
  "session_id": "rsp_20260109_123456",
  "format": "json",
  "data": "... exported data ..."
}
```

### User Management Endpoints

#### POST /api/auth/login
Authenticate a user.

**Request Body:**
```json
{
  "username": "researcher1",
  "password": "password123"
}
```

**Response:**
```json
{
  "username": "researcher1",
  "email": "researcher@example.com",
  "role": "researcher",
  "token": "token_researcher1_1234567890"
}
```

#### POST /api/auth/register
Register a new user (admin only).

**Request Body:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "role": "observer",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "role": "observer",
  "message": "User created successfully"
}
```

#### GET /api/auth/users
List all users (admin only).

**Response:**
```json
{
  "users": [
    {
      "username": "admin",
      "email": "admin@example.com",
      "role": "admin"
    }
  ]
}
```

### Remote Control Endpoints

#### POST /api/remote/start-run
Start a remote run with configuration.

**Request Body:**
```json
{
  "backend": "openai",
  "api_key": "sk-...",
  "model": "gpt-3.5-turbo",
  "max_rounds": 50,
  "max_api_cost": 10.0,
  "halt_on_critical": true,
  "mutation_rate": 0.7,
  "selected_domains": ["injection", "jailbreak"],
  "selected_strategies": ["lexical", "encoding"]
}
```

**Response:**
```json
{
  "session_id": "rsp_20260109_123456",
  "status": "started",
  "message": "Remote run started successfully",
  "config": { ... }
}
```

#### POST /api/remote/config/save
Save an experiment configuration.

**Request Body:**
```json
{
  "name": "My Experiment",
  "description": "Testing GPT-4 with high mutation rate",
  "backend": "openai",
  "model": "gpt-4",
  "max_rounds": 100,
  "mutation_rate": 0.9,
  "selected_domains": ["injection", "jailbreak"],
  "selected_strategies": ["lexical", "structural"],
  "mutation_weights": {
    "lexical": 1.5,
    "structural": 1.2
  },
  "thresholds": {
    "critical": 0.85,
    "high": 0.65
  }
}
```

**Response:**
```json
{
  "config_id": "config_20260109_123456",
  "name": "My Experiment",
  "message": "Configuration saved successfully"
}
```

#### GET /api/remote/config/list
List all saved configurations.

**Response:**
```json
{
  "configs": [
    {
      "config_id": "config_20260109_123456",
      "name": "My Experiment",
      "description": "Testing GPT-4 with high mutation rate",
      "backend": "openai",
      "model": "gpt-4"
    }
  ]
}
```

#### GET /api/remote/config/{config_id}
Get a specific configuration.

**Response:**
```json
{
  "config_id": "config_20260109_123456",
  "config": { ... }
}
```

#### DELETE /api/remote/config/{config_id}
Delete a configuration.

**Response:**
```json
{
  "message": "Configuration deleted successfully"
}
```

---

## UI Components

### InfraDashboard Component

Located at: `rsp-ui/src/components/InfraDashboard.tsx`

**Props:** None

**Features:**
- Tabbed interface (Live/Historical)
- Auto-refresh for live sessions
- Export buttons for historical data

### ModelVersionComparison Component

Located at: `rsp-ui/src/components/ModelVersionComparison.tsx`

**Props:** None

**Features:**
- Input fields for two model versions
- Visual comparison display
- Trend indicators

### UserManagement Component

Located at: `rsp-ui/src/components/UserManagement.tsx`

**Props:**
- `currentUser`: User object with role information

**Features:**
- Role-based access control
- User creation form
- User list display
- Permission matrix

### RemoteControl Component

Located at: `rsp-ui/src/components/RemoteControl.tsx`

**Props:**
- `apiKey`: API key for starting runs
- `userRole`: Current user's role

**Features:**
- Configuration save/load
- Parameter customization
- Mutation weights adjustment
- Threshold configuration

### AdminDashboard Page

Located at: `rsp-ui/src/pages/AdminDashboard.tsx`

**Props:**
- `user`: Current user object
- `apiKey`: API key

**Features:**
- Unified navigation
- Component routing
- Role-based visibility

---

## Security Considerations

1. **API Keys**: Never hardcode API keys in the frontend. Use environment variables and secure storage.

2. **Password Storage**: In production, passwords must be hashed using bcrypt or similar. The current demo uses plain text for simplicity.

3. **Token Management**: Implement proper JWT tokens with expiration for production use.

4. **CORS**: Restrict allowed origins in production (currently set to "*" for development).

5. **Input Validation**: All user inputs are validated on both frontend and backend.

6. **Database Security**: Use parameterized queries to prevent SQL injection.

---

## Future Enhancements

1. **Advanced Analytics**
   - Time-series visualization
   - Fatigue detection over extended sessions
   - Cross-model benchmarking

2. **Collaboration Features**
   - Team workspaces
   - Shared experiment configurations
   - Comment and annotation system

3. **Notifications**
   - Email alerts for critical findings
   - Slack/Discord integration
   - Webhook support

4. **Enhanced Security**
   - OAuth integration
   - SSO support
   - Audit logging

5. **API Improvements**
   - Rate limiting
   - Pagination for large datasets
   - GraphQL endpoint

---

## Troubleshooting

### Common Issues

#### "Admin Access Required" Message
**Solution:** Your user role doesn't have permission. Contact an admin to update your role.

#### Configuration Not Loading
**Solution:** Ensure the configuration was saved successfully. Check browser console for errors.

#### Export Fails
**Solution:** Verify the session exists and the database is accessible.

#### Can't Start Run
**Solution:** Verify you have researcher or admin role and a valid API key.

### Logging

Enable detailed logging by setting log level to DEBUG in the backend:

```python
logging.basicConfig(level=logging.DEBUG)
```

### Support

For issues or questions:
- GitHub Issues: [red-set-protocell/issues](https://github.com/Arnoldlarry15/red-set-protocell/issues)
- Documentation: [README.md](../README.md)

---

## Version History

- **v1.3.0** (2026-01-09)
  - Initial release of Unified Infrastructure Dashboard
  - User Management with RBAC
  - Remote Triggering capabilities
  - Comprehensive API endpoints
  - Full UI component suite
