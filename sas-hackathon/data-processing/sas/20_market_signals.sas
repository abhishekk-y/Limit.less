/*
  Limit.less | conservative market signals (run only inside approved VFL)
  Analytics Jobs: field-specific skill mentions; key_skills and job_description
  are deliberately never concatenated. DataScience Jobs: row counts and
  num_of_jobs weights are reported as different quantities.
  No row identifiers or raw source text are written to output tables.
*/

%if not %symexist(SB_LIB) %then %let SB_LIB=CASUSER;
%if not %symexist(SB_ANALYTICS_TABLE) %then %let SB_ANALYTICS_TABLE=ANALYTICS_JOBS;
%if not %symexist(SB_DS_TABLE) %then %let SB_DS_TABLE=DATASCIENCE_JOBS;
%if not %symexist(SB_ANALYTICS_TITLE) %then %let SB_ANALYTICS_TITLE=job_desig;
%if not %symexist(SB_SKILLS_VAR) %then %let SB_SKILLS_VAR=key_skills;
%if not %symexist(SB_DESCRIPTION_VAR) %then %let SB_DESCRIPTION_VAR=job_description;
%if not %symexist(SB_DS_TITLE) %then %let SB_DS_TITLE=job_title;
%if not %symexist(SB_DS_WEIGHT) %then %let SB_DS_WEIGHT=num_of_jobs;
%if not %symexist(SB_DS_REF) %then %let SB_DS_REF=reference_no;
%if not %symexist(SB_MIN_SKILL_SUPPORT) %then %let SB_MIN_SKILL_SUPPORT=10;

%macro sb_market_signals;
  %if %sysfunc(exist(&SB_LIB..&SB_ANALYTICS_TABLE))=0 %then %do;
    %put ERROR: [SignalBridge] Analytics Jobs source is missing. No market signals were created.;
    %return;
  %end;
  %if %sysfunc(exist(&SB_LIB..&SB_DS_TABLE))=0 %then %do;
    %put ERROR: [SignalBridge] DataScience Jobs source is missing. No weighted signals were created.;
    %return;
  %end;

  /* Confirm configurable source fields before referencing them. */
  proc contents data=&SB_LIB..&SB_ANALYTICS_TABLE
    out=work._sb_market_meta(keep=name) noprint; run;
  proc sql noprint;
    select sum(upcase(name)=upcase("&SB_ANALYTICS_TITLE")),
           sum(upcase(name)=upcase("&SB_SKILLS_VAR")),
           sum(upcase(name)=upcase("&SB_DESCRIPTION_VAR"))
      into :_sb_title_ok, :_sb_skills_ok, :_sb_desc_ok
      from work._sb_market_meta;
  quit;
  %if %sysevalf(&_sb_title_ok=0 or &_sb_skills_ok=0 or &_sb_desc_ok=0) %then %do;
    %put ERROR: [SignalBridge] Required Analytics Jobs fields were not found. Check 00_vfl_preflight metadata and configure macro names.;
    %return;
  %end;

  /* Preparation is a required upstream stage; never fall back to raw text. */
  %if not %sysfunc(exist(work.sb_analytics_prepared)) %then %do;
    %put ERROR: [SignalBridge] WORK.SB_ANALYTICS_PREPARED is missing. Run 15_deep_data_prep.sas before market analysis.;
    %return;
  %end;

  /* Count roles with simple normalized title labels; not a role taxonomy. */
  data work._sb_role_rows;
    set work.sb_analytics_prepared(keep=normalized_title);
    if not missing(normalized_title);
    keep normalized_title;
  run;
  proc sql;
    create table work.sb_market_role_counts as
    select normalized_title, count(*) as posting_row_count
    from work._sb_role_rows group by normalized_title;
  quit;

  /* Canonical phrase scan. These rules are candidate extraction, not an NLP model. */
  data work._sb_skill_hits(keep=text_field skill content_fingerprint)
       work._sb_skill_pairs(keep=text_field skill_a skill_b content_fingerprint);
    set work.sb_analytics_prepared(keep=normalized_skill_text normalized_description content_fingerprint);
    length text_field $32 skill $48 skill_a skill_b $48 source_text $32767;
    array labels[33] $48 _temporary_ (
      'Python' 'R' 'SQL' 'SAS' 'Excel' 'Statistics' 'Probability'
      'Machine learning' 'Deep learning' 'Artificial intelligence'
      'Natural language processing' 'Computer vision' 'Data visualization'
      'Tableau' 'Power BI' 'Data cleaning' 'ETL' 'Data engineering'
      'Data mining' 'Big data' 'Apache Spark' 'Hadoop' 'Cloud computing'
      'AWS' 'Azure' 'Google Cloud' 'Database design' 'Communication'
      'Problem solving' 'Project management' 'Business analysis'
      'Data storytelling' 'Research'
    );
    array patterns[33] $100 _temporary_ (
      '/(^|[^a-z0-9])python([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])r([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])sql([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])sas([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])excel([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])statistics?([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])probability([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])machine[ -]learning([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])deep[ -]learning([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])artificial intelligence([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])(natural language processing|nlp)([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])(computer vision|opencv)([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])data visualization([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])tableau([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])(power[ -]?bi)([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])data cleaning([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])etl([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])data engineering([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])data mining([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])big data([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])apache spark([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])hadoop([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])cloud computing([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])aws([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])azure([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])google cloud([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])database design([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])communication([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])problem solving([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])project management([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])business analysis([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])data storytelling([^a-z0-9]|$)/i'
      '/(^|[^a-z0-9])research([^a-z0-9]|$)/i'
    );
    array regex_ids[33] _temporary_;
    array flags[33] _temporary_;
    if _n_=1 then do _i=1 to dim(regex_ids); regex_ids[_i]=prxparse(patterns[_i]); end;
    do _field=1 to 2;
      if _field=1 then do; text_field='key_skills'; source_text=normalized_skill_text; end;
      else do; text_field='job_description'; source_text=normalized_description; end;
      do _i=1 to dim(flags); flags[_i]=0; end;
      if not missing(source_text) then do _i=1 to dim(labels);
        flags[_i]=(prxmatch(regex_ids[_i], source_text)>0);
      end;
      do _i=1 to dim(flags);
        if flags[_i] then do; skill=labels[_i]; output work._sb_skill_hits; end;
      end;
      do _i=1 to dim(flags)-1;
        if flags[_i] then do _j=_i+1 to dim(flags);
          if flags[_j] then do;
            skill_a=labels[_i]; skill_b=labels[_j]; output work._sb_skill_pairs;
          end;
        end;
      end;
    end;
  run;

  /* Separate denominators: rows with content in each source field. */
  proc sql;
    create table work.sb_market_field_denominators as
    select 'key_skills' as text_field length=32,
           count(*) as source_row_count,
           sum(not missing(normalized_skill_text)) as rows_with_text
    from work.sb_analytics_prepared
    union all
    select 'job_description' as text_field length=32,
           count(*) as source_row_count,
           sum(not missing(normalized_description)) as rows_with_text
    from work.sb_analytics_prepared;
  quit;

  proc sql;
    create table work._sb_skill_counts as
    select text_field, skill, count(*) as posting_rows_with_mention
    from work._sb_skill_hits group by text_field, skill;

    /* Exact normalized-content deduplication is a sensitivity view only. */
    create table work._sb_distinct_skill_hits as
    select distinct text_field, content_fingerprint, skill
    from work._sb_skill_hits
    where not missing(content_fingerprint);
    create table work._sb_unique_skill_counts as
    select text_field, skill, count(*) as unique_content_rows_with_mention
    from work._sb_distinct_skill_hits group by text_field, skill;
    create table work._sb_unique_text_denominators as
    select 'key_skills' as text_field length=32,
           count(distinct content_fingerprint) as unique_content_rows_with_text
    from work.sb_analytics_prepared where not missing(normalized_skill_text)
    union all
    select 'job_description' as text_field length=32,
           count(distinct content_fingerprint) as unique_content_rows_with_text
    from work.sb_analytics_prepared where not missing(normalized_description);

    create table work.sb_market_skills as
    select c.text_field, c.skill, c.posting_rows_with_mention,
           d.source_row_count, d.rows_with_text,
           c.posting_rows_with_mention / d.rows_with_text as share_of_rows_with_text format=percent8.2,
           &SB_MIN_SKILL_SUPPORT as minimum_support,
           case when c.posting_rows_with_mention >= &SB_MIN_SKILL_SUPPORT
             then 'CANDIDATE_UNREVIEWED' else 'LOW_SUPPORT' end as review_status length=24
    from work._sb_skill_counts c inner join work.sb_market_field_denominators d
      on c.text_field=d.text_field;
    create table work.sb_market_skill_sensitivity as
    select b.text_field, b.skill,
           b.posting_rows_with_mention as raw_record_mentions,
           u.unique_content_rows_with_mention as exact_unique_content_mentions,
           d.rows_with_text as raw_eligible_rows,
           q.unique_content_rows_with_text as exact_unique_eligible_rows,
           b.posting_rows_with_mention/d.rows_with_text as raw_mention_rate format=percent8.2,
           u.unique_content_rows_with_mention/q.unique_content_rows_with_text as exact_unique_mention_rate format=percent8.2,
           (u.unique_content_rows_with_mention/q.unique_content_rows_with_text)
              -(b.posting_rows_with_mention/d.rows_with_text) as rate_change format=percent8.2
    from work._sb_skill_counts b
    inner join work._sb_unique_skill_counts u on b.text_field=u.text_field and b.skill=u.skill
    inner join work.sb_market_field_denominators d on b.text_field=d.text_field
    inner join work._sb_unique_text_denominators q on b.text_field=q.text_field;
    create table work._sb_pair_counts as
    select text_field, skill_a, skill_b, count(*) as posting_rows_with_pair
    from work._sb_skill_pairs group by text_field, skill_a, skill_b;
    create table work.sb_market_skill_edges as
    select p.text_field, p.skill_a, p.skill_b, p.posting_rows_with_pair,
           a.posting_rows_with_mention as skill_a_rows,
           b.posting_rows_with_mention as skill_b_rows,
           p.posting_rows_with_pair /
             (a.posting_rows_with_mention+b.posting_rows_with_mention-p.posting_rows_with_pair)
             as jaccard format=8.4,
           &SB_MIN_SKILL_SUPPORT as minimum_support,
           case when p.posting_rows_with_pair >= &SB_MIN_SKILL_SUPPORT
             then 'CANDIDATE_UNREVIEWED' else 'LOW_SUPPORT' end as review_status length=24
    from work._sb_pair_counts p
    inner join work._sb_skill_counts a on p.text_field=a.text_field and p.skill_a=a.skill
    inner join work._sb_skill_counts b on p.text_field=b.text_field and p.skill_b=b.skill;
  quit;

  /* DataScience Jobs: row volume is not weighted demand. */
  proc contents data=&SB_LIB..&SB_DS_TABLE out=work._sb_ds_meta(keep=name) noprint; run;
  proc sql noprint;
    select sum(upcase(name)=upcase("&SB_DS_TITLE")),
           sum(upcase(name)=upcase("&SB_DS_WEIGHT")),
           sum(upcase(name)=upcase("&SB_DS_REF"))
      into :_sb_ds_title_ok, :_sb_ds_weight_ok, :_sb_ds_ref_ok
      from work._sb_ds_meta;
  quit;
  %if %sysevalf(&_sb_ds_title_ok=0 or &_sb_ds_weight_ok=0) %then %do;
    %put ERROR: [SignalBridge] DataScience Jobs title/weight fields not found. Market extraction completed; weighted summary skipped.;
    %return;
  %end;

  data work._sb_ds_weights;
    set &SB_LIB..&SB_DS_TABLE(keep=&SB_DS_TITLE &SB_DS_WEIGHT
      %if %sysevalf(&_sb_ds_ref_ok>0) %then &SB_DS_REF;
    );
    length normalized_title $300;
    normalized_title=lowcase(compbl(strip(vvaluex("&SB_DS_TITLE"))));
    weight_value=input(strip(vvaluex("&SB_DS_WEIGHT")), ?? best32.);
    invalid_weight=(missing(weight_value) or weight_value<0);
    if weight_value<0 then weight_value=.;
    keep normalized_title weight_value invalid_weight
      %if %sysevalf(&_sb_ds_ref_ok>0) %then &SB_DS_REF;
    ;
  run;

  proc means data=work._sb_ds_weights n nmiss sum median q1 q3 max noprint;
    var weight_value;
    output out=work.sb_datascience_weight_summary(drop=_type_ _freq_)
      n=valid_weight_rows nmiss=missing_weight_rows sum=weighted_job_total
      median=median_weight q1=q1_weight q3=q3_weight max=max_weight;
  run;
  proc sql;
    create table work.sb_datascience_row_summary as
    select count(*) as source_row_count,
           sum(invalid_weight) as missing_or_negative_weight_rows,
           max(weight_value) as maximum_row_weight
    from work._sb_ds_weights;
    create table work.sb_datascience_title_summary as
    select normalized_title, count(*) as source_row_count,
           sum(weight_value) as weighted_job_total,
           sum(invalid_weight) as invalid_weight_rows
    from work._sb_ds_weights group by normalized_title;
    create table work.sb_datascience_reference_duplicates as
    %if %sysevalf(&_sb_ds_ref_ok>0) %then %do;
      select count(*) as duplicate_reference_groups,
             sum(group_rows-1) as excess_rows
      from (select &SB_DS_REF, count(*) as group_rows
            from work._sb_ds_weights where not missing(&SB_DS_REF)
            group by &SB_DS_REF having count(*)>1) as grouped_ref;
    %end;
    %else %do;
      select . as duplicate_reference_groups, . as excess_rows;
    %end;
  quit;

  data work.sb_datascience_weight_summary;
    merge work.sb_datascience_weight_summary work.sb_datascience_row_summary;
    if not missing(weighted_job_total) then
      leave_one_max_out_total=weighted_job_total-maximum_row_weight;
    label source_row_count='Source records (not jobs)'
      weighted_job_total='Sum of num_of_jobs (weighted proxy)'
      leave_one_max_out_total='Weighted total excluding one maximum row';
  run;

  title "Limit.less | Market evidence outputs | VFL only";
  proc print data=work.sb_market_field_denominators noobs; run;
  proc print data=work.sb_market_skills noobs; run;
  proc print data=work.sb_market_skill_sensitivity noobs; run;
  proc print data=work.sb_datascience_weight_summary noobs; run;
  title;
  %put NOTE: [SignalBridge] Market tables created in WORK only. Skill labels and edges remain unreviewed candidates.;
%mend;

%sb_market_signals;
