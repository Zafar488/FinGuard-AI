from database.database import engine, Base, SessionLocal
from database.models import Customer, TransactionRecord 
from datetime import datetime, timezone

print("Creating database tables...")
Base.metadata.create_all(bind=engine)

def seed_customers():
    db = SessionLocal()
    
    # Check if we already have customers
    if db.query(Customer).first():
        print("✅ Database already has customers. Skipping seed.")
        db.close()
        return

    # Add dummy customers for our testing scenarios
    customers = [
        Customer(
            customer_id="CUST-NORMAL-001",
            name="Ali Ahmed",
            account_status="VIP",
            country_of_origin="Pakistan",
            avg_monthly_spend=2500.00,
            created_at=datetime(2019, 5, 1, tzinfo=timezone.utc)  # <-- CHANGED HERE
        ),
        Customer(
            customer_id="CUST-FRAUD-999",
            name="Suspicious User",
            account_status="NEW",
            country_of_origin="Unknown",
            avg_monthly_spend=50.00,
            created_at=datetime(2026, 7, 1, tzinfo=timezone.utc)  # <-- CHANGED HERE
        )
    ]
    
    db.add_all(customers)
    db.commit()
    print("✅ Seeded database with dummy customers!")
    db.close()

if __name__ == "__main__":
    seed_customers()