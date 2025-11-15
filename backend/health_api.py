"""
Health and Chronic Care Management API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from health_models import (
    Medication, MedicationDose, SymptomLog, VitalSign,
    CarePlan, HealthGoal, HealthNote
)
from health_schemas import (
    MedicationCreate, MedicationUpdate, MedicationResponse,
    MedicationDoseCreate, MedicationDoseUpdate, MedicationDoseResponse,
    SymptomLogCreate, SymptomLogResponse,
    VitalSignCreate, VitalSignResponse,
    CarePlanCreate, CarePlanUpdate, CarePlanResponse,
    HealthGoalCreate, HealthGoalUpdate, HealthGoalResponse,
    HealthDashboardSummary, MedicationAdherenceStats
)

router = APIRouter(prefix="/api/health", tags=["health"])


# ============================================================================
# MEDICATION ENDPOINTS
# ============================================================================

@router.post("/medications", response_model=MedicationResponse)
async def create_medication(medication: MedicationCreate, db: Session = Depends(get_db)):
    """Create a new medication entry"""
    db_medication = Medication(**medication.dict())
    db.add(db_medication)
    db.commit()
    db.refresh(db_medication)

    # Generate reminder schedule if enabled
    if medication.reminder_enabled and medication.reminder_times:
        generate_medication_reminders(db, db_medication)

    return db_medication


@router.get("/medications", response_model=List[MedicationResponse])
async def get_medications(
    user_id: int,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all medications for a user"""
    query = db.query(Medication).filter(Medication.user_id == user_id)

    if active_only:
        query = query.filter(Medication.is_active == True)

    return query.order_by(Medication.created_at.desc()).all()


@router.get("/medications/{medication_id}", response_model=MedicationResponse)
async def get_medication(medication_id: int, db: Session = Depends(get_db)):
    """Get a specific medication"""
    medication = db.query(Medication).filter(Medication.id == medication_id).first()
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")
    return medication


@router.patch("/medications/{medication_id}", response_model=MedicationResponse)
async def update_medication(
    medication_id: int,
    medication_update: MedicationUpdate,
    db: Session = Depends(get_db)
):
    """Update a medication"""
    medication = db.query(Medication).filter(Medication.id == medication_id).first()
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")

    for field, value in medication_update.dict(exclude_unset=True).items():
        setattr(medication, field, value)

    db.commit()
    db.refresh(medication)
    return medication


@router.delete("/medications/{medication_id}")
async def delete_medication(medication_id: int, db: Session = Depends(get_db)):
    """Delete a medication"""
    medication = db.query(Medication).filter(Medication.id == medication_id).first()
    if not medication:
        raise HTTPException(status_code=404, detail="Medication not found")

    db.delete(medication)
    db.commit()
    return {"message": "Medication deleted successfully"}


# ============================================================================
# MEDICATION DOSE TRACKING
# ============================================================================

@router.post("/medications/doses/record")
async def record_medication_dose(
    dose_update: MedicationDoseUpdate,
    dose_id: int,
    db: Session = Depends(get_db)
):
    """Record that a medication dose was taken"""
    dose = db.query(MedicationDose).filter(MedicationDose.id == dose_id).first()
    if not dose:
        raise HTTPException(status_code=404, detail="Dose not found")

    dose.taken_time = dose_update.taken_time or datetime.utcnow()
    dose.status = dose_update.status
    dose.notes = dose_update.notes

    db.commit()
    db.refresh(dose)
    return dose


@router.get("/medications/{medication_id}/doses", response_model=List[MedicationDoseResponse])
async def get_medication_doses(
    medication_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """Get dose history for a medication"""
    query = db.query(MedicationDose).filter(MedicationDose.medication_id == medication_id)

    if start_date:
        query = query.filter(MedicationDose.scheduled_time >= start_date)
    if end_date:
        query = query.filter(MedicationDose.scheduled_time <= end_date)

    return query.order_by(MedicationDose.scheduled_time.desc()).all()


@router.get("/medications/doses/upcoming")
async def get_upcoming_doses(
    user_id: int,
    hours: int = 24,
    db: Session = Depends(get_db)
):
    """Get upcoming medication doses for the next N hours"""
    now = datetime.utcnow()
    end_time = now + timedelta(hours=hours)

    doses = db.query(MedicationDose).join(Medication).filter(
        and_(
            Medication.user_id == user_id,
            Medication.is_active == True,
            MedicationDose.scheduled_time >= now,
            MedicationDose.scheduled_time <= end_time,
            MedicationDose.status == "scheduled"
        )
    ).order_by(MedicationDose.scheduled_time).all()

    return doses


# ============================================================================
# SYMPTOM LOGGING
# ============================================================================

@router.post("/symptoms", response_model=SymptomLogResponse)
async def log_symptom(symptom: SymptomLogCreate, db: Session = Depends(get_db)):
    """Log a new symptom"""
    db_symptom = SymptomLog(**symptom.dict())
    db.add(db_symptom)
    db.commit()
    db.refresh(db_symptom)

    # Check if symptom is severe and requires alert
    if symptom.severity >= 8:
        # TODO: Trigger alert to care team
        pass

    return db_symptom


@router.get("/symptoms", response_model=List[SymptomLogResponse])
async def get_symptoms(
    user_id: int,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    symptom_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get symptom logs for a user"""
    query = db.query(SymptomLog).filter(SymptomLog.user_id == user_id)

    if start_date:
        query = query.filter(SymptomLog.logged_at >= start_date)
    if end_date:
        query = query.filter(SymptomLog.logged_at <= end_date)
    if symptom_type:
        query = query.filter(SymptomLog.symptom.ilike(f"%{symptom_type}%"))

    return query.order_by(SymptomLog.logged_at.desc()).all()


@router.get("/symptoms/trends")
async def get_symptom_trends(
    user_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get symptom trends over time"""
    start_date = datetime.utcnow() - timedelta(days=days)

    # Group symptoms by type and calculate average severity
    trends = db.query(
        SymptomLog.symptom,
        func.count(SymptomLog.id).label('count'),
        func.avg(SymptomLog.severity).label('avg_severity'),
        func.max(SymptomLog.severity).label('max_severity')
    ).filter(
        and_(
            SymptomLog.user_id == user_id,
            SymptomLog.logged_at >= start_date
        )
    ).group_by(SymptomLog.symptom).all()

    return [{
        "symptom": trend[0],
        "count": trend[1],
        "avg_severity": round(trend[2], 1),
        "max_severity": trend[3]
    } for trend in trends]


# ============================================================================
# VITAL SIGNS TRACKING
# ============================================================================

@router.post("/vitals", response_model=VitalSignResponse)
async def record_vital_sign(vital: VitalSignCreate, db: Session = Depends(get_db)):
    """Record a new vital sign measurement"""
    db_vital = VitalSign(**vital.dict())

    # Check if measurement is abnormal
    db_vital.is_abnormal = check_vital_abnormality(vital)

    db.add(db_vital)
    db.commit()
    db.refresh(db_vital)

    # Alert if abnormal
    if db_vital.is_abnormal:
        # TODO: Send alert to user and care team
        pass

    return db_vital


@router.get("/vitals", response_model=List[VitalSignResponse])
async def get_vital_signs(
    user_id: int,
    measurement_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get vital sign measurements"""
    query = db.query(VitalSign).filter(VitalSign.user_id == user_id)

    if measurement_type:
        query = query.filter(VitalSign.measurement_type == measurement_type)
    if start_date:
        query = query.filter(VitalSign.measured_at >= start_date)
    if end_date:
        query = query.filter(VitalSign.measured_at <= end_date)

    return query.order_by(VitalSign.measured_at.desc()).limit(limit).all()


@router.get("/vitals/latest")
async def get_latest_vitals(user_id: int, db: Session = Depends(get_db)):
    """Get latest reading for each vital sign type"""
    # Subquery to get the latest measurement for each type
    latest_vitals = {}

    vital_types = ["blood_pressure", "glucose", "temperature", "heart_rate", "weight", "oxygen_saturation"]

    for vital_type in vital_types:
        latest = db.query(VitalSign).filter(
            and_(
                VitalSign.user_id == user_id,
                VitalSign.measurement_type == vital_type
            )
        ).order_by(VitalSign.measured_at.desc()).first()

        if latest:
            latest_vitals[vital_type] = latest

    return latest_vitals


# ============================================================================
# CARE PLAN MANAGEMENT
# ============================================================================

@router.post("/care-plans", response_model=CarePlanResponse)
async def create_care_plan(plan: CarePlanCreate, db: Session = Depends(get_db)):
    """Create a new care plan"""
    db_plan = CarePlan(**plan.dict())
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@router.get("/care-plans", response_model=List[CarePlanResponse])
async def get_care_plans(
    user_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get care plans for a user"""
    query = db.query(CarePlan).filter(CarePlan.user_id == user_id)

    if status:
        query = query.filter(CarePlan.status == status)

    return query.order_by(CarePlan.created_at.desc()).all()


@router.get("/care-plans/{plan_id}", response_model=CarePlanResponse)
async def get_care_plan(plan_id: int, db: Session = Depends(get_db)):
    """Get a specific care plan"""
    plan = db.query(CarePlan).filter(CarePlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Care plan not found")
    return plan


@router.patch("/care-plans/{plan_id}", response_model=CarePlanResponse)
async def update_care_plan(
    plan_id: int,
    plan_update: CarePlanUpdate,
    db: Session = Depends(get_db)
):
    """Update a care plan"""
    plan = db.query(CarePlan).filter(CarePlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Care plan not found")

    for field, value in plan_update.dict(exclude_unset=True).items():
        setattr(plan, field, value)

    db.commit()
    db.refresh(plan)
    return plan


# ============================================================================
# HEALTH GOALS
# ============================================================================

@router.post("/goals", response_model=HealthGoalResponse)
async def create_health_goal(goal: HealthGoalCreate, db: Session = Depends(get_db)):
    """Create a new health goal"""
    db_goal = HealthGoal(**goal.dict())
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


@router.get("/goals", response_model=List[HealthGoalResponse])
async def get_health_goals(
    user_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get health goals for a user"""
    query = db.query(HealthGoal).filter(HealthGoal.user_id == user_id)

    if status:
        query = query.filter(HealthGoal.status == status)

    return query.order_by(HealthGoal.created_at.desc()).all()


@router.patch("/goals/{goal_id}", response_model=HealthGoalResponse)
async def update_health_goal(
    goal_id: int,
    goal_update: HealthGoalUpdate,
    db: Session = Depends(get_db)
):
    """Update progress on a health goal"""
    goal = db.query(HealthGoal).filter(HealthGoal.id == goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    for field, value in goal_update.dict(exclude_unset=True).items():
        setattr(goal, field, value)

    # Mark as completed if achieved
    if goal.progress_percentage >= 100 and goal.status == "in_progress":
        goal.status = "achieved"
        goal.completed_at = datetime.utcnow()

    db.commit()
    db.refresh(goal)
    return goal


# ============================================================================
# DASHBOARD & ANALYTICS
# ============================================================================

@router.get("/dashboard/{user_id}", response_model=HealthDashboardSummary)
async def get_health_dashboard(user_id: int, db: Session = Depends(get_db)):
    """Get comprehensive health dashboard summary"""

    # Active medications count
    active_meds = db.query(func.count(Medication.id)).filter(
        and_(Medication.user_id == user_id, Medication.is_active == True)
    ).scalar()

    # Recent symptoms (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_symptoms = db.query(func.count(SymptomLog.id)).filter(
        and_(SymptomLog.user_id == user_id, SymptomLog.logged_at >= week_ago)
    ).scalar()

    # Active care plans
    active_plans = db.query(func.count(CarePlan.id)).filter(
        and_(CarePlan.user_id == user_id, CarePlan.status == "active")
    ).scalar()

    # Medication adherence
    adherence = calculate_medication_adherence(user_id, db)

    # Recent vitals (last 5 of each type)
    recent_vitals = db.query(VitalSign).filter(
        VitalSign.user_id == user_id
    ).order_by(VitalSign.measured_at.desc()).limit(10).all()

    # Health goals progress
    goals = db.query(HealthGoal).filter(
        and_(HealthGoal.user_id == user_id, HealthGoal.status == "in_progress")
    ).all()

    # Upcoming appointments
    upcoming = db.query(CarePlan.next_appointment).filter(
        and_(
            CarePlan.user_id == user_id,
            CarePlan.next_appointment >= datetime.utcnow()
        )
    ).order_by(CarePlan.next_appointment).limit(5).all()

    return HealthDashboardSummary(
        user_id=user_id,
        active_medications_count=active_meds,
        recent_symptoms_count=recent_symptoms,
        active_care_plans_count=active_plans,
        medication_adherence=adherence,
        recent_vitals=recent_vitals,
        upcoming_appointments=[apt[0] for apt in upcoming],
        health_goals_progress=goals
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def generate_medication_reminders(db: Session, medication: Medication):
    """Generate scheduled medication doses for reminders"""
    if not medication.reminder_times:
        return

    # Generate doses for the next 7 days
    for day in range(7):
        date = datetime.utcnow().date() + timedelta(days=day)
        for time_str in medication.reminder_times:
            hour, minute = map(int, time_str.split(':'))
            scheduled_time = datetime.combine(date, datetime.min.time().replace(hour=hour, minute=minute))

            dose = MedicationDose(
                medication_id=medication.id,
                scheduled_time=scheduled_time,
                status="scheduled"
            )
            db.add(dose)

    db.commit()


def check_vital_abnormality(vital: VitalSignCreate) -> bool:
    """Check if a vital sign measurement is abnormal"""
    abnormal_ranges = {
        "blood_pressure": lambda v: v.systolic > 140 or v.systolic < 90 or v.diastolic > 90 or v.diastolic < 60,
        "glucose": lambda v: v.value > 180 or v.value < 70,
        "temperature": lambda v: v.value > 100.4 or v.value < 96.8,
        "heart_rate": lambda v: v.value > 100 or v.value < 60,
        "oxygen_saturation": lambda v: v.value < 95,
    }

    check = abnormal_ranges.get(vital.measurement_type)
    if check:
        return check(vital)

    return False


def calculate_medication_adherence(user_id: int, db: Session) -> MedicationAdherenceStats:
    """Calculate medication adherence statistics"""
    # Get doses from last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    doses = db.query(MedicationDose).join(Medication).filter(
        and_(
            Medication.user_id == user_id,
            MedicationDose.scheduled_time >= thirty_days_ago,
            MedicationDose.scheduled_time <= datetime.utcnow()
        )
    ).all()

    total = len(doses)
    taken = len([d for d in doses if d.status == "taken"])
    missed = len([d for d in doses if d.status == "missed"])

    # Upcoming doses today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start + timedelta(days=1)

    upcoming_today = db.query(func.count(MedicationDose.id)).join(Medication).filter(
        and_(
            Medication.user_id == user_id,
            MedicationDose.scheduled_time >= datetime.utcnow(),
            MedicationDose.scheduled_time < today_end,
            MedicationDose.status == "scheduled"
        )
    ).scalar()

    adherence_pct = (taken / total * 100) if total > 0 else 0

    return MedicationAdherenceStats(
        total_doses_scheduled=total,
        doses_taken=taken,
        doses_missed=missed,
        adherence_percentage=round(adherence_pct, 1),
        upcoming_doses_today=upcoming_today
    )
