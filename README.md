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