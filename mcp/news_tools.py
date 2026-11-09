import json
import os
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2"


def request_news_api(endpoint: str, params: dict) -> dict:
    if not NEWS_API_KEY:
        raise RuntimeError(
            "NEWS_API_KEY is missing. Check your .env file."
        )

    url = f"{BASE_URL}/{endpoint}?{urlencode(params)}"

    request = Request(
        url,
        headers={
            "X-Api-Key": NEWS_API_KEY,
            "User-Agent": "AI-News-Intelligence-Agent/1.0",
        },
    )

    try:
        with urlopen(request, timeout=15) as response:
            data = response.read().decode("utf-8")
            return json.loads(data)

    except HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"News API HTTP {error.code}: {body}"
        )

    except URLError as error:
        raise RuntimeError(
            f"Could not connect to News API: {error.reason}"
        )


def recent_dates(days: int = 7):
    now = datetime.now(timezone.utc)

    from_date = now - timedelta(days=days)

    return (
        from_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        now.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )


def article_matches(article: dict, keyword: str) -> bool:
    """
    Extra relevance check after NewsAPI returns results.
    This prevents unrelated articles from being shown.
    """

    keyword = keyword.lower().strip()

    title = (article.get("title") or "").lower()
    description = (article.get("description") or "").lower()
    content = (article.get("content") or "").lower()

    text = f"{title} {description} {content}"

    if keyword in text:
        return True

    words = [
        word.strip(".,!?()[]{}\"'")
        for word in keyword.split()
        if len(word.strip(".,!?()[]{}\"'")) >= 3
    ]

    if not words:
        return False

    matches = sum(1 for word in words if word in text)

    return matches >= max(1, len(words) // 2)


def sort_latest(articles: list) -> list:
    return sorted(
        articles,
        key=lambda article: article.get("publishedAt", ""),
        reverse=True,
    )


def format_articles(
    data: dict,
    max_articles: int = 5,
    required_keyword: str | None = None,
) -> str:

    if data.get("status") != "ok":
        return (
            "News API error: "
            + data.get("message", "Unknown News API error.")
        )

    articles = data.get("articles", [])

    if not articles:
        return "No matching news articles found."

    if required_keyword:
        filtered = [
            article
            for article in articles
            if article_matches(article, required_keyword)
        ]
    else:
        filtered = articles

    if not filtered:
        return (
            f"No strongly matching recent articles were found "
            f"for '{required_keyword}'."
        )

    filtered = sort_latest(filtered)

    results = []

    for index, article in enumerate(
        filtered[:max_articles],
        start=1,
    ):

        source = (
            article.get("source", {}).get(
                "name",
                "Unknown source",
            )
        )

        title = article.get(
            "title",
            "No title",
        )

        description = (
            article.get("description")
            or "No description available."
        )

        published = article.get(
            "publishedAt",
            "Unknown",
        )

        url = article.get(
            "url",
            "",
        )

        results.append(
            f"""Article {index}
Source: {source}
Title: {title}
Published: {published}
Description: {description}
URL: {url}"""
        )

    return "\n\n".join(results)


def search_news(
    query: str,
    max_articles: int = 5,
) -> str:

    if not query.strip():
        return "Please provide a topic to search."

    from_date, to_date = recent_dates(7)

    data = request_news_api(
        "everything",
        {
            "q": query.strip(),
            "searchIn": "title,description,content",
            "language": "en",
            "from": from_date,
            "to": to_date,
            "sortBy": "relevancy",
            "pageSize": 20,
        },
    )

    return format_articles(
        data,
        max_articles,
        required_keyword=query.strip(),
    )


def get_company_news(
    company: str,
    max_articles: int = 5,
) -> str:

    if not company.strip():
        return "Please provide a company name."

    company_name = company.strip()

    from_date, to_date = recent_dates(14)

    # Exact phrase + relevance sorting.
    search_query = f'"{company_name}"'

    data = request_news_api(
        "everything",
        {
            "q": search_query,
            "searchIn": "title,description,content",
            "language": "en",
            "from": from_date,
            "to": to_date,
            "sortBy": "relevancy",
            "pageSize": 20,
        },
    )

    return format_articles(
        data,
        max_articles,
        required_keyword=company_name,
    )


def get_top_headlines(
    topic: str = "",
    max_articles: int = 5,
) -> str:

    params = {
        "country": "in",
        "pageSize": 20,
    }

    if topic.strip():
        params["q"] = topic.strip()

    data = request_news_api(
        "top-headlines",
        params,
    )

    
    return format_articles(
        data,
        max_articles,
        required_keyword=None,
    )
    
    
    


    
    