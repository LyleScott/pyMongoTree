MongoTree
=========

Implement tree structures using MongoDB. 

Intro
-----

A node is represented by the following structure:

    {'_id': <ObjectId>,
     'identifier: <string; Used in part of a key to look items up. ie, a user.>
     'label': <string>,
     'parent': <ObjectId>,
     'obj': <json pickled blob>,
     'path': <string; path tokens delmited by MongoDB.SEPARATOR>,
     'hits': <int; how many times a node has been accessed.}
    
mongotree.MongoTree() is responsible for creating, searching, querying,
removing, etc, nodes.

Dependencies
------------
- lxml
- jsonpickle
- mongodb
- pydot
- pymongo

Example
-------

    >>> from mongotree import MongoTree
    >>> from pprint import pprint
    >>> 
    >>> mtree = MongoTree()
    >>> 
    >>> path = ['select', '*', 'from', 'foo']
    >>> mtree.upsert(path)
    >>> 
    >>> path = ['select', '*', 'from', 'bar']
    >>> mtree.upsert(path)
    >>> 
    >>> path = ['select', 'id', 'from', 'stuff']
    >>> mtree.upsert(path)
    >>> 
    >>> path = ['select', 'id', 'from', 'bar']
    >>> mtree.upsert(path)
    >>>
    >>> mtree.node_count()
    9
    >>> print mtree.path_exists(['select', 'id', 'from'])
    True
    >>>
    >>> node = mtree.get_node(['select', '*'])
    >>>
    >>> pprint(node)
    {u'_id': ObjectId('508d7ba3acbc3a620cce684c'),
     u'children': [ObjectId('508d7ba3acbc3a620cce684d')],
     u'hits': 2,
     u'identifier': u'mongotree',
     u'label': u'*',
     u'obj': None,
     u'parent': ObjectId('508d7ba3acbc3a620cce684b'),
     u'path': u'select|$|*'}
    >>> 
    >>> graph = mtree.get_dotgraph()
    >>> graph.write_png('/tmp/mongotree.png')
    True
    
![ScreenShot](https://raw.github.com/LyleScott/pyMongoTree/master/docs/mongotree.png)
)
    