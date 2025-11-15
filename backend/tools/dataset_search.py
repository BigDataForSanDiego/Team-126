"""
Local dataset search functionality
"""

import json
import os
import math
from typing import List, Dict, Optional

# Path to datasets directory
DATASETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'datasets')


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two coordinates using Haversine formula
    Returns distance in miles
    """
    R = 3959  # Earth's radius in miles

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

    return R * c


def search_local_datasets(query: str, latitude: Optional[float] = None, longitude: Optional[float] = None, max_results: int = 5) -> List[Dict]:
    """
    Search local JSON datasets for resources

    Args:
        query: Search query (e.g., "healthcare", "shelter", "food")
        latitude: User's latitude for distance sorting
        longitude: User's longitude for distance sorting
        max_results: Maximum number of results to return

    Returns:
        List of matching resources sorted by distance
    """
    query_lower = query.lower()
    results = []

    # Determine which datasets to search based on query
    datasets_to_search = []

    if any(keyword in query_lower for keyword in ['health', 'medical', 'clinic', 'doctor', 'hospital', 'mental']):
        datasets_to_search.append('healthcare_resources.json')

    if any(keyword in query_lower for keyword in ['shelter', 'housing', 'sleep', 'bed', 'emergency shelter']):
        datasets_to_search.append('shelters.json')

    if any(keyword in query_lower for keyword in ['food', 'meal', 'hungry', 'eat', 'pantry', 'kitchen']):
        datasets_to_search.append('food_banks.json')

    # If no specific category found, search all datasets
    if not datasets_to_search:
        datasets_to_search = ['healthcare_resources.json', 'shelters.json', 'food_banks.json']

    print(f"[Dataset Search] Query: '{query}'")
    print(f"[Dataset Search] Searching datasets: {datasets_to_search}")

    # Search each relevant dataset
    for dataset_file in datasets_to_search:
        dataset_path = os.path.join(DATASETS_DIR, dataset_file)

        if not os.path.exists(dataset_path):
            print(f"[Dataset Search] Warning: {dataset_file} not found")
            continue

        try:
            with open(dataset_path, 'r') as f:
                data = json.load(f)

            for resource in data:
                # Calculate distance if coordinates provided
                distance = None
                if latitude is not None and longitude is not None and 'coordinates' in resource:
                    distance = calculate_distance(
                        latitude, longitude,
                        resource['coordinates']['latitude'],
                        resource['coordinates']['longitude']
                    )
                    resource['distance_miles'] = round(distance, 2)

                results.append(resource)

        except Exception as e:
            print(f"[Dataset Search] Error reading {dataset_file}: {str(e)}")

    # Sort by distance if coordinates provided
    if latitude is not None and longitude is not None:
        results.sort(key=lambda x: x.get('distance_miles', float('inf')))

    print(f"[Dataset Search] Found {len(results)} results")

    return results[:max_results]


def format_results_for_llm(results: List[Dict]) -> str:
    """
    Format search results for the LLM to read
    """
    if not results:
        return "No results found in local database."

    formatted = "Found the following resources in our local database:\n\n"

    for idx, resource in enumerate(results, 1):
        formatted += f"{idx}. **{resource['name']}**\n"
        formatted += f"   Type: {resource.get('category', resource.get('type', 'N/A'))}\n"
        formatted += f"   Address: {resource.get('address', 'N/A')}\n"
        formatted += f"   Phone: {resource.get('phone', 'N/A')}\n"
        formatted += f"   Hours: {resource.get('hours', 'N/A')}\n"

        if 'distance_miles' in resource:
            formatted += f"   Distance: {resource['distance_miles']} miles from you\n"

        if 'services' in resource:
            formatted += f"   Services: {', '.join(resource['services'])}\n"

        if 'requirements' in resource:
            formatted += f"   Requirements: {resource['requirements']}\n"

        if 'description' in resource:
            formatted += f"   Description: {resource['description']}\n"

        formatted += "\n"

    return formatted
