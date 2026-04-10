from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from backend.app.models import Threat, get_session
from backend.app.services.ai.analyzer import analyze_threats

app = FastAPI(
    title="Threat Intelligence Dashboard API",
    description="API for aggregating and analyzing cyber threat data",
    version="1.0.0"
)

# Allow the frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    """Health check — just confirms the API is running."""
    return {"status": "online", "message": "Threat Intel Dashboard API"}


@app.get("/threats")
def get_threats(
    source: str = Query(None, description="Filter by source: NVD or CISA KEV"),
    severity: str = Query(None, description="Filter by severity: CRITICAL, HIGH, MEDIUM, LOW"),
    limit: int = Query(20, description="Number of results to return"),
):
    """
    Get threats from the database with optional filters.
    This is what the dashboard will call to populate the threat list.
    """
    session = get_session()
    query = session.query(Threat)

    if source:
        query = query.filter(Threat.source == source)
    if severity:
        query = query.filter(Threat.severity == severity.upper())

    threats = query.limit(limit).all()
    session.close()

    return [
        {
            "id": t.id,
            "source": t.source,
            "description": t.description,
            "severity": t.severity,
            "score": t.score,
            "published": t.published,
            "vendor": t.vendor,
            "product": t.product,
        }
        for t in threats
    ]


@app.get("/threats/stats")
def get_stats():
    """
    Get summary statistics for the dashboard cards.
    Things like total threats, breakdown by severity, etc.
    """
    session = get_session()

    total = session.query(Threat).count()

    severity_counts = {}
    for level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = session.query(Threat).filter(Threat.severity == level).count()
        if count > 0:
            severity_counts[level] = count

    source_counts = {}
    for source in ["NVD", "CISA KEV"]:
        count = session.query(Threat).filter(Threat.source == source).count()
        if count > 0:
            source_counts[source] = count

    session.close()

    return {
        "total_threats": total,
        "by_severity": severity_counts,
        "by_source": source_counts,
    }


@app.get("/analyze")
def run_analysis(limit: int = Query(5, description="Number of threats to analyze")):
    """
    Send threats to Claude for AI analysis.
    Returns a structured security briefing.
    """
    session = get_session()
    threats = session.query(Threat).limit(limit).all()
    session.close()

    threat_list = [
        {
            "id": t.id,
            "source": t.source,
            "description": t.description,
            "severity": t.severity,
            "score": t.score,
        }
        for t in threats
    ]

    analysis = analyze_threats(threat_list)
    return analysis