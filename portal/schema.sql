DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS assignments CASCADE;
DROP TABLE IF EXISTS course_sessions CASCADE;

CREATE TABLE users (
    id bigserial PRIMARY KEY,
    email text UNIQUE NOT NULL,
    first_name text NOT NULL,
    last_name text NOT NULL,
    password text NOT NULL,
    role varchar(7) NOT NULL CHECK (role IN ('teacher', 'student'))
);

-- Teacher has courses
CREATE TABLE courses (
    course_id bigserial PRIMARY KEY,
    teacher text NOT NULL,
    email text NOT NULL,
    course_name text NOT NULL,
    description varchar(100) NOT NULL,
    credits smallint NOT NULL
);

-- Students prevented from making session python-side
-- When we get into the code, just check roles.-Danny
CREATE TABLE course_sessions (
    id bigserial PRIMARY KEY,
    first_name text NOT NULL,
    last_name text NOT NULL,
    student_id bigserial REFERENCES users(id),
    teacher text NOT NULL,
    email text NOT NULL UNIQUE,
    time text NOT NULL

);

-- TODO: add user_sessions.
