# Limit.less: Round 2 project definition

**Team:** Pookie Blinders · **Team ID:** 117  
Reviewed 7 October 2026 against the supplied organizer brief, data dictionary and the team's previous analytical output.

## The problem we are solving

Training teams and aspiring data professionals need to decide which skills to investigate and develop. Job advertisements contain inconsistent and incomplete descriptions, while small internal skill/outcome datasets describe a different population. Combining these without checking their meaning can produce misleading career advice.

**Our analytical objective:** identify observed role, skill, location and compensation patterns in the supplied job samples; examine separate exploratory skill/outcome associations; and translate supported findings into transparent learning and research priorities with explicit evidence limits.

Primary stakeholder: a university placement or training team planning data-career learning support. Secondary stakeholder: a learner exploring those priorities. We do not estimate an individual's hiring success or promise a salary increase.

## What we are building

A Limit.less Evidence workspace with four independent analytical views:

| View | Input | Useful output |
| --- | --- | --- |
| Job-market sample | Analytics Jobs.csv | Observed skills, roles, locations, missingness and salary/experience categories |
| Weighted demand | DataScience Jobs.csv | Record counts beside sums of num_of_jobs; company/title distributions; salary interpretation checks |
| Skill development research | JDS Skill Traits.xlsx | Within-sample skill/outcome associations, baseline comparisons and validation limits |
| Personality research | SDS Personality Traits.xlsx | Separate aggregate research findings and uncertainty; no individual screening or recommendation |

Every finding needs its source, denominator, method, missingness, uncertainty, limitation and next evidence request. Similar labels may support a reviewed conceptual comparison; they do not establish record linkage between files.

## Relationship to the existing product

The wider Limit.less application supplies career workflows: profiles, job discovery, resume preparation, learning plans and application tracking. These are a possible delivery surface for reviewed research. Scrapers, social automation, auto-apply and decorative admin graphs are not the core Round 2 analytical contribution.

The Super Admin research graph is a workflow interface. It is not proof of a running SAS pipeline, completed data analysis, or validated predictions.

## What the documents actually establish

The organizer brief describes 2024–25 sample job data and separate junior/senior trait datasets. Page 12 says to upload data to VFL **if using SAS**; page 23 says technology agnostic. Thus the supplied brief does not establish SAS as universally mandatory. Page 25 prohibits outside data transfers during the event; execution and sharing must respect the event environment. This statement is a reading of the supplied brief, not an independently confirmed organizer clarification.

The supplied files contain 15,841 Analytics rows, 1,602 DataScience rows, 139 JDS observations and 161 SDS observations. Descriptive counts and group associations have now been recalculated from these source files for the report. Prior model-performance values remain unverified until their fold assignments, preprocessing configuration and execution record are reproduced. A successful SAS VFL execution is not established without a run receipt.

## Round 2 deliverable and scoring

The organizer requests a 20–25-page Word approach note, excluding appendices, with 12-point single-spaced text preferred.

| Section | Marks | Evidence to prepare |
| --- | ---: | --- |
| Problem definition | 10 | One decision, clear stakeholder, scope and measurable objective |
| Approach | 15 | Data-to-result flow and reasons for method choices |
| Data exploration/preparation | 25 | Schemas, missingness, identifiers, parsing, weighting, exclusions and audit tables |
| Data analysis | 30 | Reproducible summaries, statistical methods, baselines and validation |
| Results and conclusions | 10 | Findings tied to the question, denominators and limitations |
| Implications | 10 | Specific stakeholder actions and a plan to measure value |

The supplied brief assigns final competition weighting of 70% Round 2 and 30% Round 3. A polished website alone does not satisfy the analytical report.

## Completion criteria

1. Record the exact source versions and schemas in the permitted environment.
2. Reproduce the reported data-quality and descriptive results; resolve any discrepancies.
3. Keep counts and supplied demand weights distinct; do not invent time trends from undated data.
4. Evaluate skill extraction on a reviewed sample or label keyword findings as unvalidated.
5. Keep JDS/SDS analyses separate; report baselines, repeated-ID handling and uncertainty for any model results.
6. Present evidence-backed charts and plain-language implications.
7. Write the required Word approach note with traceable appendix artifacts.
8. Test the implemented evidence interface and rehearse a short end-to-end demonstration.

No competition score, production readiness, causal effect, or real-world outcome is established by this scope document.
