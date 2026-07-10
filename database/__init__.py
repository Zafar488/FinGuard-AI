# Exposing key components for cleaner imports across the application
from .database import Base, engine, get_db, SessionLocal
from .models import Customer, TransactionRecord