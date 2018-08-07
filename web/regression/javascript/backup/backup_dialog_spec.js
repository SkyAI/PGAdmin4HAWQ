/////////////////////////////////////////////////////////////
//
// pgAdmin 4 - PostgreSQL Tools
//
// Copyright (C) 2013 - 2018, The pgAdmin Development Team
// This software is released under the PostgreSQL Licence
//
//////////////////////////////////////////////////////////////
import {BackupDialog} from '../../../pgadmin/tools/backup/static/js/backup_dialog';
import {TreeFake} from '../tree/tree_fake';

const context = describe;

describe('BackupDialog', () => {
  let backupDialog;
  let pgBrowser;
  let jquerySpy;
  let alertifySpy;
  let backupModelSpy;

  beforeEach(() => {
    pgBrowser = {
      treeMenu: new TreeFake(),
      Nodes: {
        server: {
          hasId: true,
          label: 'server',
          getTreeNodeHierarchy: jasmine.createSpy('server.getTreeNodeHierarchy'),
        },
        database: {
          hasId: true,
          label: 'database',
          getTreeNodeHierarchy: jasmine.createSpy('db.getTreeNodeHierarchy'),
        },
        schema: {
          hasId: true,
          label: 'schema',
          getTreeNodeHierarchy: jasmine.createSpy('db.getTreeNodeHierarchy'),
        },
      },
    };
    pgBrowser.Nodes.server.hasId = true;
    pgBrowser.Nodes.database.hasId = true;
    jquerySpy = jasmine.createSpy('jquerySpy');
    backupModelSpy = jasmine.createSpy('backupModelSpy');

    const hierarchy = {
      children: [
        {
          id: 'root',
          children: [
            {
              id: 'serverTreeNode',
              data: {
                _id: 10,
                _type: 'server',
              },
              children: [
                {
                  id: 'some_database',
                  data: {
                    _type: 'database',
                    _id: 11,
                    label: 'some_database',
                    _label: 'some_database_label',
                  },
                }, {
                  id: 'database_with_equal_in_name',
                  data: {
                    _type: 'database',
                    label: 'some_database',
                    _label: '=some_database_label',
                  },
                },
              ],
            },
            {
              id: 'ppasServer',
              data: {
                _type: 'server',
                server_type: 'ppas',
                children: [
                  {id: 'someNodeUnderneathPPASServer'},
                ],
              },
            },
          ],
        },
      ],
    };

    pgBrowser.treeMenu = TreeFake.build(hierarchy);
  });

  describe('#draw', () => {
    beforeEach(() => {
      alertifySpy = jasmine.createSpyObj('alertify', ['alert', 'dialog']);
      alertifySpy['backup_objects'] = jasmine.createSpy('backup_objects');
      backupDialog = new BackupDialog(
        pgBrowser,
        jquerySpy,
        alertifySpy,
        backupModelSpy
      );

      pgBrowser.get_preference = jasmine.createSpy('get_preferences');
    });

    context('there are no ancestors of the type server', () => {
      it('does not create a dialog', () => {
        pgBrowser.treeMenu.selectNode([{id: 'root'}]);
        backupDialog.draw(null, null, null);
        expect(alertifySpy['backup_objects']).not.toHaveBeenCalled();
      });

      it('display an alert with a Backup Error', () => {
        backupDialog.draw(null, [{id: 'root'}], null);
        expect(alertifySpy.alert).toHaveBeenCalledWith(
          'Backup Error',
          'Please select server or child node from the browser tree.'
        );
      });
    });

    context('there is an ancestor of the type server', () => {
      context('no preference can be found', () => {
        beforeEach(() => {
          pgBrowser.get_preference.and.returnValue(undefined);
        });

        context('server is a ppas server', () => {
          it('display an alert with "Backup Error"', () => {
            backupDialog.draw(null, [{id: 'some_database'}], null);
            expect(alertifySpy.alert).toHaveBeenCalledWith(
              'Backup Error',
              'Failed to load preference pg_bin_dir of module paths'
            );
          });
        });

        context('server is not a ppas server', () => {
          it('display an alert with "Backup Error"', () => {
            backupDialog.draw(null, [{id: 'ppasServer'}], null);
            expect(alertifySpy.alert).toHaveBeenCalledWith(
              'Backup Error',
              'Failed to load preference ppas_bin_dir of module paths'
            );
          });
        });
      });

      context('preference can be found', () => {
        context('binary folder is not configured', () => {
          beforeEach(() => {
            pgBrowser.get_preference.and.returnValue({});
          });

          context('server is a ppas server', () => {
            it('display an alert with "Configuration required"', () => {
              backupDialog.draw(null, [{id: 'serverTreeNode'}], null);
              expect(alertifySpy.alert).toHaveBeenCalledWith(
                'Configuration required',
                'Please configure the PostgreSQL Binary Path in the Preferences dialog.'
              );
            });
          });

          context('server is not a ppas server', () => {
            it('display an alert with "Configuration required"', () => {
              backupDialog.draw(null, [{id: 'ppasServer'}], null);
              expect(alertifySpy.alert).toHaveBeenCalledWith(
                'Configuration required',
                'Please configure the EDB Advanced Server Binary Path in the Preferences dialog.'
              );
            });
          });
        });

        context('binary folder is configured', () => {
          let backupDialogResizeToSpy;
          beforeEach(() => {
            backupDialogResizeToSpy = jasmine.createSpyObj('backupDialogResizeToSpy', ['resizeTo']);
            alertifySpy['backup_objects'].and
              .returnValue(backupDialogResizeToSpy);
            pgBrowser.get_preference.and.returnValue({value: '/some/path'});
          });

          it('displays the dialog', () => {
            backupDialog.draw(null, [{id: 'serverTreeNode'}], null);
            expect(alertifySpy['backup_objects']).toHaveBeenCalledWith(true);
            expect(backupDialogResizeToSpy.resizeTo).toHaveBeenCalledWith('60%', '50%');
          });

          context('database label contain "="', () => {
            it('should create alert dialog with backup error', () => {
              backupDialog.draw(null, [{id: 'database_with_equal_in_name'}], null);
              expect(alertifySpy.alert).toHaveBeenCalledWith('Backup Error',
                'Databases with = symbols in the name cannot be backed up or restored using this utility.');
            });
          });
        });
      });
    });
  });
});
