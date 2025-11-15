"""
Pydantic schemas for health management API requests and responses
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============================================================================
# Medication Schemas
# ============================================================================

class MedicationBase(BaseModel):
    name: str
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = None
    purpose: Optional[str] = None
    instructions: Optional[str] = None
    side_effects: Optional[str] = None
    reminder_enabled: bool = True
    reminder_times: Optional[List[str]] = None
    prescribing_provider: Optional[str] = None
    pharmacy: Optional[str] = None
    refills_remaining: int = 0


class MedicationCreate(MedicationBase):
    user_id: int


class MedicationUpdate(BaseModel):
    name: Optional[str] = None
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    route: Optional[str] = None
    purpose: Optional[str] = None
    instructions: Optional[str] = None
    reminder_enabled: Optional[bool] = None
    reminder_times: Optional[List[str]] = None
    is_active: Optional[bool] = None
    refills_remaining: Optional[int] = None


class MedicationResponse(MedicationBase):
    id: int
    user_id: int
    start_date: datetime
    end_date: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Medication Dose Schemas
# ============================================================================

class MedicationDoseCreate(BaseModel):
    medication_id: int
    scheduled_time: datetime


class MedicationDoseUpdate(BaseModel):
    taken_time: Optional[datetime] = None
    status: str  # taken, missed, skipped
    notes: Optional[str] = None


class MedicationDoseResponse(BaseModel):
    id: int
    medication_id: int
    scheduled_time: datetime
    taken_time: Optional[datetime]
    status: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Symptom Log Schemas
# ============================================================================

class SymptomLogCreate(BaseModel):
    user_id: int
    symptom: str
    severity: int = Field(ge=1, le=10)
    duration: Optional[str] = None
    triggers: Optional[List[str]] = None
    location: Optional[str] = None
    description: Optional[str] = None
    related_medication_id: Optional[int] = None


class SymptomLogResponse(BaseModel):
    id: int
    user_id: int
    symptom: str
    severity: int
    duration: Optional[str]
    triggers: Optional[List[str]]
    location: Optional[str]
    description: Optional[str]
    related_medication_id: Optional[int]
    logged_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Vital Sign Schemas
# ============================================================================

class VitalSignCreate(BaseModel):
    user_id: int
    measurement_type: str  # blood_pressure, glucose, temperature, heart_rate, weight, etc.

    # For blood pressure
    systolic: Optional[int] = None
    diastolic: Optional[int] = None

    # For single value measurements
    value: Optional[float] = None
    unit: Optional[str] = None

    notes: Optional[str] = None
    measured_at: Optional[datetime] = None


class VitalSignResponse(BaseModel):
    id: int
    user_id: int
    measurement_type: str
    systolic: Optional[int]
    diastolic: Optional[int]
    value: Optional[float]
    unit: Optional[str]
    measured_at: datetime
    notes: Optional[str]
    is_abnormal: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# Care Plan Schemas
# ============================================================================

class CarePlanCreate(BaseModel):
    user_id: int
    title: str
    condition: Optional[str] = None
    goals: Optional[List[dict]] = None
    medications: Optional[List[int]] = None
    dietary_restrictions: Optional[List[str]] = None
    exercise_plan: Optional[str] = None
    primary_provider: Optional[str] = None
    care_team: Optional[List[dict]] = None
    vital_signs_to_track: Optional[List[str]] = None
    target_ranges: Optional[dict] = None
    emergency_contacts: Optional[List[dict]] = None
    emergency_instructions: Optional[str] = None
    created_by: Optional[str] = None


class CarePlanUpdate(BaseModel):
    title: Optional[str] = None
    condition: Optional[str] = None
    status: Optional[str] = None
    goals: Optional[List[dict]] = None
    medications: Optional[List[int]] = None
    dietary_restrictions: Optional[List[str]] = None
    exercise_plan: Optional[str] = None
    vital_signs_to_track: Optional[List[str]] = None
    target_ranges: Optional[dict] = None
    next_appointment: Optional[datetime] = None
    review_date: Optional[datetime] = None


class CarePlanResponse(BaseModel):
    id: int
    user_id: int
    title: str
    condition: Optional[str]
    status: str
    goals: Optional[List[dict]]
    medications: Optional[List[int]]
    dietary_restrictions: Optional[List[str]]
    exercise_plan: Optional[str]
    primary_provider: Optional[str]
    care_team: Optional[List[dict]]
    vital_signs_to_track: Optional[List[str]]
    target_ranges: Optional[dict]
    next_appointment: Optional[datetime]
    review_date: Optional[datetime]
    emergency_contacts: Optional[List[dict]]
    emergency_instructions: Optional[str]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True


# ============================================================================
# Health Goal Schemas
# ============================================================================

class HealthGoalCreate(BaseModel):
    user_id: int
    care_plan_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    target_value: Optional[float] = None
    target_unit: Optional[str] = None
    target_date: Optional[datetime] = None


class HealthGoalUpdate(BaseModel):
    current_value: Optional[float] = None
    progress_percentage: Optional[float] = None
    status: Optional[str] = None
    milestones: Optional[List[dict]] = None


class HealthGoalResponse(BaseModel):
    id: int
    user_id: int
    care_plan_id: Optional[int]
    title: str
    description: Optional[str]
    category: Optional[str]
    target_value: Optional[float]
    target_unit: Optional[str]
    target_date: Optional[datetime]
    current_value: Optional[float]
    progress_percentage: float
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============================================================================
# Dashboard Summary Schemas
# ============================================================================

class MedicationAdherenceStats(BaseModel):
    total_doses_scheduled: int
    doses_taken: int
    doses_missed: int
    adherence_percentage: float
    upcoming_doses_today: int


class HealthDashboardSummary(BaseModel):
    user_id: int
    active_medications_count: int
    recent_symptoms_count: int
    active_care_plans_count: int
    medication_adherence: MedicationAdherenceStats
    recent_vitals: List[VitalSignResponse]
    upcoming_appointments: List[datetime]
    health_goals_progress: List[HealthGoalResponse]
