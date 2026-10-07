# Research synthesis — data processing and evidence visualization

## Findings supported across independent sources

1. **Online vacancy data is descriptive evidence with a bounded frame.** The ILO methods review, OECD methodological work, and UK ONS experimental vacancy methodology independently highlight source coverage, occupational skew, ad-versus-vacancy units, source changes, and duplicate handling. Limit.less should say “records/postings in the supplied file” and show source/denominator, not claim all-market vacancy totals.
2. **Skill extraction is a measurement pipeline, not just a model choice.** SkillSpan and weak-supervision research support explicit annotation rules/taxonomies and labeled evaluation. The current regex dictionary is a transparent baseline; it is not a trained model and should not be called validated until sampled labels and held-out evaluation exist.
3. **A supplied numeric weight needs a semantic and influence audit.** The sources support caution about posting units and representativeness; they do not validate this dataset’s `num_of_jobs` meaning. Show row counts and weight totals in parallel, check invalid values/concentration, and include predeclared cap/max-exclusion scenarios. Reweighting to a population is out of scope without a target frame and valid margins.
4. **Sensitivity analysis earns credibility only if choices are justified.** Specification-curve and multiverse literature support exposing analytic flexibility, while methodological critiques warn against treating all specifications as equally defensible. Our sensitivity scenarios should be enumerated before interpretation, preserve failures, and be called scenario comparisons—not full multiverse inference unless implemented.
5. **Charts should carry provenance and measurement limits.** Dashboard provenance work and controlled uncertainty-visualization studies motivate making source/run/denominator/method visible alongside every result. The direct usability benefit for this app remains a hypothesis to test, not a proven claim.

## Adversarial review

- **Could a sophisticated NLP model improve extraction?** Possibly; not before a locally labeled evaluation set and an approved model/evaluation procedure exist. An LLM call would risk data transfer and would make an unreviewed answer less auditable.
- **Would deduplicating be better?** It depends on the target unit. Exact-normalized-text duplicates are useful diagnostics; they may be mirrored records, repeated advertisements, or legitimately repeated records. Keep raw counts and sensitivity view, never silently delete.
- **Could the datasets be pooled for richer prediction?** No. They do not have a verified cross-file key or harmonized outcome; pooling would create a false sample and leak meaning across units.
- **Does a strong within-sample metric prove training value?** No. It would need external replication and an impact pilot. The JDS data cannot prove a causal learning intervention.
- **Would confidence intervals fix sampling bias?** No. They describe sampling variability under assumptions; they cannot repair nonprobability selection or unknown sampling design.

## Project decision

Keep the core MVP as a reproducible, four-lane evidence pipeline with source-specific charts, scenario comparisons, a JDS-only optional grouped experiment, and an SDS aggregate-only view. Prioritize correctness, mathematical definitions, auditability, and stop gates over model complexity. The deep `.mmd` diagrams are editable workflow specifications; they do not certify that SAS code executed.
