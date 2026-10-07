/*
  Limit.less SAS hackathon | separate trait research
  This script never joins JDS to SDS or to either market file.
  It creates descriptive aggregates only; there is no candidate/person scoring.
*/

/* Confirm these names in PROC CONTENTS. Leave ID fields blank until verified. */
%let SB_JDS_OUTCOME=salary_hike_high_or_low;
%let SB_JDS_TRAITS=; /* e.g. the five verified numeric skill fields, separated by spaces */
%let SB_JDS_ID=; /* optional file-local ID field; never join on it */

%let SB_SDS_OUTCOME=; /* exact VFL variable name for the supplied success label */
%let SB_SDS_TRAITS=; /* exact five verified numeric personality fields */
%let SB_SDS_ID=; /* optional file-local ID field; never join on it */

/* Edit only after reviewing the codebook and label frequencies in VFL. */
%let SB_HIGH_LABEL_REGEX=^(high|yes|success|positive|1)$;
%let SB_LOW_LABEL_REGEX=^(low|no|fail|negative|0)$;

%macro sb_id_profile(dataset_id=, table=, idvar=);
  %if %length(%superq(idvar)) %then %do;
    proc sql;
      create table work.sb_&dataset_id._id_profile as
      select count(*) as source_rows,
             sum(missing(&idvar)) as missing_id_rows,
             count(distinct &idvar) as distinct_nonmissing_ids,
             count(&idvar)-count(distinct &idvar) as repeated_id_excess
      from &SB_LIB..&table;
    quit;
    %put NOTE: [SignalBridge] &dataset_id ID counts are file-local diagnostics. No records are removed or linked.;
  %end;
  %else %put NOTE: [SignalBridge] &dataset_id ID check NOT RUN: no verified ID field is configured.;
%mend;

%macro sb_trait_summary(dataset_id=, table=, outcome=, traits=);
  %if not %sysfunc(exist(&SB_LIB..&table)) %then %do;
    %put ERROR: [SignalBridge] &dataset_id source table is unavailable.; %return;
  %end;
  %if %length(%superq(outcome))=0 or %length(%superq(traits))=0 %then %do;
    %put WARNING: [SignalBridge] &dataset_id grouped analysis NOT RUN. Confirm the outcome and five trait columns in PROC CONTENTS first.;
    %return;
  %end;

  data work._sb_&dataset_id._labels;
    set &SB_LIB..&table(keep=&outcome &traits);
    length _sb_supplied_label $128 _sb_group $12;
    _sb_supplied_label=strip(vvaluex("&outcome"));
    if prxmatch("/&SB_HIGH_LABEL_REGEX/i",strip(_sb_supplied_label)) then _sb_group='HIGH';
    else if prxmatch("/&SB_LOW_LABEL_REGEX/i",strip(_sb_supplied_label)) then _sb_group='LOW';
    else _sb_group='UNMAPPED';
    keep _sb_supplied_label _sb_group &traits;
  run;

  proc sql;
    create table work.sb_&dataset_id._label_counts as
    select _sb_group, count(*) as aggregate_rows
    from work._sb_&dataset_id._labels
    group by _sb_group;
  quit;

  proc means data=work._sb_&dataset_id._labels n mean std;
    class _sb_group;
    var &traits;
    output out=work.sb_&dataset_id._group_summary n= mean= std= / autoname;
  run;

  title "Limit.less | &dataset_id | descriptive trait summaries only";
  proc print data=work.sb_&dataset_id._label_counts noobs label;
    label _sb_group='Mapped supplied label' aggregate_rows='Aggregate row count';
  run;
  proc print data=work.sb_&dataset_id._group_summary noobs; run;
  title;
  %put NOTE: [SignalBridge] &dataset_id summaries are exploratory and are not causal, predictive, or person-level results.;
%mend;

%sb_id_profile(dataset_id=jds, table=&SB_JDS_TABLE, idvar=&SB_JDS_ID);
%sb_id_profile(dataset_id=sds, table=&SB_SDS_TABLE, idvar=&SB_SDS_ID);
%sb_trait_summary(dataset_id=jds, table=&SB_JDS_TABLE, outcome=&SB_JDS_OUTCOME, traits=&SB_JDS_TRAITS);
%sb_trait_summary(dataset_id=sds, table=&SB_SDS_TABLE, outcome=&SB_SDS_OUTCOME, traits=&SB_SDS_TRAITS);

%put NOTE: [SignalBridge] SDS is isolated governance/research only. Never route SDS outputs to learner or employment decisions.;
