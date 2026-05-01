#!/usr/bin/env python3
"""
System Health Check Script for TU Parking Location
ตรวจสอบการทำงานของระบบโดยรวม
"""

import os
import sys
import json
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

class SystemHealthCheck:
    """ตรวจสอบสถานะของระบบ"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.status = {
            'backend': {},
            'frontend': {},
            'database': {},
            'api': {}
        }
        self.errors = []
        self.warnings = []
        
    def check_python_environment(self):
        """✓ ตรวจสอบ Python environment"""
        print("\n" + "="*50)
        print("1️⃣  PYTHON ENVIRONMENT CHECK")
        print("="*50)
        
        try:
            version = sys.version
            print(f"✅ Python Version: {version.split()[0]}")
            
            # Check required packages
            packages = {
                'flask': 'Flask',
                'flask_sqlalchemy': 'Flask-SQLAlchemy',
                'flask_cors': 'Flask-CORS'
            }
            
            for module, name in packages.items():
                try:
                    __import__(module)
                    print(f"✅ {name}: Installed")
                except ImportError:
                    msg = f"❌ {name}: NOT installed"
                    print(msg)
                    self.errors.append(msg)
            
            self.status['backend']['python'] = 'OK'
            return True
        except Exception as e:
            self.errors.append(f"Python check failed: {str(e)}")
            return False

    def check_backend_structure(self):
        """✓ ตรวจสอบโครงสร้าง Backend"""
        print("\n" + "="*50)
        print("2️⃣  BACKEND STRUCTURE CHECK")
        print("="*50)
        
        required_dirs = [
            'app',
            'app/models',
            'app/routes',
            'app/services',
            'ML',
            'ML/models',
            'ML/services',
            'ML/utils',
        ]
        
        required_files = {
            'app/__init__.py': 'Flask app factory',
            'app/extensions.py': 'Extensions setup',
            'app/models/parking.py': 'Parking models',
            'app/models/ml_models.py': 'ML models',
            'app/services/parking_service.py': 'Parking service',
            'app/services/ml_manager.py': 'ML database manager',
            'app/routes/parking_routes.py': 'API routes',
            'ML/services/parking_prediction_service.py': 'Prediction service',
            'ML/utils/data_preparer.py': 'Data utilities',
            'run.py': 'Entry point',
        }
        
        all_ok = True
        
        for directory in required_dirs:
            path = self.project_root / directory
            if path.exists():
                print(f"✅ {directory}/")
            else:
                print(f"❌ {directory}/ NOT FOUND")
                all_ok = False
                self.errors.append(f"Missing directory: {directory}")
        
        for filepath, description in required_files.items():
            path = self.project_root / filepath
            if path.exists():
                print(f"✅ {filepath} ({description})")
            else:
                print(f"❌ {filepath} NOT FOUND")
                all_ok = False
                self.errors.append(f"Missing file: {filepath}")
        
        self.status['backend']['structure'] = 'OK' if all_ok else 'MISSING FILES'
        return all_ok

    def check_frontend_structure(self):
        """✓ ตรวจสอบโครงสร้าง Frontend"""
        print("\n" + "="*50)
        print("3️⃣  FRONTEND STRUCTURE CHECK")
        print("="*50)
        
        frontend_path = self.project_root / 'frontend'
        required_files = {
            'package.json': 'Dependencies config',
            'tsconfig.json': 'TypeScript config',
            'vite.config.ts': 'Vite config',
            'index.html': 'Entry HTML',
            'src/main.tsx': 'React entry',
            'src/App.tsx': 'Main component',
        }
        
        all_ok = True
        
        for filepath, description in required_files.items():
            path = frontend_path / filepath
            if path.exists():
                print(f"✅ frontend/{filepath} ({description})")
            else:
                print(f"⚠️  frontend/{filepath} - {description}")
                all_ok = False
                self.warnings.append(f"Frontend file: {filepath}")
        
        # Check node_modules
        node_modules = frontend_path / 'node_modules'
        if node_modules.exists():
            print(f"✅ node_modules/ (dependencies installed)")
        else:
            print(f"⚠️  node_modules/ NOT installed - run: npm install")
            self.warnings.append("Frontend dependencies not installed")
        
        self.status['frontend']['structure'] = 'OK' if all_ok else 'INCOMPLETE'
        return all_ok

    def check_database(self):
        """✓ ตรวจสอบฐานข้อมูล"""
        print("\n" + "="*50)
        print("4️⃣  DATABASE CHECK")
        print("="*50)
        
        db_path = self.project_root / 'instance' / 'tu_parking.db'
        
        if db_path.exists():
            size = db_path.stat().st_size / 1024  # KB
            print(f"✅ Database exists: {db_path}")
            print(f"   Size: {size:.2f} KB")
            self.status['database']['exists'] = 'YES'
        else:
            print(f"ℹ️  Database not created yet (will be created on first run)")
            self.status['database']['exists'] = 'NO'
            self.warnings.append("Database will be created automatically")
        
        return True

    def check_api_endpoints(self):
        """✓ ตรวจสอบ API endpoints"""
        print("\n" + "="*50)
        print("5️⃣  API ENDPOINTS CHECK")
        print("="*50)
        
        # Read routes file
        routes_file = self.project_root / 'app' / 'routes' / 'parking_routes.py'
        
        endpoints = {
            '/api/parking/areas': 'GET - ดึงข้อมูลพื้นที่จอดรถทั้งหมด',
            '/api/parking/areas/<id>': 'GET - ดึงข้อมูลพื้นที่จอดรถเฉพาะ',
            '/api/parking/areas/<id>/slots': 'GET - ดึงข้อมูลช่องจอดรถในพื้นที่',
        }
        
        try:
            with open(routes_file, 'r') as f:
                content = f.read()
                for endpoint, description in endpoints.items():
                    if endpoint.replace('<id>', '') in content or 'parking/areas' in content:
                        print(f"✅ {endpoint}")
                        print(f"   {description}")
                    else:
                        print(f"⚠️  {endpoint} - might not be implemented")
                        self.warnings.append(f"Endpoint may not exist: {endpoint}")
        except Exception as e:
            self.errors.append(f"Could not read routes: {str(e)}")
        
        self.status['api']['endpoints'] = 'DEFINED'
        return True

    def check_ml_integration(self):
        """✓ ตรวจสอบ ML integration"""
        print("\n" + "="*50)
        print("6️⃣  ML INTEGRATION CHECK")
        print("="*50)
        
        ml_components = {
            'app/models/ml_models.py': 'MLModel, Prediction, TrainingHistory',
            'app/services/ml_manager.py': 'MLManager service',
            'ML/services/parking_prediction_service.py': 'ParkingPredictionService',
            'ML/utils/data_preparer.py': 'DataPreparer utility',
        }
        
        all_ok = True
        for filepath, components in ml_components.items():
            path = self.project_root / filepath
            if path.exists():
                print(f"✅ {filepath}")
                print(f"   Contains: {components}")
            else:
                print(f"❌ {filepath} NOT FOUND")
                all_ok = False
                self.errors.append(f"ML file missing: {filepath}")
        
        self.status['backend']['ml_integration'] = 'OK' if all_ok else 'INCOMPLETE'
        return all_ok

    def print_summary(self):
        """พิมพ์สรุปผลการตรวจสอบ"""
        print("\n" + "="*50)
        print("📊 SYSTEM HEALTH SUMMARY")
        print("="*50)
        
        print("\n✅ STATUS:")
        for category, checks in self.status.items():
            print(f"\n{category.upper()}:")
            for check, result in checks.items():
                status_icon = "✅" if result == "OK" else "⚠️" if result == "INCOMPLETE" else "ℹ️"
                print(f"  {status_icon} {check}: {result}")
        
        if self.errors:
            print("\n" + "="*50)
            print("❌ ERRORS:")
            for error in self.errors:
                print(f"  • {error}")
        
        if self.warnings:
            print("\n" + "="*50)
            print("⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  • {warning}")
        
        print("\n" + "="*50)
        if not self.errors:
            print("✅ SYSTEM IS READY TO RUN!")
        else:
            print(f"❌ FOUND {len(self.errors)} ERROR(S) - Please fix them first")
        print("="*50 + "\n")

    def run_all_checks(self):
        """รัน check ทั้งหมด"""
        print("\n")
        print("╔" + "="*48 + "╗")
        print("║" + " "*10 + "TU PARKING SYSTEM HEALTH CHECK" + " "*8 + "║")
        print("║" + " "*20 + "📍 v1.0.0" + " "*18 + "║")
        print("╚" + "="*48 + "╝")
        
        self.check_python_environment()
        self.check_backend_structure()
        self.check_frontend_structure()
        self.check_database()
        self.check_api_endpoints()
        self.check_ml_integration()
        self.print_summary()
        
        return len(self.errors) == 0


if __name__ == '__main__':
    checker = SystemHealthCheck()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)