from datetime import datetime
import json
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from password_utils import (
    hash_password,
    verify_password,
    is_password_strong,
    get_password_strength_score
)
from jwt_utils import generate_tokens


class User(db.Model):
    """User model with authentication and timestamp tracking"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    trips = db.relationship('Trip', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = hash_password(password)
    
    def check_password(self, password):
        """Verify the user's password"""
        return verify_password(self.password_hash, password)
    
    def validate_password_strength(self):
        """
        Validate the strength of the current password hash.
        Note: This validates the original password strength requirements.
        
        Returns:
            dict: Validation result with 'is_strong' and 'errors' keys
        """
        # Since we only have the hash, we can't validate the original password
        # This method is provided for reference; password strength should be
        # validated before calling set_password()
        return {'is_strong': True, 'errors': []}
    
    @staticmethod
    def check_password_strength(password):
        """
        Static method to check password strength before setting.
        
        Args:
            password (str): The password to check
        
        Returns:
            dict: {
                'is_strong': bool,
                'errors': list of validation messages
            }
        """
        return is_password_strong(password)
    
    @staticmethod
    def get_password_strength_score(password):
        """
        Static method to get password strength score.
        
        Args:
            password (str): The password to score
        
        Returns:
            dict: Score, level, and feedback
        """
        return get_password_strength_score(password)
    
    def generate_auth_tokens(self, access_expiry_minutes=None, refresh_expiry_days=None):
        """
        Generate JWT tokens for this user.
        
        Args:
            access_expiry_minutes (int): Access token expiry in minutes
            refresh_expiry_days (int): Refresh token expiry in days
        
        Returns:
            dict: Token data including access_token, refresh_token, and expiry info
        """
        return generate_tokens(
            self.id,
            self.email,
            access_expiry_minutes,
            refresh_expiry_days
        )
    
    def to_dict(self):
        """Return user data as dictionary (excluding password_hash)"""
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def to_dict_with_token(self):
        """Return user data with auth tokens"""
        tokens = self.generate_auth_tokens()
        user_data = self.to_dict()
        user_data['auth'] = tokens
        return user_data


class Trip(db.Model):
    """Trip model for user travel plans"""
    __tablename__ = 'trips'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    destination = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    coordinates = db.Column(db.JSON, nullable=True)  # Store as {latitude, longitude}
    itinerary = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Trip {self.destination}>'
    
    def set_coordinates(self, latitude, longitude):
        """Set coordinates as latitude and longitude"""
        self.coordinates = {'latitude': latitude, 'longitude': longitude}
    
    def get_coordinates(self):
        """Get coordinates as tuple (latitude, longitude)"""
        if self.coordinates:
            return (self.coordinates.get('latitude'), self.coordinates.get('longitude'))
        return None
    
    def to_dict(self):
        """Return trip data as dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'destination': self.destination,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'coordinates': self.coordinates,
            'itinerary': self.itinerary,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
