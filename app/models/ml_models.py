"""SQLAlchemy models for ML operations and predictions."""

from datetime import datetime, timezone
from app.extensions import db


class MLModel(db.Model):
    """Stores metadata about trained ML models."""
    __tablename__ = 'ml_models'

    id = db.Column(db.Integer, primary_key=True)
    _name = db.Column('name', db.String(100), nullable=False, unique=True)
    _model_type = db.Column('model_type', db.String(50), nullable=False)  # e.g., 'RandomForest', 'Neural Network'
    _version = db.Column('version', db.String(20), nullable=False)  # e.g., '1.0.0'
    _file_path = db.Column('file_path', db.String(255), nullable=False)  # Path to saved model artifact
    _accuracy = db.Column('accuracy', db.Float, nullable=True)  # Model performance metric
    _precision = db.Column('precision', db.Float, nullable=True)  # Precision score
    _recall = db.Column('recall', db.Float, nullable=True)  # Recall score
    _f1_score = db.Column('f1_score', db.Float, nullable=True)  # F1 score
    _created_at = db.Column('created_at', db.DateTime, default=lambda: datetime.now(timezone.utc))
    _updated_at = db.Column('updated_at', db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    _is_active = db.Column('is_active', db.Boolean, default=False)  # Current production model
    _description = db.Column('description', db.Text, nullable=True)

    # Model หนึ่งตัวมี prediction/training history หลาย record
    predictions = db.relationship('Prediction', backref='model', lazy=True)
    training_history = db.relationship('TrainingHistory', backref='model', lazy=True)

    def __init__(self, **kwargs):
        """Explicit constructor for MLModel."""
        name = kwargs.pop('name', None)
        accuracy = kwargs.pop('accuracy', None)
        model_type = kwargs.pop('model_type', None)
        version = kwargs.pop('version', None)
        file_path = kwargs.pop('file_path', None)
        is_active = kwargs.pop('is_active', None)
        precision = kwargs.pop('precision', None)
        recall = kwargs.pop('recall', None)
        f1_score = kwargs.pop('f1_score', None)
        description = kwargs.pop('description', None)
        
        super(MLModel, self).__init__(**kwargs)
        if name: self.name = name
        if accuracy is not None: self.accuracy = accuracy
        if model_type: self.model_type = model_type
        if version: self.version = version
        if file_path: self.file_path = file_path
        if is_active is not None: self.is_active = is_active
        if precision is not None: self.precision = precision
        if recall is not None: self.recall = recall
        if f1_score is not None: self.f1_score = f1_score
        if description is not None: self.description = description

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value

    @property
    def accuracy(self):
        return self._accuracy
    
    @accuracy.setter
    def accuracy(self, value):
        if value is not None and (value < 0 or value > 1):
            raise ValueError("Accuracy must be between 0 and 1")
        self._accuracy = value

    @property
    def model_type(self):
        return self._model_type

    @model_type.setter
    def model_type(self, value):
        self._model_type = value

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, value):
        self._version = value

    @property
    def file_path(self):
        return self._file_path

    @file_path.setter
    def file_path(self, value):
        self._file_path = value

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, value):
        self._is_active = value

    @property
    def precision(self):
        return self._precision

    @precision.setter
    def precision(self, value):
        self._precision = value

    @property
    def recall(self):
        return self._recall

    @recall.setter
    def recall(self, value):
        self._recall = value

    @property
    def f1_score(self):
        return self._f1_score

    @f1_score.setter
    def f1_score(self, value):
        self._f1_score = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def created_at(self):
        return self._created_at

    @property
    def updated_at(self):
        return self._updated_at

    # Complex Business Logic
    def evaluate_model_health(self) -> dict:
        """
        Analyze if the model metrics are consistent and healthy.
        Checks for overfitting/underfitting patterns.
        """
        health_status = "Excellent"
        warnings = []
        
        if self._accuracy is not None and self._accuracy < 0.6:
            health_status = "Poor"
            warnings.append("Low accuracy detected")
            
        if self.precision and self.recall:
            diff = abs(self.precision - self.recall)
            if diff > 0.3:
                health_status = "Warning"
                warnings.append("High imbalance between precision and recall")
                
        return {
            "model": self.name,
            "status": health_status,
            "warnings": warnings,
            "checked_at": datetime.now(timezone.utc).isoformat()
        }

    def __repr__(self):
        return f'<MLModel {self.name} v{self.version}>'


class Prediction(db.Model):
    """Stores prediction results linked to parking areas."""
    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('ml_models.id'), nullable=False)
    parking_area_id = db.Column(db.Integer, db.ForeignKey('parking_areas.id'), nullable=False)
    
    # ผลลัพธ์ที่ frontend ใช้แสดง เช่น likely_full พร้อม confidence
    _prediction_value = db.Column('prediction_value', db.String(50), nullable=False)  # e.g., 'likely_full', 'available', 'moderate'
    _confidence_score = db.Column('confidence_score', db.Float, nullable=False)  # 0.0 to 1.0
    predicted_available_slots = db.Column(db.Integer, nullable=True)
    
    # เก็บ input features เป็น JSON string เพื่อย้อนดูได้ว่า prediction นี้คำนวณจากข้อมูลอะไร
    input_features = db.Column(db.Text, nullable=True)  # JSON string of features
    
    # Metadata
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_accurate = db.Column(db.Boolean, nullable=True)  # Validated against actual data later

    # Relationship to parking area
    parking_area = db.relationship('ParkingArea', backref='predictions')

    def __init__(self, **kwargs):
        """Explicit constructor for Prediction."""
        val = kwargs.pop('prediction_value', None)
        conf = kwargs.pop('confidence_score', None)
        super(Prediction, self).__init__(**kwargs)
        if val: self.prediction_value = val
        if conf: self.confidence_score = conf

    @property
    def prediction_value(self):
        return self._prediction_value
    
    @prediction_value.setter
    def prediction_value(self, value):
        self._prediction_value = value

    @property
    def confidence_score(self):
        return self._confidence_score
    
    @confidence_score.setter
    def confidence_score(self, value):
        self._confidence_score = value

    # Complex Business Logic
    def get_formatted_result(self) -> str:
        """
        Process the raw prediction data into a human-friendly sentence.
        Involves conditional logic based on confidence and value.
        """
        certainty = "highly likely" if self._confidence_score > 0.8 else "likely"
        if self._prediction_value == 'available':
            return f"It is {certainty} that spaces are available ({int(self._confidence_score*100)}% confidence)."
        elif self._prediction_value == 'likely_full':
            return f"The area is {certainty} to be full. Consider alternatives."
        else:
            return f"Status is moderate with {int(self._confidence_score*100)}% confidence."

    def __repr__(self):
        return f'<Prediction {self.parking_area_id}: {self.prediction_value} ({self.confidence_score}%)>'


class TrainingHistory(db.Model):
    """Records training sessions and performance metrics."""
    __tablename__ = 'training_history'

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('ml_models.id'), nullable=False)
    
    # เก็บไว้รองรับงาน train model จริงในอนาคต
    training_start_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    training_end_time = db.Column(db.DateTime, nullable=True)
    training_duration_seconds = db.Column(db.Float, nullable=True)
    
    # Dataset info
    training_samples_count = db.Column(db.Integer, nullable=True)
    validation_split_ratio = db.Column(db.Float, default=0.2)
    
    # Performance metrics
    training_loss = db.Column(db.Float, nullable=True)
    validation_loss = db.Column(db.Float, nullable=True)
    _training_accuracy = db.Column('training_accuracy', db.Float, nullable=True)
    validation_accuracy = db.Column(db.Float, nullable=True)
    
    # Training status
    _status = db.Column('status', db.String(20), default='in_progress')  # 'in_progress', 'completed', 'failed'
    error_message = db.Column(db.Text, nullable=True)  # If training failed
    
    notes = db.Column(db.Text, nullable=True)  # Additional notes or hyperparameters used

    def __init__(self, **kwargs):
        """Explicit constructor for TrainingHistory."""
        status = kwargs.pop('status', None)
        acc = kwargs.pop('training_accuracy', None)
        super(TrainingHistory, self).__init__(**kwargs)
        if status: self.status = status
        if acc: self.training_accuracy = acc

    @property
    def status(self):
        return self._status
    
    @status.setter
    def status(self, value):
        self._status = value

    @property
    def training_accuracy(self):
        return self._training_accuracy
    
    @training_accuracy.setter
    def training_accuracy(self, value):
        self._training_accuracy = value

    # Complex Business Logic
    def analyze_training_efficiency(self) -> float:
        """
        Calculate samples processed per second.
        Handles division by zero and None values.
        """
        if not self.training_duration_seconds or not self.training_samples_count:
            return 0.0
        
        if self.training_duration_seconds <= 0:
            return 0.0
            
        return self.training_samples_count / self.training_duration_seconds

    def __repr__(self):
        return f'<TrainingHistory Model-{self.model_id}: {self.status}>'
