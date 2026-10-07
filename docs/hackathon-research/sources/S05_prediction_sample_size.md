# S05 — Sample size for prediction-model development

- Authors: Riley et al., BMJ 2020;368:m441.
- URL: https://www.bmj.com/content/368/bmj.m441
- Type/assessment: peer-reviewed statistical methodology; high credibility; method remains relevant, context is clinical prediction.
- Short evidence excerpt: “We do not recommend data splitting”; use all available data with resampling for internal validation.
- Relevance: model complexity, outcome prevalence, and anticipated performance determine sample needs; simplistic event-per-variable rules are inadequate. Machine learning models can need substantially more data due to many effective parameters.
- Use in this project: do not build a deep NLP or individual-outcome model on 139/161 records and report a high accuracy. Resampling is still not external validation and cannot create information missing from the sample.
