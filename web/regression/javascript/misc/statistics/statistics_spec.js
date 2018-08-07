//////////////////////////////////////////////////////////////////////////
//
// pgAdmin 4 - PostgreSQL Tools
//
// Copyright (C) 2013 - 2018, The pgAdmin Development Team
// This software is released under the PostgreSQL Licence
//
//////////////////////////////////////////////////////////////////////////

import {nodeHasStatistics} from '../../../../pgadmin/static/js/misc/statistics/statistics';

describe('#nodeHasStatistics', () => {
  describe('when node hasStatistics is not a function', () => {
    it('return the value of hasStatistics', () => {
      const node = {
        hasStatistics: true,
      };
      expect(nodeHasStatistics(node, {})).toBe(true);
    });
  });

  describe('when node hasStatistics is a function', () => {
    describe('when the function returns true', () => {
      it('returns true', () => {
        const node = {
          hasStatistics: () => true,
          getTreeNodeHierarchy: jasmine.createSpy(),
        };
        const item = {};

        expect(nodeHasStatistics(node, item)).toBe(true);
        expect(node.getTreeNodeHierarchy).toHaveBeenCalledWith(item);
      });
    });
  });
});
