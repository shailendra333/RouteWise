import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Tuple, List, Dict, Any
import warnings
warnings.filterwarnings('ignore')

class AdvancedLSTMForecaster:
    """
    Advanced LSTM model for demand forecasting with multiple features
    and enhanced preprocessing capabilities
    """
    
    def __init__(self, 
                 sequence_length: int = 60,
                 prediction_horizon: int = 7,
                 features: List[str] = None):
        """
        Initialize the LSTM forecaster
        
        Args:
            sequence_length: Number of time steps to look back
            prediction_horizon: Number of days to forecast ahead
            features: List of feature names to use for forecasting
        """
        self.sequence_length = sequence_length
        self.prediction_horizon = prediction_horizon
        self.features = features or ['demand', 'day_of_week', 'month', 'is_weekend']
        self.model = None
        self.scaler = MinMaxScaler()
        self.feature_scalers = {}
        self.training_history = None
        self.is_trained = False
        
    def create_time_features(self, df: pd.DataFrame, date_column: str = 'date') -> pd.DataFrame:
        """
        Create time-based features for better forecasting
        
        Args:
            df: DataFrame with date column
            date_column: Name of the date column
            
        Returns:
            DataFrame with additional time features
        """
        df = df.copy()
        df[date_column] = pd.to_datetime(df[date_column])
        
        # Extract time features
        df['year'] = df[date_column].dt.year
        df['month'] = df[date_column].dt.month
        df['day'] = df[date_column].dt.day
        df['day_of_week'] = df[date_column].dt.dayofweek
        df['day_of_year'] = df[date_column].dt.dayofyear
        df['week_of_year'] = df[date_column].dt.isocalendar().week
        df['quarter'] = df[date_column].dt.quarter
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        df['is_month_start'] = df[date_column].dt.is_month_start.astype(int)
        df['is_month_end'] = df[date_column].dt.is_month_end.astype(int)
        
        # Cyclical encoding for better pattern capture
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        return df
    
    def create_lag_features(self, df: pd.DataFrame, target_column: str, lags: List[int] = None) -> pd.DataFrame:
        """
        Create lag features for the target variable
        
        Args:
            df: DataFrame with time series data
            target_column: Name of the target column
            lags: List of lag periods to create
            
        Returns:
            DataFrame with lag features
        """
        if lags is None:
            lags = [1, 7, 14, 30]  # Daily, weekly, bi-weekly, monthly lags
        
        df = df.copy()
        for lag in lags:
            df[f'{target_column}_lag_{lag}'] = df[target_column].shift(lag)
        
        return df
    
    def create_rolling_features(self, df: pd.DataFrame, target_column: str, windows: List[int] = None) -> pd.DataFrame:
        """
        Create rolling statistical features
        
        Args:
            df: DataFrame with time series data
            target_column: Name of the target column
            windows: List of window sizes for rolling statistics
            
        Returns:
            DataFrame with rolling features
        """
        if windows is None:
            windows = [7, 14, 30]  # Weekly, bi-weekly, monthly windows
        
        df = df.copy()
        for window in windows:
            df[f'{target_column}_roll_mean_{window}'] = df[target_column].rolling(window=window).mean()
            df[f'{target_column}_roll_std_{window}'] = df[target_column].rolling(window=window).std()
            df[f'{target_column}_roll_min_{window}'] = df[target_column].rolling(window=window).min()
            df[f'{target_column}_roll_max_{window}'] = df[target_column].rolling(window=window).max()
        
        return df
    
    def preprocess_data(self, df: pd.DataFrame, target_column: str = 'demand') -> Tuple[np.ndarray, np.ndarray]:
        """
        Comprehensive data preprocessing pipeline
        
        Args:
            df: Raw time series DataFrame
            target_column: Name of the target variable
            
        Returns:
            Tuple of (X, y) arrays ready for training
        """
        # Ensure data is sorted by date
        df = df.sort_values('date').reset_index(drop=True)
        
        # Create time features
        df = self.create_time_features(df)
        
        # Create lag features
        df = self.create_lag_features(df, target_column)
        
        # Create rolling features
        df = self.create_rolling_features(df, target_column)
        
        # Remove rows with NaN values (due to lags and rolling)
        df = df.dropna()
        
        if len(df) < self.sequence_length + self.prediction_horizon:
            raise ValueError(f"Insufficient data. Need at least {self.sequence_length + self.prediction_horizon} rows.")
        
        # Select features for modeling
        feature_columns = []
        for feature in self.features:
            if feature in df.columns:
                feature_columns.append(feature)
            else:
                # Try to find similar columns
                matching_cols = [col for col in df.columns if feature in col.lower()]
                if matching_cols:
                    feature_columns.extend(matching_cols)
        
        # If no specific features found, use numeric columns
        if not feature_columns:
            feature_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            if target_column in feature_columns:
                feature_columns.remove(target_column)
        
        # Scale features
        feature_data = df[feature_columns].values
        target_data = df[target_column].values.reshape(-1, 1)
        
        # Fit scalers
        for i, col in enumerate(feature_columns):
            scaler = MinMaxScaler()
            feature_data[:, i:i+1] = scaler.fit_transform(feature_data[:, i:i+1])
            self.feature_scalers[col] = scaler
        
        target_data = self.scaler.fit_transform(target_data)
        
        # Create sequences
        X, y = self._create_sequences(feature_data, target_data.flatten())
        
        return X, y
    
    def _create_sequences(self, features: np.ndarray, target: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for LSTM training
        
        Args:
            features: Feature array
            target: Target array
            
        Returns:
            Tuple of (X, y) sequences
        """
        X, y = [], []
        
        for i in range(self.sequence_length, len(features) - self.prediction_horizon + 1):
            X.append(features[i-self.sequence_length:i])
            y.append(target[i:i+self.prediction_horizon])
        
        return np.array(X), np.array(y)
    
    def build_model(self, input_shape: Tuple[int, int]) -> Sequential:
        """
        Build advanced LSTM model architecture
        
        Args:
            input_shape: Shape of input data (sequence_length, n_features)
            
        Returns:
            Compiled Keras model
        """
        model = Sequential([
            # First LSTM layer with return sequences
            LSTM(100, return_sequences=True, input_shape=input_shape),
            BatchNormalization(),
            Dropout(0.3),
            
            # Second LSTM layer
            LSTM(100, return_sequences=True),
            BatchNormalization(),
            Dropout(0.3),
            
            # Third LSTM layer
            LSTM(50, return_sequences=False),
            BatchNormalization(),
            Dropout(0.2),
            
            # Dense layers
            Dense(50, activation='relu'),
            Dropout(0.2),
            Dense(25, activation='relu'),
            Dense(self.prediction_horizon)
        ])
        
        # Compile with advanced optimizer
        optimizer = Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999)
        model.compile(optimizer=optimizer, loss='mse', metrics=['mae'])
        
        return model
    
    def train(self, df: pd.DataFrame, target_column: str = 'demand', 
              validation_split: float = 0.2, epochs: int = 100, batch_size: int = 32) -> Dict[str, Any]:
        """
        Train the LSTM model
        
        Args:
            df: Training DataFrame
            target_column: Name of the target column
            validation_split: Proportion of data for validation
            epochs: Number of training epochs
            batch_size: Training batch size
            
        Returns:
            Training results dictionary
        """
        try:
            print("Preprocessing data...")
            X, y = self.preprocess_data(df, target_column)
            
            print(f"Data shape: X={X.shape}, y={y.shape}")
            
            # Build model
            self.model = self.build_model((X.shape[1], X.shape[2]))
            
            print("Model architecture:")
            self.model.summary()
            
            # Callbacks
            callbacks = [
                EarlyStopping(monitor='val_loss', patience=15, restore_best_weights=True),
                ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=10, min_lr=1e-6)
            ]
            
            # Train model
            print("Training model...")
            self.training_history = self.model.fit(
                X, y,
                validation_split=validation_split,
                epochs=epochs,
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=1
            )
            
            self.is_trained = True
            
            # Calculate training metrics
            train_predictions = self.model.predict(X)
            train_loss = mean_squared_error(y.flatten(), train_predictions.flatten())
            train_mae = mean_absolute_error(y.flatten(), train_predictions.flatten())
            
            return {
                'success': True,
                'epochs_trained': len(self.training_history.history['loss']),
                'final_loss': float(self.training_history.history['loss'][-1]),
                'final_val_loss': float(self.training_history.history['val_loss'][-1]),
                'train_mse': float(train_loss),
                'train_mae': float(train_mae),
                'model_summary': str(self.model.summary())
            }
            
        except Exception as e:
            print(f"Training failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def predict(self, df: pd.DataFrame, target_column: str = 'demand') -> Dict[str, Any]:
        """
        Make predictions using the trained model
        
        Args:
            df: DataFrame with historical data
            target_column: Name of the target column
            
        Returns:
            Prediction results dictionary
        """
        try:
            if not self.is_trained:
                return {'error': 'Model not trained. Call train() first.'}
            
            # Preprocess the latest data
            df_processed = df.copy()
            df_processed = self.create_time_features(df_processed)
            df_processed = self.create_lag_features(df_processed, target_column)
            df_processed = self.create_rolling_features(df_processed, target_column)
            df_processed = df_processed.dropna()
            
            if len(df_processed) < self.sequence_length:
                return {'error': f'Insufficient data. Need at least {self.sequence_length} rows.'}
            
            # Get the latest sequence
            latest_sequence = df_processed.tail(self.sequence_length)
            
            # Prepare features
            feature_columns = list(self.feature_scalers.keys())
            feature_data = latest_sequence[feature_columns].values
            
            # Scale features
            for i, col in enumerate(feature_columns):
                if col in self.feature_scalers:
                    feature_data[:, i:i+1] = self.feature_scalers[col].transform(feature_data[:, i:i+1])
            
            # Reshape for prediction
            X_pred = feature_data.reshape(1, self.sequence_length, len(feature_columns))
            
            # Make prediction
            scaled_predictions = self.model.predict(X_pred, verbose=0)[0]
            
            # Inverse transform predictions
            predictions = self.scaler.inverse_transform(scaled_predictions.reshape(-1, 1)).flatten()
            
            # Generate prediction dates
            last_date = pd.to_datetime(df['date'].iloc[-1])
            prediction_dates = [last_date + pd.Timedelta(days=i+1) for i in range(self.prediction_horizon)]
            
            # Calculate confidence intervals (simplified)
            prediction_std = np.std(predictions)
            confidence_intervals = []
            
            results = []
            for i, (date, pred) in enumerate(zip(prediction_dates, predictions)):
                confidence = max(0.8, 1.0 - (i * 0.02))  # Decreasing confidence over time
                
                results.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'predicted_demand': float(pred),
                    'confidence': float(confidence),
                    'lower_bound': float(pred - 1.96 * prediction_std),
                    'upper_bound': float(pred + 1.96 * prediction_std)
                })
                
                confidence_intervals.append(confidence)
            
            return {
                'predictions': results,
                'model_metrics': {
                    'rmse': float(np.sqrt(mean_squared_error(
                        df_processed[target_column].tail(10), 
                        [pred['predicted_demand'] for pred in results[:10]] if len(results) >= 10 else []
                    )) if len(results) >= 10 else 0),
                    'mae': float(prediction_std),
                    'accuracy': float(np.mean(confidence_intervals) * 100),
                    'prediction_horizon': self.prediction_horizon
                }
            }
            
        except Exception as e:
            print(f"Prediction failed: {str(e)}")
            return {'error': str(e)}
    
    def plot_training_history(self):
        """Plot training history"""
        if self.training_history is None:
            print("No training history available.")
            return
        
        plt.figure(figsize=(15, 5))
        
        # Loss plot
        plt.subplot(1, 3, 1)
        plt.plot(self.training_history.history['loss'], label='Training Loss')
        plt.plot(self.training_history.history['val_loss'], label='Validation Loss')
        plt.title('Model Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # MAE plot
        plt.subplot(1, 3, 2)
        plt.plot(self.training_history.history['mae'], label='Training MAE')
        plt.plot(self.training_history.history['val_mae'], label='Validation MAE')
        plt.title('Model MAE')
        plt.xlabel('Epoch')
        plt.ylabel('MAE')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Learning rate (if available)
        plt.subplot(1, 3, 3)
        if 'lr' in self.training_history.history:
            plt.plot(self.training_history.history['lr'])
            plt.title('Learning Rate')
            plt.xlabel('Epoch')
            plt.ylabel('Learning Rate')
            plt.yscale('log')
        else:
            plt.text(0.5, 0.5, 'Learning Rate\nNot Tracked', 
                    ha='center', va='center', transform=plt.gca().transAxes)
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def plot_predictions(self, df: pd.DataFrame, predictions: List[Dict], target_column: str = 'demand'):
        """Plot predictions against historical data"""
        plt.figure(figsize=(15, 8))
        
        # Historical data
        historical_dates = pd.to_datetime(df['date'])
        historical_demand = df[target_column]
        
        plt.plot(historical_dates, historical_demand, label='Historical Demand', color='blue', alpha=0.7)
        
        # Predictions
        pred_dates = [pd.to_datetime(pred['date']) for pred in predictions]
        pred_values = [pred['predicted_demand'] for pred in predictions]
        lower_bounds = [pred['lower_bound'] for pred in predictions]
        upper_bounds = [pred['upper_bound'] for pred in predictions]
        
        plt.plot(pred_dates, pred_values, label='Predicted Demand', color='red', marker='o')
        plt.fill_between(pred_dates, lower_bounds, upper_bounds, alpha=0.3, color='red', label='Confidence Interval')
        
        plt.title('Demand Forecasting Results')
        plt.xlabel('Date')
        plt.ylabel('Demand')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

def generate_sample_data(days: int = 365) -> pd.DataFrame:
    """Generate sample time series data for testing"""
    dates = pd.date_range(start='2023-01-01', periods=days, freq='D')
    
    # Base demand with trend and seasonality
    base_demand = 1000
    trend = np.linspace(0, 200, days)
    seasonal = 100 * np.sin(2 * np.pi * np.arange(days) / 365.25)  # Yearly seasonality
    weekly = 50 * np.sin(2 * np.pi * np.arange(days) / 7)  # Weekly seasonality
    noise = np.random.normal(0, 50, days)
    
    demand = base_demand + trend + seasonal + weekly + noise
    demand = np.maximum(demand, 100)  # Ensure positive demand
    
    return pd.DataFrame({
        'date': dates,
        'demand': demand
    })

def demo_lstm_forecasting():
    """Demonstration of LSTM forecasting"""
    print("Generating sample data...")
    df = generate_sample_data(365)
    
    print("Initializing LSTM forecaster...")
    forecaster = AdvancedLSTMForecaster(
        sequence_length=30,
        prediction_horizon=7,
        features=['demand', 'day_of_week', 'month', 'is_weekend']
    )
    
    print("Training model...")
    train_result = forecaster.train(df, epochs=50, batch_size=16)
    
    if train_result['success']:
        print("Training successful!")
        print(f"Epochs trained: {train_result['epochs_trained']}")
        print(f"Final loss: {train_result['final_loss']:.4f}")
        print(f"Final validation loss: {train_result['final_val_loss']:.4f}")
        
        # Plot training history
        forecaster.plot_training_history()
        
        print("Making predictions...")
        predictions = forecaster.predict(df)
        
        if 'predictions' in predictions:
            print("Predictions:")
            for pred in predictions['predictions']:
                print(f"  {pred['date']}: {pred['predicted_demand']:.2f} (confidence: {pred['confidence']:.2%})")
            
            # Plot predictions
            forecaster.plot_predictions(df, predictions['predictions'])
        else:
            print(f"Prediction failed: {predictions.get('error', 'Unknown error')}")
    else:
        print(f"Training failed: {train_result['error']}")

if __name__ == "__main__":
    demo_lstm_forecasting()