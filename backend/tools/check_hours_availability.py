"""
Tool for checking resource hours and availability
"""

from vertexai.generative_models import FunctionDeclaration
from datetime import datetime
from typing import Dict, Optional, List
import requests

# Define check hours function
check_hours_func = FunctionDeclaration(
    name="check_hours_availability",
    description="Check if a resource (shelter, food bank, clinic, etc.) is currently open and get its operating hours. Returns current status and full weekly schedule.",
    parameters={
        "type": "object",
        "properties": {
            "resource_name": {
                "type": "string",
                "description": "Name of the resource to check (e.g., 'San Diego Food Bank', 'Father Joe's Villages')"
            },
            "resource_type": {
                "type": "string",
                "description": "Type of resource: 'shelter', 'food_bank', 'healthcare', 'other'",
                "enum": ["shelter", "food_bank", "healthcare", "other"]
            },
            "phone_number": {
                "type": "string",
                "description": "Optional: phone number to call for confirmation (format: XXX-XXX-XXXX)"
            }
        },
        "required": ["resource_name", "resource_type"]
    },
)


def get_current_day_time() -> tuple:
    """
    Get current day of week and time
    
    Returns:
        Tuple of (day_name, time_string, hour_24)
    """
    now = datetime.now()
    day_name = now.strftime("%A")
    time_str = now.strftime("%I:%M %p")
    hour_24 = now.hour
    return day_name, time_str, hour_24


def parse_hours_string(hours_str: str) -> Optional[Dict]:
    """
    Parse hours string like "9:00 AM - 5:00 PM" or "24 hours"
    
    Args:
        hours_str: Hours string from search results
        
    Returns:
        Dict with 'open', 'close' times or 'is_24h' flag, or None if unparseable
    """
    if not hours_str:
        return None
        
    hours_str = hours_str.strip().lower()
    
    # Handle 24-hour facilities
    if "24" in hours_str or "24/7" in hours_str or "always" in hours_str:
        return {"is_24h": True}
    
    # Handle closed
    if "closed" in hours_str or "n/a" in hours_str:
        return {"is_closed": True}
    
    try:
        # Parse "9:00 AM - 5:00 PM" format
        if " - " in hours_str:
            parts = hours_str.split(" - ")
            if len(parts) == 2:
                return {
                    "open": parts[0].strip(),
                    "close": parts[1].strip()
                }
    except Exception as e:
        print(f"Error parsing hours: {str(e)}")
        return None
    
    return None


def check_resource_availability(resource_name: str, resource_type: str, phone_number: Optional[str] = None) -> Dict:
    """
    Check if a resource is currently open
    
    Args:
        resource_name: Name of the resource
        resource_type: Type of resource (shelter, food_bank, healthcare, other)
        phone_number: Optional phone number for verification
        
    Returns:
        Dictionary with availability status and hours information
    """
    try:
        day_name, current_time, hour_24 = get_current_day_time()
        
        # Search for resource information
        search_query = f"{resource_name} {resource_type} hours San Diego"
        url = "https://api.duckduckgo.com/"
        params = {
            'q': search_query,
            'format': 'json',
            'no_html': 1
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=10)
        data = response.json()
        
        # Extract hours information from abstract or related topics
        hours_info = None
        source = None
        
        if data.get('Abstract'):
            hours_info = data.get('Abstract', '')
            source = data.get('AbstractURL', '')
        
        result = {
            'resource_name': resource_name,
            'resource_type': resource_type,
            'current_time': current_time,
            'current_day': day_name,
            'search_query': search_query,
            'phone_number': phone_number or 'Not provided'
        }
        
        if hours_info:
            result['hours_found'] = hours_info
            result['source_url'] = source
            
            # Try to determine if open
            hours_lower = hours_info.lower()
            if "24" in hours_lower or "24/7" in hours_lower:
                result['is_open'] = True
                result['status'] = "Open 24/7"
            elif "closed" in hours_lower:
                result['is_open'] = False
                result['status'] = "Currently closed"
            else:
                result['status'] = "Hours information found - verify with resource"
                result['is_open'] = None  # Uncertain
        else:
            result['hours_found'] = None
            result['status'] = "Hours not found in search"
            result['is_open'] = None
            result['recommendation'] = f"Call {phone_number}" if phone_number else "Call the resource directly to confirm hours"
        
        return result
        
    except Exception as e:
        print(f"Error checking availability: {str(e)}")
        return {
            'resource_name': resource_name,
            'resource_type': resource_type,
            'status': 'Unable to check',
            'error': str(e),
            'recommendation': f"Call {phone_number if phone_number else 'the resource'} directly or visit 211.org"
        }


def format_availability_response(availability_data: Dict) -> str:
    """
    Format availability data into a readable response
    
    Args:
        availability_data: Dictionary from check_resource_availability
        
    Returns:
        Formatted string response
    """
    response = f"\n📍 **{availability_data['resource_name']}** ({availability_data['resource_type']})\n"
    response += f"⏰ **Current Time**: {availability_data['current_time']} ({availability_data['current_day']})\n"
    
    if availability_data.get('is_open') is True:
        response += "✅ **Status**: OPEN\n"
    elif availability_data.get('is_open') is False:
        response += "❌ **Status**: CLOSED\n"
    else:
        response += f"ℹ️ **Status**: {availability_data.get('status', 'Unknown')}\n"
    
    if availability_data.get('hours_found'):
        response += f"🕐 **Hours**: {availability_data['hours_found']}\n"
    
    if availability_data.get('phone_number') != 'Not provided':
        response += f"📞 **Phone**: {availability_data['phone_number']}\n"
    
    if availability_data.get('recommendation'):
        response += f"💡 **Recommendation**: {availability_data['recommendation']}\n"
    
    if availability_data.get('source_url'):
        response += f"🔗 **Source**: {availability_data['source_url']}\n"
    
    return response