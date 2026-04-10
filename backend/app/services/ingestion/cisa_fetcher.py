import requests


def fetch_kev():
    """
    Fetch CISA's Known Exploited Vulnerabilities catalog.
    
    Unlike the NVD which lists ALL vulnerabilities, this catalog 
    only lists ones that are confirmed to be actively exploited 
    by attackers. If a CVE is on this list, it's urgent.
    """
    
    url = "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
    
    print("Fetching CISA Known Exploited Vulnerabilities...")
    
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Error: Got status code {response.status_code}")
        return []
    
    data = response.json()
    
    # Get the 10 most recently added vulnerabilities
    vulnerabilities = data.get("vulnerabilities", [])
    recent = vulnerabilities[-10:]  # Last 10 entries are the newest
    
    kevs = []
    for vuln in recent:
        kevs.append({
            "id": vuln.get("cveID"),
            "name": vuln.get("vulnerabilityName"),
            "vendor": vuln.get("vendorProject"),
            "product": vuln.get("product"),
            "description": vuln.get("shortDescription"),
            "date_added": vuln.get("dateAdded"),
            "due_date": vuln.get("dueDate"),
            "source": "CISA KEV"
        })
    
    return kevs


if __name__ == "__main__":
    kevs = fetch_kev()
    
    print(f"\nFound {len(kevs)} recently added KEVs:\n")
    print("-" * 80)
    
    for kev in kevs:
        print(f"ID:       {kev['id']}")
        print(f"Name:     {kev['name']}")
        print(f"Vendor:   {kev['vendor']} - {kev['product']}")
        print(f"Added:    {kev['date_added']}")
        print(f"Fix by:   {kev['due_date']}")
        print(f"Description: {kev['description'][:200]}")
        print("-" * 80)