"""
Lyle Scott, III
lyle@digitalfoo.net
http://digitalfoo.net

Copyright (c) 2012 Lyle Scott, III

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

import json
import jsonpickle
import re
import unittest

from mongotree import mongotree


# Used to find strings like: ObjectId('508d606afdbf6ddc32ad1225')
OBJID_RE = r'ObjectId\(\'[a-z0-9]+\'\)'


class MongoTreeTest(unittest.TestCase):
    """Tests the MongoTree class for saneness."""

    def setUp(self):
        """Initialization."""
        self.db_name = 'mongotree_test'
        self.identifier = 'mongotest'
        self.tree = mongotree.MongoTree(db_name=self.db_name,
                                        identifier=self.identifier)

    def drop_db(self):
        """Drop a collection."""
        self.tree.db.treefoo.drop()

    def test___init__(self):
        """Test initialization."""
        assert self.tree
        assert isinstance(self.tree, mongotree.MongoTree)

    def test__repr__(self):
        """The ASCII representation of this object should be legit."""
        path = ['select', '*', 'from']
        self.tree.upsert(path)

        r = re.sub(OBJID_RE, 'OBJID', repr(self.tree))

        assert r == """[{u'_id': OBJID,
  u'children': [OBJID],
  u'hits': 1,
  u'identifier': u'mongotest',
  u'label': u'select',
  u'obj': None,
  u'parent': None,
  u'path': u'select'},
 {u'_id': OBJID,
  u'children': [OBJID],
  u'hits': 1,
  u'identifier': u'mongotest',
  u'label': u'*',
  u'obj': None,
  u'parent': OBJID,
  u'path': u'select|$|*'},
 {u'_id': OBJID,
  u'children': [],
  u'hits': 1,
  u'identifier': u'mongotest',
  u'label': u'from',
  u'obj': None,
  u'parent': OBJID,
  u'path': u'select|$|*|$|from'}]"""

    def test_fromXml(self):
        """Test that a MongoTree can be properly formed with raw XML."""
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<select>
    <all>
        <from>
            <foo/>
            <bar/>
        </from>
    </all>
    <id>
        <from>
            <bar/>
        </from>
    </id>
</select>"""
        self.tree.fromXml(xml)

        assert self.tree.node_count() == 8

        path = ('select',)
        assert self.tree.path_exists(path)

        path = ('select', 'all', 'from', 'foo')
        assert self.tree.path_exists(path)

        path = ('select', 'all', 'from', 'bar')
        assert self.tree.path_exists(path)

        path = ('select', 'id', 'from', 'bar')
        assert self.tree.path_exists(path)

        path = ('select', 'all', 'from', 'baz')
        assert not self.tree.path_exists(path)

        self.drop_db()

    def test_upsert(self):
        """upsert() should save the correct information to the DB."""
        path = ['select',]
        self.tree.upsert(path)
        assert self.tree.node_count() == 1
        assert self.tree.path_exists(path)

        path = ['select', '*', 'from', 'fruits']
        self.tree.upsert(path)
        assert self.tree.node_count() == 4
        assert self.tree.path_exists(path)

        self.drop_db()

    def test_upsert_inc(self):
        """upsert() should save the correct information to the DB."""
        path = ['select', '*',]
        self.tree.upsert(path)

        root = self.tree.get_roots()[0]

        for node in self.tree.traverse(root):
            assert node['hits'] == 1

        path = ['select', '*', 'from']
        self.tree.upsert(path)

        assert self.tree.get_node(['select'])['hits'] == 2
        assert self.tree.get_node(['select', '*'])['hits'] == 2
        assert self.tree.get_node(['select', '*', 'from'])['hits'] == 1

        path = ['select', 'id']
        self.tree.upsert(path, hit_inc=10)
        assert self.tree.get_node(['select'])['hits'] == 12
        assert self.tree.get_node(['select', 'id'])['hits'] == 10

        self.drop_db()

    def test_upsert_with_invalid_path(self):
        """upsert() should save the correct information to the DB."""
        path = 'select * from'
        self.assertRaises(ValueError, self.tree.upsert, path)

        self.drop_db()

    def test_upsert_with_obj(self):
        """upsert() should save the correct information to the DB."""
        path = ['select', 'id']
        pkl = json.loads(jsonpickle.encode('foobar'))
        self.tree.upsert(path, obj=pkl)

        node = self.tree.get_node(path)
        assert pkl == node['obj']

        assert jsonpickle.decode(json.dumps(pkl)) == 'foobar'

        self.drop_db()

    def test_get_roots(self):
        """get_roots() should only return nodes with no parents."""
        path = ['select', '*', 'from', 'foo']
        self.tree.upsert(path)

        path = ['select', '*', 'from', 'bar']
        self.tree.upsert(path)

        path = ['update', 'foobar', 'set']
        self.tree.upsert(path)

        path = ['delete', 'baz', 'from', 'foobar']
        self.tree.upsert(path)

        roots = self.tree.get_roots()

        assert len(roots) == 3

        assert roots[0]['label'] == 'select'
        assert roots[0]['parent'] == None

        assert roots[1]['label'] == 'update'
        assert roots[1]['parent'] == None

        assert roots[2]['label'] == 'delete'
        assert roots[2]['parent'] == None

        self.drop_db()

    def test_get_dotgraph(self):
        """"""
        path = ['select', '*', 'from', 'foo']
        self.tree.upsert(path)
        path = ['select', '*', 'from', 'bar']
        self.tree.upsert(path)
        path = ['select', 'id', 'from', 'baz']
        self.tree.upsert(path)

        graph = self.tree.get_dotgraph().to_string()

        lines = graph.split('\n')

        assert lines[1].split()[1] == '[label=select];'
        assert lines[2].split()[1] == '[label="*"];'
        assert lines[4].split()[1] == '[label=select];'
        assert lines[5].split()[1] == '[label=id];'
        assert lines[7].split()[1] == '[label="*"];'
        assert lines[8].split()[1] == '[label=from];'
        assert lines[10].split()[1] == '[label=from];'
        assert lines[11].split()[1] == '[label=foo];'
        assert lines[13].split()[1] == '[label=from];'
        assert lines[14].split()[1] == '[label=bar];'
        assert lines[16].split()[1] == '[label=id];'
        assert lines[17].split()[1] == '[label=from];'
        assert lines[19].split()[1] == '[label=from];'
        assert lines[20].split()[1] == '[label=baz];'

        self.drop_db()

    def test_get_dotgraph_invalid_root(self):
        """dotgraph() should throw an exception if the roots argument is
        invalid.
        """
        path = ['select', 'id', 'from', 'baz']
        self.tree.upsert(path)

        self.assertRaises(ValueError, self.tree.get_dotgraph, 'select')

    def test_get_children_via_node(self):
        """Get all children of a node."""
        path = ['select', 'foo', 'from']
        self.tree.upsert(path)
        path = ['select', 'bar', 'from']
        self.tree.upsert(path)
        path = ['select', 'baz', 'from']
        self.tree.upsert(path)
        path = ['select', 'baz', 'derp']
        self.tree.upsert(path)

        root = self.tree.get_roots()[0]
        children = self.tree.children(node=root)
        assert len(children) == 3

        self.drop_db()

    def test_get_children_via_path(self):
        """Get all children of a node."""
        path = ['select', 'foo', 'from']
        self.tree.upsert(path)
        path = ['select', 'bar', 'from']
        self.tree.upsert(path)
        path = ['select', 'baz', 'from']
        self.tree.upsert(path)
        path = ['select', 'baz', 'derp']
        self.tree.upsert(path)

        path = ['select']
        children = self.tree.children(path=path)
        assert len(children) == 3

        node = self.tree.get_node(path=['select', 'baz'])
        children = self.tree.children(node=node)
        assert len(children) == 2

        self.drop_db()

    def test_get_children_no_args(self):
        """Supplying no args should blow up. Need a node or a path."""
        path = ['select', 'foo', 'from']
        self.tree.upsert(path)
        self.assertRaises(ValueError, self.tree.children)
        self.drop_db()

    def test_get_children_invalid_path(self):
        """Supplying no args should blow up. Need a node or a path."""
        path = ['select', 'foo', 'from']
        self.tree.upsert(path)
        kwargs = {'path': 'select * from'}
        self.assertRaises(ValueError, self.tree.children, **kwargs)
        self.drop_db()

    def test_get_node(self):
        """Get a node belonging to a path."""
        path1 = ['select', 'foo', 'from']
        self.tree.upsert(path1)
        path2 = ['select', 'foo', 'blah']
        self.tree.upsert(path2)

        node = self.tree.get_node(['select', 'foo'])
        assert node['label'] == 'foo'

        node = self.tree.get_node(path2)
        assert node['label'] == 'blah'

        self.drop_db()

    def test_get_node_invalid_path(self):
        """Get a node belonging to a path."""
        path = ['select', 'foo', 'from']
        self.tree.upsert(path)
        assert self.tree.get_node(['bar']) is None

        self.drop_db()

    def test_remove_no_children(self):
        """Remove a node from a tree."""
        path1 = ['select', 'foo', 'from', 'bar']
        self.tree.upsert(path1)
        path2 = ['select', 'foo', 'from', 'baz']
        self.tree.upsert(path2)

        node = self.tree.get_node(path1)
        self.tree.remove(node)

        assert self.tree.get_node(path1) is None

        node = self.tree.get_node(['select', 'foo'])
        self.tree.remove(node)

        assert self.tree.get_node(['select', 'foo', 'bar']) is None
        assert self.tree.get_node(['select', 'foo', 'baz']) is None
        assert self.tree.get_node(['select', 'foo']) is None

        self.drop_db()

    def test_remove_invalid_node(self):
        """Specifying an invalid node should throw ValueError exception."""
        path1 = ['select', 'foo', 'from', 'bar']
        self.tree.upsert(path1)

        self.assertRaises(ValueError, self.tree.remove, {'invalid': 'node'})

    def test_parent(self):
        """Get the parent node of the node pointed at by path."""
        path = ['select', 'foo', 'from', 'bar']
        self.tree.upsert(path)

        assert self.tree.parent(path)['label'] == 'from'

        self.drop_db()

    def test_parent_node_not_found(self):
        """Get the parent node of the node pointed at by path."""
        path = ['select', 'foo', 'from', 'bar']
        self.tree.upsert(path)

        assert self.tree.parent(['select', 'invalid', 'path']) is None

        self.drop_db()

    def test_valid_node_with_valid(self):
        """Should return True if the dict contains all the necessary keys."""
        node = {'identifier': 'foobar',
                'label': 'foo',
                'path': 'foo',
                'parent': None,
                'children': [],
                'hits': 1,
                'obj': None,
                '_id': 'abc123'}

        assert self.tree.valid_node(node)

        self.drop_db()

    def test_valid_node_with_different_count(self):
        """Should return False if dict doesn't contain the necessary keys."""
        node = {'identifier': 'foobar',
                'label': 'foo',
                'path': 'foo',
                #'parent': None,
                'children': [],
                #'hits': 1,
                'obj': None,
                '_id': 'abc123'}

        assert not self.tree.valid_node(node)

        self.drop_db()

    def test_valid_node_with_invalid_dict(self):
        """Should return False if dict doesn't contain the necessary keys."""
        node = {'identifier': 'foobar',
                'label': 'foo',
                'path': 'foo',
                'INVALIDKEY': None,
                'children': [],
                'hits': 1,
                'obj': None,
                '_id': 'abc123'}

        assert not self.tree.valid_node(node)

        self.drop_db()

    def tearDown(self):
        """Denitialization."""
        self.tree.mongo.drop_database(self.db_name)
