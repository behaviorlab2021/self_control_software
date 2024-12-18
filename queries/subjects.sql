CREATE TABLE subjects (
    subject_id SERIAL PRIMARY KEY,
    subject_name VARCHAR(255) NOT NULL
);

INSERT INTO subjects (subject_name)
VALUES 
    ('Adam'),
    ('Moses'),
    ('Snik'),
    ('Ermis');

SELECT * FROM subjects;
