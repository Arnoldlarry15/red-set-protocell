#!/usr/bin/env python3
"""
RedSet ProtoCell - Secure Setup Script
Initializes the secure dashboard with proper security configurations
"""

import os
import sys
import secrets
import sqlite3
from werkzeug.security import generate_password_hash

def create_directory_structure():
    """Create required directories for secure operation"""
    directories = [
        'templates',
        'static/css',
        'static/js',
        'static/images',
        'prompts/sniper',
        'logs/spotter',
        'logs/transcripts',
        'logs/security',
        'backups'
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Created directory: {directory}")

def create_security_config():
    """Create secure environment configuration"""
    flask_secret = secrets.token_hex(32)
    csrf_secret = secrets.token_hex(32)
    
    env_content = f"""# RedSet ProtoCell - Secure Configuration
# IMPORTANT: Keep this file secure and never commit to version control

# Flask Security
FLASK_SECRET_KEY={flask_secret}
FLASK_ENV=production
FLASK_DEBUG=false

# CSRF Protection
WTF_CSRF_SECRET_KEY={csrf_secret}
WTF_CSRF_TIME_LIMIT=3600

# API Keys (fill in your actual keys)
OPENAI_API_KEY=your_openai_api_key_here

# Database
DATABASE_URL=sqlite:///redset_secure.db

# Security Settings
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=28800

# Rate Limiting
RATELIMIT_STORAGE_URL=memory://
RATELIMIT_DEFAULT=100/hour

# SSL/TLS (for production)
FORCE_HTTPS=true
HSTS_MAX_AGE=31536000

# Logging
LOG_LEVEL=INFO
SECURITY_LOG_FILE=logs/security/security.log
"""

    with open('.env', 'w') as f:
        f.write(env_content)

    # Also create a sample file
    with open('.env.sample', 'w') as f:
        f.write(env_content.replace(flask_secret, 'your_flask_secret_key_here')
                          .replace(csrf_secret, 'your_csrf_secret_key_here'))

    print("✓ Created secure environment configuration")
    print("⚠️  WARNING: .env file contains sensitive keys - keep secure!")

def create_ssl_certificate():
    """Create self-signed SSL certificate for development"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Create certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Development"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "Local"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "RedSet ProtoCell"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
                x509.DNSName("127.0.0.1"),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Write private key
        with open("server.key", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Write certificate
        with open("server.crt", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        
        print("✓ Created SSL certificate for HTTPS (development only)")
        
    except ImportError:
        print("⚠️  Could not create SSL certificate (cryptography not installed)")
        print("   Install with: pip install cryptography")

def init_secure_database():
    """Initialize database with security features"""
    conn = sqlite3.connect('redset_secure.db')
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute('PRAGMA foreign_keys = ON')
    
    # Users table with security features
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'analyst' CHECK(role IN ('admin', 'analyst', 'viewer')),
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            failed_login_attempts INTEGER DEFAULT 0,
            locked_until TIMESTAMP,
            password_changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            must_change_password BOOLEAN DEFAULT 0
        )
    ''')
    
    # API keys table (encrypted storage)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            service TEXT NOT NULL,
            key_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Test runs table with security audit
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            run_id TEXT NOT NULL,
            config TEXT NOT NULL,
            status TEXT DEFAULT 'queued' CHECK(status IN ('queued', 'running', 'completed', 'failed', 'cancelled')),
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            results TEXT,
            risk_score REAL,
            approved_by INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (approved_by) REFERENCES users (id)
        )
    ''')
    
    # Comprehensive audit log
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            resource TEXT,
            resource_id TEXT,
            details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            success BOOLEAN DEFAULT 1,
            risk_level TEXT DEFAULT 'low' CHECK(risk_level IN ('low', 'medium', 'high', 'critical')),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Security events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            severity TEXT NOT NULL CHECK(severity IN ('info', 'warning', 'critical')),
            source_ip TEXT,
            user_id INTEGER,
            description TEXT,
            metadata TEXT,
            resolved BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            resolved_by INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (resolved_by) REFERENCES users (id)
        )
    ''')
    
    # Session management
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sessions (
            id TEXT PRIMARY KEY,
            user_id INTEGER,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Create indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_runs_user_id ON test_runs(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_security_events_severity ON security_events(severity)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON user_sessions(user_id)')
    
    # Create default admin user if none exists
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        admin_password = secrets.token_urlsafe(16)
        password_hash = generate_password_hash(admin_password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role, must_change_password)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin@redset.local', password_hash, 'admin', 1))
        
        # Log the admin creation
        cursor.execute('''
            INSERT INTO audit_log (action, details, risk_level)
            VALUES (?, ?, ?)
        ''', ('admin_user_created', 'Default admin user created during setup', 'high'))
        
        print(f"✓ Created default admin user:")
        print(f"  Username: admin")
        print(f"  Password: {admin_password}")
        print(f"  ⚠️  SECURITY: Change this password immediately after first login!")
        
        # Create additional sample users for testing
        sample_users = [
            ('analyst1', 'analyst1@redset.local', 'analyst'),
            ('viewer1', 'viewer1@redset.local', 'viewer')
        ]
        
        for username, email, role in sample_users:
            sample_password = secrets.token_urlsafe(12)
            password_hash = generate_password_hash(sample_password)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role, must_change_password)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, role, 1))
            print(f"  Sample {role}: {username} / {sample_password}")
    
    conn.commit()
    conn.close()
    print("✓ Initialized secure database with audit trails")

def create_security_policies():
    """Create security policy files"""
    
    # Password policy
    password_policy = """# RedSet ProtoCell - Password Policy

MINIMUM_LENGTH = 12
REQUIRE_UPPERCASE = True
REQUIRE_LOWERCASE = True
REQUIRE_NUMBERS = True
REQUIRE_SPECIAL_CHARS = True
MAX_PASSWORD_AGE_DAYS = 90
PASSWORD_HISTORY_COUNT = 5
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30
SESSION_TIMEOUT_HOURS = 8
"""
    
    with open('security_policy.py', 'w') as f:
        f.write(password_policy)
    
    # Security headers configuration
    security_headers = """# RedSet ProtoCell - Security Headers Configuration
# Configure Flask-Talisman for security headers

SECURITY_HEADERS = {
    'force_https': True,
    'force_https_permanent': True,
    'force_file_save': True,
    'strict_transport_security': True,
    'strict_transport_security_max_age': 31536000,
    'strict_transport_security_include_subdomains': True,
    'content_security_policy': {
        'default-src': "'self'",
        'script-src': "'self' 'unsafe-inline' https://cdnjs.cloudflare.com",
        'style-src': "'self' 'unsafe-inline' https://cdnjs.cloudflare.com",
        'font-src': "'self' https://cdnjs.cloudflare.com",
        'img-src': "'self' data:",
        'connect-src': "'self'",
        'frame-ancestors': "'none'",
        'base-uri': "'self'",
        'form-action': "'self'"
    },
    'referrer_policy': 'strict-origin-when-cross-origin',
    'feature_policy': {
        'camera': "'none'",
        'microphone': "'none'",
        'geolocation': "'none'"
    }
}
"""
    
    with open('security_headers.py', 'w') as f:
        f.write(security_headers)
    
    print("✓ Created security policy files")

def create_deployment_script():
    """Create production deployment script"""
    
    deploy_script = """#!/bin/bash
# RedSet ProtoCell - Production Deployment Script

echo "🚀 RedSet ProtoCell Production Deployment"
echo "=========================================="

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Do not run this script as root for security reasons"
    exit 1
fi

# Create production user if not exists
if ! id "redset" &>/dev/null; then
    echo "📝 Creating redset user..."
    sudo useradd -r -s /bin/false -d /opt/redset redset
fi

# Create application directory
sudo mkdir -p /opt/redset
sudo chown redset:redset /opt/redset
sudo chmod 750 /opt/redset

# Install Python dependencies
pip install -r requirements.txt

# Set up systemd service
sudo tee /etc/systemd/system/redset.service > /dev/null <<EOF
[Unit]
Description=RedSet ProtoCell Secure Dashboard
After=network.target

[Service]
Type=notify
User=redset
Group=redset
WorkingDirectory=/opt/redset
Environment=PATH=/opt/redset/venv/bin
ExecStart=/opt/redset/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 4 --worker-class gevent --worker-connections 1000 --timeout 120 --keepalive 5 --max-requests 1000 --max-requests-jitter 100 --access-logfile /var/log/redset/access.log --error-logfile /var/log/redset/error.log app:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=10

# Security settings
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/opt/redset
CapabilityBoundingSet=CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_BIND_SERVICE

[Install]
WantedBy=multi-user.target
EOF

# Create log directories
sudo mkdir -p /var/log/redset
sudo chown redset:redset /var/log/redset
sudo chmod 750 /var/log/redset

# Set up log rotation
sudo tee /etc/logrotate.d/redset > /dev/null <<EOF
/var/log/redset/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 redset redset
    postrotate
        systemctl reload redset
    endscript
}
EOF

# Configure nginx (if installed)
if command -v nginx &> /dev/null; then
    echo "🌐 Configuring nginx..."
    sudo tee /etc/nginx/sites-available/redset > /dev/null <<EOF
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=redset:10m rate=10r/m;
    limit_req zone=redset burst=20 nodelay;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Security
        proxy_hide_header X-Powered-By;
        proxy_hide_header Server;
    }
    
    # Static files
    location /static/ {
        alias /opt/redset/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://\$server_name\$request_uri;
}
EOF
    
    sudo ln -sf /etc/nginx/sites-available/redset /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl reload nginx
fi

# Set up firewall (if ufw is installed)
if command -v ufw &> /dev/null; then
    echo "🔥 Configuring firewall..."
    sudo ufw allow 22/tcp
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw --force enable
fi

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable redset
sudo systemctl start redset

echo "✅ Deployment complete!"
echo "🔧 Don't forget to:"
echo "   1. Update SSL certificates in nginx config"
echo "   2. Set your domain name in nginx config"
echo "   3. Configure your firewall rules"
echo "   4. Set up monitoring and backups"
echo "   5. Change default passwords!"
"""
    
    with open('deploy.sh', 'w') as f:
        f.write(deploy_script)
    
    os.chmod('deploy.sh', 0o755)
    print("✓ Created production deployment script")

def create_backup_script():
    """Create automated backup script"""
    
    backup_script = """#!/bin/bash
# RedSet ProtoCell - Backup Script

BACKUP_DIR="/opt/redset/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DATABASE_FILE="redset_secure.db"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
echo "📦 Creating database backup..."
sqlite3 "$DATABASE_FILE" ".backup $BACKUP_DIR/redset_backup_$TIMESTAMP.db"

# Backup configuration files
echo "📋 Backing up configuration..."
tar -czf "$BACKUP_DIR/config_backup_$TIMESTAMP.tar.gz" \\
    .env security_policy.py security_headers.py \\
    prompts/ logs/ --exclude="logs/*.log"

# Cleanup old backups (keep last 30 days)
find "$BACKUP_DIR" -name "*.db" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "✅ Backup completed: $TIMESTAMP"

# Optional: Upload to cloud storage
# aws s3 cp "$BACKUP_DIR/" s3://your-backup-bucket/redset/ --recursive
"""
    
    with open('backup.sh', 'w') as f:
        f.write(backup_script)
    
    os.chmod('backup.sh', 0o755)
    print("✓ Created automated backup script")

def create_monitoring_config():
    """Create monitoring and alerting configuration"""
    
    monitoring_config = """# RedSet ProtoCell - Monitoring Configuration
# Health check endpoints and alerting rules

import logging
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

class SecurityMonitor:
    def __init__(self):
        self.alert_thresholds = {
            'failed_logins': 10,  # per hour
            'high_risk_tests': 5,  # per day
            'api_errors': 20,  # per hour
            'suspicious_ips': 3   # different IPs per user per hour
        }
    
    def check_security_events(self):
        # Implementation for checking security events
        pass
    
    def send_alert(self, severity, message):
        # Implementation for sending alerts
        pass

# Prometheus metrics (if using Prometheus)
PROMETHEUS_METRICS = '''
# HELP redset_active_users_total Number of active users
# TYPE redset_active_users_total gauge
redset_active_users_total

# HELP redset_test_runs_total Total number of test runs
# TYPE redset_test_runs_total counter
redset_test_runs_total

# HELP redset_high_risk_detections_total High risk detections
# TYPE redset_high_risk_detections_total counter
redset_high_risk_detections_total

# HELP redset_security_events_total Security events by severity
# TYPE redset_security_events_total counter
redset_security_events_total{severity="critical"}
redset_security_events_total{severity="warning"}
redset_security_events_total{severity="info"}
'''
"""
    
    with open('monitoring.py', 'w') as f:
        f.write(monitoring_config)
    
    print("✓ Created monitoring configuration")

def main():
    """Main setup function"""
    print("🎯 RedSet ProtoCell - Secure Setup")
    print("=" * 40)
    
    try:
        # Create directory structure
        create_directory_structure()
        
        # Create security configuration
        create_security_config()
        
        # Create SSL certificate for development
        create_ss