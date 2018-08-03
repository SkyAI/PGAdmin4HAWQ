SELECT
    procpid AS {{ conn|qtIdent('PID') }},
    usename AS {{ conn|qtIdent(_('User')) }},
    datname AS {{ conn|qtIdent(_('Database')) }},
    backend_start AS {{ conn|qtIdent(_('Backend start')) }},
    CASE
    WHEN client_addr IS NOT NULL AND client_addr::text != '' THEN
        client_addr::text || ':' || client_port
    WHEN client_port = -1 THEN
        'local pipe'
    ELSE
        'localhost:' || client_port
    END AS {{ conn|qtIdent(_('Client')) }},
    application_name AS {{ conn|qtIdent(_('Application')) }},
    waiting AS {{ conn|qtIdent(_('Waiting?')) }},
    current_query AS {{ conn|qtIdent(_('Query')) }},
    query_start AS {{ conn|qtIdent(_('Query start')) }},
    xact_start AS {{ conn|qtIdent(_('Xact start')) }}
FROM
    pg_stat_activity sa
WHERE
    (SELECT r.rolsuper OR r.oid = sa.usesysid  FROM pg_roles r WHERE r.rolname = current_user)
