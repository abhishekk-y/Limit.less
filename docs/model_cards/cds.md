# Career Distance Score (CDS) Model Card

## Purpose
CDS quantifies the effort or "distance" a candidate must traverse to qualify for a target role, factoring in missing prerequisite skills.

## Training Data
Based on the NetworkX `skill_relations` graph (prerequisites and co-occurrences).

## Evaluation Metrics
- **Path Length**: Shortest path sum in the directed graph.
- **Node Weight**: Complexity of the missing skill (inferred from average learning time data).

## Limitations
- Assumes linear learning paths, which might not reflect self-taught non-linear journeys.

## Fairness & Lineage
- **Lineage**: Candidate skills vs Role skills -> Graph traversal -> CDS (0-100, lower is closer).
- **Fairness**: Validated against diverse educational backgrounds to ensure distance isn't inflated for non-traditional degrees.
