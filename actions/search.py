import logging
import asyncio
from typing import List, Optional
from dataclasses import dataclass
try:
    from ddgs import DDGS          # new package name
except ImportError:
    try:
        from duckduckgo_search import DDGS  # legacy fallback
    except ImportError:
        DDGS = None
import requests
from deep_translator import GoogleTranslator

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    title: str
    snippet: str
    url: str
    source: str

class WebSearch:
    def __init__(self, news_api_key: Optional[str] = None):
        self.news_api_key = news_api_key
        self.ddgs = DDGS() if DDGS is not None else None

    def translate_text(self, text: str, target_lang: str) -> str:
        if target_lang.lower() in ('en', 'english'):
            return text
        try:
            return GoogleTranslator(source='auto', target=target_lang).translate(text)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return text

    def search(self, query: str, mode: str = 'general', language: str = 'en') -> List[SearchResult]:
        logger.info(f"Searching for '{query}' in mode '{mode}' with language '{language}'")
        results = []
        try:
            if self.ddgs is None:
                return [SearchResult(title='Search unavailable', snippet='Install ddgs: pip install ddgs', url='', source='error')]
            if mode == 'news':
                results = self._search_news(query)
            else:
                # General, research, price, compare mostly use regular web search
                raw_results = self.ddgs.text(query, max_results=10)
                for r in raw_results:
                    results.append(SearchResult(
                        title=r.get('title', ''),
                        snippet=r.get('body', ''),
                        url=r.get('href', ''),
                        source='DuckDuckGo'
                    ))
        except Exception as e:
            logger.error(f"Search failed: {e}")
        
        return self.format_results(results, language)

    def _search_news(self, query: str) -> List[SearchResult]:
        results = []
        try:
            raw_ddg = self.ddgs.news(query, max_results=5)
            for r in raw_ddg:
                results.append(SearchResult(
                    title=r.get('title', ''),
                    snippet=r.get('body', ''),
                    url=r.get('url', ''),
                    source=r.get('source', 'DuckDuckGo News')
                ))
        except Exception as e:
            logger.error(f"DDG News search failed: {e}")
            
        if self.news_api_key:
            try:
                url = f"https://newsapi.org/v2/everything?q={query}&apiKey={self.news_api_key}&pageSize=5"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    articles = response.json().get('articles', [])
                    for a in articles:
                        results.append(SearchResult(
                            title=a.get('title', ''),
                            snippet=a.get('description', ''),
                            url=a.get('url', ''),
                            source=a.get('source', {}).get('name', 'NewsAPI')
                        ))
            except Exception as e:
                logger.error(f"NewsAPI search failed: {e}")
                
        return results

    def format_results(self, results: List[SearchResult], language: str) -> List[SearchResult]:
        formatted = []
        for r in results:
            title = self.translate_text(r.title, language) if r.title else ''
            snippet = self.translate_text(r.snippet, language) if r.snippet else ''
            formatted.append(SearchResult(title=title, snippet=snippet, url=r.url, source=r.source))
        return formatted
