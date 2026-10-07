/*
  Limit.less SAS hackathon | same-session run closeout
  This is an execution inventory, not an approval to export or publish results.
*/

%let SB_CLOSED_AT=%sysfunc(datetime());

data work.sb_closeout;
  length run_id $32 artifact $48 status $12 evidence_ref $120 interpretation $220;
  format checked_at datetime20.;
  run_id="&SB_RUN_ID"; checked_at=&SB_CLOSED_AT;

  artifact='source_presence'; evidence_ref='WORK.SB_SOURCE_PRESENCE';
  if exist(evidence_ref) then do; status='PRESENT'; interpretation='Source-table presence check recorded; this is not a quality approval.'; end;
  else do; status='NOT RUN'; interpretation='No source-presence result exists in this session.'; end; output;

  artifact='field_profile'; evidence_ref='WORK.SB_FIELD_PROFILE';
  if exist(evidence_ref) then do; status='PRESENT'; interpretation='Aggregate missingness profile exists; quality thresholds remain unapproved.'; end;
  else do; status='NOT RUN'; interpretation='Field profile has not been produced.'; end; output;

  artifact='market_skill_counts'; evidence_ref='WORK.SB_MARKET_SKILLS';
  if exist(evidence_ref) then do; status='PRESENT'; interpretation='Draft phrase counts exist; human extraction audit is still required.'; end;
  else do; status='NOT RUN'; interpretation='Market skill analysis has not been produced.'; end; output;

  artifact='market_skill_sensitivity'; evidence_ref='WORK.SB_MARKET_SKILL_SENSITIVITY';
  if exist(evidence_ref) then do; status='PRESENT'; interpretation='Raw-record and exact normalized-content rates are compared; neither identifies true duplicate vacancies.'; end;
  else do; status='NOT RUN'; interpretation='Exact-content sensitivity has not been produced.'; end; output;

  artifact='analytics_preparation_profile'; evidence_ref='WORK.SB_ANALYTICS_PREP_PROFILE';
  if exist(evidence_ref) then do; status='PRESENT'; interpretation='Aggregate coverage and missingness diagnostics exist; source rows remain unchanged.'; end;
  else do; status='NOT RUN'; interpretation='Deep preparation diagnostics have not been produced.'; end; output;

  artifact='candidate_skill_edges'; evidence_ref='WORK.SB_MARKET_SKILL_EDGES';
  if exist(evidence_ref) then do; status='PRESENT'; interpretation='Candidate co-occurrence exists; it is not a reviewed SkillGraph.'; end;
  else do; status='NOT RUN'; interpretation='No candidate co-occurrence graph exists.'; end; output;

  artifact='datascience_weight_summary'; evidence_ref='WORK.SB_DATASCIENCE_WEIGHT_SUMMARY';
  if exist(evidence_ref) then do; status='PRESENT'; interpretation='Row counts and supplied weights are summarized separately.'; end;
  else do; status='NOT RUN'; interpretation='Weighted-demand summary has not been produced.'; end; output;

  artifact='jds_group_summary'; evidence_ref='WORK.SB_JDS_GROUP_SUMMARY';
  if exist(evidence_ref) then do; status='PRESENT'; interpretation='JDS aggregate description exists; it is exploratory and not a personal model.'; end;
  else do; status='NOT RUN'; interpretation='JDS outcome/trait mapping must be confirmed before analysis.'; end; output;

  artifact='sds_group_summary'; evidence_ref='WORK.SB_SDS_GROUP_SUMMARY';
  if exist(evidence_ref) then do; status='PRESENT'; interpretation='Separate SDS aggregate description exists; excluded from individual decisions.'; end;
  else do; status='NOT RUN'; interpretation='SDS outcome/trait mapping must be confirmed before analysis.'; end; output;

  artifact='jds_exploratory_model'; evidence_ref='WORK.SB_JDS_MODEL_METRICS';
  if exist('WORK.SB_JDS_MODEL_METRICS') then do; status='PRESENT'; interpretation='JDS-only exploratory grouped model metrics exist in VFL; not a personal or hiring model.'; end;
  else do; status='NOT RUN'; interpretation='No verified grouped model run exists; do not claim training or performance.'; end; output;

  artifact='sds_individual_model'; evidence_ref=''; status='BLOCKED'; interpretation='SDS is aggregate governance research only; no individual model is permitted.'; output;

  artifact='datascience_title_summary'; evidence_ref='WORK.SB_DATASCIENCE_TITLE_SUMMARY';
  if exist(evidence_ref) then do; status='PRESENT'; interpretation='Normalized title row and weight counts exist; titles are not a validated taxonomy.'; end;
  else do; status='NOT RUN'; interpretation='DataScience Jobs title summary has not been produced.'; end; output;

  artifact='reviewed_extraction'; evidence_ref=''; status='NOT RUN'; interpretation='No manually labeled extraction benchmark is recorded.'; output;
  artifact='reviewed_crosswalk'; evidence_ref=''; status='NOT RUN'; interpretation='No reviewer-approved aggregate skill-family crosswalk is recorded.'; output;
  artifact='external_validation'; evidence_ref=''; status='NOT RUN'; interpretation='No independent external validation is recorded.'; output;
  artifact='organizer_transfer_approval'; evidence_ref=''; status='BLOCKED'; interpretation='Do not transfer challenge-derived results without written organizer approval.'; output;
  artifact='limitless_sync'; evidence_ref=''; status='NOT RUN'; interpretation='No SAS VFL to Limit.less connector is configured.'; output;
run;

title 'Limit.less | VFL run closeout | no export';
proc print data=work.sb_closeout noobs label;
  var artifact status evidence_ref checked_at interpretation;
  label artifact='Pipeline artifact' status='Availability' evidence_ref='In-VFL evidence reference'
    checked_at='Checked at' interpretation='Scope/limitation';
run;
title;

%put NOTE: [SignalBridge] Closeout is local to this VFL session. It does not authorize export, product sync, or claims beyond the recorded evidence.;
