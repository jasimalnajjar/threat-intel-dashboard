import anthropic
import json
import os
from dotenv import load_dotenv

# Load the API key from .env file
load_dotenv()


def analyze_threats(threats):
    """
    Send a batch of threats to Claude and get back a structured analysis
    including summaries, categories, and risk assessment.
    """
    
    client = anthropic.Anthropic()
    
    # Build a prompt with the threat data
    threat_text = ""
    for t in threats:
        threat_text += f"""
CVE ID: {t['id']}
Source: {t['source']}
Severity: {t['severity']} (Score: {t['score']})
Description: {t['description'][:300]}
---
"""
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a cybersecurity analyst. Analyze these vulnerabilities and return a JSON response with this exact structure:

{{
    "summary": "A 2-3 sentence overview of the current threat landscape based on these vulnerabilities",
    "threats": [
        {{
            "id": "CVE-XXXX-XXXXX",
            "category": "one of: Remote Code Execution, Privilege Escalation, Data Exposure, Denial of Service, Authentication Bypass, Injection, Other",
            "risk_level": "CRITICAL, HIGH, MEDIUM, or LOW",
            "plain_summary": "A one-sentence explanation a non-technical person could understand",
            "action": "A one-sentence recommended action"
        }}
    ],
    "top_priority": "The CVE ID that should be addressed first and why in one sentence"
}}

Here are the vulnerabilities to analyze:

{threat_text}

Return ONLY valid JSON, no other text."""
            }
        ]
    )
    
    # Parse the JSON response
    response_text = message.content[0].text
    
    try:
        analysis = json.loads(response_text)
    except json.JSONDecodeError:
        # Sometimes the response has markdown code blocks around it
        cleaned = response_text.strip().strip("```json").strip("```").strip()
        analysis = json.loads(cleaned)
    
    return analysis


if __name__ == "__main__":
    # Pull threats from the database and analyze them
    from backend.app.models import Threat, get_session
    
    session = get_session()
    threats = session.query(Threat).limit(5).all()
    session.close()
    
    # Convert database objects to dictionaries
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
    
    print("Sending threats to Claude for analysis...\n")
    analysis = analyze_threats(threat_list)
    
    print("=== THREAT LANDSCAPE SUMMARY ===")
    print(analysis["summary"])
    print()
    
    print("=== INDIVIDUAL THREAT ANALYSIS ===")
    for t in analysis["threats"]:
        print(f"\n{t['id']}")
        print(f"  Category:    {t['category']}")
        print(f"  Risk Level:  {t['risk_level']}")
        print(f"  Summary:     {t['plain_summary']}")
        print(f"  Action:      {t['action']}")
    
    print(f"\n=== TOP PRIORITY ===")
    print(analysis["top_priority"])