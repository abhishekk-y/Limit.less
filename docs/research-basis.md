# Limit.less research and data basis

Updated 7 October 2026. This is the source register for the current individual job-search insights prototype. External references inform taxonomy and evaluation choices; unless identified as imported in the user's workspace, they are not represented as live data in the product.

For the SAS hackathon's research design, data boundary, adversarial review, and stretch-score evidence plan, see [the hackathon methodology decision](hackathon-research/2026-10-07_methodology.md) and its [auditable source register](hackathon-research/sources.csv). No challenge records or computed findings are included in this repository.

## Current product data

The opportunity pulse reads user-selected public employer postings imported through the official Greenhouse and Lever public-board interfaces. It stores a dated, private snapshot for the current user containing active-posting counts, role titles, locations, employers, internship tags, matched taxonomy skills, skill-coverage rate and board refresh times. Re-importing a board marks missing prior postings inactive. A posting is counted once per provider/board/posting identifier. A same-day refresh updates that day's snapshot, so history represents daily observations rather than every button click.

Skill counts mean **posting mentions matched by the current curated taxonomy**. They are not a complete extraction of all skills, an employer's importance ranking, a vacancy probability, or a forecast. Role titles and locations are grouped from source text; they are not yet normalized across synonyms or geographies. Users can import multiple company boards, but the selected boards are a convenience sample, not a representative labor-market panel.

## Public references and appropriate use

| Reference | What it can support | Limits and use in Limit.less |
| --- | --- | --- |
| [SkillSpan dataset](https://github.com/kris927b/SkillSpan) and [NAACL 2022 paper](https://aclanthology.org/2022.naacl-main.366/) | An annotated English job-posting skill-span benchmark for evaluating extraction. | It is not Indian market coverage. Review the dataset license and terms before packaging it; do not train/evaluate on examples and claim Indian labor-market validity. |
| [JobBERT paper](https://arxiv.org/abs/2109.09605) and [evaluation dataset](https://huggingface.co/datasets/TechWolf/JobBERT-evaluation-dataset) | Job-title normalization and cross-title evaluation ideas. | Domain and language shift matter; this is a benchmark/reference, not proof a model works for Indian postings. |
| [ESCO classification and download/API](https://esco.ec.europa.eu/en/use-esco) | A multilingual occupation/skills vocabulary and linked concepts for normalization. | EU-oriented coverage. Check the specific dataset reuse terms and attribution before distribution; API software licensing does not automatically establish data licensing. |
| [O*NET database](https://www.onetcenter.org/database.html) and [license](https://www.onetcenter.org/license_agreements.html) | US occupation/task/skill reference data; possible enrichment with an attribution/change notice under CC BY 4.0. | US labor context is not an India-demand source. Do not present O*NET occupation ratings as observed local vacancies. |
| [India National Classification of Occupations 2015](https://labour.gov.in/sites/default/files/National%20Classification%20of%20Occupations_Vol%20II-B-%202015.pdf) | India-oriented occupation names and coding structure aligned to ISCO-08. | It is a classification, not current job posting or salary data. |
| [NCS portal](https://www.ncs.gov.in/) | Potential India public employment-service source and future partnership/connector discovery. | No public vacancy API is currently connected in this product. Do not scrape, claim NCS integration, or treat dated ministry statistics as a live feed. |
| [PLFS publications](https://mospi.gov.in/) | Official macro-level labor-force indicators for context and outcome measures. | Survey aggregates are not job-level requirements, skills, or real-time vacancy counts; they cannot validate this product's role/skill demand pulse by themselves. |
| [Nesta Open Jobs Observatory](https://www.nesta.org.uk/project/open-jobs-observatory/) and [skills library](https://www.nesta.org.uk/project/open-jobs/) | Methods for skill extraction, mapping and aggregated online-job-ad analysis. | UK scope and historic project data; its code or methods do not turn its observations into Indian market evidence. |
| [Job-ad skill extraction comparison, Information Processing & Management](https://www.sciencedirect.com/science/article/pii/S0306457322002862) | Evidence that method choice trades interpretability against explanatory power; a large UK job-ad comparison. | Different geography and period; methods need local evaluation before adoption. |
| [Deep Learning Job Market Analysis survey, NLP4HR 2024](https://aclanthology.org/2024.nlp4hr-1.1/) | Research overview of job-market datasets, methods and benchmark concerns. | Survey context, not a production data source or proof of prediction accuracy. |

## Analysis and prediction policy

The dashboard reports a descriptive snapshot and lineage. A 28-day comparison is withheld until at least eight dated refreshes span 28 days and the imported source-board set stays stable. It compares average active postings in two observed windows; it is not a forecast and can be biased by when and which boards are refreshed. Skill-level movement uses the same windows and remains taxonomy-dependent.

Forecast output is currently always `null`. A future forecast should be enabled only after enough regular history exists (initial gate: at least six monthly observations), the method is specified, rolling-origin out-of-sample evaluation beats a simple baseline, uncertainty intervals are calibrated, and drift/coverage are visible. Report error metrics and data exclusions beside any forecast. A visually polished line cannot substitute for validation.

Recommended next data work is a consented, labeled sample of representative postings across regions, occupation families and languages; annotation guidelines and double-review; title/skill normalization evaluation (precision, recall, F1, coverage and subgroup breakdown); and a time-based backtest. Keep source date, board, location, description/version, extraction version and taxonomy version for reproducibility. Any additional dataset should record provenance, license, collection date and geographic scope.
