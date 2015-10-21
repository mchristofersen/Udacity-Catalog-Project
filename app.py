from flask import Flask
from flask import render_template
from flask import request
from flask import make_response
from flask import redirect
from flask import session
from database import execute_query
from database import get_categories
from database import get_database_items
from database import recursive_item_search
import sys
import random
import string
# oauth dependencies
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
from jinja2 import Environment, PackageLoader
import json
from flask.json import jsonify
import requests
from xml.sax.saxutils import unescape
import dicttoxml

# import and set Google client id
CLIENT_ID = {"web":{"client_id":"579744299893-4u2m4thipn6a2a2t12e4fv3nscc6l2dc.apps.googleusercontent.com","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://accounts.google.com/o/oauth2/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"5cZZxzcdN4OKdCk4EM08513y","redirect_uris":["http://mc-catalog.elasticbeanstalk.com"],"javascript_origins":["http://localhost:8000","http://mc-catalog.elasticbeanstalk.com"]}}['web']['client_id']

secrets = {"web":{"client_id":"579744299893-4u2m4thipn6a2a2t12e4fv3nscc6l2dc.apps.googleusercontent.com","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://accounts.google.com/o/oauth2/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"5cZZxzcdN4OKdCk4EM08513y","redirect_uris":["http://mc-catalog.elasticbeanstalk.com"],"javascript_origins":["http://localhost:8000","http://mc-catalog.elasticbeanstalk.com","http://52.27.150.183"]}}

env = Environment(loader=PackageLoader('app', 'templates'))

reload(sys)
sys.setdefaultencoding('utf8')

app = Flask(__name__)
app.config.from_object(__name__)


# create callback for google login
@app.route('/gconnect', methods=['POST'])
def gconnect():
    print >> sys.stderr, request.args.get('state'), session['state']
    if request.args.get('state') != session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    code = request.data
    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets(secrets,
                                             scope='')
        print 'nope'
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check that the access token is valid.
    access_token = credentials.access_token
    url = (
        'https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
        % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url,
                                  'GET')[1])
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
    # Verify that the access token is used for the intended user
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."
                       ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Check to see if user is already logged in
    stored_credentials = session.get('credentials')
    stored_gplus_id = session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'

    # Store the access token in the session for later use.
    session['credentials'] = credentials.access_token
    session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    session['username'] = data['name']
    session['picture'] = data['picture']
    session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += session['username']
    output += '!</h1>'
    output += '<img src="'
    output += session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:\
     150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    session.permanent = True
    return output


# Logout Google +
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = session.get('credentials')
    if credentials is None:
        response = make_response(json.dumps('Current user not connected.'),
                                 401)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/')
    # Execute HTTP GET request to revoke current token.
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del session['credentials']
        del session['gplus_id']
        del session['username']
        del session['email']
        del session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        session.clear()
        flash("Successfully logged out!")
        return redirect('/')
    else:
        # For whatever reason, the given token was invalid.
        session.clear()
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return redirect('/')


# controls creation of a new item in the database
# a get request routes to the new item form
# a post inserts the item into the database and redirects to the items
# category view page
@app.route('/items/new', methods=['GET', 'POST'])
def new_item():
    if 'username' not in session:
        return redirect('/login')
    if request.method == 'POST':
        data = request.form
        user_email = session.get('email')
        success = False
        while success is False:
            asin = ''.join(
                random.choice(string.ascii_uppercase + string.digits
                              ) for x in xrange(16))
            query = """INSERT INTO items (name,
                                          description,
                                           price,
                                            images,
                                             browse_node_id,
                                              posted_by,
                                               asin)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            variables = [data['name'],
                         data['description'],
                         data['price'],
                         data['images'].split(','),
                         data['browse_node_id'],
                         user_email, asin, ]
            success = execute_query(query, variables)
        return redirect('/search_category?category='+data['browse_node_id'])
    else:
        return render_template("items_form.html")


# the home page loads the root categories for the category tree
@app.route('/', methods=['GET'])
def home():
    categories = get_categories()
    print categories
    return render_template("home.html", categories=categories)


# generates a state variable to prevent forgery and routes to login page
@app.route('/login')
def show_login():
    try:
        redirection = session['redirect']
    except KeyError:
        redirection = '/'
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    session['state'] = state
    return render_template("login.html",
                           STATE=session['state'],
                           redirection='/items/new')


# an endpoint that returns the subcategories for a given parent category
@app.route('/category')
def category():
    try:
        category = request.args.get('category')
    except AttributeError:
        category = 'ROOT'
    list = execute_query("""SELECT * FROM get_subcategories(%s)
                            ORDER BY name""", (category,))
    return render_template("list.html", list=list)


# endpoint to get subcategories of parent category in json
@app.route('/form_categories')
def form_categories(category='ROOT'):
    if request.args.get('category') is not None:
        category = request.args.get('category')
    list = get_categories(category)
    return jsonify({'items': list})


# displays items for the selected category
@app.route('/search_category')
def search_category():
    email = session.get('email')
    category = request.args.get('category')
    session['redirect'] = '/search_category?category='+category
    list = get_database_items(category)
    next = []
    for item in list:
        next.append([item[0],
                     item[1],
                     item[2],
                     item[3],
                     len(item[3]),
                     item[4]+'myCarousel',
                     "#"+item[4]+'myCarousel',
                     item[4],
                     item[5]])
    return render_template('search_results.html', list=next, email=email)


# deletes an item from the database
@app.route('/delete_item', methods=["POST"])
def delete_item():
    asin = request.form.get('asin')
    if session.get('email') is None:
        return redirect('/login')
    query = execute_query("DELETE FROM items WHERE asin = %s", (asin,))
    if query:
        return jsonify({'response': 'True'})
    else:
        return jsonify({'response': 'False'})


# controls the routes for editing an item
# a get request routes to the edit item form
# a post edits the item and then redirects to the category view page
@app.route('/edit_item', methods=['GET', 'POST'])
def edit_item():
    if request.method == 'GET':
        asin = request.args.get('asin')
        name, description, images, price, browse_node_id = execute_query("""
        SELECT name, description, images, price, browse_node_id FROM items
        WHERE asin = %s
        """, (asin,))[0]
        item = {
            'name': name,
            'description': description,
            'images': ','.join(images),
            'price': price,
            'asin': asin,
            'browse_node_id': browse_node_id
        }
        return render_template('edit_item.html', item=item)
    elif request.method == 'POST':
        if session.get('email') is None:
            return redirect('/login')
        data = request.form
        images = "{"+data['images']+"}"
        query = execute_query("""UPDATE items SET
                                  (name, images, price, description)
                                  = (%s,%s,%s,%s)
                                  WHERE asin = %s""",
                              (data['name'],
                               images,
                               data['price'],
                               unescape(data['description']),
                               data['asin'],))
        return redirect('/search_category?category='+data['browse_node_id'])


# categories endpoint
@app.route('/api/categories')
def category_tree():
    category = request.args.get('category')
    if category is None:
        query = execute_query("""SELECT browse_node_name,
                                        browse_node_id,
                                         children_tree
                                FROM browse_nodes
                                WHERE child_of = 'ROOT'
                                ORDER BY browse_node_name
                                """)
    else:
        query = execute_query("""SELECT browse_node_name,
                                        browse_node_id,
                                         children_tree
                                FROM browse_nodes
                                WHERE browse_node_id = %s
                                ORDER BY browse_node_name
                                """, (category,))
    list = []
    for x in query:
        list.append({'name': x[0], 'id': x[1], 'tree': x[2]})
    return jsonify({'categories': list})


# leaf nodes endpoint
@app.route('/api/leaf_nodes')
def leaf_nodes():
    list = execute_query("""SELECT browse_node_name, browse_node_id
                            FROM browse_nodes
                            WHERE leaf = TRUE
    """)
    nodes_dict = [{'name': x[0], 'id': x[1]} for x in list]
    return jsonify({"leaf_nodes": nodes_dict})


# items endpoint
@app.route('/api/items')
def items_list():
    category = request.args.get('category')
    list = execute_query("""SELECT name, description, images, price, asin
                            FROM items
                            WHERE browse_node_id = %s
    """, (category,))
    items_dict = [{'name': x[0],
                   'description': x[1],
                   'image_URLs': x[2],
                   'price': x[3],
                   'id': x[4]}
                  for x in list]
    return jsonify({'items': items_dict})


# accepts a browse_node_id and recursively searches for all items
# encompassed by the given browse node
@app.route('/api/recursive_items')
def recursive_items_list():
    category = request.args.get('category')
    if category is None:
        return make_response("ERROR! Category must be present in query string")
    list = recursive_item_search(category)
    return jsonify({'nodes': list})


# a route that allows for easy database querying
@app.route('/admin', methods=['GET', 'POST'])
def database_query():
    if request.method == 'GET':
        return render_template("query.html")
    else:
        query = request.form.get('query')
        list = execute_query(query)
        return jsonify({'results': list})


# xml categories endpoint
@app.route('/xml/categories')
def xml_category_tree():
    category = request.args.get('category')
    if category is None:
        query = execute_query("""SELECT browse_node_name,
                                        browse_node_id,
                                         children_tree
                                FROM browse_nodes
                                WHERE child_of = 'ROOT'
                                ORDER BY browse_node_name
                                """)
    else:
        query = execute_query("""SELECT browse_node_name,
                                        browse_node_id,
                                         children_tree
                                FROM browse_nodes
                                WHERE browse_node_id = %s
                                ORDER BY browse_node_name
                                """, (category,))
    list = []
    for x in query:
        list.append({'name': x[0], 'id': x[1], 'tree': x[2]})
    return dicttoxml.dicttoxml({'categories': list})


# xml leaf nodes endpoint
@app.route('/xml/leaf_nodes')
def xml_leaf_nodes():
    list = execute_query("""SELECT browse_node_name, browse_node_id
                            FROM browse_nodes
                            WHERE leaf = TRUE
    """)
    nodes_dict = [{'name': x[0], 'id': x[1]} for x in list]
    return dicttoxml.dicttoxml({"leaf_nodes": nodes_dict})


# xml items endpoint
@app.route('/xml/items')
def xml_items_list():
    category = request.args.get('category')
    list = execute_query("""SELECT name, description, images, price, asin
                            FROM items
                            WHERE browse_node_id = %s
    """, (category,))
    items_dict = [{'name': x[0],
                   'description': x[1],
                   'image_URLs': x[2],
                   'price': x[3],
                   'id': x[4]}
                  for x in list]
    return dicttoxml.dicttoxml({'items': items_dict})


# accepts a browse_node_id and recursively searches for all items
# encompassed by the given browse node
# returns the results as xml
@app.route('/xml/recursive_items')
def xml_recursive_items_list():
    category = request.args.get('category')
    if category is None:
        return make_response("ERROR! Category must be present in query string")
    list = recursive_item_search(category)
    return dicttoxml.dicttoxml({'nodes': list})


app.secret_key = "\xc3\x8a\xee\xe9:\xb6v\x12c\x07\x10R\xc3\xe9U\xc9\
\x81\xd0&\x16\xce\xf8k\x99"


if __name__ == '__main__':
    app.run(debug=True)
