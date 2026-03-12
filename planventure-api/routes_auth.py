"""
Authentication routes for user registration and login.

Endpoints:
- POST /auth/register - Register a new user
- POST /auth/login - Login with email and password
- POST /auth/refresh - Refresh access token
"""
from flask import Blueprint, request, jsonify
from app import db
from models import User
from schemas import UserSchema, user_schema
from password_utils import is_password_strong, get_password_strength_score
from jwt_utils import (
    generate_tokens,
    validate_token,
    refresh_access_token,
    token_required,
    TokenExpiredError,
    TokenInvalidError,
    extract_token_from_request,
    get_current_user_from_token
)
import re


# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


def validate_email(email):
    """
    Validate email format using regex.
    
    Args:
        email (str): Email address to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    # Basic email validation regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user with email and password.
    
    Request body:
    {
        "email": "user@example.com",
        "password": "SecurePass123!"
    }
    
    Returns:
        201: User created successfully with tokens
        400: Invalid input or validation failed
        409: Email already registered
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Request body must be JSON'
            }), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate email
        if not email:
            return jsonify({
                'error': 'validation_error',
                'message': 'Email is required'
            }), 400
        
        if not validate_email(email):
            return jsonify({
                'error': 'validation_error',
                'message': 'Invalid email format',
                'example': 'user@example.com'
            }), 400
        
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'error': 'email_exists',
                'message': f'Email {email} is already registered'
            }), 409
        
        # Validate password
        if not password:
            return jsonify({
                'error': 'validation_error',
                'message': 'Password is required'
            }), 400
        
        # Check password strength
        strength = is_password_strong(password)
        if not strength['is_strong']:
            return jsonify({
                'error': 'weak_password',
                'message': 'Password does not meet strength requirements',
                'requirements': strength['errors']
            }), 400
        
        # Create new user
        user = User(email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate tokens
        tokens = user.generate_auth_tokens()
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'email': user.email,
                'created_at': user.created_at.isoformat()
            },
            'auth': {
                'access_token': tokens['access_token'],
                'refresh_token': tokens['refresh_token'],
                'token_type': tokens['token_type'],
                'access_token_expiry': tokens['access_token_expiry'],
                'refresh_token_expiry': tokens['refresh_token_expiry']
            }
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'registration_error',
            'message': str(e)
        }), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login user with email and password.
    
    Request body:
    {
        "email": "user@example.com",
        "password": "SecurePass123!"
    }
    
    Returns:
        200: Login successful with tokens
        400: Invalid input
        401: Invalid credentials
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Request body must be JSON'
            }), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate input
        if not email or not password:
            return jsonify({
                'error': 'validation_error',
                'message': 'Email and password are required'
            }), 400
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({
                'error': 'invalid_credentials',
                'message': 'Invalid email or password'
            }), 401
        
        # Verify password
        if not user.check_password(password):
            return jsonify({
                'error': 'invalid_credentials',
                'message': 'Invalid email or password'
            }), 401
        
        # Generate tokens
        tokens = user.generate_auth_tokens()
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email,
                'created_at': user.created_at.isoformat()
            },
            'auth': {
                'access_token': tokens['access_token'],
                'refresh_token': tokens['refresh_token'],
                'token_type': tokens['token_type'],
                'access_token_expiry': tokens['access_token_expiry'],
                'refresh_token_expiry': tokens['refresh_token_expiry']
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'login_error',
            'message': str(e)
        }), 500


@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    """
    Refresh access token using refresh token.
    
    Request body:
    {
        "refresh_token": "<refresh_token>"
    }
    
    Or via Authorization header:
    Authorization: Bearer <refresh_token>
    
    Returns:
        200: New access token generated
        400: Refresh token invalid or expired
    """
    try:
        # Try to get refresh token from body first, then from header
        data = request.get_json() or {}
        refresh_token = data.get('refresh_token')
        
        if not refresh_token:
            try:
                refresh_token = extract_token_from_request()
            except TokenInvalidError:
                return jsonify({
                    'error': 'missing_token',
                    'message': 'Refresh token is required in body or Authorization header'
                }), 400
        
        # Refresh the token
        new_tokens = refresh_access_token(refresh_token)
        
        return jsonify({
            'success': True,
            'message': 'Access token refreshed successfully',
            'auth': {
                'access_token': new_tokens['access_token'],
                'token_type': new_tokens['token_type'],
                'access_token_expiry': new_tokens['access_token_expiry']
            }
        }), 200
    
    except TokenExpiredError:
        return jsonify({
            'error': 'token_expired',
            'message': 'Refresh token has expired. Please login again.'
        }), 401
    
    except TokenInvalidError as e:
        return jsonify({
            'error': 'invalid_token',
            'message': str(e)
        }), 401
    
    except Exception as e:
        return jsonify({
            'error': 'refresh_error',
            'message': str(e)
        }), 500


@auth_bp.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    """
    Get current authenticated user information.
    
    Headers:
    Authorization: Bearer <access_token>
    
    Returns:
        200: Current user information
        401: Invalid or expired token
    """
    try:
        user = User.query.get(current_user['user_id'])
        
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'message': 'User not found'
            }), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user.id,
                'email': user.email,
                'created_at': user.created_at.isoformat(),
                'updated_at': user.updated_at.isoformat()
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'user_error',
            'message': str(e)
        }), 500


@auth_bp.route('/validate-email', methods=['POST'])
def validate_email_endpoint():
    """
    Validate email format and check if already registered.
    
    Request body:
    {
        "email": "user@example.com"
    }
    
    Returns:
        200: Email validation result
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'valid': False,
                'message': 'Request body must be JSON'
            }), 400
        
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({
                'valid': False,
                'message': 'Email is required'
            }), 400
        
        # Check format
        is_valid_format = validate_email(email)
        
        if not is_valid_format:
            return jsonify({
                'valid': False,
                'format_valid': False,
                'message': 'Invalid email format'
            }), 200
        
        # Check if already registered
        existing_user = User.query.filter_by(email=email).first()
        
        if existing_user:
            return jsonify({
                'valid': False,
                'format_valid': True,
                'exists': True,
                'message': f'Email {email} is already registered'
            }), 200
        
        return jsonify({
            'valid': True,
            'format_valid': True,
            'exists': False,
            'message': 'Email is valid and available'
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'validation_error',
            'message': str(e)
        }), 500


@auth_bp.route('/password-strength', methods=['POST'])
def check_password_strength():
    """
    Check password strength without creating user.
    
    Request body:
    {
        "password": "SecurePass123!"
    }
    
    Returns:
        200: Password strength analysis
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Request body must be JSON'
            }), 400
        
        password = data.get('password', '')
        
        if not password:
            return jsonify({
                'error': 'validation_error',
                'message': 'Password is required'
            }), 400
        
        strength = is_password_strong(password)
        score = get_password_strength_score(password)
        
        return jsonify({
            'password_strength': {
                'is_strong': strength['is_strong'],
                'score': score['score'],
                'level': score['level'],
                'feedback': score['feedback'],
                'requirements': {
                    'met': [] if not strength['errors'] else None,
                    'failed': strength['errors']
                }
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'strength_check_error',
            'message': str(e)
        }), 500
