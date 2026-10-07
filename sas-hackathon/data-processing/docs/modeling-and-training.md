# Limit.less modeling and training plan

## Decision: what the project is modeling

The hackathon's main objective is to analyze the supplied job datasets and produce traceable skill-demand evidence. The market files do not contain a trustworthy labeled outcome for supervised prediction, so the primary analytical engine is a set of auditable statistical and graph methods—not a fabricated “AI predicts hiring” model.

There are two deliberately separate lanes:

1. **Challenge analysis (SAS VFL only):** Analytics Jobs and DataScience Jobs support posting-level demand summaries, skill co-occurrence, weighted/unweighted comparisons, and robustness scenarios. JDS is a separate, optional exploratory model lane. SDS remains separate and descriptive only.
2. **Limit.less guided search (web product):** A user enters a role goal, preferred skills and location. The service ranks that account's active, non-demo public listings and explains the match. It does not read the SAS challenge files or another user's listings.

## Current implementation and truthful status

| Component | Current state | What that means |
| --- | --- | --- |
| Skill extraction from a posting | Curated phrase/alias rules in the current taxonomy | Deterministic; not a trained NLP extractor, can miss synonyms and context. |
| Existing career readiness and role match | Deterministic evidence coverage and curated taxonomy | An interpretable planning signal; not a probability of getting hired. |
| Guided listing ranker | Implemented as `guided-tfidf-1.0`; fit per request to one user's active, non-demo saved listings | A corpus-fitted, unsupervised retrieval model; no supervised relevance labels, persisted model file, cross-user corpus, or hiring outcomes. |
| SAS challenge models | VFL starter programs exist; no successful VFL run receipt is available | No challenge-data model has been trained or evaluated yet. Do not claim otherwise. |
| JDS exploratory classifier | Draft SAS logistic experiment exists, and its invalid unused SQL diagnostics were removed | Not run. It requires exact verified field mappings and organizer approval in VFL. |
| Demand forecast | Withheld | The challenge files do not provide enough verified, comparable time observations to support it. |

The guided search implementation passing local software tests demonstrates that the code path runs on test fixtures. It does not establish ranking quality on live user data or a trained challenge-data model.

## Guided search: inputs, processing, and score

Inputs are the user's typed role/career goal, optional preferred location, optional priority skills, the user's own saved skill evidence, and their own active postings imported from public boards. Demo listings are excluded. The listing documents are limited to title, curated detected skills, description, and location. Account scoping happens before the ranker is fit.

Processing sequence:

1. Normalize text to lowercase tokens and bound the description length.
2. Give job-title tokens threefold weight and detected-skill tokens fourfold weight, then include description tokens.
3. Fit inverse document-frequency weights to the current account's candidate listings for this request. No SAS challenge file, external service, or other account contributes to this fit.
4. Build a query vector from the user's goal and priority skills. Calculate TF-IDF cosine similarity to each listing.
5. Separately calculate whether priority skills appear in listing text, whether listing skills overlap saved user evidence (with the current STS evidence score), and whether the requested location appears in the listing location.
6. Renormalize weights over the evidence that exists, sort by score, and return the component breakdown and matched/missing skills.

For token (t) in listing (d), the corpus fit uses:

\[
\operatorname{tf}(t,d)=1+\ln(c_{t,d}),\qquad
\operatorname{idf}(t)=\ln\!\left(1+\frac{N+1}{\operatorname{df}(t)+1}\right),
\]

where (c_{t,d}) is the bounded token count, (N) is the number of the user's candidate listings, and \(\operatorname{df}(t)\) is the number of those listings containing the token. The weighted vector is \(v_{t,d}=\operatorname{tf}(t,d)\operatorname{idf}(t)\). Text relevance is the cosine similarity:

\[
R(q,d)=\frac{\sum_t v_{t,q}v_{t,d}}{\sqrt{\sum_t v_{t,q}^{2}}\sqrt{\sum_t v_{t,d}^{2}}}.
\]

The current normalized component score is:

\[
S(d)=100\,\frac{0.55\,\widetilde R(d)+0.20\,T(d)+0.20\,P(d)+0.05\,L(d)}{\sum_{k\in A}w_k},
\]

where \(\widetilde R(d)=R(q,d)/\max_j R(q,j)\) for this result set, \(T(d)\) is the fraction of user-priority skills found in the listing, \(P(d)=|K_d|^{-1}\sum_{s\in K_d} E_u(s)\) is evidence coverage over the listing's detected skills, and \(L(d)\in\{0,1\}\) is a simple location text match. Here \(E_u(s)=\mathrm{STS}_u(s)/100\) when the saved skill score is at least 50, and zero otherwise; a missing skill therefore contributes zero. The active component set \(A\) and its weights \(w_k\) are renormalized if the user did not provide a location, priority skills, or saved profile evidence. If a listing has no detected skills, the profile coverage component is omitted rather than treating the user as a zero match.

**Interpretation:** 0–100 is a relative ordering aid for the current saved listing set. It is not calibrated across searches, not a percentage chance, not evidence of eligibility, and not an employment prediction. A one-listing corpus is marked `small_corpus_fallback`; a two-listing fit is still not an evaluation. The code currently has no relevance-label training or offline ranking benchmark.

## What would make guided search a genuinely supervised model

With explicit consent, collect query–listing relevance judgments such as “not relevant / relevant / strong fit,” with enough users, employers, time periods, and positive/negative examples. Do not treat a click or an application alone as proof of quality. Keep this feedback separate from challenge data.

Then freeze a baseline and evaluation protocol before training:

- Baseline: current corpus-fitted TF-IDF plus explicit skill evidence.
- Candidate learner: a small learning-to-rank model (for example, LambdaMART) only if there are sufficient independent labeled queries; otherwise retain the baseline.
- Split by user and employer, and preferably by time, to prevent the same user/employer/template from appearing in training and test. Fit normalization and feature selection only inside each training fold.
- Primary metric: NDCG@10; also report Recall@10 and MRR with confidence intervals, query coverage, subgroup/source breakdowns, and sample counts.
- Release gate: ranker must beat the baseline on a locked holdout without unacceptable source, location, or other measured subgroup regressions. If it does not, ship the simpler baseline and report the negative result.

There is currently no approved labeled interaction dataset, so a supervised ranker must not be described as trained.

## SAS/VFL exploratory JDS model (not the main product model)

The optional program `sas/40_jds_exploratory_model.sas` tests one narrow question: do the five verified JDS skill-dimension fields discriminate the dataset's supplied binary high/low salary-hike label within that workbook? It must never be interpreted as predicting a salary amount, job offer, individual performance, or a learner's job match. It does not read Analytics Jobs, DataScience Jobs, or SDS; no cross-file joins are allowed.

### Inputs and preprocessing

Inside VFL only: confirm the actual outcome field, five numeric skill-dimension fields, label mapping, and a file-local repeated-person ID from `PROC CONTENTS` and the organizer's codebook. The program keeps only mapped high/low outcomes and complete numeric feature rows; unparseable and incomplete values are counted in the coverage table and excluded from the model fit. A verified repeated ID is hashed deterministically so every row for that person stays in one fold. A fold with either class missing blocks the experiment. No ID or row-level prediction is exported.

### Model and evaluation

For each held-out group fold (f), fit logistic regression on the other folds:

\[
\operatorname{logit}\Pr(Y_i=1\mid\mathbf{x}_i)
=\beta_0+\sum_{j=1}^{5}\beta_jx_{ij},\qquad
\operatorname{logit}(p)=\ln\!\left(\frac{p}{1-p}\right).
\]

The fold-only prevalence baseline predicts (\hat p_{i,0}=\bar Y_{-f}\); the logistic model predicts (\hat p_{i,1}\). Pool only out-of-fold predictions for:

\[
\mathrm{Brier}=\frac{1}{n}\sum_i(\hat p_i-y_i)^2,\qquad
\mathrm{Accuracy}_{0.5}=\frac{1}{n}\sum_i\mathbb{1}[\mathbb{1}(\hat p_i\ge0.5)=y_i],
\]

and ROC AUC from pooled out-of-fold ranks. Compare the logistic model with the prevalence baseline; a model is not useful merely because it ran. The final full-sample coefficient table is exploratory description only and stays in the VFL session. Given the small sample, this experiment is likely underpowered and cannot justify deployment even if within-sample metrics look high.

### VFL run requirements

1. Confirm organizer permission for this JDS experiment.
2. Import and inspect source schemas within VFL. Verify all variable meanings; do not infer them from spreadsheet column positions.
3. Execute preflight, quality, market and trait programs; inspect SAS logs and gates.
4. Populate the JDS model mappings only after the label, scales, and repeated-ID semantics are confirmed.
5. Run the JDS experiment in the same VFL session and save configuration, code version, fold diagnostics, complete-case coverage, baseline/model metrics, and a safe run receipt in VFL.
6. Report status as NOT RUN / BLOCKED until the run receipt exists. Do not export raw, row-level, or derived challenge results into the web app without written organizer authorization.

## Immediate status

The product's guided retrieval code is implemented and covered by local software tests. SAS/VFL has not been authenticated or executed in this environment, so the JDS model and challenge-data analysis remain **NOT RUN**. The next evidence needed for the SAS model is an authorized VFL session and verified schema/label/ID mappings; actual run metrics must come from that session.
