import numpy as np
from scipy.optimize import curve_fit
from pydantic import BaseModel
from typing import List, Tuple
from datetime import datetime

class SHIResult(BaseModel):
    k: float
    half_life_or_doubling: float
    r2: float
    confidence_interval: Tuple[float, float]
    trend_class: str

class SHICalculator:
    def __init__(self, min_data_points: int = 6):
        self.min_data_points = min_data_points

    def exponential_model(self, t, A, k):
        return A * np.exp(k * t)

    def compute(self, skill_id: str, monthly_counts: List[Tuple[datetime, int]]) -> SHIResult:
        if len(monthly_counts) < self.min_data_points:
            raise ValueError("Insufficient data points")
        
        times = np.array([(d[0] - monthly_counts[0][0]).days / 30.0 for d in monthly_counts])
        counts = np.array([d[1] for d in monthly_counts])
        
        try:
            popt, pcov = curve_fit(self.exponential_model, times, counts, p0=(counts[0], 0))
            A, k = popt
            err = np.sqrt(np.diag(pcov))
            ci = (float(k - 1.96*err[1]), float(k + 1.96*err[1]))
            
            residuals = counts - self.exponential_model(times, *popt)
            ss_res = np.sum(residuals**2)
            ss_tot = np.sum((counts - np.mean(counts))**2)
            r2 = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            half_life_or_doubling = float(np.log(2) / abs(k)) if k != 0 else float('inf')
            trend = self.get_trend_class(k, r2)
            
            return SHIResult(k=k, half_life_or_doubling=half_life_or_doubling, r2=r2, confidence_interval=ci, trend_class=trend)
        except:
            return SHIResult(k=0.0, half_life_or_doubling=float('inf'), r2=0.0, confidence_interval=(0.0, 0.0), trend_class='stable')

    def get_trend_class(self, k: float, r2: float) -> str:
        if r2 < 0.3: return 'stable'
        if k > 0.1: return 'exploding'
        if k > 0.02: return 'emerging'
        if k < -0.1: return 'decaying'
        if k < -0.02: return 'cooling'
        return 'stable'
