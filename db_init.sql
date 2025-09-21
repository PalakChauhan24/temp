-- Create database schema (run this after creating database `nextstop`)


CREATE TABLE IF NOT EXISTS users (
id serial PRIMARY KEY,
username varchar(150) UNIQUE NOT NULL,
password_hash text NOT NULL,
created_at timestamptz DEFAULT now()
);


-- Optional: table for bus devices (if you plan to store static info)
CREATE TABLE IF NOT EXISTS buses (
id serial PRIMARY KEY,
route_name varchar(200),
last_lat numeric,
last_lng numeric,
updated_at timestamptz DEFAULT now()
);