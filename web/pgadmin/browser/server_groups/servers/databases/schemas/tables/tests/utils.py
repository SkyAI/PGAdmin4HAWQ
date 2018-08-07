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


def create_table(server, db_name, schema_name, table_name):
    """
    This function creates a table under provided schema.
    :param server: server details
    :type server: dict
    :param db_name: database name
    :type db_name: str
    :param schema_name: schema name
    :type schema_name: str
    :param table_name: table name
    :type table_name: str
    :return table_id: table id
    :rtype: int
    """
    try:
        connection = utils.get_db_connection(db_name,
                                             server['username'],
                                             server['db_password'],
                                             server['host'],
                                             server['port'],
                                             server['sslmode'])
        old_isolation_level = connection.isolation_level
        connection.set_isolation_level(0)
        pg_cursor = connection.cursor()
        query = "CREATE TABLE %s.%s(id serial UNIQUE NOT NULL, name text," \
                " location text)" %\
                (schema_name, table_name)
        pg_cursor.execute(query)
        connection.set_isolation_level(old_isolation_level)
        connection.commit()
        # Get 'oid' from newly created table
        pg_cursor.execute("select oid from pg_class where relname='%s'" %
                          table_name)
        table = pg_cursor.fetchone()
        table_id = ''
        if table:
            table_id = table[0]
        connection.close()
        return table_id
    except Exception:
        traceback.print_exc(file=sys.stderr)
        raise


def verify_table(server, db_name, table_id):
    """
    This function verifies table exist in database or not.
    :param server: server details
    :type server: dict
    :param db_name: database name
    :type db_name: str
    :param table_id: schema name
    :type table_id: int
    :return table: table record from database
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
        pg_cursor.execute("SELECT * FROM pg_class tb WHERE tb.oid=%s" %
                          table_id)
        table = pg_cursor.fetchone()
        connection.close()
        return table
    except Exception:
        traceback.print_exc(file=sys.stderr)
        raise


def create_table_for_partition(
    server, db_name, schema_name, table_name,
    table_type, partition_type, partition_name=None
):
    """
    This function creates partitioned/partition/regular table
    under provided schema.

    :param server: server details
    :param db_name: database name
    :param schema_name: schema name
    :param table_name: table name
    :param table_type: regular/partitioned/partition
    :param partition_type: partition table type (range/list)
    :param partition_name: Partition Name
    :return table_id: table id
    """
    try:
        connection = utils.get_db_connection(db_name,
                                             server['username'],
                                             server['db_password'],
                                             server['host'],
                                             server['port'],
                                             server['sslmode'])
        old_isolation_level = connection.isolation_level
        connection.set_isolation_level(0)
        pg_cursor = connection.cursor()

        query = ''
        if table_type == 'partitioned':
            if partition_type == 'range':
                query = "CREATE TABLE %s.%s(country text, sales bigint, " \
                        "saledate date) PARTITION BY RANGE(saledate)" % \
                        (schema_name, table_name)
            else:
                query = "CREATE TABLE %s.%s(country text, sales bigint, " \
                        "saledate date) PARTITION BY LIST(saledate)" % \
                        (schema_name, table_name)
        elif table_type == 'partition':
            if partition_type == 'range':
                query = "CREATE TABLE %s.%s PARTITION OF %s.%s " \
                        "FOR VALUES FROM ('2012-01-01') TO ('2012-12-31')" % \
                        (schema_name, partition_name, schema_name, table_name)
            else:
                query = "CREATE TABLE %s.%s PARTITION OF %s.%s " \
                        "FOR VALUES IN ('2013-01-01')" % \
                        (schema_name, partition_name, schema_name, table_name)

            # To fetch OID table name is actually partition name
            table_name = partition_name
        elif table_type == 'regular':
            query = "CREATE TABLE %s.%s(country text, sales bigint," \
                    "saledate date NOT NULL)" % (schema_name, table_name)

        pg_cursor.execute(query)
        connection.set_isolation_level(old_isolation_level)
        connection.commit()
        # Get 'oid' from newly created table
        pg_cursor.execute("select oid from pg_class where relname='%s'" %
                          table_name)
        table = pg_cursor.fetchone()
        table_id = ''
        if table:
            table_id = table[0]
        connection.close()
        return table_id
    except Exception:
        traceback.print_exc(file=sys.stderr)
        raise


def set_partition_data(server, db_name, schema_name, table_name,
                       partition_type, data, mode):
    """
    This function is used to set the partitions data on the basis of
    partition type and action.

    :param server: server details
    :param db_name: Database Name
    :param schema_name: Schema Name
    :param table_name: Table Name
    :param partition_type: range or list
    :param data: Data
    :param mode: create/detach
    :return:
    """

    data['partitions'] = dict()
    if partition_type == 'range' and mode == 'create':
        data['partitions'].update(
            {'added': [{'values_from': "'2014-01-01'",
                        'values_to': "'2014-12-31'",
                        'is_attach': False,
                        'partition_name': 'sale_2014'},
                       {'values_from': "'2015-01-01'",
                        'values_to': "'2015-12-31'",
                        'is_attach': False,
                        'partition_name': 'sale_2015'
                        }]
             }
        )
    elif partition_type == 'list' and mode == 'create':
        data['partitions'].update(
            {'added': [{'values_in': "'2016-01-01', '2016-12-31'",
                        'is_attach': False,
                        'partition_name': 'sale_2016'},
                       {'values_in': "'2017-01-01', '2017-12-31'",
                        'is_attach': False,
                        'partition_name': 'sale_2017'
                        }]
             }
        )
    elif partition_type == 'range' and mode == 'detach':
        partition_id = create_table_for_partition(server, db_name, schema_name,
                                                  table_name, 'partition',
                                                  partition_type, 'sale_2012')
        data['partitions'].update(
            {'deleted': [{'oid': partition_id}]
             }
        )
    elif partition_type == 'list' and mode == 'detach':
        partition_id = create_table_for_partition(server, db_name, schema_name,
                                                  table_name, 'partition',
                                                  partition_type, 'sale_2013')
        data['partitions'].update(
            {'deleted': [{'oid': partition_id}]
             }
        )
    elif partition_type == 'range' and mode == 'attach':
        partition_id = create_table_for_partition(
            server, db_name, schema_name, 'attach_sale_2010', 'regular',
            partition_type
        )
        data['partitions'].update(
            {'added': [{'values_from': "'2010-01-01'",
                        'values_to': "'2010-12-31'",
                        'is_attach': True,
                        'partition_name': partition_id
                        }]
             }
        )
    elif partition_type == 'list' and mode == 'attach':
        partition_id = create_table_for_partition(
            server, db_name, schema_name, 'attach_sale_2011', 'regular',
            partition_type
        )
        data['partitions'].update(
            {'added': [{'values_in': "'2011-01-01'",
                        'is_attach': True,
                        'partition_name': partition_id
                        }]
             }
        )
