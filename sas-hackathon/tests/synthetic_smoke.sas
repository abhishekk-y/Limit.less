/*
  SYNTHETIC ONLY — tiny invented rows to test the package mechanics.
  This is not challenge data. Submit inside VFL, then submit the numbered programs.
  Set SB_LIB=WORK before 00_vfl_preflight.sas. It creates only WORK tables.
*/

%let SB_LIB=WORK;
%let SB_ANALYTICS_TABLE=ANALYTICS_JOBS;
%let SB_DS_TABLE=DATASCIENCE_JOBS;
%let SB_JDS_TABLE=JDS_SKILL_TRAITS;
%let SB_SDS_TABLE=SDS_PERSONALITY_TRAITS;

data work.ANALYTICS_JOBS;
  infile datalines dsd dlm='|' truncover;
  length job_desig $40 job_description $240 key_skills $120;
  input job_desig :$40. job_description :$240. key_skills :$120.;
  datalines;
Data Analyst|Build dashboards with SQL and Python|SQL, Python, Tableau
Data Scientist|Use machine learning and statistics|Python, SAS, Machine learning
;
run;

data work.DATASCIENCE_JOBS;
  infile datalines dsd dlm='|' truncover;
  length job_title $40 reference_no $20;
  input job_title :$40. num_of_jobs reference_no :$20.;
  datalines;
Data Analyst|12|REF-1
Data Scientist|22|REF-1
;
run;

data work.JDS_SKILL_TRAITS;
  infile datalines dsd dlm='|' truncover;
  length case_id $12 salary_hike_high_or_low $12;
  input case_id :$12. salary_hike_high_or_low :$12. coding_skill analysis_skill
        dashboard_storytelling communication_skill problem_solving;
  datalines;
J-01|High|4|4|5|3|4
J-02|Low|2|3|2|3|2
J-03|High|4|3|4|4|3
;
run;

data work.SDS_PERSONALITY_TRAITS;
  infile datalines dsd dlm='|' truncover;
  length case_id $12 success_label $12;
  input case_id :$12. success_label :$12. openness conscientiousness extraversion agreeableness emotional_stability;
  datalines;
S-01|High|0.8|0.9|0.6|0.7|0.7
S-02|Low|0.5|0.4|0.5|0.6|0.4
S-03|High|0.7|0.8|0.7|0.6|0.8
;
run;

/* For a synthetic-only pass, also edit the mapping block in 30_trait_research.sas:
   SB_JDS_TRAITS=coding_skill analysis_skill dashboard_storytelling communication_skill problem_solving
   SB_JDS_ID=case_id; SB_SDS_OUTCOME=success_label;
   SB_SDS_TRAITS=openness conscientiousness extraversion agreeableness emotional_stability
   SB_SDS_ID=case_id.
*/
