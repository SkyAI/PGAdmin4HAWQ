SELECT
    pr.oid, pr.xmin, pr.*, pr.prosrc AS prosrc_c,
    pr.proname AS name, typ.typname as prorettypename,
    typns.nspname AS typnsp, lanname, proargnames, oidvectortypes(proargtypes) AS proargtypenames,
    null as proargdefaultvals,
    null as pronargdefaults,
    null  as proconfig,
    pg_get_userbyid(proowner) AS funcowner, description,
    NULL AS seclabels
FROM
    pg_proc pr
JOIN
    pg_type typ ON typ.oid=prorettype
JOIN
    pg_namespace typns ON typns.oid=typ.typnamespace
JOIN
    pg_language lng ON lng.oid=prolang
LEFT OUTER JOIN
    pg_description des ON (des.objoid=pr.oid AND des.classoid='pg_proc'::regclass)
WHERE
    proisagg = FALSE
{% if fnid %}
    AND pr.oid = {{fnid}}::oid
{% else %}
    AND pronamespace = {{scid}}::oid
{% endif %}
    AND typname NOT IN ('trigger', 'event_trigger')
ORDER BY
    proname;
