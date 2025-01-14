-- Tabelle: roles
CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL
);

-- Tabelle: users
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(128) NOT NULL,
    salt VARCHAR(32) NOT NULL,
    role_id INTEGER REFERENCES roles(id) ON DELETE SET NULL
);

-- Tabelle: qr_codes
CREATE TABLE IF NOT EXISTS qr_codes (
    id SERIAL PRIMARY KEY,
    data VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabelle: products
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(255),
    price FLOAT,
    qr_code_id INTEGER REFERENCES qr_codes(id) ON DELETE SET NULL
);

-- Tabelle: failed_classifications
CREATE TABLE IF NOT EXISTS failed_classifications (
    id SERIAL PRIMARY KEY,
    image_id VARCHAR(100) NOT NULL,
    reason VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabelle: metadata
CREATE TABLE IF NOT EXISTS metadata (
    id SERIAL PRIMARY KEY,
    key VARCHAR(50) UNIQUE NOT NULL,
    value VARCHAR(255) NOT NULL
);

-- Initialdaten für Rollen
INSERT INTO roles (role_name) VALUES ('Admin'), ('Mitarbeiter'), ('Kunde')
ON CONFLICT (role_name) DO NOTHING;
