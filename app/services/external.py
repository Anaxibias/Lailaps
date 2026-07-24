from urllib.parse import urlparse
import json
from ddgs import DDGS
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
    return json.loads(response_json)

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

def fetch_job_url(title, company):

    search_string = title + "@" + company + " jobs"

    search_results = DDGS().text(search_string, max_results=5)
    for result in search_results:
        result_headline = result["title"]
        result_url = result["href"]

        is_blocked = check_blocklist(result_url)
        if is_blocked:
            continue

        
        company_match_score_url = fuzz.partial_ratio(company, result_url)
        company_match_score_headline = fuzz.partial_ratio(company, result_headline)
        title_match_score_headline = fuzz.token_set_ratio(title, result_headline)

        if (company_match_score_url > 50 or company_match_score_headline > 50) and title_match_score_headline > 50:
            return result_url

    return ""