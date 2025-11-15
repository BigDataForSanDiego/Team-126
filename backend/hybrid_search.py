"""
Hybrid search combining geospatial distance and semantic similarity
"""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from dataset_models import HealthService, TransitStop
from embeddings import generate_embedding
import math


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two points in kilometers using Haversine formula

    Args:
        lat1, lon1: First point coordinates
        lat2, lon2: Second point coordinates

    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers

    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))

    return R * c


def search_health_services_hybrid(
    db: Session,
    user_lat: float,
    user_lon: float,
    query: Optional[str] = None,
    max_distance_km: float = 50.0,
    limit: int = 10,
    semantic_weight: float = 0.5
) -> List[Dict]:
    """
    Hybrid search for health services combining distance and semantic similarity

    Args:
        db: Database session
        user_lat: User's latitude
        user_lon: User's longitude
        query: Optional search query for semantic filtering
        max_distance_km: Maximum distance to search (km)
        limit: Maximum number of results
        semantic_weight: Weight for semantic score (0-1), distance weight is (1 - semantic_weight)

    Returns:
        List of health services with distance, similarity scores, and ranking
    """

    # Step 1: Find services within max distance using PostGIS
    distance_query = text("""
        SELECT
            id,
            longitude,
            latitude,
            region,
            program,
            address,
            phone,
            website,
            description,
            taking_new_referrals,
            population,
            services,
            language,
            embedding,
            ST_Distance(
                location::geography,
                ST_SetSRID(ST_MakePoint(:user_lon, :user_lat), 4326)::geography
            ) / 1000.0 as distance_km
        FROM health_services
        WHERE location IS NOT NULL
        AND ST_DWithin(
            location::geography,
            ST_SetSRID(ST_MakePoint(:user_lon, :user_lat), 4326)::geography,
            :max_distance_meters
        )
        ORDER BY distance_km
        LIMIT :query_limit
    """)

    # Execute distance query
    results = db.execute(
        distance_query,
        {
            "user_lat": user_lat,
            "user_lon": user_lon,
            "max_distance_meters": max_distance_km * 1000,  # Convert km to meters
            "query_limit": limit * 3 if query else limit  # Get more results for semantic filtering
        }
    ).fetchall()

    # If no query provided, return results sorted by distance only
    if not query:
        return [
            {
                "id": row[0],
                "longitude": row[1],
                "latitude": row[2],
                "region": row[3],
                "program": row[4],
                "address": row[5],
                "phone": row[6],
                "website": row[7],
                "description": row[8],
                "taking_new_referrals": row[9],
                "population": row[10],
                "services": row[11],
                "language": row[12],
                "distance_km": float(row[14]),
                "distance_miles": float(row[14]) * 0.621371,
                "similarity_score": None,
                "combined_score": None
            }
            for row in results
        ]

    # Step 2: Generate embedding for search query
    query_embedding = generate_embedding(query)

    if not query_embedding:
        # Fallback to distance-only if embedding fails
        print("Warning: Failed to generate query embedding, using distance-only search")
        return search_health_services_hybrid(db, user_lat, user_lon, None, max_distance_km, limit)

    # Step 3: Calculate semantic similarity and combined scores
    scored_results = []

    for row in results:
        service_embedding = row[13]  # embedding column

        # Calculate cosine similarity if embedding exists
        if service_embedding:
            # Convert pgvector to list if needed
            if hasattr(service_embedding, '__iter__'):
                service_emb_list = list(service_embedding)
            else:
                service_emb_list = service_embedding

            # Calculate cosine similarity
            import numpy as np
            query_vec = np.array(query_embedding)
            service_vec = np.array(service_emb_list)

            similarity = np.dot(query_vec, service_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(service_vec)
            )
            similarity_score = float(similarity)
        else:
            similarity_score = 0.0

        # Normalize distance score (inverse - closer is better)
        # Max distance gets score of 0, min distance gets score of 1
        distance_km = float(row[14])
        max_dist = max_distance_km
        distance_score = 1.0 - (distance_km / max_dist) if max_dist > 0 else 1.0

        # Combined score (weighted average)
        combined_score = (semantic_weight * similarity_score) + ((1 - semantic_weight) * distance_score)

        scored_results.append({
            "id": row[0],
            "longitude": row[1],
            "latitude": row[2],
            "region": row[3],
            "program": row[4],
            "address": row[5],
            "phone": row[6],
            "website": row[7],
            "description": row[8],
            "taking_new_referrals": row[9],
            "population": row[10],
            "services": row[11],
            "language": row[12],
            "distance_km": distance_km,
            "distance_miles": distance_km * 0.621371,
            "similarity_score": similarity_score,
            "distance_score": distance_score,
            "combined_score": combined_score
        })

    # Sort by combined score (highest first)
    scored_results.sort(key=lambda x: x['combined_score'], reverse=True)

    # Return top N results
    return scored_results[:limit]


def find_nearest_transit_stops(
    db: Session,
    latitude: float,
    longitude: float,
    limit: int = 5,
    max_distance_km: float = 2.0
) -> List[Dict]:
    """
    Find nearest transit stops to a location

    Args:
        db: Database session
        latitude: Location latitude
        longitude: Location longitude
        limit: Maximum number of stops to return
        max_distance_km: Maximum search radius in km

    Returns:
        List of nearest transit stops with distance
    """

    query = text("""
        SELECT
            id,
            stop_name,
            stop_lat,
            stop_lon,
            stop_agency,
            stop_code,
            wheelchair_boarding,
            ST_Distance(
                location::geography,
                ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography
            ) / 1000.0 as distance_km
        FROM transit_stops
        WHERE location IS NOT NULL
        AND ST_DWithin(
            location::geography,
            ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography,
            :max_distance_meters
        )
        ORDER BY distance_km
        LIMIT :limit
    """)

    results = db.execute(
        query,
        {
            "latitude": latitude,
            "longitude": longitude,
            "max_distance_meters": max_distance_km * 1000,
            "limit": limit
        }
    ).fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
            "latitude": row[2],
            "longitude": row[3],
            "agency": row[4],
            "code": row[5],
            "wheelchair_accessible": row[6] == '1',
            "distance_km": float(row[7]),
            "distance_miles": float(row[7]) * 0.621371
        }
        for row in results
    ]
