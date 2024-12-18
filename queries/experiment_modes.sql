CREATE TABLE experiment_modes (
    mode_id SERIAL PRIMARY KEY,
    mode_name VARCHAR(255) NOT NULL UNIQUE
);

INSERT INTO experiment_modes (mode_name) VALUES
('NORMAL MODE'),
('RANDOM WARNING'),
('WARNING TRAINING'),
('BASIC TRAINING');

SELECT * FROM experiment_modes;
