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
        
def query_gemini(query):
    client = genai.Client()

    interaction = client.interactions.create(
        model = "gemini-3.1-flash-lite",
        input = query,
        tools=[{"type": "google_search"}]
    )

    response_json = interaction.output_text
    return response_json.loads(response_json)

def fetch_job_details(job_url):

    # search_results = DDGS().text(job_url, max_results=1)

    # if len(search_results) < 1:
    #     return "unknown", "unknown"

    # result_headline = search_results[0]["title"]
    # result_body = search_results[0]["body"]

    query = f"""Extract the hiring company and the job title from the search results for this url
                
                url: {job_url}.

                Return strictly a JSON object in this format: {{"company": "company-name", "job_title": "job-title"}}. Output raw JSON only. Do not include markdown formatting, backticks, or any additional text."""

    response = query_gemini(query)
    
    company = response['company']
    job_title = response['job_title']
    
    return job_title, company

def fetch_job_url(job_title, company):

    allowlist_string = " OR site:".join(allowlist)

    search_string = f'''"{job_title}" "{company}" (site:{allowlist_string})'''

    company, job_title = company.lower(), job_title.lower()

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
    json_response = json.loads(data)

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

        if (company_match_score_url > 50 or company_match_score_headline > 50) and title_match_score_headline > 50:
            return link

    return ""