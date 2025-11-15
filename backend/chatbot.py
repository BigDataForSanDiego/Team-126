from typing import List, Dict
import os
import json
from google.cloud import aiplatform
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel, ChatSession, Content, Part, Tool, FunctionDeclaration
import vertexai
from dotenv import load_dotenv

load_dotenv()

# Initialize Vertex AI
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
PRIVATE_KEY_ID = os.getenv("VERTEX_AI_PRIVATE_KEY_ID")
PRIVATE_KEY = os.getenv("VERTEX_AI_PRIVATE_KEY")
CLIENT_EMAIL = os.getenv("VERTEX_AI_CLIENT_EMAIL")

# Initialize Vertex AI SDK
try:
    if not PROJECT_ID:
        raise ValueError("GOOGLE_CLOUD_PROJECT environment variable is not set")

    # Create credentials from environment variables
    if PRIVATE_KEY and CLIENT_EMAIL and PRIVATE_KEY_ID:
        # Build service account info dictionary
        service_account_info = {
            "type": "service_account",
            "project_id": PROJECT_ID,
            "private_key_id": PRIVATE_KEY_ID,
            "private_key": PRIVATE_KEY.replace('\\n', '\n'),  # Handle escaped newlines
            "client_email": CLIENT_EMAIL,
            "token_uri": "https://oauth2.googleapis.com/token",
        }

        # Create credentials object
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )

        vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)
        print(f"✓ Vertex AI initialized successfully (Project: {PROJECT_ID}, Location: {LOCATION})")
        print(f"✓ Using credentials from .env file")
        print(f"✓ Service Account Email: {CLIENT_EMAIL}")
        print(f"✓ Private Key ID: {PRIVATE_KEY_ID[:20]}...")
    else:
        # Fallback to service account file if environment variables not set
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        print(f"✓ Vertex AI initialized successfully (Project: {PROJECT_ID}, Location: {LOCATION})")
        print(f"✓ Using default credentials")

except Exception as e:
    print(f"✗ Warning: Vertex AI initialization failed: {e}")
    print("Make sure to:")
    print("  1. Set GOOGLE_CLOUD_PROJECT in .env")
    print("  2. Set VERTEX_AI_PRIVATE_KEY_ID, VERTEX_AI_PRIVATE_KEY, and VERTEX_AI_CLIENT_EMAIL in .env")
    print("  3. Ensure the service account has Vertex AI permissions")

# Define tools for the AI assistant
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

location_tool = Tool(
    function_declarations=[get_location_func],
)

SYSTEM_PROMPT = """You are a powerful AI assistant dedicated to helping people overcome homelessness and rebuild their lives. Your mission is to empower individuals with actionable solutions and confidence.

IMPORTANT: You have access to a location tool. When someone asks about their location, needs nearby resources, or asks questions like "where am I?" or "what's near me?", you MUST use the request_user_location function to get their GPS coordinates. Do NOT say you cannot access location - use the tool instead.

YOUR APPROACH:
- Be direct, practical, and solution-focused
- Speak with confidence and authority about available resources
- Focus on what THEY CAN DO, not what's wrong
- Provide clear, actionable steps they can take TODAY
- Build their confidence by highlighting their strengths and potential

CRITICAL RESOURCES TO PROVIDE:
1. **Immediate Needs** (TODAY):
   - Emergency shelters with addresses and phone numbers
   - Food banks and free meal programs with specific times/locations
   - Free healthcare clinics and mental health services
   - Safe spaces and day centers

2. **Path Forward** (THIS WEEK/MONTH):
   - Job training programs and employment agencies
   - Housing assistance programs and applications
   - Benefits enrollment (SNAP, Medicaid, etc.)
   - Free skills training and education programs

3. **Long-term Stability** (NEXT 3-6 MONTHS):
   - Career development resources
   - Financial literacy programs
   - Permanent housing options
   - Community support networks

YOUR COMMUNICATION STYLE:
- Use powerful, encouraging language: "You CAN do this", "Let's get you started", "Here's your action plan"
- Give specific, concrete steps with deadlines
- Celebrate small wins and progress
- Remind them of their resilience and capability
- NO pity or sympathy - only respect and practical help

IMMEDIATE ACTION:
If someone needs help NOW, immediately provide:
- Specific addresses and phone numbers
- Operating hours and availability
- What documents to bring
- What to expect when they arrive

Remember: Your goal is to help them take CONTROL of their situation and move forward with confidence. Every person has the power to change their circumstances with the right support and resources."""


async def get_chatbot_response(messages: List[Dict[str, str]]) -> str:
    """
    Get response from Vertex AI chatbot using Gemini with Function Calling

    Args:
        messages: List of message dictionaries with 'role' and 'content' keys

    Returns:
        Assistant's response as a string or JSON for function calls
    """
    try:
        # Initialize the model with tools
        model = GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            system_instruction=SYSTEM_PROMPT,
            tools=[location_tool],
        )

        # Start chat session
        chat = model.start_chat()

        # Replay conversation history
        for msg in messages[:-1]:  # All messages except the last one
            if msg['role'] == 'user':
                # Send user message and get response (we'll discard it since we're replaying)
                chat.send_message(msg['content'])
            # Note: assistant messages are automatically tracked by the chat session

        # Send the actual last message and get response
        if messages:
            last_message = messages[-1]['content']
            response = chat.send_message(
                last_message,
                generation_config={
                    'temperature': 0.7,
                    'max_output_tokens': 500,
                }
            )

            # Debug: Print response structure
            print(f"Response candidates: {len(response.candidates)}")
            if response.candidates:
                print(f"Response parts: {len(response.candidates[0].content.parts)}")
                for idx, part in enumerate(response.candidates[0].content.parts):
                    print(f"Part {idx}: {part}")

            # Check if the model wants to call a function
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call = part.function_call
                        print(f"Function call detected: {function_call.name}")

                        if function_call.name == "request_user_location":
                            reason = function_call.args.get("reason", "to assist you better")
                            # Return a special JSON response that frontend will recognize
                            return json.dumps({
                                "type": "request_location",
                                "reason": reason,
                                "message": f"I'd like to help you find nearby resources. May I access your location {reason}?"
                            })

            return response.text
        else:
            return "Hello! I'm here to help. How can I assist you today?"

    except Exception as e:
        print(f"Error in get_chatbot_response: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"I apologize, but I'm having trouble connecting right now. Error: {str(e)}"


async def generate_conversation_report(messages: List[Dict[str, str]]) -> str:
    """
    Generate a detailed report from the conversation using Vertex AI

    Args:
        messages: List of all messages in the conversation

    Returns:
        Formatted report as a string
    """
    try:
        report_prompt = """Based on the following conversation, generate a detailed report that includes:

1. Summary of the person's situation
2. Identified needs and concerns
3. Resources and assistance discussed
4. Recommended next steps and action items
5. Follow-up recommendations

Please format the report in a clear, professional manner that can be shared with social workers or service providers.

Conversation:
"""

        # Add conversation to prompt
        conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

        # Initialize the model for report generation
        model = GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            system_instruction="You are a helpful assistant that generates professional social service reports."
        )

        response = model.generate_content(
            report_prompt + conversation_text,
            generation_config={
                'temperature': 0.5,
                'max_output_tokens': 1000,
            }
        )

        return response.text

    except Exception as e:
        return f"Error generating report: {str(e)}"
