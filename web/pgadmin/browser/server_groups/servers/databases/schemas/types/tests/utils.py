##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2018, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################

from __future__ import print_function

import sys
import traceback

from regression.python_test_utils import test_utils as utils


def create_type(server, db_name, schema_name, type_name):
    """
    This function creates a type under provided schema.
    :param server: server details
    :type server: dict
    :param db_name: database name
    :type db_name: str
    :param schema_name: schema name
    :type schema_name: str
    :param type_name: type name
    :type type_name: str
    :return type_id: type id
    :rtype: int
    """
    try:
        connection = utils.get_db_connection(db_name,
                                             server['username'],
                                             server['db_password'],
                                             server['host'],
                                             server['port'])
        old_isolation_level = connection.isolation_level
        connection.set_isolation_level(0)
        pg_cursor = connection.cursor()
        query = 'CREATE TYPE %s.%s AS  (one "char", two "char"[]); ' \
                'ALTER TYPE %s.%s  OWNER TO %s' % (schema_name, type_name,
                                                   schema_name, type_name,
                                                   server['username'])
        pg_cursor.execute(query)
        connection.set_isolation_level(old_isolation_level)
        connection.commit()
        # Get 'oid' from newly created type
        pg_cursor.execute(
            "select oid from pg_type where typname='%s'" % type_name)
        schema_type = pg_cursor.fetchone()
        type_id = schema_type[0]
        connection.close()
        return type_id
    except Exception:
        traceback.print_exc(file=sys.stderr)


def verify_type(server, db_name, type_name):
    """
    This function verifies type exist in database or not.
    :param server: server details
    :type server: dict
    :param db_name: database name
    :type db_name: str
    :param type_name: type name
    :type type_name: str
    :return schema_type: type record from database
    :rtype: tuple
    """
    try:
        connection = utils.get_db_connection(db_name,
                                             server['username'],
                                             server['db_password'],
                                             server['host'],
                                             server['port'])
        pg_cursor = connection.cursor()
        pg_cursor.execute(
            "select oid from pg_type where typname='%s'" % type_name)
        schema_type = pg_cursor.fetchone()
        connection.close()
        return schema_type
    except Exception:
        traceback.print_exc(file=sys.stderr)
