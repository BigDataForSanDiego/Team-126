# Guest Mode Health Tracking 🏥

## Overview

The health tracking system works seamlessly in **guest mode** (no login required). All health data tracked during a conversation is automatically included in the conversation report when it's generated.

## How It Works

### 1. **Guest Users Can Track Health Data**

In guest mode, users can:
- Add medications with dosages and schedules
- Log symptoms with severity ratings
- Record vital signs (blood pressure, glucose, etc.)
- Create care plans
- Set health goals

**No authentication required** - the system uses the `conversation_id` as the `user_id` internally.

### 2. **Health Data is Highlighted in Reports**

When a conversation report is generated, any health data tracked during that session is automatically included in a special section:

```markdown
## 🏥 Health Tracking Summary (Guest Mode)
**Important**: The following health data was tracked during this conversation session.
This information should be highlighted for healthcare providers.

**Note**: This health information was self-reported during the conversation
and should be verified by healthcare professionals.

### 💊 Medications Tracked
- **Metformin** (500mg)
  - Frequency: twice daily
  - Purpose: Diabetes management
  - Reminder times: 08:00, 20:00

### 📋 Symptoms Logged
- 🟡 **headache** (Severity: 6/10)
  - Duration: 3 hours
  - Notes: Throbbing pain, stress-related
  - Logged: 2025-11-14 10:30

### ❤️ Vital Signs Recorded
- **Blood Pressure**: 130/85 mmHg
  - Measured: 2025-11-14 09:00
  - Notes: Morning reading

### 📖 Active Care Plans
- **Diabetes Management Plan**
  - Condition: Type 2 Diabetes
  - Provider: Dr. Smith
  - Next Appointment: 2025-12-01
```

---

## API Usage Examples

### Track Medication (Guest Mode)

```bash
curl -X POST http://localhost:8000/api/health/medications \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "name": "Aspirin",
    "dosage": "81mg",
    "frequency": "once daily",
    "reminder_times": ["08:00"]
  }'
```

**Note**: For guest mode, use the `conversation_id` as the `user_id`.

### Log Symptom (Guest Mode)

```bash
curl -X POST http://localhost:8000/api/health/symptoms \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "symptom": "chest pain",
    "severity": 8,
    "duration": "30 minutes",
    "description": "Sharp pain, radiating to left arm"
  }'
```

### Record Vital Sign (Guest Mode)

```bash
curl -X POST http://localhost:8000/api/health/vitals \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 123,
    "measurement_type": "blood_pressure",
    "systolic": 140,
    "diastolic": 90,
    "notes": "Feeling dizzy"
  }'
```

### Generate Report with Health Data

```bash
curl -X POST http://localhost:8000/conversations/123/report
```

The report will automatically include all health data tracked during conversation #123.

---

## Frontend Integration

### Using Health Dashboard in Guest Mode

```typescript
// In your chat component or health dashboard
const conversationId = 123; // Current conversation ID

// Track medication
await api.post('/api/health/medications', {
  user_id: conversationId,  // Use conversation ID as user ID
  name: 'Insulin',
  dosage: '10 units',
  frequency: 'twice daily'
});

// Log symptom
await api.post('/api/health/symptoms', {
  user_id: conversationId,
  symptom: 'nausea',
  severity: 5,
  duration: '2 hours'
});

// Generate report (includes health data)
const report = await api.post(`/conversations/${conversationId}/report`);
console.log(report.data.report); // Contains health tracking section
```

---

## Report Structure

The conversation report includes health data in this order:

1. **Executive Summary**
2. **User Requirements and Requests**
3. **Resources and Services Provided**
4. **Additional Recommendations**
5. **Action Items**
6. **Follow-up Information**
7. **🏥 Health Tracking Summary (Guest Mode)** ← **HIGHLIGHTED SECTION**
   - Medications Tracked
   - Symptoms Logged
   - Vital Signs Recorded
   - Active Care Plans

---

## Example Complete Report

```markdown
# Assistance Report

## Executive Summary
User sought help with managing diabetes and finding nearby health services...

## User Requirements and Requests
- Emergency insulin supply needed
- Blood glucose monitoring assistance
- Diabetes management guidance

## Resources and Services Provided
- **Community Health Clinic**: Free diabetes care and insulin...
- **Pharmacy Assistance Program**: Help obtaining insulin...

## Additional Recommendations
- Regular blood glucose monitoring
- Dietary consultation recommended

## Action Items
1. Visit Community Health Clinic at 123 Main St
2. Call pharmacy assistance program: (555) 123-4567
3. Schedule follow-up appointment

## Follow-up Information
- Follow up in 2 weeks
- Emergency contact: 911
- Clinic hours: Mon-Fri 8am-5pm

## 🏥 Health Tracking Summary (Guest Mode)
**Important**: The following health data was tracked during this conversation session.
This information should be highlighted for healthcare providers.

**Note**: This health information was self-reported during the conversation
and should be verified by healthcare professionals.

### 💊 Medications Tracked
- **Insulin Glargine** (20 units)
  - Frequency: once daily
  - Purpose: Type 1 Diabetes - basal insulin
  - Reminder times: 22:00

### 📋 Symptoms Logged
- 🔴 **dizziness** (Severity: 8/10)
  - Duration: 1 hour
  - Notes: After missing insulin dose
  - Logged: 2025-11-14 14:30

- 🟡 **fatigue** (Severity: 6/10)
  - Duration: all day
  - Logged: 2025-11-14 10:00

### ❤️ Vital Signs Recorded
- **Blood Glucose**: 280 mg/dL ⚠️ **ABNORMAL**
  - Measured: 2025-11-14 14:00
  - Notes: Before seeking help

- **Blood Pressure**: 125/80 mmHg
  - Measured: 2025-11-14 14:00

### 📖 Active Care Plans
- **Diabetes Management Plan**
  - Condition: Type 1 Diabetes
  - Provider: Dr. Johnson
  - Next Appointment: 2025-11-25
```

---

## Key Benefits

### For Users (Guest Mode)
✅ **No login required** - Immediate access to health tracking
✅ **All data included in report** - Comprehensive health summary
✅ **Easy to share** - Give printed/emailed report to healthcare providers
✅ **Highlights critical info** - Abnormal vitals clearly marked

### For Healthcare Providers
✅ **Complete picture** - All health data in one place
✅ **Verified context** - Linked to conversation about resources
✅ **Actionable information** - Medications, symptoms, and vitals clearly listed
✅ **Professional format** - Well-formatted markdown report

### For Social Workers
✅ **Holistic view** - Health needs alongside resource needs
✅ **Better referrals** - Can match health conditions to appropriate services
✅ **Documentation** - Complete record of assistance provided

---

## Technical Implementation

### Backend Flow

1. **User tracks health data**
   ```python
   POST /api/health/medications
   # user_id = conversation_id
   ```

2. **Data stored in database**
   ```python
   medication = Medication(
       user_id=conversation_id,  # Guest mode
       name="Aspirin",
       ...
   )
   db.add(medication)
   db.commit()
   ```

3. **Report generation includes health data**
   ```python
   report = await generate_conversation_report(
       messages,
       conversation_id=conversation_id,  # Fetch health data
       db=db
   )
   ```

4. **Health summary fetched and formatted**
   ```python
   health_summary = await get_health_summary(conversation_id, db)
   # Returns formatted markdown with all health data
   ```

5. **Combined into final report**
   ```python
   # Health section automatically inserted into report template
   formatted_report = template.format(health_section=health_summary)
   ```

### Frontend Flow

```typescript
// 1. User interacts with health dashboard
<HealthDashboard />

// 2. Health data saved with conversation_id
await api.post('/api/health/medications', {
  user_id: conversationId,
  ...
})

// 3. Report generated at end of conversation
const report = await api.post(`/conversations/${conversationId}/report`)

// 4. Display or download report with health data
console.log(report.data.report) // Includes health tracking section
```

---

## Privacy & Security Notes

⚠️ **Important Considerations**:

1. **Guest Mode Data Retention**
   - Data persists for the conversation session
   - Consider implementing auto-deletion after report generation
   - Or allow users to optionally save data by creating an account

2. **HIPAA Compliance**
   - Guest mode health data may need special handling
   - Ensure reports are transmitted securely (HTTPS)
   - Consider encryption for sensitive health information

3. **User Consent**
   - Display clear notice that health data will be included in reports
   - Allow users to review before finalizing report
   - Provide option to exclude health data from report

---

## Future Enhancements

1. **Export Options**
   - PDF export with health data highlighted
   - Email report directly to provider
   - Print-friendly format

2. **Data Persistence Options**
   - "Save this data" - create account to keep tracking
   - QR code with encrypted health data
   - SMS summary of critical health info

3. **Integration Features**
   - Direct referral to health services based on conditions
   - Medication interaction warnings
   - Emergency alert if critical vitals logged

---

## Testing

### Test Health Tracking in Guest Mode

```bash
# 1. Start a conversation
curl -X POST http://localhost:8000/conversations \
  -d '{"user_id": null}' # Guest mode

# 2. Track some health data (use conversation ID as user_id)
curl -X POST http://localhost:8000/api/health/medications \
  -d '{"user_id": 1, "name": "Aspirin", "dosage": "81mg"}'

curl -X POST http://localhost:8000/api/health/symptoms \
  -d '{"user_id": 1, "symptom": "headache", "severity": 5}'

# 3. Generate report
curl -X POST http://localhost:8000/conversations/1/report

# 4. Verify health data is included in the report
```

---

## Summary

The guest mode health tracking system provides:
- ✅ **Zero friction** - No login/signup required
- ✅ **Comprehensive tracking** - Medications, symptoms, vitals, care plans
- ✅ **Automatic reporting** - Health data highlighted in conversation reports
- ✅ **Professional output** - Well-formatted for sharing with providers
- ✅ **Privacy-conscious** - Session-based, can be deleted after use

This makes it easy for individuals experiencing homelessness to track their health needs during a single conversation and receive a complete report they can share with healthcare providers or social workers.
