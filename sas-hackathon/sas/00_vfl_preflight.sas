/*
  Limit.less SAS hackathon | VFL preflight
  Run this inside the organizer-approved SAS Viya for Learners session.
  No HTTP calls, exports, source-row prints, or cross-file joins are performed.
*/

options validvarname=any;

/* Defaults may be overridden before submission (for example, WORK in the synthetic smoke test). */
%if not %symexist(SB_LIB) %then %let SB_LIB=CASUSER;
%if not %symexist(SB_ANALYTICS_TABLE) %then %let SB_ANALYTICS_TABLE=ANALYTICS_JOBS;
%if not %symexist(SB_DS_TABLE) %then %let SB_DS_TABLE=DATASCIENCE_JOBS;
%if not %symexist(SB_JDS_TABLE) %then %let SB_JDS_TABLE=JDS_SKILL_TRAITS;
%if not %symexist(SB_SDS_TABLE) %then %let SB_SDS_TABLE=SDS_PERSONALITY_TRAITS;
%if not %symexist(SB_CODE_VERSION) %then %let SB_CODE_VERSION=0.1.0;
%if not %symexist(SB_RUN_ID) %then %let SB_RUN_ID=%sysfunc(compress(%sysfunc(uuidgen()),-));
%if not %symexist(SB_STARTED_AT) %then %let SB_STARTED_AT=%sysfunc(datetime());

%macro sb_inventory(dataset_id=, table=);
  %if %sysfunc(libref(&SB_LIB)) ne 0 %then %do;
    %put ERROR: [SignalBridge] Library &SB_LIB is not assigned. Assign the approved VFL library and rerun.;
  %end;
  %else %if %sysfunc(exist(&SB_LIB..&table)) %then %do;
    %put NOTE: [SignalBridge] Source table present: &dataset_id (&SB_LIB..&table).;
    proc contents data=&SB_LIB..&table
      out=work._sb_meta_&dataset_id(keep=name type length varnum label format)
      noprint;
    run;
  %end;
  %else %do;
    %put ERROR: [SignalBridge] Source table missing: &dataset_id (&SB_LIB..&table). No source data were read.;
  %end;
%mend;

%sb_inventory(dataset_id=analytics_jobs, table=&SB_ANALYTICS_TABLE);
%sb_inventory(dataset_id=datascience_jobs, table=&SB_DS_TABLE);
%sb_inventory(dataset_id=jds_skill_traits, table=&SB_JDS_TABLE);
%sb_inventory(dataset_id=sds_personality_traits, table=&SB_SDS_TABLE);

/* Only table existence is evaluated here. This is not a schema/data-quality PASS. */
data work.sb_source_presence;
  length run_id $32 dataset_id $40 table_name $128 status $12 blocking 8
         check_version $16 evidence_ref $180 message $240;
  format evaluated_at datetime20.;
  run_id="&SB_RUN_ID";
  evaluated_at=&SB_STARTED_AT;
  check_version="&SB_CODE_VERSION";

  dataset_id='analytics_jobs'; table_name=cats("&SB_LIB", '.', "&SB_ANALYTICS_TABLE");
  if exist(table_name) then do; status='PASS'; blocking=0; message='The named source table exists in the selected SAS library.'; end;
  else do; status='BLOCKED'; blocking=1; message='Source table is missing; import it inside the approved VFL environment.'; end;
  evidence_ref=cats('metadata:', table_name); output;

  dataset_id='datascience_jobs'; table_name=cats("&SB_LIB", '.', "&SB_DS_TABLE");
  if exist(table_name) then do; status='PASS'; blocking=0; message='The named source table exists in the selected SAS library.'; end;
  else do; status='BLOCKED'; blocking=1; message='Source table is missing; import it inside the approved VFL environment.'; end;
  evidence_ref=cats('metadata:', table_name); output;

  dataset_id='jds_skill_traits'; table_name=cats("&SB_LIB", '.', "&SB_JDS_TABLE");
  if exist(table_name) then do; status='PASS'; blocking=0; message='The named source table exists in the selected SAS library.'; end;
  else do; status='BLOCKED'; blocking=1; message='Source table is missing; import it inside the approved VFL environment.'; end;
  evidence_ref=cats('metadata:', table_name); output;

  dataset_id='sds_personality_traits'; table_name=cats("&SB_LIB", '.', "&SB_SDS_TABLE");
  if exist(table_name) then do; status='PASS'; blocking=0; message='The named source table exists in the selected SAS library.'; end;
  else do; status='BLOCKED'; blocking=1; message='Source table is missing; import it inside the approved VFL environment.'; end;
  evidence_ref=cats('metadata:', table_name); output;
run;

/* Explicitly unrun gates prevent absence of evidence from appearing successful. */
data work.sb_gate_status;
  set work.sb_source_presence;
  length gate_id $80;
  gate_id=cats('source_presence.', dataset_id);
  keep run_id gate_id dataset_id status blocking check_version evaluated_at evidence_ref message;
run;

data work._sb_unrun_gates;
  length run_id $32 gate_id $80 dataset_id $40 status $12 blocking 8
         check_version $16 evidence_ref $180 message $240;
  format evaluated_at datetime20.;
  run_id="&SB_RUN_ID"; check_version="&SB_CODE_VERSION";
  evaluated_at=&SB_STARTED_AT; status='NOT RUN'; blocking=0; evidence_ref='';
  gate_id='quality.field_profile'; dataset_id='all_sources'; message='Field-level profile has not been executed.'; output;
  gate_id='analysis.skill_audit'; dataset_id='analytics_jobs'; message='Human-reviewed extraction benchmark has not been executed.'; output;
  gate_id='analysis.skill_graph_review'; dataset_id='analytics_jobs'; message='Candidate co-occurrence graph has not been audited by a reviewer.'; output;
  gate_id='analysis.weight_sensitivity'; dataset_id='datascience_jobs'; message='Weighted-demand sensitivity analysis has not been executed.'; output;
  gate_id='analysis.jds_group_summary'; dataset_id='jds_skill_traits'; message='JDS grouped descriptive analysis has not been executed.'; output;
  gate_id='governance.sds_summary'; dataset_id='sds_personality_traits'; message='Separate SDS governance summary has not been executed.'; output;
  gate_id='release.aggregate_approval'; dataset_id='all_sources'; status='BLOCKED'; blocking=1; message='No organizer approval for transferring challenge-derived results is recorded.'; output;
  gate_id='release.limitless_sync'; dataset_id='all_sources'; status='NOT RUN'; blocking=0; message='No VFL-to-Limit.less integration is configured.'; output;
run;

proc append base=work.sb_gate_status data=work._sb_unrun_gates force; run;

title "Limit.less | VFL source preflight | &SB_RUN_ID";
proc print data=work.sb_gate_status noobs label;
  var gate_id dataset_id status blocking evaluated_at message;
  label gate_id='Gate' dataset_id='Independent source' status='Outcome'
        blocking='Blocking' evaluated_at='Evaluated at' message='Evidence note';
run;
title;

%put NOTE: [SignalBridge] Preflight ended. Run ID=&SB_RUN_ID. All tables and outputs remain in SAS WORK/VFL.;
