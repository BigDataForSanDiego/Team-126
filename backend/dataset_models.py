"""
Database models for San Diego County datasets
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from pgvector.sqlalchemy import Vector
from database import Base


class HealthService(Base):
    """Behavioral Health Services in San Diego County"""
    __tablename__ = "health_services"

    id = Column(Integer, primary_key=True, index=True)
    longitude = Column(Float, nullable=False, index=True)
    latitude = Column(Float, nullable=False, index=True)
    region = Column(String)
    program = Column(String)
    address = Column(Text)
    phone = Column(String)
    website = Column(String)
    description = Column(Text)
    taking_new_referrals = Column(String)
    population = Column(Text)
    services = Column(Text)
    language = Column(String)
    fid = Column(String)

    # Geospatial column for PostGIS queries
    location = Column(Geometry('POINT', srid=4326), nullable=True)

    # Vector embedding for semantic search
    embedding = Column(Vector(768), nullable=True)


class TransitStop(Base):
    """Public Transit Stops in San Diego County"""
    __tablename__ = "transit_stops"

    id = Column(Integer, primary_key=True, index=True)
    objectid = Column(Integer)
    stop_uid = Column(String, index=True)
    stop_agency = Column(String)
    stop_id = Column(String, index=True)
    stop_name = Column(String)
    stop_lat = Column(Float, nullable=False, index=True)
    stop_lon = Column(Float, nullable=False, index=True)
    stop_code = Column(String)
    location_type = Column(String)
    parent_station = Column(String)
    wheelchair_boarding = Column(String)
    intersection_code = Column(String)
    stop_place = Column(String)

    # Geospatial column for PostGIS queries
    location = Column(Geometry('POINT', srid=4326), nullable=True)


class TransitRoute(Base):
    """Public Transit Routes in San Diego County"""
    __tablename__ = "transit_routes"

    id = Column(Integer, primary_key=True, index=True)
    objectid = Column(Integer)
    shape_id = Column(String)
    route_id = Column(String, index=True)
    route_short_name = Column(String)
    route_long_name = Column(String)
    route_type = Column(String)
    agency_id = Column(String)
    route_desc = Column(Text)
    route_url = Column(String)
    route_color = Column(String)
    route_text_color = Column(String)
    route_type_text = Column(String)
    routeshapename = Column(String)
    route_color_rgb = Column(String)
    route_text_color_rgb = Column(String)
    shape_length = Column(Float)


class HousingElement(Base):
    """Housing Elements in San Diego County"""
    __tablename__ = "housing_elements"

    id = Column(Integer, primary_key=True, index=True)
    objectid = Column(Integer)
    jurisdiction = Column(String)
    apn = Column(String)
    vacancy = Column(String)
    units = Column(Integer)
    zoning = Column(String)
    zoning_simplified = Column(String)
    min_density = Column(Float)
    max_density = Column(Float)
    links = Column(String)
    shape_area = Column(Float)
    shape_length = Column(Float)
