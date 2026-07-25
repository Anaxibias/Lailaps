from urllib.parse import urlparse
import os
import http.client
import json
from dotenv import load_dotenv
from rapidfuzz import fuzz
from google import genai

blocklist = [
    "indeed.com",
    "glassdoor.com",
    "linkedin.com",
    "ziprecruiter.com",
    "monster.com",
    "wellfound.com",
    "otta.com",
    "dice.com",
    "builtin.com",
    "workatastartup.com",
    "simplyhired.com",
]

allowlist = [
    "greenhouse.io", 
    "lever.co", 
    "ashbyhq.com", 
    "workable.com", 
    "bamboohr.com", 
    "myworkdayjobs.com", 
    "smartrecruiters.com", 
    "icims.com"
]

load_dotenv()
SERPERDEV_API_KEY = os.environ.get('SERPERDEV_API_KEY')

def check_blocklist(job_url):
    netloc = urlparse(job_url.strip()).netloc
    for blocked_domain in blocklist:
        if blocked_domain == netloc or netloc.endswith("." + blocked_domain):
            return True

    return False
        
def query_gemini(query, output_type):
    client = genai.Client()

    interaction = client.interactions.create(
        model = "gemini-3.1-flash-lite",
        input = query,
        tools=[{"type": "google_search"}]
    )

    response = interaction.output_text

    if output_type == "json":
        return json.loads(response)
    else:
        return response

def call_serper(search_string):

    conn = http.client.HTTPSConnection("google.serper.dev")
    payload = json.dumps({
        "q": search_string,
        "autocorrect": False,
    })
    headers = {
        'X-API-KEY': SERPERDEV_API_KEY,
        'Content-Type': 'application/json'
    }
    conn.request("POST", "/search", payload, headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    conn.close()
    return json.loads(data)

def fetch_job_details(job_url):

    # search_results = DDGS().text(job_url, max_results=1)

    # if len(search_results) < 1:
    #     return "unknown", "unknown"

    # result_headline = search_results[0]["title"]
    # result_body = search_results[0]["body"]

    query = f'''Convert this messy job URL into a highly targeted Google Search query designed to find the original, canonical job posting.

                URL: {job_url}
                Requirements:

                    Extract the likely company name from the subdomain (e.g., 'acme' in acme.greenhouse.io) or the path.
                    Extract the slugified job title and replace hyphens/underscores with spaces.
                    Extract any unique requisition IDs or job numbers.
                    Discard all tracking parameters (e.g., utm_source, gh_src, session_id).
                    Format the output using Google Search operators where appropriate. For example, use quotes around the company name and title, or include the ATS domain.
                    Do not include the original tracking URL in the query.
                    Do not attempt to access the url.
    
                Return ONLY the raw search query string. Do not include markdown formatting, JSON, or any conversational text.'''

    search_string = query_gemini(query, "string")
    json_response = call_serper(search_string)

    for obj in json_response.get("organic", []):
        headline = obj["title"]
        snippet = obj["snippet"]
        if obj["position"] == 1:
            break

    query = f'''Extract the hiring company and the job title from this search result headline and description snippet:


                headline: {headline}
                snippet: {snippet}

                Return strictly a JSON object in this format {{"company": "company-name", "job_title": "job-title"}}'''

    response = query_gemini(query, "json")
    
    company = response.get('company') or ''
    job_title = response.get('job_title') or ''
    
    return job_title, company

def fetch_job_url(job_title, company):

    allowlist_string = " OR site:".join(allowlist)

    search_string = f'''"{job_title}" "{company}" (site:{allowlist_string})'''

    company = company.lower()
    job_title = job_title.lower()

    json_response = call_serper(search_string)

    for obj in json_response.get("organic", []):
        title = obj["title"]
        link = obj["link"]
        #snippet = ["organic"]["snippet"]
        url_netloc = urlparse(link.strip()).netloc

        url_match = False
        for allowed in allowlist:
            if url_netloc.endswith(allowed):
                url_match = True
                break
            
        if not url_match:
            continue

        title = title.lower()

        company_match_score_url = fuzz.partial_ratio(company, link.lower())
        company_match_score_headline = fuzz.partial_ratio(company, title)
        title_match_score_headline = fuzz.token_set_ratio(job_title, title)

        if (company_match_score_url > 40 or company_match_score_headline > 50) and title_match_score_headline > 50:
            return link

    search_string = f'''"{job_title}" "{company}" "jobs"'''

    json_response = call_serper(search_string)

    for obj in json_response.get("organic", []):
        title = obj["title"].lower()
        link = obj["link"]

        company_match_score_url = fuzz.partial_ratio(company, link.lower())
        company_match_score_headline = fuzz.partial_ratio(company, title)
        title_match_score_headline = fuzz.token_set_ratio(job_title, title)

        if (company_match_score_headline > 60 or company_match_score_url > 60) and title_match_score_headline > 60:

            return link

    return ""
