# Architecture

SkillSetu X is built as a robust intelligence engine with NLP pipelines, ML scoring modules, and graph algorithms.

## System Overview

```mermaid
flowchart TD
    A[Data Ingestion] --> B[Skill Extraction NLP]
    B --> C[Normalization & Taxonomy]
    C --> D[Skill Graph / NetworkX]
    C --> E[Scoring Modules]
    D --> E
    E --> F[Match & Career GPS]
    F --> G[API Layer]
```

## Core Components
- **Taxonomy Engine**: Normalizes ESCO + O*NET data.
- **Scoring Modules**: Calculates STS, SHI, CDS, SOE deterministically.
- **Skill Graph**: Manages prerequisite and co-occurrence graphs using NetworkX.
