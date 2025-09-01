-- Sample schema for survey data in Alloy DB
-- Adjust this based on your actual survey data structure

CREATE TABLE IF NOT EXISTS surveys (
    survey_id SERIAL PRIMARY KEY,
    respondent_id VARCHAR(255) NOT NULL,
    survey_date DATE NOT NULL,
    location VARCHAR(500),
    respondent_type VARCHAR(100),
    questions_responses JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_surveys_date ON surveys(survey_date);
CREATE INDEX IF NOT EXISTS idx_surveys_location ON surveys(location);
CREATE INDEX IF NOT EXISTS idx_surveys_respondent_type ON surveys(respondent_type);
CREATE INDEX IF NOT EXISTS idx_surveys_questions_gin ON surveys USING GIN(questions_responses);

-- Sample data (remove this in production)
INSERT INTO surveys (respondent_id, survey_date, location, respondent_type, questions_responses, metadata) VALUES 
(
    'RESP001',
    '2024-01-15',
    'New York, NY',
    'urban_resident',
    '{
        "questions": [
            {"id": 1, "question": "How satisfied are you with local public transport?", "response": "Very satisfied"},
            {"id": 2, "question": "Rate the cleanliness of your neighborhood (1-10)", "response": "8"},
            {"id": 3, "question": "What is your primary mode of transportation?", "response": "Public transit"}
        ]
    }',
    '{"survey_version": "1.0", "device": "mobile", "duration_minutes": 12}'
),
(
    'RESP002',
    '2024-01-16',
    'Los Angeles, CA',
    'suburban_resident',
    '{
        "questions": [
            {"id": 1, "question": "How satisfied are you with local public transport?", "response": "Somewhat dissatisfied"},
            {"id": 2, "question": "Rate the cleanliness of your neighborhood (1-10)", "response": "6"},
            {"id": 3, "question": "What is your primary mode of transportation?", "response": "Personal vehicle"}
        ]
    }',
    '{"survey_version": "1.0", "device": "desktop", "duration_minutes": 8}'
),
(
    'RESP003',
    '2024-01-17',
    'Chicago, IL',
    'urban_resident',
    '{
        "questions": [
            {"id": 1, "question": "How satisfied are you with local public transport?", "response": "Neutral"},
            {"id": 2, "question": "Rate the cleanliness of your neighborhood (1-10)", "response": "7"},
            {"id": 3, "question": "What is your primary mode of transportation?", "response": "Mixed (public transit and walking)"}
        ]
    }',
    '{"survey_version": "1.0", "device": "tablet", "duration_minutes": 15}'
);
