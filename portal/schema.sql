DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS courses CASCADE;
DROP TABLE IF EXISTS assignments CASCADE;
DROP TABLE IF EXISTS course_sessions CASCADE;
DROP TABLE IF EXISTS user_sessions CASCADE;

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
    course_number text NOT NULL,
    course_name text NOT NULL,
    description text NOT NULL,
    teacher_id bigserial NOT NULL REFERENCES users(id)
);

-- Students prevented from making session python-side
-- When we get into the code, just check roles.-Danny
CREATE TABLE course_sessions (
    id bigserial PRIMARY KEY,
    number varchar(4),
    course_id bigint REFERENCES courses(course_id) NOT NULL,
    time text NOT NULL,
    number_students int NOT NULL
);


CREATE TABLE user_sessions (
    student_id smallint REFERENCES users(id),
    session_id smallint REFERENCES course_sessions(id)
);

-- Grades handled python side --
-- Type of assignment? --
CREATE TABLE assignments (
    assignment_id bigserial UNIQUE PRIMARY KEY,
    points_available int NOT NULL,
    points_earned int NOT NULL,
    -- due_date TIMESTAMP,
    completed BOOLEAN
    student_id  bigserial PRIMARY KEY,
    course_name TEXT NOT NULL,
    FOREIGN KEY course_name REFERENCES sessions(session_id),
    FOREIGN KEY student_id REFERENCES users(id)
);

INSERT INTO users(email, password, role, first_name, last_name) VALUES ('dev@dev.com', 'qwerty', 'teacher', 'John', 'Cena'),('student@student.com', 'student12345', 'student', 'Morty', 'Smith')
