"""
Search tool for finding resources online and in local datasets
"""

from vertexai.generative_models import FunctionDeclaration
import requests
from typing import List, Dict, Optional
from .dataset_search import search_local_datasets, format_results_for_llm

# Define search function (searches local datasets first, then web)
search_web_func = FunctionDeclaration(
    name="search_web",
    description="Search for resources like shelters, food banks, healthcare services, and other assistance programs. This function FIRST searches our local verified database of resources, then falls back to web search if needed. Use this when you need to find real, current information about resources. If the user's location is known, results will be sorted by distance.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query, e.g., 'food banks' or 'homeless shelters' or 'free healthcare clinics'. Do NOT include location in the query if coordinates are available - they will be automatically added."
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of search results to return (default: 5)",
                "default": 5
            }
        },
        "required": ["query"]
    },
)


def get_location_name(latitude: float, longitude: float) -> Optional[str]:
    """
    Get city/location name from coordinates using Nominatim reverse geocoding

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        Location string (e.g., "Los Angeles, CA") or None if failed
    """
    try:
        # Use Nominatim (OpenStreetMap) reverse geocoding API
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': latitude,
            'lon': longitude,
            'format': 'json',
            'zoom': 10  # City level
        }
        headers = {
            'User-Agent': 'HomelessAssistantApp/1.0'
        }

        response = requests.get(url, params=params, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})

            # Try to get city, state, country
            city = address.get('city') or address.get('town') or address.get('village')
            state = address.get('state')
            country = address.get('country')

            if city and state:
                return f"{city}, {state}"
            elif city and country:
                return f"{city}, {country}"
            elif city:
                return city

        return None
    except Exception as e:
        print(f"Reverse geocoding error: {str(e)}")
        return None


def perform_web_search(query: str, max_results: int = 5, latitude: Optional[float] = None, longitude: Optional[float] = None) -> List[Dict[str, str]]:
    """
    Search for resources - first checks local datasets, then falls back to web search

    Args:
        query: Search query string
        max_results: Maximum number of results to return
        latitude: Optional user latitude for location-based search
        longitude: Optional user longitude for location-based search

    Returns:
        List of search results with title, snippet, and URL
    """
    try:
        # FIRST: Try to find results in local datasets
        print(f"[Search] Searching local datasets for: {query}")
        local_results = search_local_datasets(query, latitude, longitude, max_results)

        if local_results:
            # Format local results for the LLM
            formatted_text = format_results_for_llm(local_results)
            print(f"[Search] Found {len(local_results)} results in local datasets")

            # Also include structured data for the frontend map
            import json
            structured_data = json.dumps({
                'type': 'resource_list',
                'resources': local_results
            })

            return [{
                'title': 'Local Resources Database',
                'snippet': formatted_text + f"\n\n<!-- RESOURCE_DATA:{structured_data} -->",
                'url': 'local://database'
            }]

        # If no local results, fall back to web search
        print("[Search] No local results found, falling back to web search")
        # If location is provided, enhance the query with location
        enhanced_query = query
        if latitude is not None and longitude is not None:
            location_name = get_location_name(latitude, longitude)
            if location_name:
                enhanced_query = f"{query} near {location_name}"
                print(f"[Search] Enhanced query with location: {enhanced_query}")
            else:
                # Fallback: use coordinates directly
                enhanced_query = f"{query} near {latitude},{longitude}"
                print(f"[Search] Using coordinates in query: {enhanced_query}")

        # Use DuckDuckGo's HTML API for better results
        url = "https://html.duckduckgo.com/html/"
        params = {
            'q': enhanced_query
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, params=params, headers=headers, timeout=10)

        if response.status_code == 200:
            # Parse the HTML response to extract results
            # For simplicity, we'll use the Instant Answer API instead
            pass

        # Fallback: Use DuckDuckGo Instant Answer API
        instant_url = "https://api.duckduckgo.com/"
        params = {
            'q': enhanced_query,
            'format': 'json',
            'no_html': 1,
            'skip_disambig': 1
        }

        response = requests.get(instant_url, params=params, timeout=10)
        data = response.json()

        results = []

        # Extract Abstract
        if data.get('Abstract'):
            results.append({
                'title': data.get('Heading', 'Result'),
                'snippet': data.get('Abstract', ''),
                'url': data.get('AbstractURL', '')
            })

        # Extract Related Topics
        for topic in data.get('RelatedTopics', [])[:max_results]:
            if isinstance(topic, dict) and 'Text' in topic:
                results.append({
                    'title': topic.get('Text', '').split(' - ')[0] if ' - ' in topic.get('Text', '') else 'Related',
                    'snippet': topic.get('Text', ''),
                    'url': topic.get('FirstURL', '')
                })

        return results[:max_results] if results else [
            {
                'title': 'Search Info',
                'snippet': f'Search query: {enhanced_query}. For better results, try searching online directly or contact local 211 services.',
                'url': f'https://duckduckgo.com/?q={requests.utils.quote(enhanced_query)}'
            }
        ]

    except Exception as e:
        print(f"Search error: {str(e)}")
        return [
            {
                'title': 'Search Unavailable',
                'snippet': f'Unable to search at this time. Try: Call 211 for local resources, or visit https://www.211.org',
                'url': 'https://www.211.org'
            }
        ]
