from app.config.database import SessionLocal


# Helper function to get database session
def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        print("Session Closed!")
