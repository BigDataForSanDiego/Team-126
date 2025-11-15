"""
Tool definitions for the AI assistant
"""

from vertexai.generative_models import Tool, FunctionDeclaration

# Define location request function
get_location_func = FunctionDeclaration(
    name="request_user_location",
    description="Request the user's current GPS location to help find nearby resources such as shelters, food banks, or services. Use this when the user needs location-based assistance.",
    parameters={
        "type": "object",
        "properties": {
            "reason": {
                "type": "string",
                "description": "Brief explanation of why location is needed (e.g., 'to find nearby shelters')"
            }
        },
        "required": ["reason"]
    },
)

# Create location tool
location_tool = Tool(
    function_declarations=[get_location_func],
)
