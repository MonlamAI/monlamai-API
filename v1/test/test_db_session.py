import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from sqlalchemy import create_engine,Column,Integer,String
import os

# Load environment variables
load_dotenv()

# Database URL for testing (use a test database or an in-memory database)
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite:///:memory:")

# Create the engine and sessionmaker for testing
engine = create_engine(TEST_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Example model
class ExampleModel(Base):
    __tablename__ = "example"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

# Create a test fixture for the database session
@pytest.fixture(scope="module")
def db_session() -> Session:
    # Create all tables
    Base.metadata.create_all(bind=engine)
    # Create a new session
    session = SessionLocal()
    try:
        yield session
    finally:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        session.close()

# Example test case
def test_example_model(db_session: Session):
    # Create a new instance of ExampleModel
    example = ExampleModel(name="Test Name")
    db_session.add(example)
    db_session.commit()
    
    # Query the database
    result = db_session.query(ExampleModel).filter_by(name="Test Name").first()
    
    # Assertions
    assert result is not None
    assert result.name == "Test Name"
