# Skill Health Index (SHI) Model Card

## Purpose
The SHI module evaluates the market demand trend and relevance of a skill over time.

## Training Data
Uses aggregated monthly job posting data, calculating rolling averages and momentum indicators.
Source data: Publicly available tech job boards and survey datasets.

## Evaluation Metrics
- **Momentum Score**: Derivative of skill counts over a 6-month period.
- **Base Demand**: Log-normalized counts.

## Limitations
- Lags behind sudden micro-trends (e.g., a viral new library).
- Depends heavily on the quality and volume of job postings crawled.

## Fairness & Lineage
- **Lineage**: Raw job counts -> 6-month MA -> Log-normalization -> SHI (0-100).
- **Fairness**: Assessed for regional biases to ensure SHI isn't skewed solely by Tier-1 city data.
