# Authentication API Documentation

## Overview
The Authentication API provides endpoints for user registration, login, token management, and email/password validation.

## Base URL
```
http://localhost:5000/auth
```

## Endpoints

### 1. Register New User
**POST** `/auth/register`

Create a new user account with email and password.

#### Request
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

#### Requirements
- **Email**: Valid email format, must not already exist
- **Password**: 
  - Minimum 8 characters
  - At least one uppercase letter (A-Z)
  - At least one lowercase letter (a-z)
  - At least one digit (0-9)
  - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)

#### Response (201 Created)
```json
{
  "success": true,
  "message": "User registered successfully",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2026-03-11T10:30:00"
  },
  "auth": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "Bearer",
    "access_token_expiry": 1710149400,
    "refresh_token_expiry": 1710667800
  }
}
```

#### Error Responses
- **400**: Invalid email format or weak password
- **409**: Email already registered
- **500**: Server error

---

### 2. Login
**POST** `/auth/login`

Authenticate user with email and password.

#### Request
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2026-03-11T10:30:00"
  },
  "auth": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "Bearer",
    "access_token_expiry": 1710149400,
    "refresh_token_expiry": 1710667800
  }
}
```

#### Error Responses
- **400**: Missing email or password
- **401**: Invalid email or password
- **500**: Server error

---

### 3. Refresh Access Token
**POST** `/auth/refresh`

Generate a new access token using a refresh token.

#### Request (Option 1: JSON Body)
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

#### Request (Option 2: Authorization Header)
```
POST /auth/refresh
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

#### Response (200 OK)
```json
{
  "success": true,
  "message": "Access token refreshed successfully",
  "auth": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "Bearer",
    "access_token_expiry": 1710149400
  }
}
```

#### Error Responses
- **400**: Refresh token missing
- **401**: Refresh token expired or invalid
- **500**: Server error

---

### 4. Get Current User
**GET** `/auth/me`

Get information about the currently authenticated user.

#### Request
```
GET /auth/me
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

#### Response (200 OK)
```json
{
  "success": true,
  "user": {
    "id": 1,
    "email": "user@example.com",
    "created_at": "2026-03-11T10:30:00",
    "updated_at": "2026-03-11T10:30:00"
  }
}
```

#### Error Responses
- **401**: Missing or invalid token
- **404**: User not found
- **500**: Server error

---

### 5. Validate Email
**POST** `/auth/validate-email`

Check if an email is valid and available for registration.

#### Request
```json
{
  "email": "user@example.com"
}
```

#### Response (200 OK - Valid and Available)
```json
{
  "valid": true,
  "format_valid": true,
  "exists": false,
  "message": "Email is valid and available"
}
```

#### Response (200 OK - Already Registered)
```json
{
  "valid": false,
  "format_valid": true,
  "exists": true,
  "message": "Email user@example.com is already registered"
}
```

#### Response (200 OK - Invalid Format)
```json
{
  "valid": false,
  "format_valid": false,
  "message": "Invalid email format"
}
```

---

### 6. Check Password Strength
**POST** `/auth/password-strength`

Analyze password strength without creating a user account.

#### Request
```json
{
  "password": "SecurePass123!"
}
```

#### Response (200 OK - Strong Password)
```json
{
  "password_strength": {
    "is_strong": true,
    "score": 5,
    "level": "very_strong",
    "feedback": "Password is very strong",
    "requirements": {
      "met": [],
      "failed": []
    }
  }
}
```

#### Response (200 OK - Weak Password)
```json
{
  "password_strength": {
    "is_strong": false,
    "score": 1,
    "level": "weak",
    "feedback": "Password is very weak",
    "requirements": {
      "met": null,
      "failed": [
        "Password must be at least 8 characters long",
        "Password must contain at least one uppercase letter",
        "Password must contain at least one digit"
      ]
    }
  }
}
```

---

## Authentication

Protected endpoints require a valid JWT access token in the Authorization header.

### Format
```
Authorization: Bearer <access_token>
```

### Token Expiry
- **Access Token**: 15 minutes (configurable)
- **Refresh Token**: 7 days (configurable)

---

## Error Handling

### Standard Error Response
```json
{
  "error": "error_code",
  "message": "Human readable error message"
}
```

### Common Error Codes
- `invalid_request` - Invalid request format
- `validation_error` - Data validation failed
- `invalid_credentials` - Wrong email or password
- `email_exists` - Email already registered
- `weak_password` - Password doesn't meet requirements
- `missing_token` - Authorization token missing
- `invalid_token` - Invalid or malformed token
- `token_expired` - Token has expired
- `user_not_found` - User does not exist

---

## Example Usage (cURL)

### Register User
```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
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

### Get Current User (Protected)
```bash
curl -X GET http://localhost:5000/auth/me \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

### Refresh Token
```bash
curl -X POST http://localhost:5000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }'
```

### Validate Email
```bash
curl -X POST http://localhost:5000/auth/validate-email \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

### Check Password Strength
```bash
curl -X POST http://localhost:5000/auth/password-strength \
  -H "Content-Type: application/json" \
  -d '{"password": "MyPassword123!"}'
```

---

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK - Request successful |
| 201 | Created - User created successfully |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Invalid/expired token or credentials |
| 404 | Not Found - Resource doesn't exist |
| 409 | Conflict - Email already registered |
| 500 | Server Error - Unexpected error |

---

## Password Requirements

Valid passwords must contain:
- ✓ Minimum 8 characters
- ✓ At least one uppercase letter (A-Z)
- ✓ At least one lowercase letter (a-z)
- ✓ At least one digit (0-9)
- ✓ At least one special character: `!@#$%^&*()_+-=[]{}|;:,.<>?`

### Examples of Valid Passwords
- `SecurePass123!`
- `MyP@ssw0rd`
- `Test#Pass2024`

### Examples of Invalid Passwords
- `weakpass` - Too simple, no uppercase/digits/special
- `12345678` - Only digits
- `Password123` - No special character
- `Pass@1` - Too short (less than 8 characters)
