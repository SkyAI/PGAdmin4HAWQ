##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2018, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################
import sys
from pgadmin.browser.server_groups.servers.databases.schemas.tables import \
    BaseTableView
from pgadmin.utils.route import BaseTestGenerator

if sys.version_info < (3, 3):
    from mock import patch, MagicMock
else:
    from unittest.mock import patch, MagicMock


class TestBaseView(BaseTableView):
    @BaseTableView.check_precondition
    def test(self, did, sid):
        pass


class TestUtils(BaseTestGenerator):
    scenarios = [
        ('Test wrapping function', dict(test='wrap'))
    ]

    def runTest(self):
        if self.test == 'wrap':
            self.__wrap_tests()

    def __wrap_tests(self):
        subject = TestBaseView(cmd='something')
        with patch('pgadmin.browser.server_groups.servers.databases.schemas'
                   '.tables.utils.get_driver') as get_driver_mock:
            get_driver_mock.return_value = MagicMock(
                connection_manager=MagicMock(
                    return_value=MagicMock(
                        connection=MagicMock(),
                        db_info={
                            1: dict(datlastsysoid=False)
                        },
                        version=10,
                        server_type='gpdb'
                    )
                ),
                qtIndent=MagicMock(),
                qtTypeIdent=MagicMock()
            )
            subject.test(did=1, sid=2)
            self.assertEqual(
                subject.table_template_path, 'table/sql/#gpdb#10#')
            self.assertEqual(
                subject.data_type_template_path, 'datatype/sql/#gpdb#10#')
            self.assertEqual(
                subject.check_constraint_template_path,
                'check_constraint/sql/#gpdb#10#')
            self.assertEqual(
                subject.exclusion_constraint_template_path,
                'exclusion_constraint/sql/#gpdb#10#')
            self.assertEqual(
                subject.foreign_key_template_path,
                'foreign_key/sql/#gpdb#10#')
            self.assertEqual(
                subject.index_template_path,
                'index/sql/#gpdb#10#')
            self.assertEqual(
                subject.trigger_template_path,
                'trigger/sql/#gpdb#10#')
