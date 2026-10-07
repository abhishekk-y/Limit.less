# Semantic Textual Similarity (STS) Model Card

## Purpose
The STS module computes the semantic similarity between two textual descriptions (e.g., job requirements and candidate profiles) to determine how closely they align.

## Training Data
Uses pre-trained sentence-transformer models (`all-MiniLM-L6-v2`) fine-tuned on public domain-specific datasets (resume and job description pairs). 

## Evaluation Metrics
- **Pearson Correlation**: Evaluated on hand-calculated similarity pairs.
- **Cosine Similarity**: Baseline metric for deterministic matching.

## Limitations
- Struggles with highly abbreviated or poorly formatted text.
- Over-indexes on exact keyword matches if semantic context is minimal.

## Fairness & Lineage
- **Lineage**: Outputs deterministic scores backed by model version.
- **Fairness Audits**: Periodically audited to ensure no gender/racial bias is introduced by implicit associations in text embeddings.
