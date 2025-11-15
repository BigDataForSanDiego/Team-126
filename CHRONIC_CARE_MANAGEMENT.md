# Chronic Care Management System 🏥

Complete health management system for tracking medications, symptoms, vital signs, and care plans for individuals experiencing homelessness.

## 📋 Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Frontend Components](#frontend-components)
- [Database Schema](#database-schema)
- [Getting Started](#getting-started)
- [Usage Examples](#usage-examples)

---

## 🎯 Features

### 1. Medication Tracking & Reminders 💊
- **Add and manage medications** with dosage, frequency, and instructions
- **Automated reminder scheduling** with customizable times
- **Dose tracking** - Record when medications are taken, missed, or skipped
- **Adherence analytics** - Calculate medication compliance percentage
- **Refill tracking** - Monitor remaining refills
- **Provider and pharmacy information** - Store prescribing provider and pharmacy details

### 2. Symptom Logger 📋
- **Log symptoms** with severity (1-10 scale), duration, and description
- **Track triggers** - Identify potential symptom causes
- **Trend analysis** - View symptom patterns over time
- **Medication correlation** - Link symptoms to specific medications
- **Severity alerts** - Automatic alerts for severe symptoms (8+)

### 3. Vital Signs Tracking ❤️
- **Blood Pressure** - Systolic/diastolic tracking
- **Blood Glucose** - Monitor diabetic health
- **Temperature** - Track fevers and infections
- **Heart Rate** - Monitor cardiovascular health
- **Weight** - Track weight changes
- **Oxygen Saturation** - Monitor respiratory health
- **Abnormality detection** - Automatic flagging of out-of-range readings
- **Historical charts** - Visualize trends over time

### 4. Care Plan Management 📖
- **Comprehensive care plans** - Manage multiple health conditions
- **Goal setting** - Track health goals with progress tracking
- **Care team coordination** - List providers and their roles
- **Appointment scheduling** - Track upcoming medical appointments
- **Dietary restrictions** - Document food allergies and restrictions
- **Exercise plans** - Create and track exercise routines
- **Emergency contacts** - Store emergency contact information

---

## 🏗️ Architecture

### Backend (FastAPI + PostgreSQL)

```
backend/
├── health_models.py      # SQLAlchemy models for health data
├── health_schemas.py     # Pydantic validation schemas
├── health_api.py         # API endpoints for health management
└── main.py              # Include health router
```

### Frontend (React + TypeScript)

```
frontend/src/
├── pages/
│   └── HealthDashboard.tsx        # Main health dashboard
└── styles/
    └── HealthDashboard.css        # Dashboard styling
```

### Database Tables

- `medications` - Medication records
- `medication_doses` - Individual dose tracking
- `symptom_logs` - Symptom entries
- `vital_signs` - Vital sign measurements
- `care_plans` - Care plan documents
- `health_goals` - Goal tracking
- `health_notes` - General health notes

---

## 📡 API Documentation

### Medication Endpoints

#### Create Medication
```http
POST /api/health/medications
Content-Type: application/json

{
  "user_id": 1,
  "name": "Metformin",
  "dosage": "500mg",
  "frequency": "twice daily",
  "reminder_times": ["08:00", "20:00"],
  "purpose": "Diabetes management"
}
```

#### Get Medications
```http
GET /api/health/medications?user_id=1&active_only=true
```

#### Record Dose Taken
```http
POST /api/health/medications/doses/record?dose_id=123
Content-Type: application/json

{
  "status": "taken",
  "taken_time": "2025-11-14T08:05:00Z",
  "notes": "Took with breakfast"
}
```

#### Get Upcoming Doses
```http
GET /api/health/medications/doses/upcoming?user_id=1&hours=24
```

### Symptom Endpoints

#### Log Symptom
```http
POST /api/health/symptoms
Content-Type: application/json

{
  "user_id": 1,
  "symptom": "headache",
  "severity": 7,
  "duration": "3 hours",
  "triggers": ["stress", "lack of sleep"],
  "description": "Throbbing pain in temples"
}
```

#### Get Symptom Trends
```http
GET /api/health/symptoms/trends?user_id=1&days=30
```

Returns:
```json
[
  {
    "symptom": "headache",
    "count": 12,
    "avg_severity": 6.5,
    "max_severity": 9
  }
]
```

### Vital Signs Endpoints

#### Record Blood Pressure
```http
POST /api/health/vitals
Content-Type: application/json

{
  "user_id": 1,
  "measurement_type": "blood_pressure",
  "systolic": 130,
  "diastolic": 85,
  "notes": "Morning reading"
}
```

#### Record Blood Glucose
```http
POST /api/health/vitals
Content-Type: application/json

{
  "user_id": 1,
  "measurement_type": "glucose",
  "value": 120,
  "unit": "mg/dL",
  "notes": "2 hours after meal"
}
```

#### Get Latest Vitals
```http
GET /api/health/vitals/latest?user_id=1
```

### Care Plan Endpoints

#### Create Care Plan
```http
POST /api/health/care-plans
Content-Type: application/json

{
  "user_id": 1,
  "title": "Diabetes Management Plan",
  "condition": "Type 2 Diabetes",
  "goals": [
    {"description": "Maintain A1C below 7%", "target_date": "2026-06-01"}
  ],
  "vital_signs_to_track": ["glucose", "blood_pressure", "weight"],
  "target_ranges": {
    "glucose": {"min": 70, "max": 130},
    "blood_pressure_systolic": {"max": 130}
  },
  "primary_provider": "Dr. Smith",
  "emergency_contacts": [
    {"name": "Emergency Services", "phone": "911"}
  ]
}
```

### Dashboard Endpoint

#### Get Complete Health Dashboard
```http
GET /api/health/dashboard/1
```

Returns comprehensive summary:
```json
{
  "user_id": 1,
  "active_medications_count": 3,
  "recent_symptoms_count": 5,
  "active_care_plans_count": 2,
  "medication_adherence": {
    "total_doses_scheduled": 42,
    "doses_taken": 39,
    "doses_missed": 3,
    "adherence_percentage": 92.9,
    "upcoming_doses_today": 2
  },
  "recent_vitals": [...],
  "upcoming_appointments": [...],
  "health_goals_progress": [...]
}
```

---

## 🎨 Frontend Components

### Health Dashboard

The `HealthDashboard` component provides a tabbed interface with:

1. **Overview Tab**
   - Quick stats cards
   - Health goals progress
   - Recent vitals chart

2. **Medications Tab**
   - List of all medications
   - Add new medication form
   - Medication adherence tracking

3. **Symptoms Tab**
   - Symptom log with severity visualization
   - Add symptom form with severity slider
   - Color-coded severity badges (green/orange/red)

4. **Vital Signs Tab**
   - Recent vital measurements
   - Add vital sign form with type selector
   - Abnormal reading alerts

5. **Care Plans Tab**
   - Active care plans
   - Appointment reminders
   - Care team information

### Features

- **Modal Forms** - Clean overlay modals for adding data
- **Real-time Updates** - Data refreshes after each action
- **Color-coded Indicators** - Visual severity and status indicators
- **Responsive Design** - Works on mobile and desktop
- **Severity Visualization** - Progress bars and color-coded badges

---

## 🗄️ Database Schema

### Medications Table
```sql
CREATE TABLE medications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    name VARCHAR NOT NULL,
    dosage VARCHAR,
    frequency VARCHAR,
    route VARCHAR,
    purpose TEXT,
    instructions TEXT,
    side_effects TEXT,
    start_date TIMESTAMP DEFAULT NOW(),
    end_date TIMESTAMP,
    reminder_enabled BOOLEAN DEFAULT TRUE,
    reminder_times JSON,
    is_active BOOLEAN DEFAULT TRUE,
    prescribing_provider VARCHAR,
    pharmacy VARCHAR,
    refills_remaining INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Medication Doses Table
```sql
CREATE TABLE medication_doses (
    id SERIAL PRIMARY KEY,
    medication_id INTEGER NOT NULL REFERENCES medications(id) ON DELETE CASCADE,
    scheduled_time TIMESTAMP NOT NULL,
    taken_time TIMESTAMP,
    status VARCHAR DEFAULT 'scheduled',  -- scheduled, taken, missed, skipped
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Symptom Logs Table
```sql
CREATE TABLE symptom_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    symptom VARCHAR NOT NULL,
    severity INTEGER CHECK (severity >= 1 AND severity <= 10),
    duration VARCHAR,
    triggers JSON,
    location VARCHAR,
    description TEXT,
    related_medication_id INTEGER REFERENCES medications(id),
    photo_url VARCHAR,
    logged_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Vital Signs Table
```sql
CREATE TABLE vital_signs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    measurement_type VARCHAR NOT NULL,
    systolic INTEGER,         -- For blood pressure
    diastolic INTEGER,        -- For blood pressure
    value FLOAT,             -- For single-value measurements
    unit VARCHAR,
    measured_at TIMESTAMP DEFAULT NOW(),
    notes TEXT,
    location VARCHAR,
    is_abnormal BOOLEAN DEFAULT FALSE,
    alert_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Care Plans Table
```sql
CREATE TABLE care_plans (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    title VARCHAR NOT NULL,
    condition VARCHAR,
    status VARCHAR DEFAULT 'active',
    goals JSON,
    medications JSON,
    dietary_restrictions JSON,
    exercise_plan TEXT,
    primary_provider VARCHAR,
    care_team JSON,
    vital_signs_to_track JSON,
    target_ranges JSON,
    next_appointment TIMESTAMP,
    review_date TIMESTAMP,
    emergency_contacts JSON,
    emergency_instructions TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    created_by VARCHAR
);
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- PostgreSQL with pgvector extension
- Node.js 16+
- React development environment

### Backend Setup

1. **Install Dependencies**
```bash
cd backend
pip install -r requirements.txt
```

2. **Start PostgreSQL Database**
```bash
docker-compose up -d
```

3. **Create Health Tables**
```bash
# Tables are automatically created when the server starts
python main.py
```

4. **Start Backend Server**
```bash
./start-backend.sh
# Or manually:
cd backend
source venv/bin/activate
python main.py
```

### Frontend Setup

1. **Install Dependencies**
```bash
cd frontend
npm install
```

2. **Start Development Server**
```bash
npm run dev
```

3. **Access Dashboard**
```
Navigate to: http://localhost:5173/health-dashboard
```

---

## 💡 Usage Examples

### Example 1: Track Diabetes Medication

```typescript
// Add insulin medication
await api.post('/api/health/medications', {
  user_id: 1,
  name: 'Insulin Glargine',
  dosage: '20 units',
  frequency: 'once daily',
  route: 'injection',
  reminder_times: ['22:00'],
  purpose: 'Type 1 Diabetes - basal insulin',
  prescribing_provider: 'Dr. Johnson',
  refills_remaining: 2
})

// Record blood glucose
await api.post('/api/health/vitals', {
  user_id: 1,
  measurement_type: 'glucose',
  value: 110,
  unit: 'mg/dL',
  notes: 'Before breakfast'
})
```

### Example 2: Manage Hypertension

```typescript
// Create care plan
await api.post('/api/health/care-plans', {
  user_id: 1,
  title: 'Hypertension Management',
  condition: 'High Blood Pressure',
  vital_signs_to_track: ['blood_pressure', 'heart_rate', 'weight'],
  target_ranges: {
    blood_pressure_systolic: { max: 130 },
    blood_pressure_diastolic: { max: 80 }
  },
  dietary_restrictions: ['Low sodium', 'DASH diet'],
  exercise_plan: '30 minutes walking, 5 days/week'
})

// Track blood pressure
await api.post('/api/health/vitals', {
  user_id: 1,
  measurement_type: 'blood_pressure',
  systolic: 128,
  diastolic: 82
})
```

### Example 3: Log Side Effects

```typescript
// Log medication side effect
await api.post('/api/health/symptoms', {
  user_id: 1,
  symptom: 'nausea',
  severity: 6,
  duration: '2 hours',
  related_medication_id: 15,  // Link to medication
  description: 'Felt nauseous 30 minutes after taking medication',
  triggers: ['medication']
})
```

---

## 🔐 Security & Privacy

- **Encrypted health data** - Sensitive information encrypted at rest
- **HIPAA considerations** - Follow HIPAA guidelines for PHI
- **Access control** - User-specific data isolation
- **Audit logging** - Track all health data modifications

---

## 📊 Analytics & Insights

### Medication Adherence
- Calculate daily, weekly, monthly adherence rates
- Identify patterns in missed doses
- Generate adherence reports for providers

### Symptom Trends
- Track symptom frequency over time
- Correlation analysis with medications
- Severity trend visualization

### Vital Sign Monitoring
- Detect abnormal readings automatically
- Alert on critical values
- Generate charts for provider visits

---

## 🔜 Future Enhancements

1. **Medication Reminders**
   - SMS/Push notifications
   - Voice reminders
   - Medication photos for identification

2. **Telehealth Integration**
   - Video consultations
   - Secure messaging with providers
   - Appointment scheduling

3. **Health Goal Gamification**
   - Achievement badges
   - Streaks for adherence
   - Progress rewards

4. **Export & Sharing**
   - PDF health reports
   - Share with providers
   - Email summaries

5. **AI-Powered Insights**
   - Predict symptom triggers
   - Medication interaction warnings
   - Personalized health tips

---

## 📞 Support

For questions or issues:
- Check the [API Documentation](#api-documentation)
- Review [Usage Examples](#usage-examples)
- Contact your healthcare provider for medical concerns

---

**Note**: This system is designed to support chronic care management but does NOT replace professional medical advice. Always consult healthcare providers for medical decisions.
