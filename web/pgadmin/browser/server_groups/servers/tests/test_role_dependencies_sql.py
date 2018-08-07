##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2018, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################
import os

from pgadmin.utils.route import BaseTestGenerator
from regression.python_test_utils import test_utils
from regression.python_test_utils.template_helper import file_as_template


class TestRoleDependenciesSql(BaseTestGenerator):
    scenarios = [
        # Fetching default URL for schema node.
        ('Test Role Dependencies SQL file', dict())
    ]

    def __init__(self):
        super(TestRoleDependenciesSql, self).__init__()
        self.table_id = -1

    def setUp(self):
        with test_utils.Database(self.server) as (connection, database_name):
            cursor = connection.cursor()
            try:
                cursor.execute(
                    "CREATE ROLE testpgadmin LOGIN PASSWORD '%s'"
                    % self.server['db_password'])
            except Exception as exception:
                print(exception)
            connection.commit()

        self.server_with_modified_user = self.server.copy()
        self.server_with_modified_user['username'] = "testpgadmin"

    def runTest(self):
        if hasattr(self, "ignore_test"):
            return

        with test_utils.Database(self.server) as (connection, database_name):
            test_utils.create_table(self.server_with_modified_user,
                                    database_name, "test_new_role_table")
            cursor = connection.cursor()
            cursor.execute("SELECT pg_class.oid AS table_id "
                           "FROM pg_class "
                           "WHERE pg_class.relname='test_new_role_table'")
            self.table_id = cursor.fetchone()[0]

            sql = self.generate_sql('default')
            cursor.execute(sql)

            fetch_result = cursor.fetchall()
            self.assertions(fetch_result, cursor.description)

    def tearDown(self):
        with test_utils.Database(self.server) as (connection, database_name):
            cursor = connection.cursor()
            cursor.execute("DROP ROLE testpgadmin")
            connection.commit()

    def generate_sql(self, version):
        template_file = self.get_template_file(version,
                                               "role_dependencies.sql")
        template = file_as_template(template_file)
        sql = template.render(
            where_clause="WHERE dep.objid=%s::oid" % self.table_id)

        return sql

    def assertions(self, fetch_result, descriptions):
        self.assertEqual(1, len(fetch_result))

        first_row = {}
        for index, description in enumerate(descriptions):
            first_row[description.name] = fetch_result[0][index]

        self.assertEqual('o', first_row["deptype"])

    @staticmethod
    def get_template_file(version, filename):
        return os.path.join(os.path.dirname(__file__), "..", "templates",
                            "depends", "sql", version, filename)
