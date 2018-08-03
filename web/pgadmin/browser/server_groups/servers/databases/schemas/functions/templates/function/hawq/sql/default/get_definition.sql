SELECT proretset, prosrc, probin,
  pg_catalog.oidvectortypes(proargtypes)  AS funcargs,
  pg_catalog.oidvectortypes(proargtypes)  AS funciargs,
  typ.typname AS funcresult,
  proiswin, provolatile, proisstrict, prosecdef,
  prodataaccess,
  'a' as proexeclocation,
  (SELECT lanname FROM pg_catalog.pg_language WHERE pg_proc.oid = prolang) as lanname,
  COALESCE(pg_catalog.oidvectortypes(proargtypes), '') AS func_with_identity_arguments,
  nspname,
  proname,
  COALESCE(pg_catalog.oidvectortypes(proargtypes), '') AS func_args
FROM pg_catalog.pg_proc
  JOIN pg_namespace nsp ON nsp.oid=pg_proc.pronamespace
  JOIN
   pg_type typ on typ.oid=prorettype
WHERE proisagg = FALSE
  AND pronamespace = {{scid}}::oid
  AND pg_proc.oid = {{fnid}}::oid;
