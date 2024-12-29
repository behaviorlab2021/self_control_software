CREATE TABLE weights (
    weight_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),          -- Primary key
    subject_id INTEGER NOT NULL REFERENCES subjects(subject_id),    -- Foreign key to subjects table
    weighted_at TIMESTAMP DEFAULT NOW(),                            -- Record creation timestamp
    subject_weight INTEGER NOT NULL,                                -- Weight of the subject
);