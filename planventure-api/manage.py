"""
Database and application management CLI.

Usage:
    python manage.py db init       - Initialize database (create all tables)
    python manage.py db drop       - Drop all tables
    python manage.py db reset      - Drop and recreate all tables
    python manage.py db seed       - Seed database with sample data
    python manage.py security test-password - Test password strength
    python manage.py jwt generate  - Generate tokens for a user
    python manage.py jwt validate  - Validate a token
    python manage.py jwt refresh   - Refresh an access token
    python manage.py shell         - Start Flask shell
"""
import click
from datetime import datetime, timedelta
from app import create_app, db
from models import User, Trip
from password_utils import (
    hash_password,
    verify_password,
    is_password_strong,
    get_password_strength_score
)
from jwt_utils import (
    generate_tokens,
    validate_token,
    refresh_access_token,
    format_token_expiry,
    TokenExpiredError,
    TokenInvalidError
)


app = create_app()


@click.group()
def cli():
    """Database and application management commands"""
    pass


@cli.group()
def db():
    """Database management commands"""
    pass


@cli.group()
def security():
    """Security and password management commands"""
    pass


@cli.group()
def jwt():
    """JWT token management commands"""
    pass


@db.command()
def init():
    """Initialize the database (create all tables)"""
    with app.app_context():
        click.echo("Creating database tables...")
        db.create_all()
        click.secho("✓ Database initialized successfully!", fg='green')
        click.echo("\nTables created:")
        click.echo("  - users")
        click.echo("  - trips")


@db.command()
def drop():
    """Drop all database tables"""
    with app.app_context():
        if click.confirm('⚠️  WARNING: This will delete all tables and data. Continue?'):
            click.echo("Dropping all tables...")
            db.drop_all()
            click.secho("✓ All tables dropped successfully!", fg='green')
        else:
            click.echo("Operation cancelled.")


@db.command()
def reset():
    """Drop and recreate all database tables"""
    with app.app_context():
        if click.confirm('⚠️  WARNING: This will delete all tables and data. Continue?'):
            click.echo("Dropping all tables...")
            db.drop_all()
            click.echo("Creating database tables...")
            db.create_all()
            click.secho("✓ Database reset successfully!", fg='green')
        else:
            click.echo("Operation cancelled.")


@db.command()
def seed():
    """Seed the database with sample data"""
    with app.app_context():
        try:
            # Create sample users
            sample_users = [
                User(email='user1@example.com'),
                User(email='user2@example.com'),
                User(email='user3@example.com'),
            ]
            
            # Set passwords for sample users
            sample_users[0].set_password('password123')
            sample_users[1].set_password('securepass456')
            sample_users[2].set_password('mypassword789')
            
            # Add users to database
            for user in sample_users:
                db.session.add(user)
            
            db.session.flush()  # Flush to get user IDs
            
            # Create sample trips
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=7)
            
            sample_trips = [
                Trip(
                    user_id=sample_users[0].id,
                    destination='Paris, France',
                    start_date=start_date,
                    end_date=end_date,
                    itinerary='Visit Eiffel Tower, Louvre Museum, and Notre-Dame'
                ),
                Trip(
                    user_id=sample_users[0].id,
                    destination='Tokyo, Japan',
                    start_date=start_date + timedelta(days=30),
                    end_date=start_date + timedelta(days=37),
                    itinerary='Explore temples, enjoy street food, visit anime districts'
                ),
                Trip(
                    user_id=sample_users[1].id,
                    destination='New York, USA',
                    start_date=start_date,
                    end_date=start_date + timedelta(days=5),
                    itinerary='Broadway shows, Times Square, Central Park'
                ),
                Trip(
                    user_id=sample_users[2].id,
                    destination='Barcelona, Spain',
                    start_date=start_date + timedelta(days=14),
                    end_date=start_date + timedelta(days=21),
                    itinerary='Sagrada Familia, Park Güell, Gothic Quarter'
                ),
            ]
            
            # Set coordinates for sample trips
            sample_trips[0].set_coordinates(48.8566, 2.3522)  # Paris
            sample_trips[1].set_coordinates(35.6762, 139.6503)  # Tokyo
            sample_trips[2].set_coordinates(40.7128, -74.0060)  # New York
            sample_trips[3].set_coordinates(41.3851, 2.1734)  # Barcelona
            
            # Add trips to database
            for trip in sample_trips:
                db.session.add(trip)
            
            db.session.commit()
            click.secho(f"✓ Seeded database with {len(sample_users)} users and {len(sample_trips)} trips!", fg='green')
            
            # Display created users
            click.echo("\nCreated users:")
            for user in sample_users:
                user_trips = Trip.query.filter_by(user_id=user.id).count()
                click.echo(f"  - {user.email} ({user_trips} trips)")
            
            # Display created trips
            click.echo("\nCreated trips:")
            for trip in sample_trips:
                click.echo(f"  - {trip.destination} ({trip.user.email})")
        except Exception as e:
            db.session.rollback()
            click.secho(f"✗ Error seeding database: {str(e)}", fg='red')


@cli.command()
def shell():
    """Start an interactive Flask shell"""
    with app.app_context():
        import code
        import readline
        
        # Make app and db available in shell
        local_vars = {
            'app': app,
            'db': db,
            'User': User,
            'Trip': Trip,
            'hash_password': hash_password,
            'verify_password': verify_password,
            'is_password_strong': is_password_strong,
            'get_password_strength_score': get_password_strength_score,
            'generate_tokens': generate_tokens,
            'validate_token': validate_token,
            'refresh_access_token': refresh_access_token,
        }
        
        click.echo("Starting interactive Flask shell...")
        click.echo("Available objects: app, db, User, Trip")
        click.echo("Available functions: hash_password, verify_password, is_password_strong,")
        click.echo("                     get_password_strength_score, generate_tokens,")
        click.echo("                     validate_token, refresh_access_token")
        click.echo("Type 'exit()' or press Ctrl+D to exit\n")
        
        code.InteractiveConsole(
            local_vars,
            filename="<console>"
        ).interact(banner="")


@security.command(name='test-password')
@click.option('--password', prompt='Enter password to test', hide_input=True, confirmation_prompt=False)
def test_password(password):
    """Test password strength and hashing"""
    click.echo("\n" + "="*50)
    click.echo("PASSWORD STRENGTH ANALYSIS")
    click.echo("="*50)
    
    # Test strength
    strength = is_password_strong(password)
    click.echo(f"\nBasic Validation: {'✓ PASS' if strength['is_strong'] else '✗ FAIL'}")
    
    if strength['errors']:
        click.echo("Requirements not met:")
        for error in strength['errors']:
            click.secho(f"  • {error}", fg='red')
    else:
        click.secho("  All requirements met!", fg='green')
    
    # Get score
    score_info = get_password_strength_score(password)
    colors = {
        'very_weak': 'red',
        'weak': 'red',
        'fair': 'yellow',
        'good': 'yellow',
        'strong': 'green',
        'very_strong': 'green'
    }
    color = colors.get(score_info['level'], 'white')
    
    click.echo(f"\nStrength Score: {score_info['score']}/5")
    click.secho(f"Level: {score_info['level'].upper()}", fg=color)
    click.echo(f"Feedback: {score_info['feedback']}")
    
    # Test hashing and verification
    click.echo("\n" + "="*50)
    click.echo("HASH VERIFICATION TEST")
    click.echo("="*50)
    
    try:
        password_hash = hash_password(password)
        click.secho("✓ Password hashed successfully", fg='green')
        click.echo(f"\nHash: {password_hash[:50]}...")
        
        # Verify
        is_valid = verify_password(password_hash, password)
        if is_valid:
            click.secho("✓ Password verification: SUCCESS", fg='green')
        else:
            click.secho("✗ Password verification: FAILED", fg='red')
        
    except ValueError as e:
        click.secho(f"✗ Error: {str(e)}", fg='red')
    
    click.echo()


@security.command(name='hash-password')
@click.option('--password', prompt='Enter password to hash', hide_input=True, confirmation_prompt=True)
def hash_cmd(password):
    """Hash a password and display the hash"""
    try:
        password_hash = hash_password(password)
        click.secho("✓ Password hashed successfully!\n", fg='green')
        click.echo(f"Hash: {password_hash}")
    except ValueError as e:
        click.secho(f"✗ Error: {str(e)}", fg='red')


@jwt.command(name='generate')
@click.option('--user-id', type=int, prompt='Enter user ID')
@click.option('--email', prompt='Enter user email')
@click.option('--access-expiry', type=int, default=15, help='Access token expiry in minutes (default: 15)')
@click.option('--refresh-expiry', type=int, default=7, help='Refresh token expiry in days (default: 7)')
def jwt_generate(user_id, email, access_expiry, refresh_expiry):
    """Generate JWT tokens for a user"""
    try:
        tokens = generate_tokens(user_id, email, access_expiry, refresh_expiry)
        
        click.secho("\n" + "="*60, fg='cyan')
        click.secho("JWT TOKENS GENERATED SUCCESSFULLY", fg='green')
        click.secho("="*60 + "\n", fg='cyan')
        
        click.secho("User Information:", fg='yellow')
        click.echo(f"  User ID: {user_id}")
        click.echo(f"  Email: {email}\n")
        
        click.secho("Access Token:", fg='yellow')
        click.echo(f"  Token: {tokens['access_token']}\n")
        click.echo(f"  Expires: {format_token_expiry(tokens['access_token_expiry'])}")
        click.echo(f"  Expires in: {access_expiry} minutes\n")
        
        click.secho("Refresh Token:", fg='yellow')
        click.echo(f"  Token: {tokens['refresh_token']}\n")
        click.echo(f"  Expires: {format_token_expiry(tokens['refresh_token_expiry'])}")
        click.echo(f"  Expires in: {refresh_expiry} days\n")
        
        click.secho("Authorization Header:", fg='yellow')
        click.echo(f"  Authorization: Bearer {tokens['access_token'][:50]}...\n")
        
    except Exception as e:
        click.secho(f"✗ Error generating tokens: {str(e)}", fg='red')


@jwt.command(name='validate')
@click.option('--token', prompt='Enter token to validate', hide_input=False)
def jwt_validate(token):
    """Validate a JWT token and display its payload"""
    try:
        payload = validate_token(token)
        
        click.secho("\n" + "="*60, fg='cyan')
        click.secho("TOKEN VALIDATION SUCCESSFUL", fg='green')
        click.secho("="*60 + "\n", fg='cyan')
        
        click.secho("Token Payload:", fg='yellow')
        click.echo(f"  User ID: {payload.get('user_id')}")
        click.echo(f"  Email: {payload.get('email')}")
        click.echo(f"  Token Type: {payload.get('token_type')}")
        click.echo(f"  Issued At: {format_token_expiry(payload.get('iat'))}")
        click.echo(f"  Expires At: {format_token_expiry(payload.get('exp'))}\n")
        
        # Calculate remaining time
        from datetime import datetime
        exp_time = datetime.utcfromtimestamp(payload.get('exp'))
        now = datetime.utcnow()
        remaining = exp_time - now
        
        if remaining.total_seconds() > 0:
            hours = remaining.total_seconds() // 3600
            minutes = (remaining.total_seconds() % 3600) // 60
            click.secho(f"  Time Remaining: {int(hours)}h {int(minutes)}m\n", fg='green')
        else:
            click.secho(f"  Time Remaining: EXPIRED\n", fg='red')
        
    except TokenExpiredError:
        click.secho("✗ Token has expired", fg='red')
    except TokenInvalidError as e:
        click.secho(f"✗ Invalid token: {str(e)}", fg='red')
    except Exception as e:
        click.secho(f"✗ Error validating token: {str(e)}", fg='red')


@jwt.command(name='refresh')
@click.option('--token', prompt='Enter refresh token', hide_input=False)
def jwt_refresh(token):
    """Generate a new access token from a refresh token"""
    try:
        new_tokens = refresh_access_token(token)
        
        click.secho("\n" + "="*60, fg='cyan')
        click.secho("ACCESS TOKEN REFRESHED SUCCESSFULLY", fg='green')
        click.secho("="*60 + "\n", fg='cyan')
        
        click.secho("New Access Token:", fg='yellow')
        click.echo(f"  Token: {new_tokens['access_token']}\n")
        click.echo(f"  Expires: {format_token_expiry(new_tokens['access_token_expiry'])}\n")
        
        click.secho("Authorization Header:", fg='yellow')
        click.echo(f"  Authorization: Bearer {new_tokens['access_token'][:50]}...\n")
        
    except TokenExpiredError:
        click.secho("✗ Refresh token has expired. Please login again.", fg='red')
    except TokenInvalidError as e:
        click.secho(f"✗ Invalid refresh token: {str(e)}", fg='red')
    except Exception as e:
        click.secho(f"✗ Error refreshing token: {str(e)}", fg='red')


if __name__ == '__main__':
    cli()
