#!/usr/bin/env python3
"""
Integration Test Script for TU Parking System
ทดสอบการทำงานของ Frontend ↔ Backend communication
"""

import requests
import json
import sys
from typing import Dict, Any

class IntegrationTester:
    """ทดสอบ Frontend-Backend integration"""
    
    def __init__(self, base_url: str = "http://localhost:5000/api"):
        self.base_url = base_url
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def check_backend_alive(self) -> bool:
        """ตรวจสอบว่า backend กำลังทำงาน"""
        print("\n" + "="*50)
        print("🔍 CHECKING BACKEND SERVER")
        print("="*50)
        
        try:
            response = requests.get(f"{self.base_url}/parking/areas", timeout=5)
            if response.status_code == 200:
                print(f"✅ Backend is running at {self.base_url}")
                self.results['passed'].append("Backend alive")
                return True
            else:
                print(f"❌ Backend returned status {response.status_code}")
                self.results['failed'].append(f"Backend status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to backend at {self.base_url}")
            print(f"   Make sure backend is running: python run.py")
            self.results['failed'].append("Backend connection failed")
            return False
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            self.results['failed'].append(str(e))
            return False
    
    def test_get_all_areas(self) -> bool:
        """ทดสอบ GET /api/parking/areas"""
        print("\n" + "="*50)
        print("📍 TEST 1: Get All Parking Areas")
        print("="*50)
        
        try:
            response = requests.get(f"{self.base_url}/parking/areas")
            response.raise_for_status()
            
            areas = response.json()
            
            if not isinstance(areas, list):
                print("❌ Response is not a list")
                self.results['failed'].append("All areas response format incorrect")
                return False
            
            print(f"✅ Retrieved {len(areas)} parking areas")
            
            # Check each area has required fields
            required_fields = ['id', 'name', 'total_slots', 'available_slots', 'unavailable_slots']
            
            for i, area in enumerate(areas):
                for field in required_fields:
                    if field not in area:
                        print(f"⚠️  Area {i} missing field: {field}")
                        self.results['warnings'].append(f"Area missing field: {field}")
                
                print(f"\n  Area {i+1}: {area.get('name', 'Unknown')}")
                print(f"    - ID: {area.get('id')}")
                print(f"    - Slots: {area.get('available_slots')}/{area.get('total_slots')} available")
                print(f"    - Location: ({area.get('latitude')}, {area.get('longitude')})")
            
            self.results['passed'].append("Get all areas")
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            self.results['failed'].append(f"Get all areas: {str(e)}")
            return False
    
    def test_get_specific_area(self, area_id: int = 1) -> bool:
        """ทดสอบ GET /api/parking/areas/<id>"""
        print("\n" + "="*50)
        print(f"📍 TEST 2: Get Specific Parking Area (ID={area_id})")
        print("="*50)
        
        try:
            response = requests.get(f"{self.base_url}/parking/areas/{area_id}")
            
            if response.status_code == 404:
                print(f"⚠️  Area {area_id} not found")
                self.results['warnings'].append(f"Area {area_id} not found")
                return False
            
            response.raise_for_status()
            
            area = response.json()
            
            print(f"✅ Retrieved area: {area.get('name')}")
            print(f"\n  Area Details:")
            print(f"    - ID: {area.get('id')}")
            print(f"    - Name: {area.get('name')}")
            print(f"    - Address: {area.get('address')}")
            print(f"    - Total Slots: {area.get('total_slots')}")
            print(f"    - Available: {area.get('available_slots')}")
            print(f"    - Unavailable: {area.get('unavailable_slots')}")
            print(f"    - Location: ({area.get('latitude')}, {area.get('longitude')})")
            
            # Verify data consistency
            total = area.get('total_slots', 0)
            available = area.get('available_slots', 0)
            unavailable = area.get('unavailable_slots', 0)
            
            if available + unavailable != total:
                print(f"⚠️  Data inconsistency: {available} + {unavailable} ≠ {total}")
                self.results['warnings'].append("Data consistency issue")
            else:
                print(f"✅ Data consistency verified")
            
            self.results['passed'].append(f"Get specific area ({area_id})")
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            self.results['failed'].append(f"Get specific area: {str(e)}")
            return False
    
    def test_get_slots(self, area_id: int = 1) -> bool:
        """ทดสอบ GET /api/parking/areas/<id>/slots"""
        print("\n" + "="*50)
        print(f"🚗 TEST 3: Get Parking Slots (Area {area_id})")
        print("="*50)
        
        try:
            response = requests.get(f"{self.base_url}/parking/areas/{area_id}/slots")
            
            if response.status_code == 404:
                print(f"⚠️  Area {area_id} not found")
                self.results['warnings'].append(f"Area {area_id} not found for slots")
                return False
            
            response.raise_for_status()
            
            slots = response.json()
            
            if not isinstance(slots, list):
                print("❌ Response is not a list")
                self.results['failed'].append("Slots response format incorrect")
                return False
            
            print(f"✅ Retrieved {len(slots)} parking slots")
            
            # Count by status
            available_count = sum(1 for s in slots if s.get('status') == 'available')
            occupied_count = sum(1 for s in slots if s.get('status') == 'occupied')
            maintenance_count = sum(1 for s in slots if s.get('status') == 'maintenance')
            
            print(f"\n  Slot Status Summary:")
            print(f"    - Available: {available_count}")
            print(f"    - Occupied: {occupied_count}")
            print(f"    - Maintenance: {maintenance_count}")
            print(f"    - Total: {len(slots)}")
            
            # Show first 5 slots
            print(f"\n  First 5 Slots:")
            for i, slot in enumerate(slots[:5]):
                print(f"    {i+1}. {slot.get('name')} - {slot.get('status')}")
            
            if len(slots) > 5:
                print(f"    ... and {len(slots)-5} more")
            
            self.results['passed'].append("Get slots")
            return True
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            self.results['failed'].append(f"Get slots: {str(e)}")
            return False
    
    def test_data_consistency(self) -> bool:
        """ทดสอบความสอดคล้องของข้อมูล"""
        print("\n" + "="*50)
        print("🔄 TEST 4: Data Consistency Verification")
        print("="*50)
        
        try:
            # Get all areas
            areas_response = requests.get(f"{self.base_url}/parking/areas")
            areas = areas_response.json()
            
            consistency_ok = True
            
            for area in areas:
                area_id = area.get('id')
                available = area.get('available_slots', 0)
                unavailable = area.get('unavailable_slots', 0)
                total = area.get('total_slots', 0)
                
                # Check math
                if available + unavailable != total:
                    print(f"⚠️  {area.get('name')}: inconsistent slot counts")
                    consistency_ok = False
                
                # Get slots and verify
                slots_response = requests.get(f"{self.base_url}/parking/areas/{area_id}/slots")
                if slots_response.status_code == 200:
                    slots = slots_response.json()
                    actual_available = sum(1 for s in slots if s.get('status') == 'available')
                    
                    if actual_available != available:
                        print(f"⚠️  {area.get('name')}: slot count mismatch")
                        print(f"     Expected: {available}, Actual: {actual_available}")
                        consistency_ok = False
            
            if consistency_ok:
                print(f"✅ Data consistency verified for {len(areas)} areas")
                self.results['passed'].append("Data consistency")
            else:
                print(f"⚠️  Some data inconsistencies found")
                self.results['warnings'].append("Data consistency issues")
            
            return consistency_ok
            
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            self.results['failed'].append(f"Data consistency: {str(e)}")
            return False
    
    def print_summary(self) -> None:
        """พิมพ์สรุปผลทดสอบ"""
        print("\n" + "="*50)
        print("📊 TEST SUMMARY")
        print("="*50)
        
        if self.results['passed']:
            print(f"\n✅ PASSED ({len(self.results['passed'])}):")
            for test in self.results['passed']:
                print(f"   • {test}")
        
        if self.results['failed']:
            print(f"\n❌ FAILED ({len(self.results['failed'])}):")
            for test in self.results['failed']:
                print(f"   • {test}")
        
        if self.results['warnings']:
            print(f"\n⚠️  WARNINGS ({len(self.results['warnings'])}):")
            for warning in self.results['warnings']:
                print(f"   • {warning}")
        
        print("\n" + "="*50)
        
        if not self.results['failed']:
            print("✅ ALL TESTS PASSED!")
        else:
            print(f"❌ {len(self.results['failed'])} TEST(S) FAILED")
        
        print("="*50 + "\n")
    
    def run_all_tests(self) -> bool:
        """รัน test ทั้งหมด"""
        print("\n")
        print("╔" + "="*48 + "╗")
        print("║" + " "*8 + "TU PARKING - INTEGRATION TEST SUITE" + " "*5 + "║")
        print("║" + " "*20 + "🔗 Frontend ↔ Backend" + " "*11 + "║")
        print("╚" + "="*48 + "╝")
        
        # Check backend first
        if not self.check_backend_alive():
            print("\n" + "="*50)
            print("❌ CANNOT PROCEED - Backend is not running")
            print("="*50)
            return False
        
        # Run tests
        self.test_get_all_areas()
        self.test_get_specific_area(1)
        self.test_get_slots(1)
        self.test_data_consistency()
        
        # Print summary
        self.print_summary()
        
        return len(self.results['failed']) == 0


if __name__ == '__main__':
    tester = IntegrationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)