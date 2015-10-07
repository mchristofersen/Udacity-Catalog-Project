import re
from xml.sax.saxutils import unescape
import psycopg2

import HTMLParser
h = HTMLParser.HTMLParser()

def connect():
    """Connect to the PostgreSQL database.
    Returns a database connection."""
    pg = psycopg2.connect(dbname = 'catalog_project',
                          user='site_user',
                          password='password',
                          host='catalog-project.csclhe4v5cyl.us-west-2.rds.amazonaws.com',
                          port='5432')
    c = pg.cursor()
    return pg, c


# Handles execution of a query in the database
# accepts two arguments: The query string (ie "SELECT * FROM ...)
#                       any variables necessary (as a tuple)
def execute_query(query, variables=()):
    """Handle connection to the database as well
    as execution of a query"""
    pg, c = connect()
    try:
        c.execute(query, variables)
    except psycopg2.IntegrityError:
        pg.rollback()
        pg.close()
        return False
    if re.match("(^INSERT|^UPDATE|^DELETE)", query, re.I) is not None:
        pg.commit()
        pg.close()
        return True
    else:
        fetch = c.fetchall()
        pg.close()
        return fetch


# returns a list of all subcategories of a given browse_node_id.
# defaults to root node, so will return all root categories.
def get_categories(category='ROOT'):
    categories = execute_query("""
    SELECT browse_node_name, browse_node_id
    FROM browse_nodes
    WHERE child_of = %s
    ORDER BY browse_node_name
    """, (category,))
    return categories


# accepts a leaf node's browse_node_id as an argument (string or int) and
# returns a list of all items within that leaf node.
def get_database_items(node):
    items = execute_query("""SELECT name, description, price, images, asin
                             FROM items
                             WHERE browse_node_id = %s""",
                          (str(node),))
    return [[x[0],unescape(x[1]),x[2],x[3],str(x[4])] for x in items]


# accepts a browse_node_id as an argument (string) and recursively searches
# for all encompassed leaf_nodes and returns all items from within
# said nodes.
def recursive_item_search(browse_node_id):
    try:
        node = execute_query("""SELECT browse_node_name, browse_node_id, leaf
                            FROM browse_nodes
                            WHERE browse_node_id = %s
    """, (browse_node_id,))[0]
    except IndexError:
        return None
    if node[2]==True:
        items = execute_query("""SELECT name,
                                        description,
                                         images,
                                          price,
                                           asin
                            FROM items
                            WHERE browse_node_id = %s
    """, (browse_node_id,))
        items_dict = [{'name' : x[0],
                       'description' : x[1],
                       'image_URLs' : x[2],
                       'price' : x[3],
                       'id' : x[4]}
                      for x in items]
        return {str(node[0])+" items" : items_dict}
    else:
        nodes = execute_query("""SELECT browse_node_id
                                FROM browse_nodes
                                WHERE child_of = %s
        """, (browse_node_id,))
        return {str(node[0]) : [recursive_item_search(x[0]) for x in nodes]}

