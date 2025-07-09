# scrape_site.py
import asyncio, os
from crawl4ai import AsyncWebCrawler

TARGET_URL = os.getenv("SCRAPE_URL", "https://www.globalnestsolutions.com")

async def scrape(url: str = TARGET_URL) -> str:
    async with AsyncWebCrawler() as crawler:       # Crawl4AI quick-start pattern
        result = await crawler.arun(
            url=url,
            deep_crawl="bfs",  # breadth-first search
            max_pages=20,  # increase as needed
            max_depth=3,  # increase if needed
            timeout=30
        )
        return result.markdown.raw_markdown        # plain markdown

if __name__ == "__main__":
    md = asyncio.run(scrape())
    print(md[:800], "...")
