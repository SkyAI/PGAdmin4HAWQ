##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2018, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################

import uuid

from pgadmin.browser.server_groups.servers.databases.schemas.tests import \
    utils as schema_utils
from pgadmin.browser.server_groups.servers.databases.tests import utils as \
    database_utils
from pgadmin.utils import server_utils as server_utils
from pgadmin.utils.route import BaseTestGenerator
from regression import parent_node_dict
from regression.python_test_utils import test_utils as utils
from . import utils as views_utils


class ViewsGetTestCase(BaseTestGenerator):
    """This class will fetch the view under schema node."""
    view_sql = "CREATE OR REPLACE VIEW %s.%s AS SELECT 'Hello World'; " \
               "ALTER TABLE %s.%s OWNER TO %s"
    m_view_sql = "CREATE MATERIALIZED VIEW %s.%s TABLESPACE pg_default AS " \
                 "SELECT 'test_pgadmin' WITH NO DATA;ALTER TABLE %s.%s OWNER" \
                 " TO %s"
    scenarios = [
        ('Get view under schema node', dict(
            url='/browser/view/obj/',
            view_name="test_view_get_%s" % (str(uuid.uuid4())[1:8]),
            sql_query=view_sql)),
        ('Get materialized view under schema node',
         dict(url='/browser/mview/obj/',
              view_name="test_mview_get_%s" % (str(uuid.uuid4())[1:8]),
              sql_query=m_view_sql))
    ]

    def setUp(self):
        self.db_name = parent_node_dict["database"][-1]["db_name"]
        schema_info = parent_node_dict["schema"][-1]
        self.server_id = schema_info["server_id"]
        self.db_id = schema_info["db_id"]
        server_response = server_utils.connect_server(self, self.server_id)

        if server_response["data"]["version"] < 90300 and "mview" in self.url:
            message = "Materialized Views are not supported by PG9.2 " \
                      "and PPAS9.2 and below."
            self.skipTest(message)

        db_con = database_utils.connect_database(self, utils.SERVER_GROUP,
                                                 self.server_id, self.db_id)
        if not db_con['data']["connected"]:
            raise Exception("Could not connect to database to fetch the view.")
        self.schema_id = schema_info["schema_id"]
        self.schema_name = schema_info["schema_name"]
        schema_response = schema_utils.verify_schemas(self.server,
                                                      self.db_name,
                                                      self.schema_name)
        if not schema_response:
            raise Exception("Could not find the schema to fetch the view.")
        self.view_id = views_utils.create_view(self.server,
                                               self.db_name,
                                               self.schema_name,
                                               self.sql_query,
                                               self.view_name)

    def runTest(self):
        """This function will fetch the view/mview under schema node."""
        response = self.tester.get(
            "{0}{1}/{2}/{3}/{4}/{5}".format(self.url, utils.SERVER_GROUP,
                                            self.server_id, self.db_id,
                                            self.schema_id, self.view_id
                                            ),
            follow_redirects=True
        )
        self.assertEquals(response.status_code, 200)

    def tearDown(self):
        # Disconnect the database
        database_utils.disconnect_database(self, self.server_id, self.db_id)
