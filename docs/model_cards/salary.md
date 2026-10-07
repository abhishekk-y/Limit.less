# Salary Predictor Model Card

## Purpose
Predicts expected salary ranges based on role, location, experience, and skill set, adjusting for cost of living.

## Training Data
- Aggregated public survey data
- Cost of living indices for 30+ Indian cities

## Evaluation Metrics
- Mean Absolute Error (MAE) evaluated on holdout survey datasets.

## Limitations
- Salary predictions may lag behind real-time market shifts.
- Heavily dependent on self-reported data accuracy.

## Fairness & Lineage
- **Lineage**: Base Salary Data -> Location Index Multiplier -> Experience Multiplier.
- **Fairness**: Does not use demographic data (age, gender, ethnicity) for predictions.
