from lxml import etree
import pymongo


class MongoTree(object):
    
    SEPARATOR = '|$|'
    
    def __init__(self):
        """Initialization"""
        self.db = pymongo.Connection().treefoo
        
    def __str__(self):
        s = []
        for root in self.get_roots():
            ss = 'path=%s parent=%s' % (root['path'], root['parent'])
            s.append(ss)
        return '\n'.join(s)
        
    def transverse_bredth(self, root, function=None):
        """Transverse the tree in bredth first order."""
        if not callable(function):
            raise ValueError('MongoTree::transverse_bredth:> '
                             'function needs to be callable.')
        
    
    
    def get_roots(self):
        """Get the root nodes that contain the start of a tree."""
        key = {'identifier': 'lyle', 'parent': ''}
        return (row for row in self.db.treefoo.find(key))
        
    def add(self, path, obj=None, remove_existing_children=False):
        """Add a node to the tree."""
        path_tokens = path.split(self.SEPARATOR)
        
        current_path = ''
        for token in path_tokens:
            parent_path = current_path
            if current_path:
                current_path = self.SEPARATOR.join((current_path, token))
            else:
                current_path = token

            # What to find.
            key = {'identifier': 'lyle', 'path': current_path}
            
            if not self.db.treefoo.find_one(key):
                # The row wasn't found so create a new node.
                
                data = {'$set': {'name': token}}
                self.db.treefoo.update(key, data, upsert=True)
                
                data = {'$set': {'parent': parent_path}}
                self.db.treefoo.update(key, data, upsert=True)
            
            data = {'$inc': {'hits': 1}}
            self.db.treefoo.update(key, data, upsert=True)
            
            
            
            
            data = {'$set': {'parent': parent_path}}
            self.db.treefoo.update(key, data, upsert=True)
        
            
            
            
            
            if obj:
                data = {'$set': {'obj': obj}}
                self.db.treefoo.update(key, data, upsert=True)
        
    def remove(self, path):
        """Remove a node from the tree."""
        key = {'identifier': 'lyle', 'path': path}
        self.db.treefoo.remove(key)
        
    def children(self, path):
        """Get all children of a node."""
        key = {'identifier': 'lyle', 'parent': path}
        return self.db.treefoo.find(key)
    
    def parent(self, path):
        """Get the parent of a node."""
        key = {'identifier': 'lyle', 'path': path}
        return self.db.treefoo.find_one(key)
        
    def siblings(self, path):
        """Get the siblings of a node."""
        key = {'identifier': 'lyle', 'parent': path}
        return self.db.treefoo.find(key)
    
    def generate_path(self, elements):
        """TODO"""
        path = [child.tag for child in elements if len(child)]
        return self.SEPARATOR.join(path)
        
    def fromXml(self, xml):
        """Build a tree from an XML string."""
        root = etree.fromstring(xml)
        
        def add_nodes(root, path=None):
            """Get all parent/children node combinations and add to the
            tree collection.
            """
            if path is None:
                path = []
                
            p = path + [root,]
            self.add(self.SEPARATOR.join([p_.tag for p_ in p]))

            for child in root.getchildren():
                add_nodes(child, path=p)
                    
        add_nodes(root)


if __name__ == '__main__':
    query = "select * from foo bar = 'derp'"
    identifier = 'lyle'
    tree = MongoTree()
    tree.fromXml(open('test1.xml', 'r').read())
    print 'done'
    #root = tree.add(tree.query)
    

