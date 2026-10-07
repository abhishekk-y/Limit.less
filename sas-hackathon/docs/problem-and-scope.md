# Limit.less — SAS hackathon problem and scope

## Problem statement

How can Limit.less help an early-career data professional or career adviser identify skills observed in the supplied job-posting sample and inspect separate development-research signals, while preserving the data boundary, showing coverage and uncertainty, and refusing unsupported hiring or personality-screening claims?

## Stakeholders and supported decision

- **Primary user:** an early-career analytics/data professional deciding which skill evidence or learning project to strengthen next.
- **Supporting user:** a career adviser helping a learner interpret sample-based market evidence.
- **Decision supported:** prioritize, investigate, collect more evidence, or defer a skill-development question.
- **Not supported:** hiring, shortlisting, candidate ranking, promotion, individual success prediction, or salary guarantees.

## Three answerable questions

1. In the supplied Analytics Jobs sample, which explicit skill phrases, role labels, locations, and salary/experience fields are observed, and how does missingness constrain each result?
2. In the separate DataScience Jobs file, how do title record counts differ from totals weighted by `num_of_jobs`, and how sensitive is the weighted summary to extreme values?
3. What descriptive hypotheses appear within JDS, and what separate governance findings appear within SDS? Which claims should be reviewed, supported with new evidence, or deferred?

## Four evidence islands

Analytics Jobs and DataScience Jobs are separate market samples. JDS is a separate development-research sample. SDS is a separate governance/research sample. Their identifiers are file-local; there is no verified common person, employer, role, or time key. The only potential comparison is an explicitly reviewed **skill-family concept crosswalk** between aggregate market signals and aggregate JDS findings. It is not a row join and does not establish causality. SDS has no path into learner recommendations.

## Claims we will not make

- “India’s live demand,” a national vacancy count, or a time trend from cross-sectional files.
- That a missing mention means a skill is not required.
- That `num_of_jobs` is a count of unique vacancies unless its source definition says so.
- That a JDS/SDS association is causal, generalizable, or a personal prediction.
- That a prior model score is production accuracy or independent validation.
- That the SAS analysis is integrated into Limit.less before an approved, tested connection exists.
