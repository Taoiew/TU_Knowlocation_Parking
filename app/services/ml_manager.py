"""ML Manager Service for database operations related to models and predictions."""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import json

from app.extensions import db
from app.models.ml_models import MLModel, Prediction, TrainingHistory
from app.models.parking import ParkingArea


class MLModelDict:
    """Type definition for ML model data."""
    pass


class MLManager:
    """Manages all ML-related database interactions."""

    def __init__(self, db_session=None):
        """Constructor for MLManager."""
        self._db_session = db_session or db.session
        self._last_error = None

    @property
    def db_session(self):
        return self._db_session
    
    @db_session.setter
    def db_session(self, session):
        self._db_session = session

    @property
    def last_error(self):
        return self._last_error

    # ============= MLModel Operations =============
    
    def add_ml_model(
        self, 
        name: str, 
        model_type: str, 
        version: str, 
        file_path: str,
        description: str = None,
        **metrics
    ) -> MLModel:
        """Add a new trained model to the database."""
        # เก็บเฉพาะ metadata ของ model ส่วนไฟล์ model จริงอยู่ตาม file_path
        model = MLModel(
            name=name,
            model_type=model_type,
            version=version,
            file_path=file_path,
            description=description,
            accuracy=metrics.get('accuracy'),
            precision=metrics.get('precision'),
            recall=metrics.get('recall'),
            f1_score=metrics.get('f1_score')
        )
        db.session.add(model)
        db.session.commit()
        return model

    def get_all_ml_models(self) -> List[Dict[str, Any]]:
        """Retrieve all trained models."""
        models = MLModel.query.all()
        return [self._model_to_dict(m) for m in models]

    def get_ml_model_by_id(self, model_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a specific model by ID."""
        model = MLModel.query.get(model_id)
        return self._model_to_dict(model) if model else None

    def get_active_model(self) -> Optional[Dict[str, Any]]:
        """Get the currently active production model."""
        model = MLModel.query.filter_by(is_active=True).first()
        return self._model_to_dict(model) if model else None

    def set_active_model(self, model_id: int) -> bool:
        """Set a model as the active production model."""
        # ให้มี active model แค่ตัวเดียว เพื่อให้ prediction endpoint เลือกใช้ได้ชัดเจน
        MLModel.query.update({MLModel._is_active: False})
        
        # Activate the selected model
        model = MLModel.query.get(model_id)
        if model:
            model.is_active = True
            db.session.commit()
            return True
        return False

    def update_model_metrics(self, model_id: int, **metrics) -> bool:
        """Update performance metrics for a model."""
        model = MLModel.query.get(model_id)
        if model:
            model.accuracy = metrics.get('accuracy', model.accuracy)
            model.precision = metrics.get('precision', model.precision)
            model.recall = metrics.get('recall', model.recall)
            model.f1_score = metrics.get('f1_score', model.f1_score)
            db.session.commit()
            return True
        return False

    def delete_ml_model(self, model_id: int) -> bool:
        """Delete a model (and associated predictions/training history)."""
        model = MLModel.query.get(model_id)
        if model:
            # Delete associated records
            Prediction.query.filter_by(model_id=model_id).delete()
            TrainingHistory.query.filter_by(model_id=model_id).delete()
            db.session.delete(model)
            db.session.commit()
            return True
        return False

    # ============= Prediction Operations =============

    def add_prediction(
        self, 
        model_id: int, 
        parking_area_id: int,
        prediction_value: str,
        confidence_score: float,
        predicted_available_slots: int = None,
        input_features: Dict = None
    ) -> Prediction:
        """Store a prediction result."""
        # input_features ถูกเก็บไว้ด้วย เพื่อ debug ได้ว่า prediction นี้คำนวณจากข้อมูลชุดไหน
        prediction = Prediction(
            model_id=model_id,
            parking_area_id=parking_area_id,
            prediction_value=prediction_value,
            confidence_score=confidence_score,
            predicted_available_slots=predicted_available_slots,
            input_features=json.dumps(input_features) if input_features else None
        )
        db.session.add(prediction)
        db.session.commit()
        return prediction

    def get_predictions_by_area(self, parking_area_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent predictions for a specific parking area."""
        predictions = Prediction.query.filter_by(
            parking_area_id=parking_area_id
        ).order_by(Prediction.created_at.desc()).limit(limit).all()
        return [self._prediction_to_dict(p) for p in predictions]

    def get_predictions_by_model(self, model_id: int, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all predictions made by a specific model."""
        predictions = Prediction.query.filter_by(
            model_id=model_id
        ).order_by(Prediction.created_at.desc()).limit(limit).all()
        return [self._prediction_to_dict(p) for p in predictions]

    def get_latest_prediction_for_area(self, parking_area_id: int) -> Optional[Dict[str, Any]]:
        """Get the most recent prediction for an area."""
        prediction = Prediction.query.filter_by(
            parking_area_id=parking_area_id
        ).order_by(Prediction.created_at.desc()).first()
        return self._prediction_to_dict(prediction) if prediction else None

    def mark_prediction_accuracy(self, prediction_id: int, is_accurate: bool) -> bool:
        """Mark if a prediction was accurate after validation."""
        prediction = Prediction.query.get(prediction_id)
        if prediction:
            prediction.is_accurate = is_accurate
            db.session.commit()
            return True
        return False

    # ============= Training History Operations =============

    def start_training_session(self, model_id: int, notes: str = None) -> TrainingHistory:
        """Create a new training session record."""
        session = TrainingHistory(
            model_id=model_id,
            notes=notes,
            status='in_progress'
        )
        db.session.add(session)
        db.session.commit()
        return session

    def end_training_session(
        self, 
        session_id: int, 
        training_samples_count: int = None,
        training_accuracy: float = None,
        validation_accuracy: float = None,
        training_loss: float = None,
        validation_loss: float = None,
        status: str = 'completed'
    ) -> bool:
        """Complete a training session with final metrics."""
        session = TrainingHistory.query.get(session_id)
        if session:
            # normalize timezone ก่อนลบเวลา เพื่อกัน error เวลามี datetime แบบ naive/aware ปนกัน
            session.training_end_time = datetime.now(timezone.utc)
            start_time = session.training_start_time
            if start_time and start_time.tzinfo is None:
                start_time = start_time.replace(tzinfo=timezone.utc)
            session.training_duration_seconds = (
                (session.training_end_time - start_time).total_seconds()
            )
            session.status = status
            session.training_samples_count = training_samples_count
            session.training_accuracy = training_accuracy
            session.validation_accuracy = validation_accuracy
            session.training_loss = training_loss
            session.validation_loss = validation_loss
            db.session.commit()
            return True
        return False

    def get_training_history(self, model_id: int) -> List[Dict[str, Any]]:
        """Get all training sessions for a model."""
        sessions = TrainingHistory.query.filter_by(
            model_id=model_id
        ).order_by(TrainingHistory.training_start_time.desc()).all()
        return [self._training_to_dict(s) for s in sessions]

    def fail_training_session(self, session_id: int, error_message: str) -> bool:
        """Mark a training session as failed."""
        session = TrainingHistory.query.get(session_id)
        if session:
            session.status = 'failed'
            session.error_message = error_message
            session.training_end_time = datetime.now(timezone.utc)
            db.session.commit()
            return True
        return False

    # ============= Helper Methods =============

    @staticmethod
    def _model_to_dict(model: MLModel) -> Optional[Dict[str, Any]]:
        """Convert MLModel to dictionary."""
        if not model:
            return None
        return {
            'id': model.id,
            'name': model.name,
            'model_type': model.model_type,
            'version': model.version,
            'file_path': model.file_path,
            'accuracy': model.accuracy,
            'precision': model.precision,
            'recall': model.recall,
            'f1_score': model.f1_score,
            'is_active': model.is_active,
            'description': model.description,
            'created_at': model.created_at.isoformat() if model.created_at else None,
            'updated_at': model.updated_at.isoformat() if model.updated_at else None
        }

    @staticmethod
    def _prediction_to_dict(prediction: Prediction) -> Optional[Dict[str, Any]]:
        """Convert Prediction to dictionary."""
        if not prediction:
            return None
        input_features = None
        if prediction.input_features:
            try:
                input_features = json.loads(prediction.input_features)
            except json.JSONDecodeError:
                input_features = prediction.input_features
        
        return {
            'id': prediction.id,
            'model_id': prediction.model_id,
            'parking_area_id': prediction.parking_area_id,
            'prediction_value': prediction.prediction_value,
            'confidence_score': prediction.confidence_score,
            'predicted_available_slots': prediction.predicted_available_slots,
            'input_features': input_features,
            'is_accurate': prediction.is_accurate,
            'created_at': prediction.created_at.isoformat() if prediction.created_at else None
        }

    @staticmethod
    def _training_to_dict(training: TrainingHistory) -> Optional[Dict[str, Any]]:
        """Convert TrainingHistory to dictionary."""
        if not training:
            return None
        return {
            'id': training.id,
            'model_id': training.model_id,
            'status': training.status,
            'training_samples_count': training.training_samples_count,
            'training_accuracy': training.training_accuracy,
            'validation_accuracy': training.validation_accuracy,
            'training_loss': training.training_loss,
            'validation_loss': training.validation_loss,
            'training_duration_seconds': training.training_duration_seconds,
            'error_message': training.error_message,
            'created_at': training.training_start_time.isoformat() if training.training_start_time else None,
            'ended_at': training.training_end_time.isoformat() if training.training_end_time else None,
            'notes': training.notes
        }
