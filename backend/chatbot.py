from typing import List, Dict, Optional
import os
import json
from google.cloud import aiplatform
from google.oauth2 import service_account
from vertexai.generative_models import GenerativeModel, ChatSession, Content, Part, Tool
import vertexai
from dotenv import load_dotenv

from prompts import HOMELESS_ASSISTANT_PROMPT, REPORT_GENERATION_PROMPT
from tools import get_location_func, search_web_func, perform_web_search

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


async def get_chatbot_response(messages: List[Dict[str, str]], conversation: Optional[object] = None) -> str:
    """
    Get response from Vertex AI chatbot using Gemini with Function Calling

    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        conversation: Optional Conversation object containing user's location (latitude, longitude)

    Returns:
        Assistant's response as a string or JSON for function calls
    """
    try:
        # Combine all function declarations into a single tool
        # Vertex AI requires all functions in one Tool object
        combined_tool = Tool(
            function_declarations=[get_location_func, search_web_func],
        )

        # Initialize the model with the combined tool
        model = GenerativeModel(
            model_name="gemini-2.5-pro",
            system_instruction=HOMELESS_ASSISTANT_PROMPT,
            tools=[combined_tool],
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
                    'max_output_tokens': 20000,
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

                        elif function_call.name == "search_web":
                            # Execute the web search
                            query = function_call.args.get("query", "")
                            max_results = function_call.args.get("max_results", 5)
                            print(f"Performing web search: {query}")

                            # Get location from conversation if available
                            latitude = None
                            longitude = None
                            if conversation and hasattr(conversation, 'latitude') and hasattr(conversation, 'longitude'):
                                latitude = conversation.latitude
                                longitude = conversation.longitude
                                print(f"Using conversation location: {latitude}, {longitude}")

                            search_results = perform_web_search(query, max_results, latitude, longitude)

                            # Extract resource data marker if present (before formatting for LLM)
                            resource_data_marker = ""
                            for result in search_results:
                                if 'snippet' in result and '<!-- RESOURCE_DATA:' in result['snippet']:
                                    import re
                                    match = re.search(r'<!-- RESOURCE_DATA:.+? -->', result['snippet'], re.DOTALL)
                                    if match:
                                        resource_data_marker = match.group(0)
                                        print(f"[Resource Data] Extracted marker from search results")
                                        break

                            # Format search results for the LLM
                            results_text = f"Search results for '{query}':\n\n"
                            for idx, result in enumerate(search_results, 1):
                                results_text += f"{idx}. {result['title']}\n"
                                results_text += f"   {result['snippet']}\n"
                                if result['url']:
                                    results_text += f"   URL: {result['url']}\n"
                                results_text += "\n"

                            # Send search results back to the model to continue the conversation
                            function_response = Part.from_function_response(
                                name="search_web",
                                response={"results": results_text}
                            )

                            # Continue the conversation with the search results
                            response = chat.send_message(
                                Content(parts=[function_response]),
                                generation_config={
                                    'temperature': 0.7,
                                    'max_output_tokens': 20000,
                                }
                            )

                            # Append resource data marker to the response
                            final_response = response.text
                            if resource_data_marker:
                                final_response += "\n\n" + resource_data_marker
                                print(f"[Resource Data] Appended marker to LLM response")

                            return final_response

            return response.text
        else:
            return "Hello! I'm here to help. How can I assist you today?"

    except Exception as e:
        print(f"Error in get_chatbot_response: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"I apologize, but I'm having trouble connecting right now. Error: {str(e)}"


async def generate_conversation_report(messages: List[Dict[str, str]], conversation_id: Optional[int] = None, db = None) -> str:
    """
    Generate a detailed report from the conversation using Vertex AI
    Includes health tracking data if available (medications, symptoms, vitals)

    Args:
        messages: List of all messages in the conversation
        conversation_id: Optional conversation ID to fetch health data
        db: Optional database session to query health data

    Returns:
        Formatted report as a string in Markdown format
    """
    try:
        # Fetch health data if conversation_id and db provided
        health_data_text = ""
        if conversation_id and db:
            health_data_text = await get_health_summary(conversation_id, db)

        report_prompt = """Based on the following conversation, generate a comprehensive assistance report in **Markdown format**.

Focus primarily on:
- **User Requirements**: What specific help the person asked for and their expressed needs
- **Corresponding Resources**: The specific resources, services, and assistance that were provided or recommended

The report should include these sections:

# Assistance Report

## Executive Summary
Brief overview of the conversation and main assistance provided.

## User Requirements and Requests
List each specific request or need expressed by the user:
- What they asked for help with
- Their current situation and challenges
- Any urgent needs mentioned

## Resources and Services Provided
For each requirement, list the corresponding resources discussed:
- **Resource Name**: Description and how it addresses the need
- Contact information (phone, address, website)
- Eligibility requirements
- Next steps to access the resource

## Additional Recommendations
Any supplementary resources or follow-up actions that may be helpful.

## Action Items
Clear, numbered list of next steps the person should take.

## Follow-up Information
- When to follow up
- Contact information for continued assistance
- Any additional notes

{health_section}

Please format the report professionally using proper Markdown syntax (headings, lists, bold text, etc.) suitable for sharing with social workers or service providers.

Conversation:
"""

        # Add health tracking section if data exists
        health_section = ""
        if health_data_text:
            health_section = """
## 🏥 Health Tracking Summary (Guest Mode)
**Important**: The following health data was tracked during this conversation session. This information should be highlighted for healthcare providers.

""" + health_data_text

        # Format the prompt with health section
        formatted_prompt = report_prompt.format(health_section=health_section)

        # Add conversation to prompt
        conversation_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

        # Initialize the model for report generation
        model = GenerativeModel(
            model_name="gemini-2.5-pro",
            system_instruction="You are a professional social service assistant that generates well-structured, markdown-formatted reports focusing on user needs and available resources. Use proper markdown syntax with headers, lists, bold text, and clear organization."
        )

        response = model.generate_content(
            formatted_prompt + conversation_text,
            generation_config={
                'temperature': 0.5,
                'max_output_tokens': 2000,
            }
        )

        # Extract all resource data from conversation messages
        all_resources = []
        import re
        for msg in messages:
            if msg['role'] == 'assistant' and 'content' in msg:
                match = re.search(r'<!-- RESOURCE_DATA:(.+?) -->', msg['content'], re.DOTALL)
                if match:
                    try:
                        import json
                        resource_data = json.loads(match.group(1))
                        if resource_data.get('type') == 'resource_list' and resource_data.get('resources'):
                            all_resources.extend(resource_data['resources'])
                            print(f"[Report] Found {len(resource_data['resources'])} resources in message")
                    except Exception as e:
                        print(f"[Report] Failed to parse resource data: {e}")

        # Append resource data marker to the report if resources found
        final_report = response.text
        if all_resources:
            # Remove duplicates based on resource ID
            unique_resources = {r['id']: r for r in all_resources}.values()
            resource_marker = f"\n\n<!-- RESOURCE_DATA:{json.dumps({'type': 'resource_list', 'resources': list(unique_resources)})} -->"
            final_report += resource_marker
            print(f"[Report] Appended {len(unique_resources)} unique resources to report")

        return final_report

    except Exception as e:
        return f"# Error Generating Report\n\nAn error occurred while generating the report: {str(e)}"


async def get_health_summary(conversation_id: int, db) -> str:
    """
    Get formatted health tracking summary for a conversation (guest mode)

    Args:
        conversation_id: The conversation ID
        db: Database session

    Returns:
        Formatted markdown string with health data
    """
    try:
        from health_models import Medication, SymptomLog, VitalSign, CarePlan
        from sqlalchemy import and_

        summary_parts = []

        # Get user_id from conversation (for guest mode, we use conversation_id as user_id)
        user_id = conversation_id

        # Get medications
        medications = db.query(Medication).filter(
            and_(Medication.user_id == user_id, Medication.is_active == True)
        ).all()

        if medications:
            summary_parts.append("### 💊 Medications Tracked")
            for med in medications:
                summary_parts.append(f"- **{med.name}** ({med.dosage})")
                summary_parts.append(f"  - Frequency: {med.frequency}")
                if med.purpose:
                    summary_parts.append(f"  - Purpose: {med.purpose}")
                if med.reminder_times:
                    summary_parts.append(f"  - Reminder times: {', '.join(med.reminder_times)}")
            summary_parts.append("")

        # Get symptoms
        symptoms = db.query(SymptomLog).filter(
            SymptomLog.user_id == user_id
        ).order_by(SymptomLog.logged_at.desc()).limit(10).all()

        if symptoms:
            summary_parts.append("### 📋 Symptoms Logged")
            for symptom in symptoms:
                severity_indicator = "🟢" if symptom.severity <= 3 else "🟡" if symptom.severity <= 6 else "🔴"
                summary_parts.append(f"- {severity_indicator} **{symptom.symptom}** (Severity: {symptom.severity}/10)")
                if symptom.duration:
                    summary_parts.append(f"  - Duration: {symptom.duration}")
                if symptom.description:
                    summary_parts.append(f"  - Notes: {symptom.description}")
                summary_parts.append(f"  - Logged: {symptom.logged_at.strftime('%Y-%m-%d %H:%M')}")
            summary_parts.append("")

        # Get vital signs
        vitals = db.query(VitalSign).filter(
            VitalSign.user_id == user_id
        ).order_by(VitalSign.measured_at.desc()).limit(10).all()

        if vitals:
            summary_parts.append("### ❤️ Vital Signs Recorded")
            for vital in vitals:
                abnormal_flag = " ⚠️ **ABNORMAL**" if vital.is_abnormal else ""
                if vital.measurement_type == 'blood_pressure':
                    summary_parts.append(f"- **Blood Pressure**: {vital.systolic}/{vital.diastolic} mmHg{abnormal_flag}")
                else:
                    summary_parts.append(f"- **{vital.measurement_type.replace('_', ' ').title()}**: {vital.value} {vital.unit}{abnormal_flag}")
                summary_parts.append(f"  - Measured: {vital.measured_at.strftime('%Y-%m-%d %H:%M')}")
                if vital.notes:
                    summary_parts.append(f"  - Notes: {vital.notes}")
            summary_parts.append("")

        # Get care plans
        care_plans = db.query(CarePlan).filter(
            and_(CarePlan.user_id == user_id, CarePlan.status == 'active')
        ).all()

        if care_plans:
            summary_parts.append("### 📖 Active Care Plans")
            for plan in care_plans:
                summary_parts.append(f"- **{plan.title}**")
                if plan.condition:
                    summary_parts.append(f"  - Condition: {plan.condition}")
                if plan.primary_provider:
                    summary_parts.append(f"  - Provider: {plan.primary_provider}")
                if plan.next_appointment:
                    summary_parts.append(f"  - Next Appointment: {plan.next_appointment.strftime('%Y-%m-%d')}")
            summary_parts.append("")

        if summary_parts:
            summary_parts.insert(0, "**Note**: This health information was self-reported during the conversation and should be verified by healthcare professionals.")
            summary_parts.insert(1, "")
            return "\n".join(summary_parts)
        else:
            return ""

    except Exception as e:
        print(f"Error fetching health summary: {e}")
        return ""
