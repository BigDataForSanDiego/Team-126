from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
from typing import Optional, List
import json
import re
# import face_recognition  # Commented out - install dlib if you need face recognition
import numpy as np
from pydantic import BaseModel

from database import engine, get_db, Base
from models import User, Conversation, Message
from auth import (
    authenticate_user,
    authenticate_face,
    create_access_token,
    get_password_hash,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from chatbot import get_chatbot_response, generate_conversation_report
from embeddings import generate_embedding, get_similar_messages
from hybrid_search import search_health_services_hybrid, find_nearest_transit_stops
from health_api import router as health_router
import health_models  # Import health models to ensure they're created

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Homeless Assistant API")

# Include health management routes
app.include_router(health_router)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserCreate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    is_guest: bool = False


class UserResponse(BaseModel):
    id: int
    username: Optional[str]
    email: Optional[str]
    is_guest: bool
    character_id: Optional[int]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class CharacterSelect(BaseModel):
    character_id: int
    user_id: int  # Temporarily added for no-auth mode


class ChatMessage(BaseModel):
    content: str
    is_voice: bool = False


class ConversationResponse(BaseModel):
    id: int
    started_at: datetime
    ended_at: Optional[datetime]
    report: Optional[str]

    class Config:
        from_attributes = True


# Connection manager for WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_message(self, message: str, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)


manager = ConnectionManager()


# Routes
@app.get("/")
async def root():
    return {"message": "Homeless Assistant API"}


class RegisterResponse(BaseModel):
    user: UserResponse
    access_token: Optional[str] = None
    token_type: Optional[str] = None

    class Config:
        from_attributes = True


@app.post("/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    if user.is_guest:
        # Create guest user
        db_user = User(is_guest=True)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Generate token for guest user
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(db_user.id)}, expires_delta=access_token_expires
        )

        return {
            "user": db_user,
            "access_token": access_token,
            "token_type": "bearer"
        }

    # Check if user exists
    if user.username and get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if user.email and get_user_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user with password
    hashed_password = get_password_hash(user.password) if user.password else None
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        is_guest=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Generate token for registered user
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )

    return {
        "user": db_user,
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login with username/email and password"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


# Face recognition temporarily disabled - install dlib if needed
# @app.post("/login/face", response_model=Token)
# async def login_face(file: UploadFile = File(...), db: Session = Depends(get_db)):
#     """Login with facial recognition"""
#     try:
#         # Read image file
#         contents = await file.read()
#         nparr = np.frombuffer(contents, np.uint8)

#         # Load image with face_recognition
#         import cv2
#         image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#         rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#         # Get face encodings
#         face_encodings = face_recognition.face_encodings(rgb_image)

#         if len(face_encodings) == 0:
#             raise HTTPException(status_code=400, detail="No face detected in image")

#         # Use first detected face
#         face_encoding = face_encodings[0]

#         # Authenticate
#         user = authenticate_face(db, face_encoding.tolist())
#         if not user:
#             raise HTTPException(status_code=401, detail="Face not recognized")

#         access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#         access_token = create_access_token(
#             data={"sub": str(user.id)}, expires_delta=access_token_expires
#         )
#         return {"access_token": access_token, "token_type": "bearer"}

#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")


# Face recognition temporarily disabled - install dlib if needed
# @app.post("/register/face")
# async def register_face(
#     file: UploadFile = File(...),
#     user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
#     """Register face encoding for existing user"""
#     try:
#         contents = await file.read()
#         nparr = np.frombuffer(contents, np.uint8)

#         import cv2
#         image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#         rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#         face_encodings = face_recognition.face_encodings(rgb_image)

#         if len(face_encodings) == 0:
#             raise HTTPException(status_code=400, detail="No face detected in image")

#         face_encoding = face_encodings[0]

#         # Store encoding
#         user.face_encoding = json.dumps(face_encoding.tolist())
#         db.commit()

#         return {"message": "Face registered successfully"}

#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Error processing image: {str(e)}")


@app.post("/character/select")
async def select_character(
    character: CharacterSelect,
    db: Session = Depends(get_db)
):
    """Select a 3D character for the user - TEMPORARY NO AUTH"""
    user = db.query(User).filter(User.id == character.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.character_id = character.character_id
    db.commit()
    return {"message": "Character selected successfully", "character_id": character.character_id}


@app.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    """Get current user information"""
    return user


class ConversationStart(BaseModel):
    user_id: int  # Temporarily added for no-auth mode

@app.post("/conversation/start")
async def start_conversation(
    data: ConversationStart,
    db: Session = Depends(get_db)
):
    """Start a new conversation - TEMPORARY NO AUTH"""
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    conversation = Conversation(user_id=user.id)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return {"conversation_id": conversation.id}


@app.post("/conversation/{conversation_id}/end")
async def end_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """End conversation and generate report - TEMPORARY NO AUTH"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get all messages
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).all()
    message_list = [{"role": msg.role, "content": msg.content} for msg in messages]

    # Generate report with health data (for guest mode, use conversation_id as user_id)
    report = await generate_conversation_report(message_list, conversation_id=conversation_id, db=db)

    conversation.ended_at = datetime.utcnow()
    conversation.report = report
    db.commit()

    return {"report": report}


@app.get("/conversation/{conversation_id}/report")
async def get_report(
    conversation_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get report for a conversation"""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user.id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if not conversation.report:
        raise HTTPException(status_code=404, detail="Report not generated yet")

    return {"report": conversation.report}


class SimilaritySearchRequest(BaseModel):
    query: str
    limit: int = 5
    threshold: float = 0.7


@app.post("/conversation/{conversation_id}/search")
async def search_similar_messages(
    conversation_id: int,
    request: SimilaritySearchRequest,
    db: Session = Depends(get_db)
):
    """
    Search for similar messages in a conversation using semantic similarity

    Args:
        conversation_id: ID of the conversation to search
        query: Search query text
        limit: Maximum number of results (default: 5)
        threshold: Minimum similarity score 0-1 (default: 0.7)

    Returns:
        List of similar messages with their similarity scores
    """
    # Verify conversation exists
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Generate embedding for search query
    query_embedding = generate_embedding(request.query)

    if not query_embedding:
        raise HTTPException(status_code=500, detail="Failed to generate query embedding")

    # Search for similar messages
    similar_messages = get_similar_messages(
        query_embedding=query_embedding,
        conversation_id=conversation_id,
        db=db,
        limit=request.limit,
        similarity_threshold=request.threshold
    )

    # Format results
    results = [
        {
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.timestamp.isoformat() if msg.timestamp else None,
        }
        for msg in similar_messages
    ]

    return {
        "query": request.query,
        "conversation_id": conversation_id,
        "results": results,
        "count": len(results)
    }


class HealthServiceSearchRequest(BaseModel):
    latitude: float
    longitude: float
    query: Optional[str] = None
    max_distance_km: float = 50.0
    limit: int = 10
    semantic_weight: float = 0.5


@app.post("/search/health-services")
async def search_health_services(
    request: HealthServiceSearchRequest,
    db: Session = Depends(get_db)
):
    """
    Hybrid search for health services combining geospatial distance and semantic similarity

    Args:
        latitude: User's latitude
        longitude: User's longitude
        query: Optional search query (e.g., "mental health", "substance abuse")
        max_distance_km: Maximum search radius in kilometers (default: 50)
        limit: Maximum number of results (default: 10)
        semantic_weight: Weight for semantic matching 0-1 (default: 0.5)

    Returns:
        List of health services with distances, transit stops, and map data
    """

    # Perform hybrid search
    results = search_health_services_hybrid(
        db=db,
        user_lat=request.latitude,
        user_lon=request.longitude,
        query=request.query,
        max_distance_km=request.max_distance_km,
        limit=request.limit,
        semantic_weight=request.semantic_weight
    )

    # For each result, find nearest transit stops
    for service in results:
        transit_stops = find_nearest_transit_stops(
            db=db,
            latitude=service['latitude'],
            longitude=service['longitude'],
            limit=3,
            max_distance_km=1.0  # Within 1km of the service
        )
        service['nearby_transit'] = transit_stops

    return {
        "user_location": {
            "latitude": request.latitude,
            "longitude": request.longitude
        },
        "query": request.query,
        "search_radius_km": request.max_distance_km,
        "search_radius_miles": request.max_distance_km * 0.621371,
        "results": results,
        "count": len(results)
    }


def parse_location_from_message(message: str) -> Optional[dict]:
    """
    Parse location coordinates from a message.
    Expected format: "My current location is: Latitude X, Longitude Y"

    Returns:
        Dict with 'latitude' and 'longitude' keys, or None if not found
    """
    # Pattern to match: "Latitude 34.052235, Longitude -118.243683"
    pattern = r"Latitude\s+([-+]?\d+\.?\d*),\s*Longitude\s+([-+]?\d+\.?\d*)"
    match = re.search(pattern, message, re.IGNORECASE)

    if match:
        try:
            latitude = float(match.group(1))
            longitude = float(match.group(2))
            return {"latitude": latitude, "longitude": longitude}
        except ValueError:
            return None
    return None


@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()

    try:
        # Get conversation
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            await websocket.send_json({"error": "Conversation not found"})
            await websocket.close()
            return

        # Get conversation history
        messages = db.query(Message).filter(Message.conversation_id == conversation_id).all()
        message_history = [{"role": msg.role, "content": msg.content} for msg in messages]

        while True:
            # Receive message from client
            data = await websocket.receive_json()
            user_message = data.get("content")
            is_voice = data.get("is_voice", False)

            # Check if message contains location data
            location_data = parse_location_from_message(user_message)
            latitude = None
            longitude = None

            if location_data:
                latitude = location_data["latitude"]
                longitude = location_data["longitude"]
                print(f"[Location] Detected coordinates: {latitude}, {longitude}")

                # Update conversation with location
                conversation.latitude = latitude
                conversation.longitude = longitude
                db.commit()

            # Generate embedding for user message
            user_embedding = generate_embedding(user_message)

            # Save user message
            db_message = Message(
                conversation_id=conversation_id,
                role="user",
                content=user_message,
                is_voice=is_voice,
                latitude=latitude,
                longitude=longitude,
                embedding=user_embedding
            )
            db.add(db_message)
            db.commit()
            print(f"[Embedding] Generated embedding for user message (dim: {len(user_embedding) if user_embedding else 0})")

            # Add to history (include location if available)
            message_dict = {"role": "user", "content": user_message}
            if latitude is not None and longitude is not None:
                message_dict["latitude"] = latitude
                message_dict["longitude"] = longitude
            message_history.append(message_dict)

            # Get AI response (pass conversation object which now has location)
            assistant_response = await get_chatbot_response(message_history, conversation)

            # Generate embedding for assistant response
            assistant_embedding = generate_embedding(assistant_response)

            # Save assistant message
            db_message = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_response,
                is_voice=False,
                embedding=assistant_embedding
            )
            db.add(db_message)
            db.commit()
            print(f"[Embedding] Generated embedding for assistant message (dim: {len(assistant_embedding) if assistant_embedding else 0})")

            # Add to history
            message_history.append({"role": "assistant", "content": assistant_response})

            # Send response to client
            await websocket.send_json({
                "role": "assistant",
                "content": assistant_response,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for conversation {conversation_id}")
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        await websocket.send_json({"error": str(e)})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


# Helper function for auth
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()
