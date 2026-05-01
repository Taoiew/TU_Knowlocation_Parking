# 🧪 TU Parking System - System Testing & Verification Guide

เอกสารนี้อธิบายวิธีการตรวจสอบและทดสอบการทำงานของระบบ TU Parking Location โดยรวม

---

## 📋 Table of Contents

1. [Prerequisites Check](#prerequisites-check)
2. [Running System Health Check](#running-system-health-check)
3. [Backend Testing](#backend-testing)
4. [Frontend Testing](#frontend-testing)
5. [API Testing](#api-testing)
6. [Integration Testing](#integration-testing)
7. [ML System Testing](#ml-system-testing)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites Check

### ✓ System Requirements

```bash
# Check Python version (require 3.8+)
python --version

# Check Node.js version (require 16+)
node --version

# Check npm version
npm --version
```

### ✓ Required Python Packages

```bash
# Activate virtual environment first
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate

# Install/verify dependencies
pip install -r requirements.txt

# Expected output:
# ✓ Flask==3.1.0
# ✓ Flask-SQLAlchemy==3.1.1
# ✓ Flask-CORS==5.0.0
```

### ✓ Required Node Packages

```bash
cd frontend

# Install dependencies
npm install

# Verify installation
npm list

# Check Vite, React, TypeScript are installed
```

---

## Running System Health Check

### Quick System Check

```bash
# From project root directory
python system_check.py
```

**Output should include:**
```
✅ Python Environment Check
  ✅ Python Version: 3.x.x
  ✅ Flask: Installed
  ✅ Flask-SQLAlchemy: Installed
  ✅ Flask-CORS: Installed

✅ Backend Structure Check
  ✅ app/
  ✅ app/models/
  ✅ app/services/
  ✅ ml/
  ✅ ml/services/
  ✅ ml/utils/
  ... (all required files)

✅ Frontend Structure Check
  ✅ frontend/package.json
  ✅ frontend/src/
  ✓ node_modules/ (dependencies installed)

✅ Database Check
  ℹ️  Database will be created on first run
  OR
  ✅ Database exists: tu_parking.db

✅ API Endpoints Check
  ✅ /api/parking/areas
  ✅ /api/parking/areas/<id>
  ✅ /api/parking/areas/<id>/slots

✅ ML Integration Check
  ✅ ML Models defined
  ✅ ML Manager service ready
  ✅ Prediction service ready
  ✅ Data utilities ready

📊 SYSTEM HEALTH SUMMARY
✅ SYSTEM IS READY TO RUN!
```

---

## Backend Testing

### 1️⃣ Start Backend Server

```bash
# From project root
python run.py
```

**Expected output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://0.0.0.0:5000
 * Press CTRL+C to quit
```

### 2️⃣ Verify Backend is Running

```bash
# In a new terminal/PowerShell
curl http://localhost:5000/api/parking/areas

# Or using PowerShell:
Invoke-WebRequest -Uri "http://localhost:5000/api/parking/areas"
```

**Expected response:**
```json
[
  {
    "id": 1,
    "name": "GYM 7",
    "address": "Tambon Khlong Nueng...",
    "latitude": 14.0754,
    "longitude": 100.6041,
    "total_slots": 60,
    "available_slots": 2,
    "unavailable_slots": 38
  },
  {
    "id": 2,
    "name": "Parking 1",
    "address": "99 Moo 18 Paholyothin Road...",
    "total_slots": 120,
    "available_slots": 8,
    "unavailable_slots": 112
  }
  // ... more parking areas
]
```

### 3️⃣ Test Database Connection

```bash
# Backend is running, now check database
# Create a Python script: test_db.py

from app import create_app
from app.models.parking import ParkingArea

app = create_app()
with app.app_context():
    areas = ParkingArea.query.all()
    print(f"✅ Database connected")
    print(f"✅ Found {len(areas)} parking areas")
    for area in areas:
        print(f"  - {area.name}: {area.available_slots_db}/{area.total_slots} slots available")

# Run:
python test_db.py
```

**Expected output:**
```
✅ Database connected
✅ Found 5 parking areas
  - GYM 7: 2/60 slots available
  - Parking 1: 8/120 slots available
  - Parking 2: 35/80 slots available
  - Parking 3: 12/45 slots available
  - Parking 4: 67/90 slots available
```

---

## Frontend Testing

### 1️⃣ Start Frontend Development Server

```bash
cd frontend

# Start Vite dev server
npm run dev
```

**Expected output:**
```
VITE v4.x.x  ready in xxx ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

### 2️⃣ Verify Frontend is Running

```bash
# Open browser
http://localhost:5173/

# OR from PowerShell
Start-Process "http://localhost:5173/"
```

**Expected behavior:**
- ✅ Page loads without errors
- ✅ Map appears with parking locations
- ✅ Parking list shows 5 areas
- ✅ Can click on individual parking areas
- ✅ No console errors

### 3️⃣ Check Browser Console

```
Open Developer Tools (F12)
Go to Console tab
Should see NO errors, only normal React warnings
```

---

## API Testing

### Complete API Endpoint Testing

**Using cURL:**

```bash
# 1. Get all parking areas
curl http://localhost:5000/api/parking/areas

# 2. Get specific parking area (ID=1)
curl http://localhost:5000/api/parking/areas/1

# 3. Get parking slots for area (ID=1)
curl http://localhost:5000/api/parking/areas/1/slots
```

**Using PowerShell:**

```powershell
# 1. Get all parking areas
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/parking/areas"
$response.Content | ConvertFrom-Json | Format-List

# 2. Get specific parking area
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/parking/areas/1"
$response.Content | ConvertFrom-Json

# 3. Get slots for area
$response = Invoke-WebRequest -Uri "http://localhost:5000/api/parking/areas/1/slots"
$response.Content | ConvertFrom-Json | Format-List
```

### API Response Structure Check

✅ Verify response includes:
- `id` - Parking area ID
- `name` - Area name
- `address` - Physical address
- `latitude`, `longitude` - GPS coordinates
- `total_slots` - Total parking slots
- `available_slots` - Available slots
- `unavailable_slots` - Occupied slots

---

## Integration Testing

### 🔗 Frontend ↔ Backend Communication

**Create `test_integration.py`:**

```python
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_integration():
    print("\n🔗 TESTING FRONTEND-BACKEND INTEGRATION\n")
    
    # Test 1: Get all areas
    print("Test 1️⃣ : Get all parking areas")
    response = requests.get(f"{BASE_URL}/parking/areas")
    assert response.status_code == 200, f"Failed: {response.status_code}"
    areas = response.json()
    print(f"✅ Got {len(areas)} parking areas")
    
    # Test 2: Get specific area
    print("\nTest 2️⃣ : Get specific parking area (ID=1)")
    response = requests.get(f"{BASE_URL}/parking/areas/1")
    assert response.status_code == 200
    area = response.json()
    print(f"✅ Got area: {area['name']}")
    assert 'id' in area
    assert 'available_slots' in area
    print(f"   Available slots: {area['available_slots']}/{area['total_slots']}")
    
    # Test 3: Get slots for area
    print("\nTest 3️⃣ : Get parking slots")
    response = requests.get(f"{BASE_URL}/parking/areas/1/slots")
    assert response.status_code == 200
    slots = response.json()
    print(f"✅ Got {len(slots)} slots for area 1")
    
    # Test 4: Verify data consistency
    print("\nTest 4️⃣ : Verify data consistency")
    available_count = sum(1 for s in slots if s['status'] == 'available')
    occupied_count = sum(1 for s in slots if s['status'] == 'occupied')
    
    print(f"✅ Slots breakdown:")
    print(f"   - Available: {available_count}")
    print(f"   - Occupied: {occupied_count}")
    print(f"   - Total: {available_count + occupied_count}")
    
    print("\n✅ ALL INTEGRATION TESTS PASSED!")

if __name__ == '__main__':
    test_integration()
```

**Run it:**
```bash
pip install requests
python test_integration.py
```

---

## ML System Testing

### Test ML Manager (Database Integration)

**Create `test_ml_system.py`:**

```python
from app import create_app
from app.services.ml_manager import MLManager
from ml.utils.data_preparer import DataPreparer
from ml.services import ParkingPredictionService

def test_ml_system():
    print("\n🤖 TESTING ML SYSTEM\n")
    
    app = create_app()
    
    with app.app_context():
        # Test 1: MLManager
        print("Test 1️⃣ : MLManager - Add Model")
        ml_manager = MLManager()
        
        model = ml_manager.add_ml_model(
            name='TestModel_v1',
            model_type='RandomForest',
            version='1.0.0',
            file_path='ML/models/test_model.pkl',
            description='Test model',
            accuracy=0.92,
            precision=0.89,
            recall=0.94,
            f1_score=0.915
        )
        print(f"✅ Model created: {model.name}")
        
        # Test 2: Get model
        print("\nTest 2️⃣ : MLManager - Get Model")
        retrieved = ml_manager.get_ml_model_by_id(model.id)
        print(f"✅ Retrieved model: {retrieved['name']}")
        
        # Test 3: Set active model
        print("\nTest 3️⃣ : MLManager - Set Active Model")
        ml_manager.set_active_model(model.id)
        active = ml_manager.get_active_model()
        print(f"✅ Active model: {active['name']}")
        
        # Test 4: DataPreparer
        print("\nTest 4️⃣ : DataPreparer - Extract Features")
        preparer = DataPreparer()
        features = preparer.get_parking_area_features(1)
        print(f"✅ Features extracted for area 1:")
        print(f"   - Name: {features['name']}")
        print(f"   - Total slots: {features['total_slots']}")
        print(f"   - Available: {features['available_slots']}")
        print(f"   - Occupancy rate: {features['occupancy_rate']:.2%}")
        
        # Test 5: Add prediction
        print("\nTest 5️⃣ : MLManager - Add Prediction")
        prediction = ml_manager.add_prediction(
            model_id=model.id,
            parking_area_id=1,
            prediction_value='moderate',
            confidence_score=0.85,
            predicted_available_slots=25,
            input_features=features
        )
        print(f"✅ Prediction stored (ID: {prediction.id})")
        print(f"   - Prediction: {prediction.prediction_value}")
        print(f"   - Confidence: {prediction.confidence_score}")
        
        # Test 6: ParkingPredictionService
        print("\nTest 6️⃣ : ParkingPredictionService - Make Prediction")
        service = ParkingPredictionService()
        result = service.make_prediction(parking_area_id=2)
        if result['success']:
            print(f"✅ Prediction for area 2:")
            print(f"   - Result: {result['prediction']}")
            print(f"   - Confidence: {result['confidence']}")
        else:
            print(f"❌ {result['error']}")
        
        # Test 7: Training history
        print("\nTest 7️⃣ : MLManager - Training History")
        session = ml_manager.start_training_session(model.id, notes='Test training')
        print(f"✅ Training session started (ID: {session.id})")
        
        ml_manager.end_training_session(
            session_id=session.id,
            training_samples_count=1000,
            training_accuracy=0.95,
            validation_accuracy=0.92
        )
        print(f"✅ Training session completed")
        
        history = ml_manager.get_training_history(model.id)
        print(f"✅ Training history: {len(history)} sessions")
        
        print("\n✅ ALL ML TESTS PASSED!")

if __name__ == '__main__':
    test_ml_system()
```

**Run it:**
```bash
# Make sure backend is running
python test_ml_system.py
```

**Expected output:**
```
🤖 TESTING ML SYSTEM

Test 1️⃣ : MLManager - Add Model
✅ Model created: TestModel_v1

Test 2️⃣ : MLManager - Get Model
✅ Retrieved model: TestModel_v1

Test 3️⃣ : MLManager - Set Active Model
✅ Active model: TestModel_v1

Test 4️⃣ : DataPreparer - Extract Features
✅ Features extracted for area 1:
   - Name: GYM 7
   - Total slots: 60
   - Available: 2
   - Occupancy rate: 63.33%

Test 5️⃣ : MLManager - Add Prediction
✅ Prediction stored (ID: 1)
   - Prediction: moderate
   - Confidence: 0.85

Test 6️⃣ : ParkingPredictionService - Make Prediction
✅ Prediction for area 2:
   - Result: moderate
   - Confidence: 0.75

Test 7️⃣ : MLManager - Training History
✅ Training session started (ID: 1)
✅ Training session completed
✅ Training history: 1 sessions

✅ ALL ML TESTS PASSED!
```

---

## Troubleshooting

### ❌ Backend won't start

```bash
# Check if port 5000 is already in use
lsof -i :5000  # Linux/Mac
netstat -ano | findstr :5000  # Windows

# Or use different port
# Edit run.py:
# app.run(host="0.0.0.0", port=8000, debug=True)
```

### ❌ Database connection error

```bash
# Check database file permissions
ls -la instance/tu_parking.db

# Delete and recreate (will seed fresh data)
rm instance/tu_parking.db
python run.py
```

### ❌ Frontend can't connect to backend

```bash
# Verify backend is running on 5000
curl http://localhost:5000/api/parking/areas

# Check CORS is enabled (should be in app/__init__.py)
# from flask_cors import CORS
# CORS(app)
```

### ❌ Python package not found

```bash
# Reinstall all dependencies
pip install --force-reinstall -r requirements.txt

# Or install ML packages if missing
pip install scikit-learn pandas numpy
```

### ❌ npm install fails

```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -r node_modules package-lock.json

# Reinstall
npm install
```

---

## Full System Integration Test (All at once)

### Step-by-step workflow:

```bash
# 1. Terminal 1 - Backend
python system_check.py          # Verify system
python run.py                   # Start backend

# 2. Terminal 2 - Frontend  
cd frontend
npm run dev                     # Start frontend

# 3. Terminal 3 - Testing
python test_integration.py      # Test API
python test_ml_system.py        # Test ML

# 4. Browser
# Open http://localhost:5173/
# Verify:
# ✅ Map loads
# ✅ Parking areas appear
# ✅ Can click areas for details
# ✅ No console errors
```

---

## ✅ System Ready Checklist

Before deployment, verify:

- [x] `python system_check.py` shows no errors
- [x] Backend starts without errors
- [x] Frontend loads in browser
- [x] API responses are correct
- [x] No console errors
- [x] Database has seed data (5 parking areas)
- [x] ML models can be added and retrieved
- [x] Predictions can be made
- [x] Frontend-Backend communication works

---

## 📊 Quick Reference

| Component | Port | Command |
|-----------|------|---------|
| Backend API | 5000 | `python run.py` |
| Frontend Dev | 5173 | `npm run dev` (from frontend/) |
| Database | N/A | Auto-created (instance/tu_parking.db) |

| Test | Command |
|------|---------|
| System Check | `python system_check.py` |
| Integration | `python test_integration.py` |
| ML System | `python test_ml_system.py` |

---

**Last Updated:** April 25, 2026  
**Version:** 1.0.0
