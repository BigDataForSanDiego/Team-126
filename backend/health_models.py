"""
Health and Chronic Care Management Models
For tracking medications, symptoms, vital signs, and care plans
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timedelta


class Medication(Base):
    """Track user medications and prescriptions"""
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Medication details
    name = Column(String, nullable=False)
    dosage = Column(String)  # e.g., "10mg", "2 tablets"
    frequency = Column(String)  # e.g., "twice daily", "every 8 hours"
    route = Column(String)  # e.g., "oral", "injection", "topical"

    # Purpose and instructions
    purpose = Column(Text)  # What condition this treats
    instructions = Column(Text)  # Special instructions
    side_effects = Column(Text)  # Known side effects to watch for

    # Scheduling
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)  # Null if ongoing
    reminder_enabled = Column(Boolean, default=True)
    reminder_times = Column(JSON)  # List of times like ["08:00", "20:00"]

    # Tracking
    is_active = Column(Boolean, default=True)
    prescribing_provider = Column(String)
    pharmacy = Column(String)
    refills_remaining = Column(Integer, default=0)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    doses = relationship("MedicationDose", back_populates="medication", cascade="all, delete-orphan")


class MedicationDose(Base):
    """Track individual medication doses taken"""
    __tablename__ = "medication_doses"

    id = Column(Integer, primary_key=True, index=True)
    medication_id = Column(Integer, ForeignKey("medications.id"), nullable=False)

    # Dose tracking
    scheduled_time = Column(DateTime, nullable=False)
    taken_time = Column(DateTime, nullable=True)  # Null if not taken yet
    status = Column(String, default="scheduled")  # scheduled, taken, missed, skipped

    # Optional notes
    notes = Column(Text)  # e.g., "Took with food", "Felt nauseous"

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    medication = relationship("Medication", back_populates="doses")


class SymptomLog(Base):
    """Track symptoms over time"""
    __tablename__ = "symptom_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Symptom details
    symptom = Column(String, nullable=False)  # e.g., "headache", "chest pain", "fatigue"
    severity = Column(Integer)  # 1-10 scale
    duration = Column(String)  # e.g., "2 hours", "all day"

    # Context
    triggers = Column(JSON)  # List of potential triggers
    location = Column(String)  # Body location if applicable
    description = Column(Text)  # Additional details

    # Associated data
    related_medication_id = Column(Integer, ForeignKey("medications.id"), nullable=True)
    photo_url = Column(String, nullable=True)  # For visible symptoms

    # Metadata
    logged_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class VitalSign(Base):
    """Track vital signs and health metrics"""
    __tablename__ = "vital_signs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Vital sign measurements
    measurement_type = Column(String, nullable=False)  # blood_pressure, glucose, temperature, etc.

    # Blood pressure
    systolic = Column(Integer, nullable=True)
    diastolic = Column(Integer, nullable=True)

    # Single value measurements
    value = Column(Float, nullable=True)
    unit = Column(String)  # mg/dL, °F, bpm, etc.

    # Context
    measured_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)  # e.g., "After meal", "Morning reading"
    location = Column(String)  # Where measured if relevant

    # Flags
    is_abnormal = Column(Boolean, default=False)
    alert_sent = Column(Boolean, default=False)  # If abnormal reading triggered alert

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)


class CarePlan(Base):
    """Comprehensive care plan for managing health conditions"""
    __tablename__ = "care_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Care plan details
    title = Column(String, nullable=False)  # e.g., "Diabetes Management Plan"
    condition = Column(String)  # Primary condition being managed
    status = Column(String, default="active")  # active, completed, paused

    # Plan components
    goals = Column(JSON)  # List of health goals
    medications = Column(JSON)  # List of medication IDs
    dietary_restrictions = Column(JSON)  # List of dietary guidelines
    exercise_plan = Column(Text)

    # Provider information
    primary_provider = Column(String)
    care_team = Column(JSON)  # List of providers and their roles

    # Monitoring
    vital_signs_to_track = Column(JSON)  # Which vitals to monitor
    target_ranges = Column(JSON)  # Target ranges for vitals

    # Appointments and follow-ups
    next_appointment = Column(DateTime, nullable=True)
    review_date = Column(DateTime)  # When to review plan

    # Emergency contacts
    emergency_contacts = Column(JSON)
    emergency_instructions = Column(Text)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String)  # Provider who created the plan


class HealthGoal(Base):
    """Track health goals and progress"""
    __tablename__ = "health_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    care_plan_id = Column(Integer, ForeignKey("care_plans.id"), nullable=True)

    # Goal details
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)  # medication_adherence, weight_loss, exercise, etc.

    # Target
    target_value = Column(Float, nullable=True)
    target_unit = Column(String, nullable=True)
    target_date = Column(DateTime, nullable=True)

    # Progress tracking
    current_value = Column(Float, nullable=True)
    progress_percentage = Column(Float, default=0.0)
    status = Column(String, default="in_progress")  # in_progress, achieved, paused, abandoned

    # Milestones
    milestones = Column(JSON)  # List of intermediate milestones

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class HealthNote(Base):
    """General health notes and journal entries"""
    __tablename__ = "health_notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Note details
    title = Column(String)
    content = Column(Text, nullable=False)
    category = Column(String)  # general, appointment, provider_visit, etc.

    # Associated records
    related_medication_id = Column(Integer, ForeignKey("medications.id"), nullable=True)
    related_symptom_id = Column(Integer, ForeignKey("symptom_logs.id"), nullable=True)
    related_care_plan_id = Column(Integer, ForeignKey("care_plans.id"), nullable=True)

    # Attachments
    attachments = Column(JSON)  # List of file URLs

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
