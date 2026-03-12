from marshmallow import Schema, fields, validate, ValidationError, post_load
from datetime import datetime


class UserSchema(Schema):
    """Schema for User serialization and validation"""
    id = fields.Int(dump_only=True)
    email = fields.Email(required=True, validate=validate.Length(min=5, max=255))
    password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=8),
        error_messages={'required': 'Password is required'}
    )
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    class Meta:
        strict = True


class CoordinatesField(fields.Field):
    """Custom field for coordinates validation"""
    def _deserialize(self, value, attr, data, **kwargs):
        """Deserialize coordinates from dict"""
        if value is None:
            return None
        if isinstance(value, dict):
            lat = value.get('latitude')
            lng = value.get('longitude')
            if lat is None or lng is None:
                raise ValidationError('Coordinates must have latitude and longitude')
            if not (-90 <= lat <= 90):
                raise ValidationError('Latitude must be between -90 and 90')
            if not (-180 <= lng <= 180):
                raise ValidationError('Longitude must be between -180 and 180')
            return value
        raise ValidationError('Coordinates must be a dictionary with latitude and longitude')


class TripSchema(Schema):
    """Schema for Trip serialization and validation"""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(required=True)
    destination = fields.Str(required=True, validate=validate.Length(min=2, max=255))
    start_date = fields.DateTime(required=True)
    end_date = fields.DateTime(required=True)
    coordinates = CoordinatesField(required=False, allow_none=True)
    itinerary = fields.Str(required=False, allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    
    class Meta:
        strict = True


# Instance for single user serialization
user_schema = UserSchema()

# Instance for multiple users serialization
users_schema = UserSchema(many=True)

# Instance for single trip serialization
trip_schema = TripSchema()

# Instance for multiple trips serialization
trips_schema = TripSchema(many=True)
