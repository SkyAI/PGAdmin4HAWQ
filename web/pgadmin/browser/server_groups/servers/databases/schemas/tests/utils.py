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
import uuid

from regression.python_test_utils import test_utils as utils


def get_schema_config_data(db_user):
    """This function is used to get advance config test data for schema"""
    data = {
        "deffuncacl": [],
        "defseqacl": [],
        "deftblacl": [],
        "deftypeacl": [],
        "name": "test_schema_{0}".format(str(uuid.uuid4())[1:8]),
        "namespaceowner": db_user,
        "nspacl": [
            {
                "grantee": db_user,
                "grantor": db_user,
                "privileges":
                    [
                        {
                            "privilege_type": "C",
                            "privilege": True,
                            "with_grant": False
                        },
                        {
                            "privilege_type": "U",
                            "privilege": True,
                            "with_grant": False
                        }
                    ]
            }
        ],
        "seclabels": []
    }
    return data


def create_schema(connection, schema_name):
    """This function add the schemas into databases"""
    try:
        old_isolation_level = connection.isolation_level
        connection.set_isolation_level(0)
        pg_cursor = connection.cursor()
        pg_cursor.execute("CREATE SCHEMA %s" % schema_name)
        connection.set_isolation_level(old_isolation_level)
        connection.commit()
        # Get schema details of newly created schema
        pg_cursor.execute("SELECT sch.oid, sch.nspname FROM pg_namespace sch"
                          " WHERE sch.nspname='%s'" % schema_name)
        schema = pg_cursor.fetchone()
        connection.close()
        return schema
    except Exception:
        traceback.print_exc(file=sys.stderr)


def verify_schemas(server, db_name, schema_name):
    """This function verifies the schema is exists"""
    try:
        connection = utils.get_db_connection(db_name,
                                             server['username'],
                                             server['db_password'],
                                             server['host'],
                                             server['port'],
                                             server['sslmode'])
        pg_cursor = connection.cursor()
        pg_cursor.execute("SELECT * FROM pg_namespace sch"
                          " WHERE sch.nspname='%s'" % schema_name)
        schema = pg_cursor.fetchone()
        connection.close()
        return schema
    except Exception:
        traceback.print_exc(file=sys.stderr)
