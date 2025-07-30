#!/usr/bin/env python3
"""
RedSet ProtoCell - Secure Setup Script
Replaces the original setup.py with security-focused initialization
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

def create_secure_env_file():
    """Create secure .env configuration file"""
    flask_secret = secrets.token_hex(32)
    csrf_secret = secrets.token_hex(32)
    
    env_content = f"""# RedSet ProtoCell - Secure Configuration
# CRITICAL: Keep this file secure and never commit to version control!

# Flask Security Keys
FLASK_SECRET_KEY={flask_secret}
FLASK_ENV=production
FLASK_DEBUG=false

# CSRF Protection
WTF_CSRF_SECRET_KEY={csrf_secret}
WTF_CSRF_TIME_LIMIT=3600

# API Keys - Replace with your actual keys
OPENAI_API_KEY=your_openai_api_key_here

# Database Configuration
DATABASE_URL=sqlite:///redset_secure.db

# Security Settings
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Lax
PERMANENT_SESSION_LIFETIME=28800

# Rate Limiting
RATELIMIT_STORAGE_URL=memory://
RATELIMIT_DEFAULT=100/hour

# SSL/TLS Configuration
FORCE_HTTPS=true
HSTS_MAX_AGE=31536000

# Logging Configuration
LOG_LEVEL=INFO
SECURITY_LOG_FILE=logs/security/security.log
"""

    # Write the actual .env file
    with open('.env', 'w') as f:
        f.write(env_content)

    # Create a sample file for reference
    sample_content = env_content.replace(flask_secret, 'your_flask_secret_key_here')
    sample_content = sample_content.replace(csrf_secret, 'your_csrf_secret_key_here')
    
    with open('.env.sample', 'w') as f:
        f.write(sample_content)

    print("✓ Created secure environment configuration")
    print("⚠️  WARNING: .env contains sensitive keys - keep it secure!")

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
        
        print("✓ Created SSL certificate for HTTPS development")
        
    except ImportError:
        print("⚠️  Could not create SSL certificate (install: pip install cryptography)")
        print("   HTTPS will use Flask's built-in certificate")

def init_secure_database():
    """Initialize secure database with proper schema"""
    conn = sqlite3.connect('redset_secure.db')
    cursor = conn.cursor()
    
    # Enable foreign keys and WAL mode for better performance
    cursor.execute('PRAGMA foreign_keys = ON')
    cursor.execute('PRAGMA journal_mode = WAL')
    
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
    
    # Test runs table
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
            FOREIGN KEY (user_id) REFERENCES users (id)
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
    
    # Create indexes for performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_test_runs_user_id ON test_runs(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_security_events_severity ON security_events(severity)')
    
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
        
        print(f"\n🔐 DEFAULT ADMIN USER CREATED:")
        print(f"    Username: admin")
        print(f"    Password: {admin_password}")
        print(f"    ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!")
        
        # Create sample users for testing
        sample_users = [
            ('analyst1', 'analyst1@redset.local', 'analyst'),
            ('viewer1', 'viewer1@redset.local', 'viewer')
        ]
        
        print(f"\n👥 SAMPLE USERS CREATED:")
        for username, email, role in sample_users:
            sample_password = secrets.token_urlsafe(12)
            password_hash = generate_password_hash(sample_password)
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role, must_change_password)
                VALUES (?, ?, ?, ?, ?)
            ''', (username, email, password_hash, role, 1))
            print(f"    {role.capitalize()}: {username} / {sample_password}")
    
    conn.commit()
    conn.close()
    print("✓ Initialized secure database with audit trails")

def create_security_policies():
    """Create security policy configuration files"""
    
    # Password policy
    password_policy = '''"""
RedSet ProtoCell - Password Security Policy
Configure password requirements and account security
"""

# Password Requirements
MINIMUM_LENGTH = 12
REQUIRE_UPPERCASE = True
REQUIRE_LOWERCASE = True
REQUIRE_NUMBERS = True
REQUIRE_SPECIAL_CHARS = True

# Account Security
MAX_PASSWORD_AGE_DAYS = 90
PASSWORD_HISTORY_COUNT = 5
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30
SESSION_TIMEOUT_HOURS = 8

# Rate Limiting
LOGIN_RATE_LIMIT = "5/minute"
API_RATE_LIMIT = "100/hour"
TEST_RATE_LIMIT = "10/hour"

def validate_password(password):
    """Validate password against policy requirements"""
    errors = []
    
    if len(password) < MINIMUM_LENGTH:
        errors.append(f"Password must be at least {MINIMUM_LENGTH} characters long")
    
    if REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")
    
    if REQUIRE_LOWERCASE and not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")
    
    if REQUIRE_NUMBERS and not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one number")
    
    if REQUIRE_SPECIAL_CHARS and not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        errors.append("Password must contain at least one special character")
    
    return errors
'''
    
    with open('security_policy.py', 'w') as f:
        f.write(password_policy)
    
    # Security headers configuration
    security_headers = '''"""
RedSet ProtoCell - Security Headers Configuration
Configure Flask-Talisman security headers
"""

SECURITY_HEADERS = {
    'force_https': True,
    'force_https_permanent': True,
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
'''
    
    with open('security_headers.py', 'w') as f:
        f.write(security_headers)
    
    print("✓ Created security policy files")

def create_template_structure():
    """Create basic template structure"""
    
    # Create a simple base template
    base_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}RedSet Dashboard{% endblock %}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
</head>
<body class="bg-gray-900 text-white min-h-screen">
    {% block content %}{% endblock %}
</body>
</html>'''
    
    with open('templates/base.html', 'w') as f:
        f.write(base_template)
    
    print("✓ Created basic template structure")

def main():
    """Main setup function"""
    print("🎯 RedSet ProtoCell - Secure Setup")
    print("=" * 50)
    
    try:
        # Create directories
        create_directory_structure()
        
        # Create secure configuration
        create_secure_env_file()
        
        # Create SSL certificate for development
        create_ssl_certificate()
        
        # Initialize database
        init_secure_database()
        
        # Create security policies
        create_security_policies()
        
        # Create basic templates
        create_template_structure()
        
        print("\n" + "=" * 50)
        print("🔒 SECURE SETUP COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        
        print("\n📋 NEXT STEPS:")
        print("1. Install dependencies:")
        print("   pip install -r requirements.txt")
        print("\n2. Configure your API keys in .env file:")
        print("   Edit OPENAI_API_KEY=your_actual_key_here")
        print("\n3. Create the Flask app (app.py) using the provided code")
        print("\n4. Create HTML templates using the provided templates")
        print("\n5. Run the application:")
        print("   python app.py")
        print("\n6. Access the dashboard:")
        print("   https://localhost:5000")
        
        print("\n⚠️  CRITICAL SECURITY REMINDERS:")
        print("• Change ALL default passwords immediately")
        print("• Keep .env file secure - never commit to version control")
        print("• Review security policies before production use")
        print("• Set up proper SSL certificates for production")
        print("• Configure monitoring and regular backups")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {str(e)}")
        print("Check error messages above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()