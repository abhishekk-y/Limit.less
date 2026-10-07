/*
  Limit.less | conservative preparation and duplicate diagnostics
  Run after 00_vfl_preflight.sas and 10_quality_profile.sas, inside the
  organizer-approved VFL session only. Source tables are read-only. All
  row-level prepared fields and fingerprints remain in WORK.

  This program does not deduplicate or delete observations. It reports the
  effect exact normalized-text duplicates could have on later counts.
*/

%if not %symexist(SB_LIB) %then %let SB_LIB=CASUSER;
%if not %symexist(SB_ANALYTICS_TABLE) %then %let SB_ANALYTICS_TABLE=ANALYTICS_JOBS;
%if not %symexist(SB_ANALYTICS_TITLE) %then %let SB_ANALYTICS_TITLE=job_desig;
%if not %symexist(SB_SKILLS_VAR) %then %let SB_SKILLS_VAR=key_skills;
%if not %symexist(SB_DESCRIPTION_VAR) %then %let SB_DESCRIPTION_VAR=job_description;

%macro sb_deep_data_prep;
  %if not %sysfunc(exist(&SB_LIB..&SB_ANALYTICS_TABLE)) %then %do;
    %put ERROR: [Limit.less] Analytics Jobs source missing. Preparation is BLOCKED.;
    %return;
  %end;

  proc contents data=&SB_LIB..&SB_ANALYTICS_TABLE
    out=work._sb_prep_meta(keep=name) noprint;
  run;
  proc sql noprint;
    select sum(upcase(name)=upcase("&SB_ANALYTICS_TITLE")),
           sum(upcase(name)=upcase("&SB_SKILLS_VAR")),
           sum(upcase(name)=upcase("&SB_DESCRIPTION_VAR"))
      into :_sb_prep_title_ok, :_sb_prep_skills_ok, :_sb_prep_desc_ok
      from work._sb_prep_meta;
  quit;
  %if %sysevalf(&_sb_prep_title_ok=0 or &_sb_prep_skills_ok=0 or &_sb_prep_desc_ok=0) %then %do;
    %put ERROR: [Limit.less] Required Analytics Jobs fields do not match. Confirm metadata; no prepared table created.;
    %return;
  %end;

  /* Stable only for this unchanged imported table and run; never a person/job key. */
  data work.sb_analytics_prepared;
    set &SB_LIB..&SB_ANALYTICS_TABLE;
    length normalized_title $300 normalized_skill_text $32767
           normalized_description $32767 content_fingerprint $32
           missing_pattern $8;
    _sb_row_number=_n_;
    normalized_title=lowcase(compbl(strip(vvaluex("&SB_ANALYTICS_TITLE"))));
    normalized_skill_text=lowcase(compbl(strip(vvaluex("&SB_SKILLS_VAR"))));
    normalized_description=strip(vvaluex("&SB_DESCRIPTION_VAR"));
    /* Strip markup and normalize whitespace/case for conservative matching. */
    normalized_description=prxchange('s/<[^>]*>/ /', -1, normalized_description);
    normalized_description=lowcase(compbl(strip(normalized_description)));
    title_missing=missing(normalized_title);
    skill_text_missing=missing(normalized_skill_text);
    description_missing=missing(normalized_description);
    missing_pattern=cats('T',title_missing,'K',skill_text_missing,'D',description_missing);
    if not (title_missing and skill_text_missing and description_missing) then
      content_fingerprint=put(md5(catx('1F'x, normalized_title,
        normalized_skill_text, normalized_description)), $hex32.);
    keep _sb_row_number normalized_title normalized_skill_text
         normalized_description content_fingerprint title_missing
         skill_text_missing description_missing missing_pattern;
  run;

  proc sql;
    create table work.sb_analytics_prep_profile as
    select count(*) as source_rows,
           sum(title_missing) as rows_missing_title,
           sum(skill_text_missing) as rows_missing_skill_text,
           sum(description_missing) as rows_missing_description,
           sum(not skill_text_missing and not description_missing) as rows_with_both_text_fields,
           count(distinct missing_pattern) as observed_missingness_patterns
    from work.sb_analytics_prepared;

    create table work._sb_exact_duplicate_groups as
    select content_fingerprint, count(*) as group_rows
    from work.sb_analytics_prepared
    where not missing(content_fingerprint)
    group by content_fingerprint
    having count(*) > 1;

    create table work.sb_analytics_duplicate_sensitivity as
    select (select count(*) from work.sb_analytics_prepared) as source_rows,
           (select count(*) from work.sb_analytics_prepared
             where not missing(content_fingerprint)) as rows_with_content,
           (select count(distinct content_fingerprint) from work.sb_analytics_prepared
             where not missing(content_fingerprint)) as distinct_normalized_records,
           (select count(*) from work._sb_exact_duplicate_groups) as exact_duplicate_groups,
           (select coalesce(sum(group_rows-1),0) from work._sb_exact_duplicate_groups) as excess_exact_duplicate_rows;

    create table work.sb_analytics_missingness_patterns as
    select missing_pattern, count(*) as row_count
    from work.sb_analytics_prepared
    group by missing_pattern;
  quit;

  title 'Limit.less | Analytics Jobs preparation diagnostics | aggregates only';
  proc print data=work.sb_analytics_prep_profile noobs; run;
  proc print data=work.sb_analytics_duplicate_sensitivity noobs; run;
  proc print data=work.sb_analytics_missingness_patterns noobs; run;
  title;
  %put NOTE: [Limit.less] Prepared rows and fingerprints remain in WORK. No source row was removed or exported.;
%mend;

%sb_deep_data_prep;
