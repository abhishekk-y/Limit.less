# Limit.less — analysis methodology

## Predeclared sequence

### 1. Freeze the scope

Record the organizer-approved data environment, source release, source filenames, receipt date, source table names, workbook sheets, data dictionary, code version, and analyst. The initial programs keep all intermediate and aggregate tables in SAS `WORK` and make no network requests.

### 2. Profile before transforming

Produce one source table per file, then field-level type, length, row count, missing count/rate, and notes. Keep exact duplicates and repeated IDs as diagnostics; do not delete records until the identifier semantics and deduplication rule are approved. For text fields, distinguish rows with no usable description from rows where the skill was not detected.

### 3. Market evidence

- Count an explicit canonical skill at most once per posting row. Begin with a transparent phrase dictionary; preserve the phrase mapping and version. Treat outputs as candidate lower-bound-like mentions, not verified requirements.
- Show the number of source rows, rows with usable text, and per-skill denominator beside every rate.
- For DataScience Jobs, report the 1,602-style record count separately from the sum of `num_of_jobs`. Show median, quartiles, maximum, and leave-one-maximum-out sensitivity. Do not call a weight sum unique vacancies.
- A SkillGraph edge means two candidate skills appeared in the same eligible posting. Predeclare minimum support and Jaccard as the edge measure. The graph remains an exploratory candidate until a human reviews mapping quality and template artifacts.
- No time trend can be inferred without reliable dates and repeated snapshots.

### 4. JDS and SDS

Keep the two workbooks separate. Confirm the exact outcome labels, five trait columns, measurement scale, and repeated-ID semantics from SAS metadata and the organizer codebook. The starter program produces aggregate group descriptions only; it does not train a person-level model. Do not interpret associations as causes. Do not use SDS for individual decisions.

### 5. Skill audit and validation

Before a skill result can support a product claim, draw a stratified phrase sample across frequent, ambiguous, and long-tail phrases and relevant role/text-availability groups. Have reviewers label an overlap subset, resolve disagreements, then freeze a separate evaluation set. Report precision, recall, F1, coverage, unmatched/abstention rate, agreement, and uncertainty. A semantic model may suggest candidate mappings but cannot replace human labels or be sent challenge text through an external API.

For the small trait samples, start with prevalence and descriptive baselines. The optional `sas/40_jds_exploratory_model.sas` experiment is restricted to JDS: the five verified skill-dimension fields predict only the supplied high/low salary-hike label within that dataset. It compares a training-fold prevalence baseline with a fixed five-feature logistic regression using five-fold grouped out-of-fold scoring; all rows with the same verified ID stay in one fold. It reports AUC, Brier score and threshold accuracy against the baseline. Incomplete feature rows are excluded and their coverage is shown; no data-driven feature selection or tuning is performed. No model is fit on SDS, job-posting rows, or cross-file joins. This experiment is not a hiring, job-fit, salary-amount, or individual recommendation model. Its small sample and single-source labels cannot support a production prediction claim. Require independent replication and new data before such a claim. The 98+ goal refers only to rubric completeness; it is not model accuracy or a guaranteed judge score.

### 6. Evidence Passport and action rule

Every eventual headline should record: claim; source and observation unit; denominator; calculation; source/code version; coverage; semantic audit quality; statistical stability; transportability; limitations; reviewer; and smallest next evidence step. Keep these dimensions separate—never average them into a cosmetic confidence score.

Permitted actions are **prioritize**, **review**, **collect evidence**, or **defer**. No finding is promoted to a Limit.less learner recommendation until event rules and an explicit aggregate-transfer contract allow it.

## Stop rules

Stop a chart or recommendation if it depends on an undocumented field, unresolved mapping, low/unknown coverage, an unreviewed parser choice, an influential extreme record, invalid join, or model performance without appropriate validation. Record it as NOT RUN, WARN, or BLOCKED as justified; do not fill gaps with demo values.
