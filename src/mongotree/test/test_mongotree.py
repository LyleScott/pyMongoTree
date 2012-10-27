import mongotree
import unittest


class MongoTreeTest(unittest.TestCase):
    """TODO"""
    
    def setUp(self):
        """Initialization."""
        self.xml = """<?xml version="1.0" encoding="UTF-8"?>
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

    def test___init__(self):
        """Test initialization."""
        self.tree = mongotree.MongoTree()
        assert self.tree
        assert isinstance(self.tree, mongotree.MongoTree)
        
    def test_fromXml(self):
        """Test that a MongoTree can be properly formed with raw XML."""
        self.tree = mongotree.MongoTree()
        self.tree.fromXml(self.xml)
        print self.tree
        assert 1 == 2
        
    '''
    def test_add(self):
        """Test adding a node."""
        self.tree.add()
        
    def test_remove(self):
        """Test removing a node."""
        pass
    '''