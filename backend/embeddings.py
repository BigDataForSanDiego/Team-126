"""
Embedding generation utilities using Vertex AI text embeddings
"""

from typing import List, Optional
from vertexai.language_models import TextEmbeddingModel
import vertexai
import os
from dotenv import load_dotenv
from google.oauth2 import service_account

load_dotenv()

# Initialize Vertex AI
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
CLIENT_EMAIL = os.getenv("VERTEX_AI_CLIENT_EMAIL")
PRIVATE_KEY = os.getenv("VERTEX_AI_PRIVATE_KEY")
PRIVATE_KEY_ID = os.getenv("VERTEX_AI_PRIVATE_KEY_ID")

# Initialize Vertex AI with service account credentials
if CLIENT_EMAIL and PRIVATE_KEY and PRIVATE_KEY_ID:
    # Create credentials from service account info
    credentials_info = {
        "type": "service_account",
        "project_id": PROJECT_ID,
        "private_key_id": PRIVATE_KEY_ID,
        "private_key": PRIVATE_KEY.replace('\\n', '\n'),
        "client_email": CLIENT_EMAIL,
        "token_uri": "https://oauth2.googleapis.com/token",
    }

    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )

    vertexai.init(project=PROJECT_ID, location=LOCATION, credentials=credentials)
else:
    # Fallback to default credentials
    vertexai.init(project=PROJECT_ID, location=LOCATION)

# Text embedding model (768 dimensions)
EMBEDDING_MODEL_NAME = "text-embedding-004"


def generate_embedding(text: str) -> Optional[List[float]]:
    """
    Generate text embedding using Vertex AI

    Args:
        text: Text string to embed

    Returns:
        List of 768 floats representing the embedding, or None if failed
    """
    try:
        # Initialize the embedding model
        model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL_NAME)

        # Generate embedding
        embeddings = model.get_embeddings([text])

        if embeddings and len(embeddings) > 0:
            # Return the embedding values as a list
            return embeddings[0].values
        else:
            print(f"Warning: No embedding generated for text: {text[:50]}...")
            return None

    except Exception as e:
        print(f"Error generating embedding: {str(e)}")
        return None


def generate_embeddings_batch(texts: List[str], batch_size: int = 5) -> List[Optional[List[float]]]:
    """
    Generate embeddings for multiple texts in batches

    Args:
        texts: List of text strings to embed
        batch_size: Number of texts to process in each batch (max 5 for Vertex AI)

    Returns:
        List of embeddings (each embedding is a list of 768 floats)
    """
    try:
        model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL_NAME)

        all_embeddings = []

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            try:
                embeddings = model.get_embeddings(batch)
                batch_embeddings = [emb.values if emb else None for emb in embeddings]
                all_embeddings.extend(batch_embeddings)
            except Exception as e:
                print(f"Error processing batch {i // batch_size + 1}: {str(e)}")
                # Add None for failed embeddings
                all_embeddings.extend([None] * len(batch))

        return all_embeddings

    except Exception as e:
        print(f"Error in batch embedding generation: {str(e)}")
        return [None] * len(texts)


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Calculate cosine similarity between two vectors

    Args:
        vec1: First embedding vector
        vec2: Second embedding vector

    Returns:
        Cosine similarity score between -1 and 1
    """
    import numpy as np

    v1 = np.array(vec1)
    v2 = np.array(vec2)

    dot_product = np.dot(v1, v2)
    norm1 = np.linalg.norm(v1)
    norm2 = np.linalg.norm(v2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def get_similar_messages(
    query_embedding: List[float],
    conversation_id: int,
    db,
    limit: int = 5,
    similarity_threshold: float = 0.7
):
    """
    Find similar messages in a conversation using vector similarity search

    Args:
        query_embedding: Embedding vector of the query text
        conversation_id: ID of the conversation to search within
        db: SQLAlchemy database session
        limit: Maximum number of results to return
        similarity_threshold: Minimum similarity score (0-1) to include

    Returns:
        List of Message objects ordered by similarity
    """
    from sqlalchemy import text
    from models import Message

    # Convert embedding to PostgreSQL vector format
    embedding_str = "[" + ",".join(map(str, query_embedding)) + "]"

    # Use pgvector's cosine similarity operator
    query = text(f"""
        SELECT id, content, role, embedding <=> :embedding as distance
        FROM messages
        WHERE conversation_id = :conversation_id
        AND embedding IS NOT NULL
        AND (1 - (embedding <=> :embedding)) >= :threshold
        ORDER BY embedding <=> :embedding
        LIMIT :limit
    """)

    result = db.execute(
        query,
        {
            "embedding": embedding_str,
            "conversation_id": conversation_id,
            "threshold": similarity_threshold,
            "limit": limit
        }
    )

    # Fetch message IDs and retrieve full Message objects
    message_ids = [row[0] for row in result]

    if not message_ids:
        return []

    messages = db.query(Message).filter(Message.id.in_(message_ids)).all()

    return messages
