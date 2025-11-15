import React, { useState, useEffect } from 'react'
import { api } from '../api/client'
import '../styles/HealthDashboard.css'

interface Medication {
  id: number
  name: string
  dosage: string
  frequency: string
  is_active: boolean
  reminder_times: string[]
}

interface Symptom {
  id: number
  symptom: string
  severity: number
  duration: string
  logged_at: string
}

interface VitalSign {
  id: number
  measurement_type: string
  value?: number
  systolic?: number
  diastolic?: number
  unit: string
  measured_at: string
  is_abnormal: boolean
}

interface CarePlan {
  id: number
  title: string
  condition: string
  status: string
  next_appointment?: string
}

interface HealthGoal {
  id: number
  title: string
  progress_percentage: number
  target_date?: string
  status: string
}

export function HealthDashboard() {
  const [userId] = useState(1) // Replace with actual user ID from auth
  const [medications, setMedications] = useState<Medication[]>([])
  const [symptoms, setSymptoms] = useState<Symptom[]>([])
  const [vitals, setVitals] = useState<VitalSign[]>([])
  const [carePlans, setCarePlans] = useState<CarePlan[]>([])
  const [goals, setGoals] = useState<HealthGoal[]>([])
  const [activeTab, setActiveTab] = useState('overview')

  // Medication form state
  const [showMedForm, setShowMedForm] = useState(false)
  const [newMed, setNewMed] = useState({
    name: '',
    dosage: '',
    frequency: '',
    reminder_times: ['08:00', '20:00']
  })

  // Symptom form state
  const [showSymptomForm, setShowSymptomForm] = useState(false)
  const [newSymptom, setNewSymptom] = useState({
    symptom: '',
    severity: 5,
    duration: '',
    description: ''
  })

  // Vital sign form state
  const [showVitalForm, setShowVitalForm] = useState(false)
  const [newVital, setNewVital] = useState({
    measurement_type: 'blood_pressure',
    systolic: '',
    diastolic: '',
    value: '',
    unit: ''
  })

  useEffect(() => {
    loadDashboardData()
  }, [userId])

  const loadDashboardData = async () => {
    try {
      // Load all health data
      const [medsRes, symptomsRes, vitalsRes, plansRes, goalsRes] = await Promise.all([
        api.get(`/api/health/medications?user_id=${userId}`),
        api.get(`/api/health/symptoms?user_id=${userId}`),
        api.get(`/api/health/vitals?user_id=${userId}&limit=10`),
        api.get(`/api/health/care-plans?user_id=${userId}`),
        api.get(`/api/health/goals?user_id=${userId}`)
      ])

      setMedications(medsRes.data)
      setSymptoms(symptomsRes.data)
      setVitals(vitalsRes.data)
      setCarePlans(plansRes.data)
      setGoals(goalsRes.data)
    } catch (error) {
      console.error('Error loading health dashboard:', error)
    }
  }

  const addMedication = async () => {
    try {
      await api.post('/api/health/medications', {
        user_id: userId,
        ...newMed
      })
      setShowMedForm(false)
      setNewMed({ name: '', dosage: '', frequency: '', reminder_times: ['08:00', '20:00'] })
      loadDashboardData()
    } catch (error) {
      console.error('Error adding medication:', error)
    }
  }

  const logSymptom = async () => {
    try {
      await api.post('/api/health/symptoms', {
        user_id: userId,
        ...newSymptom,
        triggers: []
      })
      setShowSymptomForm(false)
      setNewSymptom({ symptom: '', severity: 5, duration: '', description: '' })
      loadDashboardData()
    } catch (error) {
      console.error('Error logging symptom:', error)
    }
  }

  const recordVital = async () => {
    try {
      const vitalData: any = {
        user_id: userId,
        measurement_type: newVital.measurement_type
      }

      if (newVital.measurement_type === 'blood_pressure') {
        vitalData.systolic = parseInt(newVital.systolic)
        vitalData.diastolic = parseInt(newVital.diastolic)
      } else {
        vitalData.value = parseFloat(newVital.value)
        vitalData.unit = newVital.unit
      }

      await api.post('/api/health/vitals', vitalData)
      setShowVitalForm(false)
      setNewVital({ measurement_type: 'blood_pressure', systolic: '', diastolic: '', value: '', unit: '' })
      loadDashboardData()
    } catch (error) {
      console.error('Error recording vital:', error)
    }
  }

  const getSeverityColor = (severity: number) => {
    if (severity <= 3) return '#4caf50'
    if (severity <= 6) return '#ff9800'
    return '#f44336'
  }

  return (
    <div className="health-dashboard">
      <div className="dashboard-header">
        <h1>🏥 Health Management Dashboard</h1>
        <p>Track your medications, symptoms, and vital signs</p>
      </div>

      <div className="dashboard-tabs">
        <button
          className={activeTab === 'overview' ? 'active' : ''}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={activeTab === 'medications' ? 'active' : ''}
          onClick={() => setActiveTab('medications')}
        >
          Medications
        </button>
        <button
          className={activeTab === 'symptoms' ? 'active' : ''}
          onClick={() => setActiveTab('symptoms')}
        >
          Symptoms
        </button>
        <button
          className={activeTab === 'vitals' ? 'active' : ''}
          onClick={() => setActiveTab('vitals')}
        >
          Vital Signs
        </button>
        <button
          className={activeTab === 'care-plans' ? 'active' : ''}
          onClick={() => setActiveTab('care-plans')}
        >
          Care Plans
        </button>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div className="overview-content">
          <div className="stats-grid">
            <div className="stat-card">
              <h3>💊 Active Medications</h3>
              <p className="stat-number">{medications.filter(m => m.is_active).length}</p>
            </div>
            <div className="stat-card">
              <h3>📋 Symptoms Logged (7 days)</h3>
              <p className="stat-number">{symptoms.length}</p>
            </div>
            <div className="stat-card">
              <h3>❤️ Vital Readings</h3>
              <p className="stat-number">{vitals.length}</p>
            </div>
            <div className="stat-card">
              <h3>📖 Active Care Plans</h3>
              <p className="stat-number">{carePlans.filter(p => p.status === 'active').length}</p>
            </div>
          </div>

          {/* Health Goals Progress */}
          {goals.length > 0 && (
            <div className="goals-section">
              <h2>🎯 Health Goals</h2>
              {goals.map(goal => (
                <div key={goal.id} className="goal-item">
                  <div className="goal-header">
                    <h4>{goal.title}</h4>
                    <span>{goal.progress_percentage.toFixed(0)}%</span>
                  </div>
                  <div className="progress-bar">
                    <div
                      className="progress-fill"
                      style={{ width: `${goal.progress_percentage}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Recent Vitals Chart */}
          {vitals.length > 0 && (
            <div className="vitals-chart">
              <h2>📊 Recent Vital Signs</h2>
              {vitals.slice(0, 5).map(vital => (
                <div key={vital.id} className={`vital-reading ${vital.is_abnormal ? 'abnormal' : ''}`}>
                  <span className="vital-type">{vital.measurement_type.replace('_', ' ')}</span>
                  <span className="vital-value">
                    {vital.measurement_type === 'blood_pressure'
                      ? `${vital.systolic}/${vital.diastolic}`
                      : `${vital.value} ${vital.unit}`}
                  </span>
                  <span className="vital-date">
                    {new Date(vital.measured_at).toLocaleDateString()}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Medications Tab */}
      {activeTab === 'medications' && (
        <div className="medications-content">
          <div className="section-header">
            <h2>💊 My Medications</h2>
            <button className="add-btn" onClick={() => setShowMedForm(true)}>
              + Add Medication
            </button>
          </div>

          {showMedForm && (
            <div className="modal-overlay" onClick={() => setShowMedForm(false)}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <h3>Add New Medication</h3>
                <input
                  type="text"
                  placeholder="Medication Name"
                  value={newMed.name}
                  onChange={(e) => setNewMed({...newMed, name: e.target.value})}
                />
                <input
                  type="text"
                  placeholder="Dosage (e.g., 10mg)"
                  value={newMed.dosage}
                  onChange={(e) => setNewMed({...newMed, dosage: e.target.value})}
                />
                <input
                  type="text"
                  placeholder="Frequency (e.g., twice daily)"
                  value={newMed.frequency}
                  onChange={(e) => setNewMed({...newMed, frequency: e.target.value})}
                />
                <div className="modal-actions">
                  <button onClick={addMedication}>Save</button>
                  <button onClick={() => setShowMedForm(false)}>Cancel</button>
                </div>
              </div>
            </div>
          )}

          <div className="medications-list">
            {medications.map(med => (
              <div key={med.id} className="medication-card">
                <h3>{med.name}</h3>
                <p>Dosage: {med.dosage}</p>
                <p>Frequency: {med.frequency}</p>
                {med.reminder_times && med.reminder_times.length > 0 && (
                  <p>Reminders: {med.reminder_times.join(', ')}</p>
                )}
                <span className={`status-badge ${med.is_active ? 'active' : 'inactive'}`}>
                  {med.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Symptoms Tab */}
      {activeTab === 'symptoms' && (
        <div className="symptoms-content">
          <div className="section-header">
            <h2>📋 Symptom Log</h2>
            <button className="add-btn" onClick={() => setShowSymptomForm(true)}>
              + Log Symptom
            </button>
          </div>

          {showSymptomForm && (
            <div className="modal-overlay" onClick={() => setShowSymptomForm(false)}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <h3>Log New Symptom</h3>
                <input
                  type="text"
                  placeholder="Symptom (e.g., headache)"
                  value={newSymptom.symptom}
                  onChange={(e) => setNewSymptom({...newSymptom, symptom: e.target.value})}
                />
                <label>
                  Severity (1-10): {newSymptom.severity}
                  <input
                    type="range"
                    min="1"
                    max="10"
                    value={newSymptom.severity}
                    onChange={(e) => setNewSymptom({...newSymptom, severity: parseInt(e.target.value)})}
                  />
                </label>
                <input
                  type="text"
                  placeholder="Duration (e.g., 2 hours)"
                  value={newSymptom.duration}
                  onChange={(e) => setNewSymptom({...newSymptom, duration: e.target.value})}
                />
                <textarea
                  placeholder="Additional details..."
                  value={newSymptom.description}
                  onChange={(e) => setNewSymptom({...newSymptom, description: e.target.value})}
                />
                <div className="modal-actions">
                  <button onClick={logSymptom}>Save</button>
                  <button onClick={() => setShowSymptomForm(false)}>Cancel</button>
                </div>
              </div>
            </div>
          )}

          <div className="symptoms-list">
            {symptoms.map(symptom => (
              <div key={symptom.id} className="symptom-card">
                <div className="symptom-header">
                  <h3>{symptom.symptom}</h3>
                  <div
                    className="severity-badge"
                    style={{ backgroundColor: getSeverityColor(symptom.severity) }}
                  >
                    {symptom.severity}/10
                  </div>
                </div>
                <p>Duration: {symptom.duration}</p>
                <p className="symptom-date">
                  {new Date(symptom.logged_at).toLocaleString()}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Vital Signs Tab */}
      {activeTab === 'vitals' && (
        <div className="vitals-content">
          <div className="section-header">
            <h2>❤️ Vital Signs</h2>
            <button className="add-btn" onClick={() => setShowVitalForm(true)}>
              + Record Vital
            </button>
          </div>

          {showVitalForm && (
            <div className="modal-overlay" onClick={() => setShowVitalForm(false)}>
              <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <h3>Record Vital Sign</h3>
                <select
                  value={newVital.measurement_type}
                  onChange={(e) => setNewVital({...newVital, measurement_type: e.target.value})}
                >
                  <option value="blood_pressure">Blood Pressure</option>
                  <option value="glucose">Blood Glucose</option>
                  <option value="temperature">Temperature</option>
                  <option value="heart_rate">Heart Rate</option>
                  <option value="weight">Weight</option>
                  <option value="oxygen_saturation">Oxygen Saturation</option>
                </select>

                {newVital.measurement_type === 'blood_pressure' ? (
                  <>
                    <input
                      type="number"
                      placeholder="Systolic (e.g., 120)"
                      value={newVital.systolic}
                      onChange={(e) => setNewVital({...newVital, systolic: e.target.value})}
                    />
                    <input
                      type="number"
                      placeholder="Diastolic (e.g., 80)"
                      value={newVital.diastolic}
                      onChange={(e) => setNewVital({...newVital, diastolic: e.target.value})}
                    />
                  </>
                ) : (
                  <>
                    <input
                      type="number"
                      step="0.1"
                      placeholder="Value"
                      value={newVital.value}
                      onChange={(e) => setNewVital({...newVital, value: e.target.value})}
                    />
                    <input
                      type="text"
                      placeholder="Unit (e.g., mg/dL, °F)"
                      value={newVital.unit}
                      onChange={(e) => setNewVital({...newVital, unit: e.target.value})}
                    />
                  </>
                )}

                <div className="modal-actions">
                  <button onClick={recordVital}>Save</button>
                  <button onClick={() => setShowVitalForm(false)}>Cancel</button>
                </div>
              </div>
            </div>
          )}

          <div className="vitals-list">
            {vitals.map(vital => (
              <div key={vital.id} className={`vital-card ${vital.is_abnormal ? 'abnormal' : ''}`}>
                <h3>{vital.measurement_type.replace('_', ' ').toUpperCase()}</h3>
                <p className="vital-value">
                  {vital.measurement_type === 'blood_pressure'
                    ? `${vital.systolic}/${vital.diastolic}`
                    : `${vital.value} ${vital.unit}`}
                </p>
                <p className="vital-date">
                  {new Date(vital.measured_at).toLocaleString()}
                </p>
                {vital.is_abnormal && (
                  <span className="alert-badge">⚠️ Abnormal</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Care Plans Tab */}
      {activeTab === 'care-plans' && (
        <div className="care-plans-content">
          <h2>📖 My Care Plans</h2>
          {carePlans.map(plan => (
            <div key={plan.id} className="care-plan-card">
              <h3>{plan.title}</h3>
              <p>Condition: {plan.condition}</p>
              <p>Status: <span className={`status-badge ${plan.status}`}>{plan.status}</span></p>
              {plan.next_appointment && (
                <p>Next Appointment: {new Date(plan.next_appointment).toLocaleDateString()}</p>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
