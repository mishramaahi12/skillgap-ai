from database import get_connection


connection = get_connection()
cursor = connection.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS assessment_events (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(100),
    task_id VARCHAR(100),
    event_type VARCHAR(50),
    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    time_taken INTEGER DEFAULT 0,
    runs INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0,
    hints_used INTEGER DEFAULT 0,

    test_cases_passed INTEGER DEFAULT 0,
    test_cases_total INTEGER DEFAULT 0
);
""")


connection.commit()

print("assessment_events table created successfully!")


cursor.close()
connection.close()