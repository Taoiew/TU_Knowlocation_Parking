"""ML Service for model training and inference."""

from typing import Dict, Any, List
import json
from app.services.ml_manager import MLManager
from app.extensions import db
from app.models.ml_models import MLModel
from ML.utils.data_preparer import DataPreparer


class ParkingPredictionService:
    """Service for parking availability prediction using ML models."""

    def __init__(self):
        self.ml_manager = MLManager()
        self.data_preparer = DataPreparer()

    def make_prediction(self, parking_area_id: int) -> Dict[str, Any]:
        """
        Make a prediction for a specific parking area using the active model.
        
        Args:
            parking_area_id: ID of the parking area to predict for
            
        Returns:
            Prediction result with confidence score
        """
        features = self.data_preparer.get_parking_area_features(parking_area_id)
        if not features:
            return {
                'success': False,
                'error': f'Parking area {parking_area_id} not found'
            }

        active_model = self._get_or_create_default_model()
        # ตอนนี้ใช้ rule-based baseline ก่อน เมื่อมี model จริงค่อยเปลี่ยนใน _predict_with_model()
        prediction_result = self._predict_with_model(features, active_model)

        # บันทึกทุก prediction เพื่อให้ดู history และวัดความแม่นยำย้อนหลังได้
        stored_prediction = self.ml_manager.add_prediction(
            model_id=active_model['id'],
            parking_area_id=parking_area_id,
            prediction_value=prediction_result['prediction'],
            confidence_score=prediction_result['confidence'],
            predicted_available_slots=prediction_result.get('predicted_slots'),
            input_features=features
        )

        return {
            'success': True,
            'prediction_id': stored_prediction.id,
            'parking_area_id': parking_area_id,
            'area_name': features['name'],
            'prediction': prediction_result['prediction'],
            'confidence': prediction_result['confidence'],
            'occupancy_rate': f"{features['occupancy_rate'] * 100:.1f}%",
            'available_slots': features['available_slots'],
            'total_slots': features['total_slots'],
            'predicted_available_slots': prediction_result.get('predicted_slots'),
            'model_id': active_model['id'],
            'model_name': active_model['name']
        }

    def predict_all_areas(self) -> Dict[str, Any]:
        """Make predictions for all parking areas."""
        active_model = self._get_or_create_default_model()

        # Get features for all areas
        all_features = self.data_preparer.get_all_areas_features()
        
        predictions = []
        for features in all_features:
            prediction_result = self._predict_with_model(features, active_model)
            
            # Store each prediction
            stored_pred = self.ml_manager.add_prediction(
                model_id=active_model['id'],
                parking_area_id=features['area_id'],
                prediction_value=prediction_result['prediction'],
                confidence_score=prediction_result['confidence'],
                predicted_available_slots=prediction_result.get('predicted_slots'),
                input_features=features
            )
            
            predictions.append({
                'parking_area_id': features['area_id'],
                'area_name': features['name'],
                'prediction': prediction_result['prediction'],
                'confidence': prediction_result['confidence']
            })

        return {
            'success': True,
            'model_name': active_model['name'],
            'total_predictions': len(predictions),
            'predictions': predictions
        }

    def get_prediction_history(self, parking_area_id: int, limit: int = 10) -> List[Dict]:
        """Get recent predictions for a parking area."""
        return self.ml_manager.get_predictions_by_area(parking_area_id, limit)

    def get_active_model_info(self) -> Dict[str, Any]:
        """Get information about the currently active model."""
        model = self.ml_manager.get_active_model()
        if not model:
            return {'model': None, 'message': 'No active model set'}
        return {'model': model}

    def _get_or_create_default_model(self) -> Dict[str, Any]:
        """Return the active model metadata, creating a deterministic demo model if needed."""
        # ถ้ายังไม่มี model ใน DB เราสร้าง metadata ตัว baseline ให้ endpoint ใช้งานได้ทันที
        active_model = self.ml_manager.get_active_model()
        if active_model:
            return active_model

        model = MLModel.query.filter_by(_name='default_rule_based_v1').first()
        if model is None:
            model = MLModel(
                name='default_rule_based_v1',
                model_type='RuleBased',
                version='1.0.0',
                file_path='internal://rule-based-parking-summary',
                accuracy=0.8,
                is_active=True,
                description='Baseline occupancy-rate prediction used until a trained model is connected.'
            )
            db.session.add(model)
        else:
            model.is_active = True

        db.session.commit()
        return self.ml_manager._model_to_dict(model)

    @staticmethod
    def _predict_with_model(features: Dict, model_info: Dict) -> Dict[str, Any]:
        """
        Internal method to make prediction with model.
        
        TODO: Replace with actual model loading and inference
        """
        occupancy_rate = features.get('occupancy_rate', 0)
        
        # Baseline ง่าย ๆ: ดู occupancy rate แล้วจัดกลุ่มสถานะ
        if occupancy_rate > 0.8:
            prediction = 'likely_full'
            confidence = 0.85
        elif occupancy_rate > 0.5:
            prediction = 'moderate'
            confidence = 0.75
        else:
            prediction = 'available'
            confidence = 0.80

        return {
            'prediction': prediction,
            'confidence': confidence,
            'predicted_slots': max(0, int(features.get('available_slots', 0)))
        }
