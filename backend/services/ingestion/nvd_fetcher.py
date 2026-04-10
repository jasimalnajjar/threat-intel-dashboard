import requests
from datetime import datetime, timedelta


def fetch_recent_cves(days_back=7):
    """
    Fetch recent CVEs from the National Vulnerability Database.
    
    The NVD is a free, public API run by NIST (the National Institute 
    of Standards and Technology). It contains every publicly disclosed 
    vulnerability, each with a unique CVE ID like 'CVE-2024-12345'.
    """
    
    # Calculate the date range — we want the last 7 days of CVEs
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    
    # Format dates the way the NVD API expects them
    date_format = "%Y-%m-%dT%H:%M:%S.000"
    
    # Build the API URL with our parameters
    base_url = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    params = {
        "pubStartDate": start_date.strftime(date_format),
        "pubEndDate": end_date.strftime(date_format),
        "resultsPerPage": 10  # Start small — just 10 results
    }
    
    print(f"Fetching CVEs from the last {days_back} days...")
    print(f"URL: {base_url}")
    
    # Make the API request — this is where we actually call the NVD
    response = requests.get(base_url, params=params)
    
    # Check if the request was successful (status code 200 = OK)
    if response.status_code != 200:
        print(f"Error: Got status code {response.status_code}")
        return []
    
    # Parse the JSON response into a Python dictionary
    data = response.json()
    
    # Extract just the parts we care about from each CVE
    cves = []
    for item in data.get("vulnerabilities", []):
        cve_data = item.get("cve", {})
        
        # Get the description (it's nested in a list)
        descriptions = cve_data.get("descriptions", [])
        description = "No description available"
        for desc in descriptions:
            if desc.get("lang") == "en":
                description = desc.get("value", description)
                break
        
        # Get the severity score if available
        metrics = cve_data.get("metrics", {})
        severity = "Unknown"
        score = None
        
        # Try CVSS v3.1 first, then v3.0
        for version in ["cvssMetricV31", "cvssMetricV30"]:
            if version in metrics:
                cvss = metrics[version][0].get("cvssData", {})
                severity = cvss.get("baseSeverity", "Unknown")
                score = cvss.get("baseScore", None)
                break
        
        cves.append({
            "id": cve_data.get("id"),
            "description": description,
            "severity": severity,
            "score": score,
            "published": cve_data.get("published"),
        })
    
    return cves


# This block only runs when you execute this file directly
if __name__ == "__main__":
    cves = fetch_recent_cves()
    
    print(f"\nFound {len(cves)} CVEs:\n")
    print("-" * 80)
    
    for cve in cves:
        print(f"ID:       {cve['id']}")
        print(f"Severity: {cve['severity']} (Score: {cve['score']})")
        print(f"Published: {cve['published']}")
        print(f"Description: {cve['description'][:200]}...")
        print("-" * 80)