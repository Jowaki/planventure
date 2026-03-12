"""
Password hashing and security utility functions.

Provides functions for:
- Hashing passwords with salt
- Verifying passwords
- Password strength validation
- Generating secure password hashes
"""
from werkzeug.security import generate_password_hash, check_password_hash
import re
import secrets


# Password hashing configuration
HASH_METHOD = 'pbkdf2:sha256'
HASH_ITERATIONS = 100000


def hash_password(password, salt_length=16):
    """
    Hash a password with a salt using PBKDF2-SHA256.
    
    Args:
        password (str): The plain text password to hash
        salt_length (int): Length of the salt to generate (default: 16)
    
    Returns:
        str: The hashed password with embedded salt
    
    Raises:
        ValueError: If password is None or empty
    """
    if not password:
        raise ValueError("Password cannot be empty")
    
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    
    # Werkzeug's generate_password_hash automatically generates and embeds salt
    return generate_password_hash(password, method=HASH_METHOD)


def verify_password(stored_hash, provided_password):
    """
    Verify a provided password against a stored hash.
    
    Args:
        stored_hash (str): The stored password hash
        provided_password (str): The password to verify
    
    Returns:
        bool: True if password matches, False otherwise
    """
    if not stored_hash or not provided_password:
        return False
    
    try:
        return check_password_hash(stored_hash, provided_password)
    except Exception:
        return False


def is_password_strong(password, min_length=8):
    """
    Validate password strength.
    
    Requirements:
    - Minimum length (default: 8 characters)
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
    
    Args:
        password (str): The password to validate
        min_length (int): Minimum required length (default: 8)
    
    Returns:
        dict: {
            'is_strong': bool,
            'errors': list of validation error messages
        }
    """
    errors = []
    
    if not password:
        return {'is_strong': False, 'errors': ['Password cannot be empty']}
    
    if len(password) < min_length:
        errors.append(f'Password must be at least {min_length} characters long')
    
    if not re.search(r'[A-Z]', password):
        errors.append('Password must contain at least one uppercase letter')
    
    if not re.search(r'[a-z]', password):
        errors.append('Password must contain at least one lowercase letter')
    
    if not re.search(r'\d', password):
        errors.append('Password must contain at least one digit')
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        errors.append('Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)')
    
    return {
        'is_strong': len(errors) == 0,
        'errors': errors
    }


def generate_secure_salt(length=32):
    """
    Generate a cryptographically secure random salt.
    
    Args:
        length (int): Length of the salt in bytes (default: 32)
    
    Returns:
        str: Hexadecimal encoded salt
    """
    return secrets.token_hex(length)


def get_password_strength_score(password):
    """
    Calculate password strength score (0-5).
    
    Scoring:
    - 0: Empty or None
    - 1: Too short or only lowercase/uppercase
    - 2: Has letters and numbers
    - 3: Has letters, numbers, and special chars
    - 4: Strong (8+ chars with all requirements except length)
    - 5: Very strong (12+ chars with all requirements)
    
    Args:
        password (str): The password to score
    
    Returns:
        dict: {
            'score': int (0-5),
            'level': str ('very_weak', 'weak', 'fair', 'good', 'strong', 'very_strong'),
            'feedback': str describing the score
        }
    """
    if not password:
        return {
            'score': 0,
            'level': 'very_weak',
            'feedback': 'Password is empty'
        }
    
    score = 1  # Start with 1 for non-empty
    
    # Length bonus
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    
    # Character variety
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password))
    
    variety_count = sum([has_lower, has_upper, has_digit, has_special])
    
    if variety_count >= 2:
        score += 1
    if variety_count >= 3:
        score += 1
    
    # Cap at 5
    score = min(score, 5)
    
    # Determine level and feedback
    levels = {
        0: ('very_weak', 'Password is too weak'),
        1: ('weak', 'Password is very weak'),
        2: ('fair', 'Password is fair, consider making it stronger'),
        3: ('good', 'Password is good'),
        4: ('strong', 'Password is strong'),
        5: ('very_strong', 'Password is very strong')
    }
    
    level, feedback = levels[score]
    
    return {
        'score': score,
        'level': level,
        'feedback': feedback
    }
