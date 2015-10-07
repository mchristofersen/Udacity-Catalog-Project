This application is an item catalog with numerous item categories. Categories
are defined in the database as browse nodes and have a name and id. To get a
list of the category hierarchy visit:

http://localhost:8000/api/categories

The hierarchy for any given browse node can be obtained by supplying the
browse_node_id as the category in a the query string like:

http://localhost:8000/api/categories?category=172282


Items are only posted under browse nodes defined as "leaf" nodes (ie the node
has no children nodes). A list of these nodes can be seen at:

http://localhost:8000/api/leaf_nodes

You can view items under a given leaf node like so:

http://localhost:8000/api/items?category=1036920

You can recursively search for all items under a given browse node like so:

http://localhost:8000/api/recursive_items?category=11119

*** Due to the amount of categories and items in the database, this is slow and
    not recommended***

A URL is available for direct query of the database. It can be accessed via:

http://localhost:8000/admin