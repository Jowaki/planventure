# Authentication Implementation Guide

## Overview
The PlanVenture API now includes a complete authentication system with:
- User registration with email validation
- Secure password hashing with salt
- JWT-based token authentication
- Email already-registered checking
- Password strength validation
- Token refresh mechanism

## Architecture

### Files Created/Modified

#### New Files
1. **routes_auth.py** - Authentication endpoints blueprint
2. **jwt_utils.py** - JWT token generation and validation
3. **password_utils.py** - Password hashing and strength checking
4. **AUTH_API.md** - Complete API documentation
5. **example_auth_usage.py** - Usage examples and integration tests

#### Modified Files
1. **app.py** - Registered auth blueprint and JWT config
2. **models.py** - Added JWT methods to User model
3. **manage.py** - Added JWT management commands
4. **.env.example** - Added JWT_SECRET_KEY configuration

## Authentication Flow

### 1. User Registration
```
POST /auth/register
  ↓
Validate email format
  ↓
Check email not already registered
  ↓
Validate password strength
  ↓
Hash password with salt
  ↓
Create user in database
  ↓
Generate JWT tokens (access + refresh)
  ↓
Return user data + tokens (201 Created)
```

### 2. User Login
```
POST /auth/login
  ↓
Find user by email
  ↓
Verify password hash
  ↓
Generate JWT tokens
  ↓
Return tokens (200 OK)
```

### 3. Access Protected Routes
```
GET /auth/me
  + Authorization: Bearer <access_token>
  ↓
Extract token from header
  ↓
Validate JWT signature and expiry
  ↓
Get user from database
  ↓
Return user data (200 OK)
```

### 4. Token Refresh
```
POST /auth/refresh
  + refresh_token in body or Authorization header
  ↓
Validate refresh token
  ↓
Extract user ID
  ↓
Generate new access token
  ↓
Return new access token (200 OK)
```

## Endpoints Summary

| Method | Endpoint | Auth Required | Purpose |
|--------|----------|---------------|---------|
| POST | `/auth/register` | No | Create new user account |
| POST | `/auth/login` | No | Authenticate user |
| POST | `/auth/refresh` | No | Refresh access token |
| GET | `/auth/me` | Yes | Get current user info |
| POST | `/auth/validate-email` | No | Check email availability |
| POST | `/auth/password-strength` | No | Analyze password strength |

## Configuration

### Environment Variables (.env)
```bash
# Flask
FLASK_ENV=development
FLASK_APP=app.py

# Database
DATABASE_URL=sqlite:///planventure.db

# JWT (IMPORTANT: Change in production!)
JWT_SECRET_KEY=your-secret-key-change-this-in-production
```

Generate a secure secret key:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Usage Examples

### Register New User
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

### Access Protected Endpoint
```bash
curl -X GET http://localhost:5000/auth/me \
  -H "Authorization: Bearer <access_token>"
```

### Refresh Token
```bash
curl -X POST http://localhost:5000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

## Password Requirements

Passwords must contain:
- ✓ Minimum 8 characters
- ✓ At least one uppercase letter (A-Z)
- ✓ At least one lowercase letter (a-z)
- ✓ At least one digit (0-9)
- ✓ At least one special character: `!@#$%^&*()_+-=[]{}|;:,.<>?`

## Token Details

### Access Token
- **Expiry**: 15 minutes (configurable)
- **Use**: Access protected resources
- **Payload**: user_id, email, token_type, iat, exp

### Refresh Token
- **Expiry**: 7 days (configurable)
- **Use**: Generate new access tokens
- **Payload**: user_id, email, token_type, iat, exp

## Security Features

1. **Password Hashing**
   - Algorithm: PBKDF2-SHA256
   - Automatic salt generation via werkzeug
   - No plaintext passwords stored

2. **JWT Tokens**
   - Cryptographically signed
   - Expiry time validation
   - Token type validation (access vs refresh)

3. **Email Validation**
   - Format validation with regex
   - Uniqueness checking
   - Case-insensitive storage

4. **Password Strength**
   - Enforced requirements
   - Complexity scoring (0-5)
   - Strength feedback

## Database Schema

### users table
```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL
);
```

## Testing

Run the example usage script:
```bash
python example_auth_usage.py
```

This will test all authentication endpoints with various scenarios:
- Email validation
- Password strength checking
- User registration
- User login
- Token refresh
- Error handling (invalid credentials, weak password, duplicate email)

## Development Commands

Initialize database:
```bash
python manage.py db init
```

Seed with sample data:
```bash
python manage.py db seed
```

Test password strength:
```bash
python manage.py security test-password
```

Generate JWT tokens:
```bash
python manage.py jwt generate --user-id 1 --email user@example.com
```

Validate token:
```bash
python manage.py jwt validate --token <token>
```

Interactive shell with all utilities:
```bash
python manage.py shell
```

## API Response Format

### Success Response
```json
{
  "success": true,
  "message": "Operation successful",
  "data": {...}
}
```

### Error Response
```json
{
  "error": "error_code",
  "message": "Human readable message",
  "details": {...}  // optional
}
```

## Status Codes
- **200** - OK
- **201** - Created (successful registration)
- **400** - Bad Request (validation error)
- **401** - Unauthorized (invalid credentials, expired token)
- **404** - Not Found
- **409** - Conflict (email already exists)
- **500** - Server Error

## Next Steps

1. **Email Verification** (Optional)
   - Send verification email on registration
   - Mark email as verified
   - Skip if email verification not required

2. **Password Reset** (Optional)
   - Forgot password endpoint
   - Reset token generation
   - New password setting

3. **OAuth Integration** (Optional)
   - Google OAuth
   - GitHub OAuth
   - Social login

4. **Rate Limiting**
   - Limit login attempts
   - Prevent brute force attacks

5. **Two-Factor Authentication** (Optional)
   - TOTP support
   - SMS verification

## Troubleshooting

### JWT_SECRET_KEY not configured
**Error**: `JWT_SECRET_KEY not configured`
**Solution**: Set `JWT_SECRET_KEY` in environment variables or Flask config

### Token validation failed
**Error**: `Invalid token` or `Token expired`
**Solution**: Check token hasn't expired, is properly formatted, and matches secret key

### Duplicate email registration
**Error**: `Email ... is already registered`
**Solution**: Use a different email or reset user password

### Weak password
**Error**: `Password does not meet strength requirements`
**Solution**: Add uppercase, lowercase, digits, and special characters

## Support

For API documentation, see [AUTH_API.md](AUTH_API.md)

For usage examples, see [example_auth_usage.py](example_auth_usage.py)
