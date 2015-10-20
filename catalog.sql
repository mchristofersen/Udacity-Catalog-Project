
CREATE TABLE items
(
    name VARCHAR(1500),
    description VARCHAR,
    price VARCHAR(100),
    id SERIAL,
    images _TEXT,
    browse_node_id VARCHAR(30),
    posted_by VARCHAR(150),
    asin VARCHAR PRIMARY KEY NOT NULL,
    FOREIGN KEY (browse_node_id) REFERENCES browse_nodes (browse_node_id)
);
CREATE UNIQUE INDEX unique_name ON items (name);


-- ie categories
CREATE TABLE browse_nodes
(
    browse_node_name VARCHAR(200) NOT NULL,
    browse_node_id VARCHAR(100) PRIMARY KEY NOT NULL,
    child_of VARCHAR(100) NOT NULL,
    search_category VARCHAR NOT NULL,
    depth INT,
    leaf BOOL DEFAULT false NOT NULL
);

CREATE OR REPLACE FUNCTION get_subcategories(TEXT)
    RETURNS TABLE (name TEXT, id TEXT, leaf BOOL)
    AS $$
      SELECT browse_node_name, browse_node_id, leaf
      FROM browse_nodes
      WHERE browse_node_id = $1
    $$
    LANGUAGE SQL VOLATILE
;


