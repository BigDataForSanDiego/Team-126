from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone
from typing import Optional, List
import json
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

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Homeless Assistant API")

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

    # Generate report
    report = await generate_conversation_report(message_list)

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

            # Save user message
            db_message = Message(
                conversation_id=conversation_id,
                role="user",
                content=user_message,
                is_voice=is_voice
            )
            db.add(db_message)
            db.commit()

            # Add to history
            message_history.append({"role": "user", "content": user_message})

            # Get AI response
            assistant_response = await get_chatbot_response(message_history)

            # Save assistant message
            db_message = Message(
                conversation_id=conversation_id,
                role="assistant",
                content=assistant_response,
                is_voice=False
            )
            db.add(db_message)
            db.commit()

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
