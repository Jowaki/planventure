"""
JWT (JSON Web Token) authentication utility functions.

Provides functions for:
- Generating access and refresh tokens
- Validating tokens
- Extracting user data from tokens
- Token expiration management
"""
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import current_app, request, jsonify
import os


# JWT Configuration defaults
DEFAULT_ACCESS_TOKEN_EXPIRY = 15  # minutes
DEFAULT_REFRESH_TOKEN_EXPIRY = 7  # days
DEFAULT_ALGORITHM = 'HS256'


class JWTError(Exception):
    """Custom exception for JWT-related errors"""
    pass


class TokenExpiredError(JWTError):
    """Exception raised when a token has expired"""
    pass


class TokenInvalidError(JWTError):
    """Exception raised when a token is invalid"""
    pass


def get_jwt_secret():
    """
    Get the JWT secret key from environment or Flask config.
    
    Returns:
        str: The JWT secret key
    
    Raises:
        JWTError: If no secret is configured
    """
    secret = os.getenv('JWT_SECRET_KEY')
    
    if not secret:
        try:
            secret = current_app.config.get('JWT_SECRET_KEY')
        except RuntimeError:
            pass
    
    if not secret:
        raise JWTError(
            "JWT_SECRET_KEY not configured. Set JWT_SECRET_KEY environment variable or Flask config."
        )
    
    return secret


def generate_tokens(user_id, email, access_expiry_minutes=None, refresh_expiry_days=None):
    """
    Generate access and refresh JWT tokens for a user.
    
    Args:
        user_id (int): The user's ID
        email (str): The user's email
        access_expiry_minutes (int): Access token expiry in minutes (default: 15)
        refresh_expiry_days (int): Refresh token expiry in days (default: 7)
    
    Returns:
        dict: {
            'access_token': str,
            'refresh_token': str,
            'access_token_expiry': int (unix timestamp),
            'refresh_token_expiry': int (unix timestamp)
        }
    
    Raises:
        JWTError: If token generation fails
    """
    if access_expiry_minutes is None:
        access_expiry_minutes = DEFAULT_ACCESS_TOKEN_EXPIRY
    
    if refresh_expiry_days is None:
        refresh_expiry_days = DEFAULT_REFRESH_TOKEN_EXPIRY
    
    try:
        now = datetime.utcnow()
        
        # Calculate expiry times
        access_expiry = now + timedelta(minutes=access_expiry_minutes)
        refresh_expiry = now + timedelta(days=refresh_expiry_days)
        
        # Payload for access token
        access_payload = {
            'user_id': user_id,
            'email': email,
            'token_type': 'access',
            'iat': now,
            'exp': access_expiry
        }
        
        # Payload for refresh token
        refresh_payload = {
            'user_id': user_id,
            'email': email,
            'token_type': 'refresh',
            'iat': now,
            'exp': refresh_expiry
        }
        
        secret = get_jwt_secret()
        
        # Generate tokens
        access_token = jwt.encode(
            access_payload,
            secret,
            algorithm=DEFAULT_ALGORITHM
        )
        
        refresh_token = jwt.encode(
            refresh_payload,
            secret,
            algorithm=DEFAULT_ALGORITHM
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'access_token_expiry': int(access_expiry.timestamp()),
            'refresh_token_expiry': int(refresh_expiry.timestamp()),
            'token_type': 'Bearer'
        }
    
    except Exception as e:
        raise JWTError(f"Token generation failed: {str(e)}")


def validate_token(token):
    """
    Validate and decode a JWT token.
    
    Args:
        token (str): The JWT token to validate
    
    Returns:
        dict: The decoded token payload
    
    Raises:
        TokenExpiredError: If the token has expired
        TokenInvalidError: If the token is invalid
    """
    if not token:
        raise TokenInvalidError("Token is missing")
    
    try:
        secret = get_jwt_secret()
        payload = jwt.decode(
            token,
            secret,
            algorithms=[DEFAULT_ALGORITHM]
        )
        return payload
    
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token has expired")
    
    except jwt.InvalidTokenError as e:
        raise TokenInvalidError(f"Invalid token: {str(e)}")
    
    except Exception as e:
        raise TokenInvalidError(f"Token validation failed: {str(e)}")


def refresh_access_token(refresh_token):
    """
    Generate a new access token from a refresh token.
    
    Args:
        refresh_token (str): A valid refresh token
    
    Returns:
        dict: {
            'access_token': str,
            'access_token_expiry': int (unix timestamp),
            'token_type': 'Bearer'
        }
    
    Raises:
        TokenExpiredError: If refresh token has expired
        TokenInvalidError: If refresh token is invalid
    """
    try:
        payload = validate_token(refresh_token)
        
        if payload.get('token_type') != 'refresh':
            raise TokenInvalidError("Token is not a refresh token")
        
        user_id = payload.get('user_id')
        email = payload.get('email')
        
        if not user_id or not email:
            raise TokenInvalidError("Invalid token payload")
        
        # Generate new access token only
        tokens = generate_tokens(user_id, email)
        
        return {
            'access_token': tokens['access_token'],
            'access_token_expiry': tokens['access_token_expiry'],
            'token_type': tokens['token_type']
        }
    
    except (TokenExpiredError, TokenInvalidError):
        raise
    except Exception as e:
        raise TokenInvalidError(f"Token refresh failed: {str(e)}")


def extract_token_from_request(request_obj=None):
    """
    Extract JWT token from Authorization header.
    
    Expected format: "Bearer <token>"
    
    Args:
        request_obj: Flask request object (uses current_request if None)
    
    Returns:
        str: The extracted token
    
    Raises:
        TokenInvalidError: If token format is invalid
    """
    if request_obj is None:
        request_obj = request
    
    auth_header = request_obj.headers.get('Authorization', '')
    
    if not auth_header:
        raise TokenInvalidError("Authorization header is missing")
    
    parts = auth_header.split()
    
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        raise TokenInvalidError("Invalid Authorization header format. Expected: 'Bearer <token>'")
    
    return parts[1]


def get_current_user_from_token(token=None):
    """
    Get current user information from token.
    
    Args:
        token (str): JWT token (uses extracted token from request if None)
    
    Returns:
        dict: User data from token payload
    
    Raises:
        TokenExpiredError: If token has expired
        TokenInvalidError: If token is invalid
    """
    if token is None:
        token = extract_token_from_request()
    
    payload = validate_token(token)
    
    return {
        'user_id': payload.get('user_id'),
        'email': payload.get('email'),
        'token_type': payload.get('token_type'),
        'issued_at': payload.get('iat'),
        'expires_at': payload.get('exp')
    }


def token_required(f):
    """
    Decorator for Flask routes that require a valid JWT token.
    
    Usage:
        @app.route('/protected')
        @token_required
        def protected_route(current_user):
            return jsonify(user=current_user)
    
    Args:
        f: Flask route function
    
    Returns:
        Wrapped function that validates token before executing
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            token = extract_token_from_request()
            current_user = get_current_user_from_token(token)
            return f(current_user, *args, **kwargs)
        
        except TokenExpiredError:
            return jsonify({
                'error': 'Token expired',
                'message': 'Your session has expired. Please login again.'
            }), 401
        
        except TokenInvalidError as e:
            return jsonify({
                'error': 'Invalid token',
                'message': str(e)
            }), 401
        
        except Exception as e:
            return jsonify({
                'error': 'Authentication failed',
                'message': str(e)
            }), 401
    
    return decorated_function


def format_token_expiry(timestamp):
    """
    Format a unix timestamp as human-readable datetime.
    
    Args:
        timestamp (int): Unix timestamp
    
    Returns:
        str: Formatted datetime string
    """
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
