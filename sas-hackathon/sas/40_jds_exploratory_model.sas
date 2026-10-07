/*
  Limit.less | JDS-only exploratory model experiment
  RUN ONLY inside the organizer-approved SAS VFL workspace.

  This is not a hiring, salary, job-fit, or individual recommendation model.
  It tests whether the five supplied JDS skill dimensions discriminate the
  dataset's supplied high/low salary-hike label in this small sample.
  It never reads SDS or either job-posting dataset and never exports results.

  Required: run 00_vfl_preflight.sas first. Confirm exact names and semantics
  in PROC CONTENTS/codebook, then fill the mapping values below. The JDS ID
  must be confirmed as a repeated-person identifier before group splitting.
*/

%let SB_JDS_MODEL_OUTCOME=;
%let SB_JDS_MODEL_ID=;
%let SB_JDS_MODEL_TRAIT1=;
%let SB_JDS_MODEL_TRAIT2=;
%let SB_JDS_MODEL_TRAIT3=;
%let SB_JDS_MODEL_TRAIT4=;
%let SB_JDS_MODEL_TRAIT5=;
%let SB_JDS_MODEL_FOLDS=5;
%let SB_JDS_MODEL_HIGH_REGEX=^(high|yes|success|positive|1)$;
%let SB_JDS_MODEL_LOW_REGEX=^(low|no|fail|negative|0)$;

%macro sb_jds_model_stop(message);
  %put ERROR: [Limit.less JDS model] &message;
  %let SB_JDS_MODEL_STATUS=NOT RUN;
%mend;

%let SB_JDS_MODEL_STATUS=NOT RUN;

%macro sb_jds_model_run;
  %if %length(%superq(SB_JDS_MODEL_OUTCOME))=0 or
      %length(%superq(SB_JDS_MODEL_ID))=0 or
      %length(%superq(SB_JDS_MODEL_TRAIT1))=0 or
      %length(%superq(SB_JDS_MODEL_TRAIT2))=0 or
      %length(%superq(SB_JDS_MODEL_TRAIT3))=0 or
      %length(%superq(SB_JDS_MODEL_TRAIT4))=0 or
      %length(%superq(SB_JDS_MODEL_TRAIT5))=0 %then %do;
    %sb_jds_model_stop(Required label, verified ID, and five verified trait mappings are blank.);
    %return;
  %end;

  %if not %sysfunc(exist(&SB_LIB..&SB_JDS_TABLE)) %then %do;
    %sb_jds_model_stop(JDS source table is missing.);
    %return;
  %end;

  /* Keep only mapped labels and complete, numeric feature rows. Hashing the
     verified ID assigns every repeated ID to one deterministic fold. */
  data work._sb_jds_model_input;
    set &SB_LIB..&SB_JDS_TABLE;
    length _sb_id $256 _sb_label $128;
    _sb_id=strip(vvaluex("&SB_JDS_MODEL_ID"));
    _sb_label=strip(vvaluex("&SB_JDS_MODEL_OUTCOME"));
    if missing(_sb_id) then delete;
    if prxmatch("/&SB_JDS_MODEL_HIGH_REGEX/i",_sb_label) then _sb_y=1;
    else if prxmatch("/&SB_JDS_MODEL_LOW_REGEX/i",_sb_label) then _sb_y=0;
    else delete;
    _x1=input(strip(vvaluex("&SB_JDS_MODEL_TRAIT1")),best32.);
    _x2=input(strip(vvaluex("&SB_JDS_MODEL_TRAIT2")),best32.);
    _x3=input(strip(vvaluex("&SB_JDS_MODEL_TRAIT3")),best32.);
    _x4=input(strip(vvaluex("&SB_JDS_MODEL_TRAIT4")),best32.);
    _x5=input(strip(vvaluex("&SB_JDS_MODEL_TRAIT5")),best32.);
    _sb_complete=(nmiss(of _x1-_x5)=0);
    _sb_hash=md5(_sb_id);
    _sb_fold=mod(input(substr(put(_sb_hash,$hex32.),1,8),hex8.),&SB_JDS_MODEL_FOLDS)+1;
    keep _sb_y _x1-_x5 _sb_id _sb_fold _sb_complete;
  run;

  proc sql;
    create table work._sb_jds_model_coverage as
    select count(*) as mapped_rows,
           sum(_sb_complete) as complete_rows,
           count(distinct _sb_id) as distinct_ids,
           sum(_sb_y=1) as positive_rows,
           sum(_sb_y=0) as negative_rows
    from work._sb_jds_model_input;
  quit;

  /* Rebuild fold diagnostics explicitly; training counts exclude each held-out fold. */
  proc sql;
    create table work._sb_jds_fold_check as
    select f._sb_fold,
           sum(case when a._sb_fold=f._sb_fold and a._sb_complete=1 and a._sb_y=1 then 1 else 0 end) as test_positive,
           sum(case when a._sb_fold=f._sb_fold and a._sb_complete=1 and a._sb_y=0 then 1 else 0 end) as test_negative,
           sum(case when a._sb_fold ne f._sb_fold and a._sb_complete=1 and a._sb_y=1 then 1 else 0 end) as train_positive,
           sum(case when a._sb_fold ne f._sb_fold and a._sb_complete=1 and a._sb_y=0 then 1 else 0 end) as train_negative
    from (select distinct _sb_fold from work._sb_jds_model_input) as f,
         work._sb_jds_model_input as a
    group by f._sb_fold;
  quit;

  proc sql noprint;
    select count(*) into :_sb_bad_folds trimmed
    from work._sb_jds_fold_check
    where test_positive=0 or test_negative=0 or train_positive=0 or train_negative=0;
    select count(*) into :_sb_n_complete trimmed
    from work._sb_jds_model_input where _sb_complete=1;
  quit;

  %if &_sb_n_complete < 20 %then %do;
    %sb_jds_model_stop(Fewer than 20 complete mapped rows; no model was fit.);
    %return;
  %end;
  %if &_sb_bad_folds > 0 %then %do;
    %sb_jds_model_stop(At least one grouped fold lacks both classes in train or test; revise the predeclared fold design before fitting.);
    %return;
  %end;

  /* Grouped out-of-fold evaluation. No row from a held-out ID enters training. */
  %do _sb_f=1 %to &SB_JDS_MODEL_FOLDS;
    data work._sb_train work._sb_test;
      set work._sb_jds_model_input(where=(_sb_complete=1));
      if _sb_fold=&_sb_f then output work._sb_test;
      else output work._sb_train;
    run;

    proc sql noprint;
      select mean(_sb_y) into :_sb_prev trimmed from work._sb_train;
    quit;

    ods exclude all;
    proc logistic data=work._sb_train descending;
      model _sb_y = _x1 _x2 _x3 _x4 _x5;
      score data=work._sb_test out=work._sb_fold_score;
    run;
    ods exclude none;

    data work._sb_fold_score;
      set work._sb_fold_score;
      _sb_fold=&_sb_f;
      _sb_prob=P_1;
      _sb_baseline=&_sb_prev;
      _sb_pred=(_sb_prob ge 0.5);
      _sb_base_pred=(_sb_baseline ge 0.5);
      _sb_brier=(_sb_y-_sb_prob)**2;
      _sb_base_brier=(_sb_y-_sb_baseline)**2;
    run;

    %if &_sb_f=1 %then %do;
      data work.sb_jds_oof_predictions; set work._sb_fold_score; run;
    %end;
    %else %do;
      proc append base=work.sb_jds_oof_predictions data=work._sb_fold_score force; run;
    %end;
  %end;

  /* AUC is computed from pooled out-of-fold scores with average ranks for ties. */
  proc rank data=work.sb_jds_oof_predictions out=work._sb_jds_ranked ties=mean;
    var _sb_prob;
    ranks _sb_rank;
  run;

  proc sql;
    create table work.sb_jds_model_metrics as
    select count(*) as evaluated_rows,
           sum(_sb_y=1) as positive_rows,
           sum(_sb_y=0) as negative_rows,
           (sum(case when _sb_y=1 then _sb_rank+1 else 0 end)
              - sum(_sb_y=1)*(sum(_sb_y=1)+1)/2)
              /(sum(_sb_y=1)*sum(_sb_y=0)) as auc,
           mean(_sb_brier) as logistic_brier,
           mean(_sb_base_brier) as prevalence_baseline_brier,
           mean(_sb_pred=_sb_y) as logistic_accuracy_at_0_5,
           mean(_sb_base_pred=_sb_y) as prevalence_baseline_accuracy
    from work._sb_jds_ranked;
  quit;

  /* Final descriptive fit, retained only in this VFL WORK session. It is not
     production-ready and must not be exported to Limit.less. */
  ods output ParameterEstimates=work.sb_jds_model_coefficients;
  proc logistic data=work._sb_jds_model_input(where=(_sb_complete=1)) descending;
    model _sb_y = _x1 _x2 _x3 _x4 _x5;
    output out=work._sb_jds_fitted_sample pred=_sb_fitted_probability;
  run;
  ods output close;

  %let SB_JDS_MODEL_STATUS=TRAINED_EXPLORATORY;
  title 'Limit.less | JDS-only exploratory model | grouped out-of-fold evaluation';
  proc print data=work._sb_jds_model_coverage noobs; run;
  proc print data=work.sb_jds_model_metrics noobs; run;
  proc print data=work.sb_jds_model_coefficients noobs; run;
  title;
  %put NOTE: [Limit.less JDS model] Exploratory JDS label model completed in VFL. Not validated for individual, hiring, salary, or production use.;
%mend;

%sb_jds_model_run;
