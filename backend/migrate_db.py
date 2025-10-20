"""
Database migration script
Creates all tables and initial data
"""
import asyncio
import sys
from pathlib import Path

# Add the backend directory to the path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.ext.asyncio import create_async_engine
from app.models import Base
from app.database import engine, init_db
from app.auth.password import hash_password
from app.models import User, UserStats
from app.database import AsyncSessionLocal
from datetime import datetime


async def create_tables():
    """Create all database tables"""
    print("Creating database tables...")

    # Ensure database file and directory exist for SQLite
    from app.config import settings
    if "sqlite" in settings.DATABASE_URL:
        # Extract database path
        db_path = settings.DATABASE_URL.replace("sqlite+aiosqlite:///", "")
        db_file = Path(db_path)

        # Create parent directory if needed
        if db_file.parent != Path(".") and not db_file.parent.exists():
            db_file.parent.mkdir(parents=True, exist_ok=True)
            print(f"[OK] Created directory: {db_file.parent}")

        # Create empty database file if it doesn't exist
        if not db_file.exists():
            db_file.touch()
            print(f"[OK] Created database file: {db_file.absolute()}")
        else:
            print(f"[OK] Using existing database file: {db_file.absolute()}")

    async with engine.begin() as conn:
        # Drop all tables first (for fresh start)
        await conn.run_sync(Base.metadata.drop_all)
        print("[OK] Dropped existing tables")

        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        print("[OK] Created all tables")


async def create_admin_user():
    """Create default admin user"""
    print("\nCreating admin user...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Check if admin user already exists
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.username == "admin")
            )
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                print("[OK] Admin user already exists")
                return
            
            # Create admin user
            admin_password = hash_password("admin123")
            admin_user = User(
                username="admin",
                password_hash=admin_password,
                email="admin@tictactoe.com",
                is_admin=True,
                created_at=datetime.utcnow()
            )
            session.add(admin_user)
            await session.flush()
            
            # Create stats for admin user
            admin_stats = UserStats(
                user_id=admin_user.id,
                total_games=0,
                wins=0,
                losses=0,
                draws=0,
                games_abandoned=0,
                games_vs_bot=0,
                win_streak=0,
                best_win_streak=0,
                ranking_points=1000
            )
            session.add(admin_stats)
            
            await session.commit()
            print(f"[OK] Admin user created successfully")
            print(f"  Username: admin")
            print(f"  Password: admin123")
            print(f"  Email: admin@tictactoe.com")
            
        except Exception as e:
            await session.rollback()
            print(f"[ERROR] Error creating admin user: {e}")
            raise


async def create_test_users():
    """Create test users for development"""
    print("\nCreating test users...")
    
    test_users_data = [
        {"username": "player1", "email": "player1@test.com", "password": "test123"},
        {"username": "player2", "email": "player2@test.com", "password": "test123"},
        {"username": "testuser", "email": "test@test.com", "password": "test123"},
    ]
    
    async with AsyncSessionLocal() as session:
        try:
            from sqlalchemy import select
            
            for user_data in test_users_data:
                # Check if user already exists
                result = await session.execute(
                    select(User).where(User.username == user_data["username"])
                )
                existing_user = result.scalar_one_or_none()
                
                if existing_user:
                    print(f"  - User '{user_data['username']}' already exists")
                    continue
                
                # Create user
                password_hash = hash_password(user_data["password"])
                user = User(
                    username=user_data["username"],
                    password_hash=password_hash,
                    email=user_data["email"],
                    is_admin=False,
                    created_at=datetime.utcnow()
                )
                session.add(user)
                await session.flush()
                
                # Create stats for user
                user_stats = UserStats(
                    user_id=user.id,
                    total_games=0,
                    wins=0,
                    losses=0,
                    draws=0,
                    games_abandoned=0,
                    games_vs_bot=0,
                    win_streak=0,
                    best_win_streak=0,
                    ranking_points=1000
                )
                session.add(user_stats)
                
                print(f"  [OK] Created user: {user_data['username']} (password: {user_data['password']})")
            
            await session.commit()
            print("[OK] Test users created successfully")
            
        except Exception as e:
            await session.rollback()
            print(f"[ERROR] Error creating test users: {e}")
            raise


async def main():
    """Main migration function"""
    print("=" * 60)
    print("DATABASE MIGRATION")
    print("=" * 60)
    
    try:
        # Check database connection
        from app.config import settings
        print(f"\nDatabase URL: {settings.DATABASE_URL}")
        
        # Create tables
        await create_tables()
        
        print("\n" + "=" * 60)
        print("[OK] MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\nDatabase created with empty tables.")
        print("You can now start the application with:")
        print("  python run.py")
        print("\nRegister new users through the application interface.")
        
    except Exception as e:
        print(f"\n[ERROR] Migration failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

