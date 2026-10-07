# R16 — SkillSpan extraction benchmark

- **Source:** Zhang et al. (2022), *SkillSpan: Hard and Soft Skill Extraction from English Job Postings*, NAACL.
- **Type:** Peer-reviewed NLP conference paper and human-annotated benchmark.
- **URL:** https://aclanthology.org/2022.naacl-main.366/
- **Credibility / recency / bias:** 4 / 3 / 2. Peer-reviewed benchmark; English postings and its own annotation frame.
- **Finding used:** Skill mention extraction benefits from explicit annotation definitions and a labeled evaluation set; “skill” boundaries and hard/soft labels need operational definitions.
- **Design implication:** Version the skill phrase dictionary and ask reviewers to label an overlap sample; report precision, recall, coverage, and ambiguous/unmapped phrases before saying the parser is validated.
- **Limit:** Benchmark performance cannot be claimed for the challenge data without local evaluation.
