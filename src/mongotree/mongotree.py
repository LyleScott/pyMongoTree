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

from lxml import etree

import pydot
import pymongo
from pprint import pformat


class MongoTree(object):
    """An implEementation of modeling MongoDB values as a Tree with nodes
    that have 1 parent and N children.""" 
    
    SEPARATOR = '|$|'
    
    def __init__(self, host='localhost', port=27017, db_name='mongotree',
                 uri=None, identifier='mongotree'):
        """Initialization routines.
        
        Args:
            host (string): Hostname that is serving the MongoDB instance.
            port (integer): The port to connect to host on.
            db_name (string): The database name on the MongoDB instance.
            uri (string): The connection URI for the mongodb instance.
            identifier (string): A member of the key for all reads/writes.
        """
        if uri:
            # NOTE: pymongo requires you to have the 'optional'
            # username:password in the URI. Arg!
            self.mongo = pymongo.Connection().from_url(uri=uri)
            self.db = self.mongo.db_name
        else:
            self.mongo = pymongo.Connection(host=host, port=port)
            self.db = self.mongo[db_name]
    
        self.identifier = identifier
        
    def __repr__(self):
        s = []
        for root in self.get_roots():
            s.extend(self.traverse(root))
        return pformat(s)
        
    def get_node(self, path):
        """Return a node at specific path.
        
        Args:
            path (sequence): A sequence of tokens representing a path to a node.
        
        Returns:
            A dict representing a node || None.
        """
        path = self.SEPARATOR.join(path)
        key = {'identifier': self.identifier, 'path': path}
        
        result = self.db.treefoo.find_one(key)
        
        if not result:
            raise ValueError('MongoTree::children:> the node at path %s was '
                             'not found' % path)
        
        return result
        
    def path_exists(self, path):
        """Check if a nodes exists at a specified path.
        
        Args:
            path (sequence): A sequence of tokens representing a path to a node.
          
        Returns:
            bool. 
        """
        path = self.SEPARATOR.join(path)
        key = {'identifier': self.identifier, 'path': path}
        return bool(self.db.treefoo.find_one(key))
        
    def get_dotgraph(self, roots=None):
        """Generate a dot graph of the tree at a root via Graphviz.
        
        Args:
            roots (sequence): Roots to start graphing from.
                Default: all roots.
        """
        
        if roots and not getattr(roots, '__iter__', False):
            raise ValueError('get_dotgraph: roots argument must be a sequence')

        def add_children_nodes(node):
            """Give a parent node, create the edges between parent and children.
            """
            for child in node['children']:
                child = self.db.treefoo.find_one({'_id': child})
                
                parentNode = pydot.Node(str(node['_id']), label=node['label'])
                graph.add_node(parentNode)
                
                childNode = pydot.Node(str(child['_id']), label=child['label'])
                graph.add_node(childNode)
                
                edge = pydot.Edge(str(node['_id']), str(child['_id']))
                graph.add_edge(edge)
        
        graph = pydot.Dot(graph_type='digraph')
        
        roots = roots or self.get_roots()
        for node in self.get_roots():
            self.traverse(node, function=add_children_nodes)
            
        #graph.write_png('example1_graph.png')
        
        return graph
        
    def traverse(self, node, function=None, nodes=None):
        """Traverse the tree, optionally running a function on each node.
        
        Args:
            node (dict): A dict representing a parent node that will have its
                children traversed (if there are any).
            function (function): A function to run on a node when it is
                traversed.
            nodes (list): Holds all nodes that have been recursively traversed.  
        
        Returns:
            list. A list of all nodes that were traversed.
        """
        if nodes is None:
            nodes = []
        nodes.append(node)
        
        if function:
            function(node)

        # Traverse each child.        
        for child in node['children']:
            child = self.db.treefoo.find_one({'_id': child})
            self.traverse(child, function=function, nodes=nodes)
            
        return nodes

    def get_node_count(self, roots=None):
        """Return how many nodes there are in the tree.
        
        Args (sequence): Optional. Instead of all roots, specify nodes to start
            the traversal from.
        
        Returns:
            int
        """
        n = 0
        roots = roots or self.get_roots()
        for root in roots:
            n += len(self.traverse(root))
            
        return n

    def get_roots(self):
        """Get the root nodes that contain the start of a tree.
        
        Returns:
            list. A list of nodes with no parents (the "Top" nodes).
        """
        key = {'identifier': self.identifier, 'parent': None}
        return [row for row in self.db.treefoo.find(key)]
        
    def upsert(self, path, obj=None, hit_inc=1):
        """Add a node to the tree.
        
        Args:
            path (sequence): A sequence containing tokens.
            obj (pickle): A pickled object stored as a blob on a node.
            hit_inc (int): Incremenet the nodes hit counter.
        """
        if not getattr(path, '__iter__', False):
            raise ValueError('upsert: path argument must be a sequence')
            
        current_path = ''
        parent_objid = None
        
        for token in path:
        
            if current_path:
                # Concatenate current_path with the incoming token.
                current_path = self.SEPARATOR.join((current_path, token))
            else:
                # Initialize current_path to the incoming token.
                current_path = token

            # Try to find the row for this node.
            key = {'identifier': self.identifier, 'path': current_path}
            
            # Values we want to store on the created/updated node.
            values = {}
            
            # Increment the hit counter.
            values.setdefault('$inc', {})['hits'] = hit_inc
            
            # Create a new row for the node if it doesn't exist.
            if not self.db.treefoo.find_one(key):
                values.setdefault('$set', {})['label'] = token
                values['$set']['parent'] = parent_objid
                values['$set']['children'] = []

            # Blob data associated with the node.
            if obj and current_path == self.SEPARATOR.join(path):
                values.setdefault('$set', {})['obj'] = obj
            
            # Write to the db/collection.
            self.db.treefoo.update(key, values, upsert=True)
        
            # Update the parent node to include this node as a child.
            if current_path:
                obj_id = self.db.treefoo.find_one(key, {'_id': 1})['_id']
                key = {'_id': parent_objid}    
                values = {'$addToSet': {'children': obj_id}}
                self.db.treefoo.update(key, values, upsert=True)
                parent_objid = obj_id
        
    '''
    def remove(self, path):
        """Remove a node from the tree."""
        key = {'identifier': self.identifier, 'path': path}
        self.db.treefoo.remove(key)
    
    def parent(self, path):
        """Get the parent of a node."""
        key = {'identifier': self.identifier, 'path': path}
        return self.db.treefoo.find_one(key)
        
    def siblings(self, path):
        """Get the siblings of a node."""
        key = {'identifier': self.identifier, 'parent': path}
        return self.db.treefoo.find(key)
    '''
                
    def children(self, node=None, path=None):
        """Get all children of a node.
        
        Args:
            node (dict):  A dict representing a node.
            path (string): The path to use to find a node with a specific
                path.
        
        Returns:
            list. All children of the node with path=parent_path.
        """
        if node is None and path is None:
            raise ValueError('MongoTree::children:> node or parent_path must '
                             'be specified as arguments.')
        else:
            if path and not hasattr(path, '__iter__'):
                raise ValueError('children: path argument must be a sequence')
                
        if node:
            return node['children']
        
        node = self.get_node(path)
               
        return node['children']
        
    def fromXml(self, xml):
        """Build a tree from an XML string.
        
        Args:
            xml (string): A string of valid XML.
        """
        root = etree.fromstring(xml)
        
        def add_nodes(root, path=None):
            """Get all parent/children node combinations and add to the
            tree collection.
            """
            if path is None:
                path = []
                
            nodes = path + [root,]
            self.upsert([node.tag for node in nodes])

            for child in root.getchildren():
                add_nodes(child, path=nodes)
                    
        add_nodes(root)
