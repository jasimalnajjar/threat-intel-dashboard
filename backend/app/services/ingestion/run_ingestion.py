from backend.app.models import Threat, get_session
from backend.app.services.ingestion.nvd_fetcher import fetch_recent_cves
from backend.app.services.ingestion.cisa_fetcher import fetch_kev


def store_threats(threats, source):
    """
    Takes a list of threat dictionaries and saves them to the database.
    If a threat with the same ID already exists, it skips it (no duplicates).
    """
    session = get_session()
    added = 0

    for threat in threats:
        # Check if this CVE is already in the database
        exists = session.query(Threat).filter_by(id=threat["id"]).first()
        if exists:
            continue

        new_threat = Threat(
            id=threat["id"],
            source=source,
            description=threat.get("description", ""),
            severity=threat.get("severity", "Unknown"),
            score=threat.get("score"),
            published=threat.get("published", ""),
            vendor=threat.get("vendor"),
            product=threat.get("product"),
            date_added=threat.get("date_added"),
        )
        session.add(new_threat)
        added += 1

    session.commit()
    session.close()
    print(f"  Added {added} new threats from {source}")


def run_ingestion():
    """Fetch from all sources and store everything."""

    print("Starting ingestion...\n")

    # Fetch and store NVD data
    print("1. Fetching NVD CVEs...")
    cves = fetch_recent_cves()
    store_threats(cves, source="NVD")

    # Fetch and store CISA KEV data
    print("\n2. Fetching CISA KEVs...")
    kevs = fetch_kev()
    store_threats(kevs, source="CISA KEV")

    # Show what's in the database now
    session = get_session()
    total = session.query(Threat).count()
    session.close()
    print(f"\nDone! Total threats in database: {total}")


if __name__ == "__main__":
    run_ingestion()