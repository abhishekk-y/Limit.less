/*
  Limit.less SAS hackathon | aggregate source profile
  Requires 00_vfl_preflight.sas to have run in this same SAS session.
  Temporary long table stores only field names and missing flags, never values or IDs.
*/

%macro sb_profile(dataset_id=, table=);
  %if not %sysfunc(exist(&SB_LIB..&table)) %then %do;
    %put ERROR: [SignalBridge] Cannot profile missing table &SB_LIB..&table.;
    %return;
  %end;

  proc contents data=&SB_LIB..&table
    out=work._sb_profile_meta_&dataset_id(keep=name type varnum)
    noprint;
  run;

  proc sql noprint;
    select count(*) into :_sb_num_count trimmed from work._sb_profile_meta_&dataset_id where type=1;
    select count(*) into :_sb_char_count trimmed from work._sb_profile_meta_&dataset_id where type=2;
    select nliteral(name) into :_sb_num_vars separated by ' '
      from work._sb_profile_meta_&dataset_id where type=1 order by varnum;
    select nliteral(name) into :_sb_char_vars separated by ' '
      from work._sb_profile_meta_&dataset_id where type=2 order by varnum;
  quit;

  data work._sb_profile_long_&dataset_id;
    set &SB_LIB..&table;
    length dataset_id $40 field_name $128 missing_value 8;
    dataset_id="&dataset_id";
    %if &_sb_num_count > 0 %then %do;
      array _sb_num {*} &_sb_num_vars;
      do _sb_i=1 to dim(_sb_num);
        field_name=vname(_sb_num[_sb_i]);
        missing_value=missing(_sb_num[_sb_i]);
        output;
      end;
    %end;
    %if &_sb_char_count > 0 %then %do;
      array _sb_char {*} &_sb_char_vars;
      do _sb_i=1 to dim(_sb_char);
        field_name=vname(_sb_char[_sb_i]);
        missing_value=missing(_sb_char[_sb_i]);
        output;
      end;
    %end;
    keep dataset_id field_name missing_value;
  run;

  proc sql;
    create table work._sb_profile_result_&dataset_id as
    select dataset_id, field_name,
           count(*) as source_rows,
           sum(missing_value) as missing_rows,
           calculated missing_rows / calculated source_rows as missing_rate format=percent8.1
    from work._sb_profile_long_&dataset_id
    group by dataset_id, field_name;
  quit;
  proc append base=work.sb_field_profile data=work._sb_profile_result_&dataset_id force; run;
%mend;

data work.sb_field_profile;
  length dataset_id $40 field_name $128 source_rows missing_rows missing_rate 8;
  stop;
run;

%sb_profile(dataset_id=analytics_jobs, table=&SB_ANALYTICS_TABLE);
%sb_profile(dataset_id=datascience_jobs, table=&SB_DS_TABLE);
%sb_profile(dataset_id=jds_skill_traits, table=&SB_JDS_TABLE);
%sb_profile(dataset_id=sds_personality_traits, table=&SB_SDS_TABLE);

title 'Limit.less | Field coverage profile | aggregates only';
proc print data=work.sb_field_profile noobs label;
  var dataset_id field_name source_rows missing_rows missing_rate;
  label dataset_id='Separate source' field_name='Field' source_rows='Rows in source'
        missing_rows='Missing values' missing_rate='Missing rate';
run;
title;

/* This profile is diagnostic. No threshold has been approved, so quality remains NOT RUN. */
%put NOTE: [SignalBridge] Field profile is diagnostic only; no quality threshold or release gate has been passed.;
