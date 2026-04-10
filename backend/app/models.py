from sqlalchemy import create_engine, Column, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# This creates the base class that all our database tables will inherit from
Base = declarative_base()


class Threat(Base):
    """
    Each row in this table represents one threat/vulnerability.
    Think of it like a row in a spreadsheet.
    """
    __tablename__ = "threats"

    # Each column in our "spreadsheet"
    id = Column(String, primary_key=True)          # CVE ID like "CVE-2024-12345"
    source = Column(String)                         # "NVD" or "CISA KEV"
    description = Column(Text)                      # What the vulnerability is
    severity = Column(String)                       # "CRITICAL", "HIGH", etc.
    score = Column(Float, nullable=True)            # CVSS score like 9.8
    published = Column(String)                      # When it was published
    vendor = Column(String, nullable=True)          # Affected vendor
    product = Column(String, nullable=True)         # Affected product
    date_added = Column(String, nullable=True)      # When added to feed
    fetched_at = Column(DateTime, default=datetime.now)  # When we fetched it


# Set up the database connection — this creates a file called threats.db
engine = create_engine("sqlite:///threats.db")

# Create the table if it doesn't exist yet
Base.metadata.create_all(engine)

# Session is how we read/write data — think of it as opening the spreadsheet
Session = sessionmaker(bind=engine)


def get_session():
    return Session()