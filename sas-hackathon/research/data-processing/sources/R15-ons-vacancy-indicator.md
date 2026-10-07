# R15 — UK ONS method for an online vacancy indicator

- **Source:** UK Office for National Statistics, *Using Adzuna data to derive an indicator of weekly vacancies: experimental statistics*.
- **Type:** Official statistical methodology.
- **URL:** https://www.ons.gov.uk/peoplepopulationandcommunity/healthandsocialcare/conditionsanddiseases/methodologies/usingadzunatdatatoderiveanindicatorofweeklyvacanciesexperimentalstatistics
- **Credibility / recency / bias:** 5 / 3 / 2. Government statistical production method; particular to UK/Adzuna.
- **Finding used:** An advertisement and a vacancy are not interchangeable units; deduplication, stale listings, timing, missing geography and source definitions matter.
- **Design implication:** Keep row/posting record counts distinct from `num_of_jobs`; present exact-duplicate handling as sensitivity, not as a truth label; never call counts “openings” without unit validation.
- **Limit:** UK method cannot establish the semantics of the challenge file’s weight or IDs.
