/////////////////////////////////////////////////////////////
//
// pgAdmin 4 - PostgreSQL Tools
//
// Copyright (C) 2013 - 2018, The pgAdmin Development Team
// This software is released under the PostgreSQL Licence
//
//////////////////////////////////////////////////////////////

import MockAdapter from 'axios-mock-adapter';
import axios from 'axios/index';
import {
  enableTriggers,
  disableTriggers,
} from '../../../pgadmin/browser/server_groups/servers/databases/schemas/tables/static/js/enable_disable_triggers';
import {TreeFake} from '../tree/tree_fake';
import {TreeNode} from '../../../pgadmin/static/js/tree/tree';

describe('#enableTriggers', () => {
  let networkMock;
  let tree;
  let alertify;
  let generateUrlSpy;
  beforeEach(() => {
    networkMock = new MockAdapter(axios);
    tree = new TreeFake();
    const server1 = tree.addNewNode('server1', {_id: 1}, ['<li>server1</li>']);
    const database1 = tree.addNewNode('database1', {_type: 'database'}, ['<li>database1</li>']);
    tree.addChild(server1, database1);

    const schema1 = tree.addNewNode('schema1', {_type: 'schema'}, ['<li>schema1</li>']);
    tree.addChild(database1, schema1);

    const table1 = tree.addNewNode('table1', {_type: 'table'}, ['<li>table1</li>']);
    tree.addChild(schema1, table1);

    const column1 = tree.addNewNode('column1', {_type: 'column'}, ['<li>column1</li>']);
    tree.addChild(table1, column1);

    const tableNoData = tree.addNewNode('table-no-data', undefined, ['<li>table-no-data</li>']);
    tree.addChild(schema1, tableNoData);

    alertify = jasmine.createSpyObj('alertify', ['success', 'error']);
    generateUrlSpy = jasmine.createSpy('generateUrl');
    generateUrlSpy.and.returnValue('/some/place');
  });

  describe('no node is selected', () => {
    it('does not send the request to the backend', (done) => {
      networkMock.onAny('.*').reply(200, () => {
      });

      setTimeout(() => {
        expect(enableTriggers(tree, alertify, generateUrlSpy, {})).toBe(false);
        done();
      }, 0);
    });
  });

  describe('a node is selected', () => {
    describe('node as no data', () => {
      it('does not send the request to the backend', () => {
        tree.selectNode([{id: 'table-no-data'}]);

        networkMock.onAny('.*').reply(200, () => {
        });

        setTimeout(() => {
          expect(enableTriggers(tree, alertify, generateUrlSpy, {})).toBe(false);
        }, 0);
      });
    });

    describe('node as  data', () => {
      describe('backend responds with success', () => {
        let networkMockCalledWith;
        beforeEach(() => {
          networkMockCalledWith = false;
          networkMock.onPut(/.*/).reply((configuration) => {
            networkMockCalledWith = configuration;
            return [200, {
              success: 1,
              info: 'some information',
            }];
          });
        });

        it('displays an alert box with success', (done) => {
          tree.selectNode([{id: 'table1'}]);
          enableTriggers(tree, alertify, generateUrlSpy, {});
          setTimeout(() => {
            expect(alertify.success).toHaveBeenCalledWith('some information');
            done();
          }, 0);
        });

        it('reloads the node', (done) => {
          enableTriggers(tree, alertify, generateUrlSpy, {item: [{id: 'table1'}]});
          setTimeout(() => {
            expect(tree.selected()).toEqual(['<li>table1</li>']);
            done();
          }, 20);
        });

        it('call backend with the correct parameters', (done) => {
          enableTriggers(tree, alertify, generateUrlSpy, {item: [{id: 'table1'}]});
          setTimeout(() => {
            expect(networkMockCalledWith.data).toEqual(JSON.stringify({enable: 'true'}));
            done();
          }, 0);
        });
      });

      describe('backend responds with error', () => {
        beforeEach(() => {
          networkMock.onPut(/.*/).reply(() => {
            return [500, {
              success: 0,
              errormsg: 'some error message',
            }];
          });
        });

        it('displays an error alert', (done) => {
          tree.selectNode([{id: 'table1'}]);
          enableTriggers(tree, alertify, generateUrlSpy, {});
          setTimeout(() => {
            expect(alertify.error).toHaveBeenCalledWith('some error message');
            done();
          }, 0);
        });

        it('unload the node', (done) => {
          enableTriggers(tree, alertify, generateUrlSpy, {item: [{id: 'table1'}]});

          setTimeout(() => {
            expect(tree.findNodeByDomElement([{id: 'table1'}]).children.length).toBe(0);
            done();
          }, 20);
        });
      });
    });
  });
});

describe('#disableTriggers', () => {
  let networkMock;
  let tree;
  let alertify;
  let generateUrlSpy;
  beforeEach(() => {
    networkMock = new MockAdapter(axios);
    tree = new TreeFake();
    const server1 = tree.addNewNode('server1', {_id: 1}, ['<li>server1</li>']);
    const database1 = new TreeNode('database1', {_type: 'database'}, ['<li>database1</li>']);
    tree.addChild(server1, database1);

    const schema1 = new TreeNode('schema1', {_type: 'schema'}, ['<li>schema1</li>']);
    tree.addChild(database1, schema1);

    const table1 = new TreeNode('table1', {_type: 'table'}, ['<li>table1</li>']);
    tree.addChild(schema1, table1);

    const column1 = new TreeNode('column1', {_type: 'column'}, ['<li>column1</li>']);
    tree.addChild(table1, column1);

    const tableNoData = new TreeNode('table-no-data', undefined, ['<li>table-no-data</li>']);
    tree.addChild(schema1, tableNoData);

    alertify = jasmine.createSpyObj('alertify', ['success', 'error']);
    generateUrlSpy = jasmine.createSpy('generateUrl');
    generateUrlSpy.and.returnValue('/some/place');
  });

  describe('no node is selected', () => {
    it('does not send the request to the backend', (done) => {
      networkMock.onAny('.*').reply(200, () => {
      });

      setTimeout(() => {
        expect(disableTriggers(tree, alertify, generateUrlSpy, {})).toBe(false);
        done();
      }, 0);
    });
  });

  describe('a node is selected', () => {
    describe('node as no data', () => {
      it('does not send the request to the backend', () => {
        tree.selectNode([{id: 'table-no-data'}]);

        networkMock.onAny('.*').reply(200, () => {
        });

        setTimeout(() => {
          expect(disableTriggers(tree, alertify, generateUrlSpy, {})).toBe(false);
        }, 0);
      });
    });

    describe('node as  data', () => {
      describe('backend responds with success', () => {
        let networkMockCalledWith;
        beforeEach(() => {
          networkMockCalledWith = false;
          networkMock.onPut(/.*/).reply((configuration) => {
            networkMockCalledWith = configuration;
            return [200, {
              success: 1,
              info: 'some information',
            }];
          });
        });

        it('displays an alert box with success', (done) => {
          tree.selectNode([{id: 'table1'}]);
          disableTriggers(tree, alertify, generateUrlSpy, {});
          setTimeout(() => {
            expect(alertify.success).toHaveBeenCalledWith('some information');
            done();
          }, 0);
        });

        it('reloads the node', (done) => {
          disableTriggers(tree, alertify, generateUrlSpy, {item: [{id: 'table1'}]});
          setTimeout(() => {
            expect(tree.selected()).toEqual(['<li>table1</li>']);
            done();
          }, 20);
        });

        it('call backend with the correct parameters', (done) => {
          disableTriggers(tree, alertify, generateUrlSpy, {item: [{id: 'table1'}]});
          setTimeout(() => {
            expect(networkMockCalledWith.data).toEqual(JSON.stringify({enable: 'false'}));
            done();
          }, 0);
        });
      });

      describe('backend responds with error', () => {
        beforeEach(() => {
          networkMock.onPut(/.*/).reply(() => {
            return [500, {
              success: 0,
              errormsg: 'some error message',
            }];
          });
        });

        it('displays an error alert', (done) => {
          tree.selectNode([{id: 'table1'}]);
          disableTriggers(tree, alertify, generateUrlSpy, {});
          setTimeout(() => {
            expect(alertify.error).toHaveBeenCalledWith('some error message');
            done();
          }, 0);
        });

        it('unload the node', (done) => {
          disableTriggers(tree, alertify, generateUrlSpy, {item: [{id: 'table1'}]});

          setTimeout(() => {
            expect(tree.findNodeByDomElement([{id: 'table1'}]).children.length).toBe(0);
            done();
          }, 20);
        });
      });
    });
  });
});
