"""
Tool for finding safe places to sleep for unsheltered individuals
"""

from vertexai.generative_models import FunctionDeclaration
import requests
from typing import Dict, Optional, List
from datetime import datetime

# Define find safe places to sleep function
find_safe_sleep_func = FunctionDeclaration(
    name="find_safe_places_to_sleep",
    description="Find safe places to sleep nearby including safe parking programs, 24-hour facilities, well-lit public spaces, and legal overnight options. Prioritizes safety, accessibility, and proximity to transit.",
    parameters={
        "type": "object",
        "properties": {
            "latitude": {
                "type": "number",
                "description": "User's current latitude coordinate"
            },
            "longitude": {
                "type": "number",
                "description": "User's current longitude coordinate"
            },
            "include_type": {
                "type": "string",
                "description": "Type of safe sleep option to prioritize: 'safe_parking', 'facilities_24h', 'parks', 'transit_hubs', or 'all'",
                "enum": ["safe_parking", "facilities_24h", "parks", "transit_hubs", "all"],
                "default": "all"
            },
            "weather_condition": {
                "type": "string",
                "description": "Current weather: 'clear', 'rain', 'heat', 'cold' to get appropriate recommendations",
                "enum": ["clear", "rain", "heat", "cold"],
                "default": "clear"
            },
            "max_distance_miles": {
                "type": "number",
                "description": "Maximum distance in miles to search (default: 3)",
                "default": 3
            }
        },
        "required": ["latitude", "longitude"]
    },
)


def get_location_name(latitude: float, longitude: float) -> Optional[str]:
    """
    Get city/location name from coordinates using Nominatim reverse geocoding

    Args:
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Returns:
        Location string (e.g., "San Diego, CA") or None if failed
    """
    try:
        url = "https://nominatim.openstreetmap.org/reverse"
        params = {
            'lat': latitude,
            'lon': longitude,
            'format': 'json',
            'zoom': 10
        }
        headers = {
            'User-Agent': 'SafeSleepAssistant/1.0'
        }

        response = requests.get(url, params=params, headers=headers, timeout=5)

        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})

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


def search_safe_sleep_options(latitude: float, longitude: float, location_name: str, include_type: str = "all", max_distance_miles: int = 3) -> List[Dict]:
    """
    Search for safe sleep options using DuckDuckGo API

    Args:
        latitude: User latitude
        longitude: User longitude
        location_name: City/location name
        include_type: Type of options to search for
        max_distance_miles: Max distance to search

    Returns:
        List of safe sleep options
    """
    options = []
    search_queries = []

    if include_type in ["all", "safe_parking"]:
        search_queries.append({
            "type": "safe_parking",
            "query": f"safe parking program overnight {location_name}",
            "description": "Safe parking lot for overnight vehicle sleeping"
        })

    if include_type in ["all", "facilities_24h"]:
        search_queries.extend([
            {
                "type": "facilities_24h",
                "query": f"24 hour YMCA gym open overnight {location_name}",
                "description": "24-hour facility offering safe indoor space"
            },
            {
                "type": "facilities_24h",
                "query": f"24 hour laundromat open all night {location_name}",
                "description": "24-hour laundromat with seating areas"
            }
        ])

    if include_type in ["all", "parks"]:
        search_queries.append({
            "type": "parks",
            "query": f"well lit parks safe areas {location_name}",
            "description": "Well-lit public parks with good visibility"
        })

    if include_type in ["all", "transit_hubs"]:
        search_queries.append({
            "type": "transit_hubs",
            "query": f"24 hour bus station train station {location_name}",
            "description": "Transit hub with 24-hour access and seating"
        })

    # Perform searches
    for search_item in search_queries:
        try:
            url = "https://api.duckduckgo.com/"
            params = {
                'q': search_item['query'],
                'format': 'json',
                'no_html': 1,
                'skip_disambig': 1
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)
            data = response.json()

            # Extract result
            if data.get('Abstract'):
                options.append({
                    'type': search_item['type'],
                    'category': search_item['description'],
                    'info': data.get('Abstract', ''),
                    'source_url': data.get('AbstractURL', ''),
                    'heading': data.get('Heading', search_item['type'])
                })

        except Exception as e:
            print(f"Search error for {search_item['type']}: {str(e)}")
            continue

    return options


def get_weather_recommendations(weather_condition: str) -> str:
    """
    Get specific recommendations based on weather

    Args:
        weather_condition: Current weather condition

    Returns:
        Weather-specific advice string
    """
    recommendations = {
        "rain": "⛈️ **Rain Advisory**: Prioritize covered areas - bus stations, under highway overpasses, or indoor 24-hour facilities. Avoid parks and open areas. Keep belongings elevated and dry.",
        "heat": "🌡️ **Heat Advisory**: Seek shade and air-conditioned facilities if possible. Night cooling centers may be available. Stay hydrated - seek water fountains or ask local stores for water.",
        "cold": "❄️ **Cold Advisory**: Prioritize heated indoor facilities or warming centers. Many communities open emergency shelter during cold snaps. Call 211 for warming centers.",
        "clear": "🌙 **Clear Night**: Multiple options available - parks, transit hubs, or parking lots. Focus on well-lit, populated areas for safety."
    }
    return recommendations.get(weather_condition, "Stay safe and seek well-lit, populated areas.")


def find_safe_sleep(latitude: float, longitude: float, include_type: str = "all", weather_condition: str = "clear", max_distance_miles: int = 3) -> Dict:
    """
    Main function to find safe places to sleep

    Args:
        latitude: User latitude
        longitude: User longitude
        include_type: Type of sleep options to search
        weather_condition: Current weather
        max_distance_miles: Max distance to search

    Returns:
        Dictionary with safe sleep options and recommendations
    """
    try:
        location_name = get_location_name(latitude, longitude)
        if not location_name:
            location_name = f"{latitude}, {longitude}"

        current_time = datetime.now().strftime("%I:%M %p")

        options = search_safe_sleep_options(latitude, longitude, location_name, include_type, max_distance_miles)

        result = {
            'location': location_name,
            'latitude': latitude,
            'longitude': longitude,
            'current_time': current_time,
            'search_radius_miles': max_distance_miles,
            'weather_condition': weather_condition,
            'options_found': len(options),
            'options': options,
            'weather_recommendation': get_weather_recommendations(weather_condition),
            'safety_tips': get_safety_tips()
        }

        return result

    except Exception as e:
        print(f"Error finding safe sleep options: {str(e)}")
        return {
            'error': str(e),
            'location': f"{latitude}, {longitude}",
            'recommendation': "Call 211 or local emergency services for immediate shelter assistance"
        }


def get_safety_tips() -> List[str]:
    """
    Get general safety tips for sleeping outdoors

    Returns:
        List of safety recommendations
    """
    return [
        "🔦 Stay in well-lit, populated areas when possible",
        "🤝 Sleep near others or in groups for safety",
        "📱 Keep your phone charged and accessible",
        "🎒 Keep your belongings secure and within reach",
        "⏰ Avoid sleeping in the same spot every night",
        "🚨 Trust your instincts - if a place doesn't feel safe, move",
        "📞 Know local emergency numbers and shelter hotlines",
        "☀️ Be aware of sunrise/early activity to stay safe during vulnerable hours"
    ]


def format_sleep_response(sleep_data: Dict) -> str:
    """
    Format safe sleep data into a readable response

    Args:
        sleep_data: Dictionary from find_safe_sleep

    Returns:
        Formatted string response
    """
    if 'error' in sleep_data:
        response = f"❌ Error: {sleep_data['error']}\n"
        response += f"💡 {sleep_data['recommendation']}\n"
        return response

    response = f"\n🌙 **Safe Places to Sleep Near {sleep_data['location']}**\n"
    response += f"⏰ **Current Time**: {sleep_data['current_time']}\n"
    response += f"📍 **Search Radius**: {sleep_data['search_radius_miles']} miles\n\n"

    response += f"**Weather Condition**: {sleep_data['weather_condition'].upper()}\n"
    response += f"{sleep_data['weather_recommendation']}\n\n"

    if sleep_data['options_found'] > 0:
        response += f"**Found {sleep_data['options_found']} Safe Sleep Options:**\n\n"
        for i, option in enumerate(sleep_data['options'], 1):
            response += f"{i}. **{option['heading']}** ({option['type'].replace('_', ' ').title()})\n"
            response += f"   {option['category']}\n"
            response += f"   ℹ️ {option['info']}\n"
            if option['source_url']:
                response += f"   🔗 [More Info]({option['source_url']})\n"
            response += "\n"
    else:
        response += "⚠️ **No specific options found in search.**\n"
        response += "💡 **Alternatives**: Call 211 for local shelter/safe parking programs\n"

    response += "\n**Safety Tips:**\n"
    for tip in sleep_data['safety_tips']:
        response += f"• {tip}\n"

    return response