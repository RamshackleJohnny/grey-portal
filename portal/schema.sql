DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id bigserial PRIMARY KEY,
    email text UNIQUE NOT NULL,
    password text NOT NULL,
    role varchar(7) NOT NULL CHECK (role IN ('teacher', 'student'))
);

