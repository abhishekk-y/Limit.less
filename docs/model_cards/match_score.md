# Match Score Model Card

## Purpose
Produces a composite score (0-100) indicating the overall fit between a candidate and an opportunity.

## Training Data
A deterministic formula weighting:
- STS (Semantic Textual Similarity) of profile and JD (30%)
- CDS (Career Distance Score) inversion (40%)
- SOE (Strength of Evidence) for claimed skills (30%)

## Evaluation Metrics
- Hand-calculated match scores verified against ground truth labels provided by domain experts.

## Limitations
- Rule-based weighting may not capture nuanced soft-skill requirements.

## Fairness & Lineage
- **Lineage**: Combine STS, CDS, SOE -> Weighted sum -> Match Score.
- **Fairness**: Formulaic approach ensures no "black box" bias based on protected attributes (name, gender, etc.).
