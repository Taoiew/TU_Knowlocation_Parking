import random
#!/usr/bin/env python3
"""
ML System Test Script for TU Parking System
 ML integration  Database
"""

import sys
import json
from typing import Dict, Any

class MLSystemTester:
    """ ML"""
    
    def __init__(self):
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def test_ml_models_import(self) -> bool:
        """ import ML models"""
        print("\n" + "="*50)
        print(" TEST 1: Import ML Models")
        print("="*50)
        
        try:
            from app.models.ml_models import MLModel, Prediction, TrainingHistory
            print(" Successfully imported MLModel")
            print(" Successfully imported Prediction")
            print(" Successfully imported TrainingHistory")
            self.results['passed'].append("ML models import")
            return True
        except ImportError as e:
            print(f" Failed to import ML models: {str(e)}")
            self.results['failed'].append(f"ML models import: {str(e)}")
            return False
    
    def test_ml_manager_import(self) -> bool:
        """ import MLManager"""
        print("\n" + "="*50)
        print(" TEST 2: Import MLManager Service")
        print("="*50)
        
        try:
            from app.services.ml_manager import MLManager
            print(" Successfully imported MLManager")
            self.results['passed'].append("MLManager import")
            return True
        except ImportError as e:
            print(f" Failed to import MLManager: {str(e)}")
            self.results['failed'].append(f"MLManager import: {str(e)}")
            return False
    
    def test_data_preparer_import(self) -> bool:
        """ import DataPreparer"""
        print("\n" + "="*50)
        print(" TEST 3: Import DataPreparer Utility")
        print("="*50)
        
        try:
            from ML.utils.data_preparer import DataPreparer
            print(" Successfully imported DataPreparer")
            self.results['passed'].append("DataPreparer import")
            return True
        except ImportError as e:
            print(f" Failed to import DataPreparer: {str(e)}")
            self.results['failed'].append(f"DataPreparer import: {str(e)}")
            return False
    
    def test_prediction_service_import(self) -> bool:
        """ import ParkingPredictionService"""
        print("\n" + "="*50)
        print(" TEST 4: Import ParkingPredictionService")
        print("="*50)
        
        try:
            from ML.services import ParkingPredictionService
            print(" Successfully imported ParkingPredictionService")
            self.results['passed'].append("ParkingPredictionService import")
            return True
        except ImportError as e:
            print(f" Failed to import ParkingPredictionService: {str(e)}")
            self.results['failed'].append(f"ParkingPredictionService import: {str(e)}")
            return False
    
    def test_database_operations(self) -> bool:
        """ MLManager database operations"""
        print("\n" + "="*50)
        print(" TEST 5: MLManager Database Operations")
        print("="*50)
        
        try:
            from app import create_app
            from app.services.ml_manager import MLManager
            
            app = create_app()
            
            with app.app_context():
                ml_manager = MLManager()
                
                # Test 5a: Add model
                print("\n5a. Adding model to database...")
                model = ml_manager.add_ml_model(
                    name=f'TestModel_Integration_{random.getrandbits(32)}',
                    model_type='RandomForest',
                    version='1.0.0',
                    file_path='ML/models/test_integration.pkl',
                    description='Integration test model',
                    accuracy=0.92,
                    precision=0.89,
                    recall=0.94,
                    f1_score=0.915
                )
                print(f" Model added: ID={model.id}, Name={model.name}")
                
                # Test 5b: Retrieve model
                print("\n5b. Retrieving model from database...")
                retrieved = ml_manager.get_ml_model_by_id(model.id)
                assert retrieved is not None, "Failed to retrieve model"
                assert retrieved['name'] == 'TestModel_Integration'
                print(f" Model retrieved: {retrieved['name']}")
                print(f"   - Accuracy: {retrieved['accuracy']}")
                print(f"   - F1 Score: {retrieved['f1_score']}")
                
                # Test 5c: Set active model
                print("\n5c. Setting model as active...")
                success = ml_manager.set_active_model(model.id)
                assert success, "Failed to set active model"
                active = ml_manager.get_active_model()
                assert active is not None
                print(f" Model set as active: {active['name']}")
                
                # Test 5d: Get all models
                print("\n5d. Retrieving all models...")
                all_models = ml_manager.get_all_ml_models()
                print(f" Retrieved {len(all_models)} model(s)")
                
                self.results['passed'].append("Database operations")
                return True
                
        except Exception as e:
            print(f" Test failed: {str(e)}")
            self.results['failed'].append(f"Database operations: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_data_preparation(self) -> bool:
        """ DataPreparer"""
        print("\n" + "="*50)
        print(" TEST 6: DataPreparer Functionality")
        print("="*50)
        
        try:
            from app import create_app
            from ML.utils.data_preparer import DataPreparer
            
            app = create_app()
            
            with app.app_context():
                preparer = DataPreparer()
                
                # Test 6a: Get features for one area
                print("\n6a. Extracting features for parking area...")
                features = preparer.get_parking_area_features(1)
                assert features, "Failed to get features"
                assert 'area_id' in features
                assert 'occupancy_rate' in features
                print(f" Features extracted for area: {features['name']}")
                print(f"   - Total slots: {features['total_slots']}")
                print(f"   - Available: {features['available_slots']}")
                print(f"   - Occupancy rate: {features['occupancy_rate']:.2%}")
                
                # Test 6b: Get all features
                print("\n6b. Extracting features for all areas...")
                all_features = preparer.get_all_areas_features()
                assert len(all_features) > 0
                print(f" Features extracted for {len(all_features)} areas")
                
                # Test 6c: Feature names
                print("\n6c. Getting feature names...")
                feature_names = preparer.get_feature_names()
                print(f" Feature names: {feature_names}")
                
                # Test 6d: Normalization
                print("\n6d. Normalizing features...")
                normalized = preparer.normalize_features(all_features)
                assert len(normalized) == len(all_features)
                print(f" Features normalized: {len(normalized)} samples")
                print(f"   Sample (Area 1 occupancy): {normalized[0]['occupancy_rate']:.4f}")
                
                self.results['passed'].append("Data preparation")
                return True
                
        except Exception as e:
            print(f" Test failed: {str(e)}")
            self.results['failed'].append(f"Data preparation: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_predictions(self) -> bool:
        """ Prediction storage"""
        print("\n" + "="*50)
        print(" TEST 7: Prediction Storage")
        print("="*50)
        
        try:
            from app import create_app
            from app.services.ml_manager import MLManager
            from ML.utils.data_preparer import DataPreparer
            
            app = create_app()
            
            with app.app_context():
                ml_manager = MLManager()
                preparer = DataPreparer()
                
                # Setup: Get active model or create one
                active_model = ml_manager.get_active_model()
                if not active_model:
                    model = ml_manager.add_ml_model(
                        name=f'TestModel_Pred_{id(object())}',
                        model_type='RandomForest',
                        version='1.0.0',
                        file_path='ML/models/test_pred.pkl'
                    )
                    ml_manager.set_active_model(model.id)
                    active_model = ml_manager.get_active_model()
                
                # Test 7a: Add prediction
                print("\n7a. Adding prediction to database...")
                features = preparer.get_parking_area_features(1)
                prediction = ml_manager.add_prediction(
                    model_id=active_model['id'],
                    parking_area_id=1,
                    prediction_value='moderate',
                    confidence_score=0.85,
                    predicted_available_slots=25,
                    input_features=features
                )
                print(f" Prediction added: ID={prediction.id}")
                print(f"   - Prediction: {prediction.prediction_value}")
                print(f"   - Confidence: {prediction.confidence_score}")
                
                # Test 7b: Get predictions by area
                print("\n7b. Retrieving predictions by area...")
                predictions = ml_manager.get_predictions_by_area(1, limit=5)
                print(f" Retrieved {len(predictions)} prediction(s) for area 1")
                
                # Test 7c: Mark prediction accuracy
                print("\n7c. Marking prediction accuracy...")
                success = ml_manager.mark_prediction_accuracy(prediction.id, is_accurate=True)
                assert success
                print(f" Prediction marked as accurate")
                
                self.results['passed'].append("Predictions")
                return True
                
        except Exception as e:
            print(f" Test failed: {str(e)}")
            self.results['failed'].append(f"Predictions: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_training_history(self) -> bool:
        """ Training History"""
        print("\n" + "="*50)
        print(" TEST 8: Training History Management")
        print("="*50)
        
        try:
            from app import create_app
            from app.services.ml_manager import MLManager
            
            app = create_app()
            
            with app.app_context():
                ml_manager = MLManager()
                
                # Setup: Get or create model
                active_model = ml_manager.get_active_model()
                if not active_model:
                    model = ml_manager.add_ml_model(
                        name=f'TestModel_Train_{id(object())}',
                        model_type='RandomForest',
                        version='1.0.0',
                        file_path='ML/models/test_train.pkl'
                    )
                    ml_manager.set_active_model(model.id)
                    active_model = ml_manager.get_active_model()
                
                # Test 8a: Start training
                print("\n8a. Starting training session...")
                session = ml_manager.start_training_session(
                    model_id=active_model['id'],
                    notes='Integration test training'
                )
                print(f" Training session started: ID={session.id}")
                print(f"   Status: {session.status}")
                
                # Test 8b: End training
                print("\n8b. Ending training session...")
                success = ml_manager.end_training_session(
                    session_id=session.id,
                    training_samples_count=1000,
                    training_accuracy=0.95,
                    validation_accuracy=0.92,
                    training_loss=0.15,
                    validation_loss=0.18,
                    status='completed'
                )
                assert success
                print(f" Training session completed")
                print(f"   - Training accuracy: 0.95")
                print(f"   - Validation accuracy: 0.92")
                print(f"   - Samples: 1000")
                
                # Test 8c: Get training history
                print("\n8c. Retrieving training history...")
                history = ml_manager.get_training_history(active_model['id'])
                print(f" Retrieved {len(history)} training session(s)")
                
                self.results['passed'].append("Training history")
                return True
                
        except Exception as e:
            print(f" Test failed: {str(e)}")
            self.results['failed'].append(f"Training history: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_prediction_service(self) -> bool:
        """ ParkingPredictionService"""
        print("\n" + "="*50)
        print(" TEST 9: ParkingPredictionService")
        print("="*50)
        
        try:
            from app import create_app
            from ML.services import ParkingPredictionService
            
            app = create_app()
            
            with app.app_context():
                service = ParkingPredictionService()
                
                # Ensure active model exists
                active_model = service.ml_manager.get_active_model()
                if not active_model:
                    model = service.ml_manager.add_ml_model(
                        name=f'TestModel_Service_{id(object())}',
                        model_type='RandomForest',
                        version='1.0.0',
                        file_path='ML/models/test_service.pkl'
                    )
                    service.ml_manager.set_active_model(model.id)
                
                # Test 9a: Make single prediction
                print("\n9a. Making prediction for single area...")
                result = service.make_prediction(parking_area_id=1)
                assert result['success'], result.get('error', 'Unknown error')
                print(f" Prediction made for area {result['parking_area_id']}")
                print(f"   - Result: {result['prediction']}")
                print(f"   - Confidence: {result['confidence']}")
                print(f"   - Model: {result['model_name']}")
                
                # Test 9b: Make predictions for all areas
                print("\n9b. Making predictions for all areas...")
                result = service.predict_all_areas()
                assert result['success'], result.get('error', 'Unknown error')
                print(f" Predictions made for {result['total_predictions']} areas")
                
                # Test 9c: Get prediction history
                print("\n9c. Getting prediction history...")
                history = service.get_prediction_history(1, limit=5)
                print(f" Retrieved {len(history)} recent prediction(s)")
                
                # Test 9d: Get active model info
                print("\n9d. Getting active model info...")
                info = service.get_active_model_info()
                if info['model']:
                    print(f" Active model: {info['model']['name']}")
                    print(f"   - Version: {info['model']['version']}")
                    print(f"   - Type: {info['model']['model_type']}")
                
                self.results['passed'].append("Prediction service")
                return True
                
        except Exception as e:
            print(f" Test failed: {str(e)}")
            self.results['failed'].append(f"Prediction service: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_summary(self) -> None:
        """"""
        print("\n" + "="*50)
        print(" ML SYSTEM TEST SUMMARY")
        print("="*50)
        
        if self.results['passed']:
            print(f"\n PASSED ({len(self.results['passed'])}):")
            for test in self.results['passed']:
                print(f"    {test}")
        
        if self.results['failed']:
            print(f"\n FAILED ({len(self.results['failed'])}):")
            for test in self.results['failed']:
                print(f"    {test}")
        
        if self.results['warnings']:
            print(f"\n  WARNINGS ({len(self.results['warnings'])}):")
            for warning in self.results['warnings']:
                print(f"    {warning}")
        
        print("\n" + "="*50)
        
        total = len(self.results['passed']) + len(self.results['failed'])
        passed_pct = (len(self.results['passed']) / total * 100) if total > 0 else 0
        
        print(f"Passed: {len(self.results['passed'])}/{total} ({passed_pct:.0f}%)")
        
        if not self.results['failed']:
            print(" ALL ML SYSTEM TESTS PASSED!")
        else:
            print(f" {len(self.results['failed'])} TEST(S) FAILED")
        
        print("="*50 + "\n")
    
    def run_all_tests(self) -> bool:
        """ test """
        print("\n")
        print("" + "="*48 + "")
        print("TU PARKING - ML SYSTEM TEST SUITE")
        print("ML Integration")
        print("" + "="*48 + "")
        
        # Import tests
        self.test_ml_models_import()
        self.test_ml_manager_import()
        self.test_data_preparer_import()
        self.test_prediction_service_import()
        
        # If imports failed, stop here
        if len(self.results['failed']) > 0:
            print("\n" + "="*50)
            print(" CANNOT PROCEED - Import tests failed")
            print("="*50)
            self.print_summary()
            return False
        
        # Functional tests
        self.test_database_operations()
        self.test_data_preparation()
        self.test_predictions()
        self.test_training_history()
        self.test_prediction_service()
        
        # Print summary
        self.print_summary()
        
        return len(self.results['failed']) == 0


if __name__ == '__main__':
    tester = MLSystemTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
