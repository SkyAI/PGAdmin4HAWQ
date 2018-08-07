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


def create_sequences(server, db_name, schema_name, sequence_name):
    """
    This function used to create sequence in schema provided.
    :param server: server details
    :type server: dict
    :param db_name: database name
    :type db_name: str
    :param schema_name: schema name
    :type schema_name: str
    :param sequence_name: sequence name
    :type sequence_name: str
    :return sequence_id: sequence id
    :rtype: int
    """
    try:
        connection = utils.get_db_connection(db_name,
                                             server['username'],
                                             server['db_password'],
                                             server['host'],
                                             server['port'],
                                             server['sslmode'])
        pg_cursor = connection.cursor()
        query = "CREATE SEQUENCE %s.%s START 101" % (schema_name,
                                                     sequence_name)
        pg_cursor.execute(query)
        connection.commit()
        # Get 'oid' from newly created sequence
        pg_cursor.execute("select oid from pg_class where relname='%s'" %
                          sequence_name)
        sequence = pg_cursor.fetchone()
        sequence_id = ''
        if sequence:
            sequence_id = sequence[0]
        connection.close()
        return sequence_id
    except Exception:
        traceback.print_exc(file=sys.stderr)


def verify_sequence(server, db_name, sequence_name):
    """
    This function verifies the sequence in database
    :param server: server details
    :type server: dict
    :param db_name: database name
    :type db_name: str
    :param sequence_name: sequence name
    :type sequence_name: str
    :return sequence: sequence record from database
    :rtype: tuple
    """
    try:
        connection = utils.get_db_connection(db_name,
                                             server['username'],
                                             server['db_password'],
                                             server['host'],
                                             server['port'],
                                             server['sslmode'])
        pg_cursor = connection.cursor()
        pg_cursor.execute("select * from pg_class where relname='%s'" %
                          sequence_name)
        sequence = pg_cursor.fetchone()
        connection.close()
        return sequence
    except Exception:
        traceback.print_exc(file=sys.stderr)
