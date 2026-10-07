from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
import xgboost as xgb
import numpy as np
from typing import Dict, Any

class DemandForecaster:
    """Demand forecasting comparing multiple models."""
    
    def __init__(self):
        self.models = {
            "linear": LinearRegression(),
            "rf": RandomForestRegressor(),
            "xgb": xgb.XGBRegressor()
        }
        
    def validate_models(self, X_train, y_train, X_test, y_test) -> Dict[str, Any]:
        """Time-based validation returning metrics and best model."""
        metrics = {}
        best_model = None
        best_mape = float('inf')
        
        for name, model in self.models.items():
            model.fit(X_train, y_train)
            preds = model.predict(X_test)
            mape = np.mean(np.abs((y_test - preds) / y_test))
            mae = np.mean(np.abs(y_test - preds))
            metrics[name] = {"MAPE": float(mape), "MAE": float(mae)}
            
            if mape < best_mape:
                best_mape = mape
                best_model = name
                
        return {
            "metrics": metrics,
            "best_model": best_model,
            "reason": f"Lowest MAPE: {best_mape}"
        }
