--Introduction--
This project is an item catalog made for Udacity's full-stack web developer
program. Its focus is in implementing C.R.U.D. operations (create, read,
update, and delete), as well as using third-party OAuth (google+). Once
a user is logged in they can post new items, as well as edit or delete them.
Items can be viewed regardless of login status.

--Requirements--
Modules required to run the project locally are as follows:
dicttoxml==1.6.6
Flask==0.10.1
httplib2==0.9.1
itsdangerous==0.24
Jinja2==2.8
lxml==3.4.4
MarkupSafe==0.23
oauth2client==1.5.1
oauthlib==1.0.3
psycopg2==2.6.1
pyasn1==0.1.8
pyasn1-modules==0.0.7
python-amazon-product-api==0.2.8
requests==2.7.0
rsa==3.2
six==1.9.0
Werkzeug==0.10.4
wheel==0.24.0

Install them all with one command (navigate to project directory first):
pip install -r requirements.txt

--Installation--
To install the project, navigate to https://github.com/mchristofersen/Udacity-Catalog-Project and select "clone to desktop".
If you have git command line tools installed:
** navigate to the directory you want to install the project in **
git clone https://github.com/mchristofersen/Udacity-Catalog-Project.git

Alternatively, you can download the ZIP file and unzip the project into the directory of your choosing.

--Set Up--
The project uses a cloud-hosted database to store categories and items. The project comes preconfigured to use this database. However, if you would like to create and use a new database, instructions are as follows.
1. Install PostgreSQL if you haven't already. (http://www.postgresql.org/download/)
2. In the terminal, navigate to the project directory.
3. Create the database:
    psql createdb catalog_project
4. You should now be logged in to the database,
    next create the necessary tables and functions:
    \i catalog.sql
5. In "database.py", edit the configuration to use your PostgreSQL login info:
    (line 12) username = <your username (likely postgres by default)>
    (line 13) password = <your username password>
    (line 14) host = 'localhost'
    if you designated a port other than 5432, you should edit line 15 accordingly as well.
6. Your database should now be properly configured and you can move on to running the program.

--Running--
From within the project's directory running:
python application.py
will deploy the project to port 8000. View it in your web browser at:
http://localhost:8000
Different ports can be specified by changing line 392 in "application.py"

--Usage--
If you are using the default database, various categories and items are already provided. However, if you created your own database, you will need to create your own categories first. The browse_nodes table is defined as such:
    (
        browse_node_name VARCHAR(200) NOT NULL,
        browse_node_id VARCHAR(100) PRIMARY KEY NOT NULL,
        child_of VARCHAR(100) NOT NULL,
        search_category VARCHAR NOT NULL,
        depth INT,
        leaf BOOL DEFAULT false NOT NULL
    )
 A new root category can be created within psql as such:
 INSERT INTO browse_nodes VALUES ('New Category',
                                   '5555555', -- Only digits 0-9 allowed
                                   'ROOT',
                                   'New Category', -- will typically be the same as name if a root node
                                   0, -- A root node has a depth of 0
                                   FALSE) -- TRUE if you want items to be accessible from this node

 You can then create subcategories of this category by using it's browse_node_id
 in the "child_of" field:
 INSERT INTO browse_nodes VALUES ('New Subcategory',
                                   '55555551',
                                   '5555555',
                                   'New Category',
                                   1, -- now at depth 1
                                   TRUE); -- FALSE if you want the category tree to extend further

 You can now use the site interface to create items under the new leaf node.



