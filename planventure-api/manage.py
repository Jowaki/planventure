"""
Database and application management CLI.

Usage:
    python manage.py db init       - Initialize database (create all tables)
    python manage.py db drop       - Drop all tables
    python manage.py db reset      - Drop and recreate all tables
    python manage.py db seed       - Seed database with sample data
    python manage.py shell         - Start Flask shell
"""
import click
from datetime import datetime, timedelta
from app import create_app, db
from models import User, Trip


app = create_app()


@click.group()
def cli():
    """Database and application management commands"""
    pass


@cli.group()
def db():
    """Database management commands"""
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
        local_vars = {'app': app, 'db': db, 'User': User, 'Trip': Trip}
        
        click.echo("Starting interactive Flask shell...")
        click.echo("Available objects: app, db, User, Trip")
        click.echo("Type 'exit()' or press Ctrl+D to exit\n")
        
        code.InteractiveConsole(
            local_vars,
            filename="<console>"
        ).interact(banner="")


if __name__ == '__main__':
    cli()
