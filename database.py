import mysql.connector
from mysql.connector import Error


class DatabaseManager:
    DATABASE_CONFIG = {
        "host": "localhost",
        "user": "root",
        "password": "supy@2026$",
        "database": "internshiptracker",
    }

    def __init__(self):
        self.config = self.DATABASE_CONFIG.copy()
        self.startup_error = None
        try:
            self.ensure_core_tables()
        except RuntimeError as error:
            self.startup_error = str(error)

    def _connect(self):
        return mysql.connector.connect(**self.config)

    def ensure_core_tables(self):
        queries = (
            """CREATE TABLE IF NOT EXISTS companies (
                company_id INT AUTO_INCREMENT PRIMARY KEY,
                company_name VARCHAR(100) NOT NULL,
                industry VARCHAR(50),
                website VARCHAR(100),
                hr_contact_email VARCHAR(50)
            )""",
            """CREATE TABLE IF NOT EXISTS applications (
                application_id INT AUTO_INCREMENT PRIMARY KEY,
                company_id INT,
                role_title VARCHAR(100),
                applied_date DATE,
                status VARCHAR(30) DEFAULT 'Applied',
                stipend DECIMAL(10, 2),
                mode VARCHAR(20),
                resume_version VARCHAR(50),
                notes VARCHAR(255)
            )""",
            """CREATE TABLE IF NOT EXISTS interviews (
                interview_id INT AUTO_INCREMENT PRIMARY KEY,
                application_id INT,
                round_number INT,
                interview_date DATE,
                interview_type VARCHAR(50),
                result VARCHAR(30),
                feedback VARCHAR(255)
            )""",
            """CREATE TABLE IF NOT EXISTS contacts (
                contact_id INT AUTO_INCREMENT PRIMARY KEY,
                company_id INT,
                contact_name VARCHAR(100),
                designation VARCHAR(100),
                linkedin_url VARCHAR(255),
                phone VARCHAR(30),
                email VARCHAR(150),
                relationship VARCHAR(100)
            )""",
            """CREATE TABLE IF NOT EXISTS company_research (
                research_id INT AUTO_INCREMENT PRIMARY KEY,
                company_id INT,
                glassdoor_rating DECIMAL(3, 1),
                avg_interview_difficulty VARCHAR(50),
                common_questions VARCHAR(255),
                culture_notes VARCHAR(255),
                source VARCHAR(255)
            )""",
            """CREATE TABLE IF NOT EXISTS documents (
                document_id INT AUTO_INCREMENT PRIMARY KEY,
                application_id INT,
                doc_type VARCHAR(50),
                version_name VARCHAR(100),
                file_path VARCHAR(255),
                upload_date DATE
            )""",
            """CREATE TABLE IF NOT EXISTS goals (
                goal_id INT AUTO_INCREMENT PRIMARY KEY,
                goal_period VARCHAR(50),
                target_applications INT,
                actual_applications INT,
                target_interviews INT,
                actual_interviews INT,
                notes VARCHAR(255)
            )""",
            """CREATE TABLE IF NOT EXISTS offers_comparison (
                offer_id INT AUTO_INCREMENT PRIMARY KEY,
                application_id INT,
                stipend_offered DECIMAL(10, 2),
                joining_date DATE,
                location VARCHAR(100),
                work_hours VARCHAR(50),
                perks VARCHAR(255),
                overall_rating INT,
                final_decision VARCHAR(30)
            )""",
            """CREATE TABLE IF NOT EXISTS preparation_tasks (
                task_id INT AUTO_INCREMENT PRIMARY KEY,
                application_id INT,
                task_name VARCHAR(150),
                due_date DATE,
                is_completed TINYINT
            )""",
            """CREATE TABLE IF NOT EXISTS reminders (
                reminder_id INT AUTO_INCREMENT PRIMARY KEY,
                application_id INT,
                reminder_type VARCHAR(50),
                reminder_date DATE,
                message VARCHAR(255),
                is_sent TINYINT
            )""",
            """CREATE TABLE IF NOT EXISTS skills_required (
                skill_id INT AUTO_INCREMENT PRIMARY KEY,
                application_id INT,
                skill_name VARCHAR(100),
                proficiency_needed VARCHAR(50),
                self_rating INT
            )""",
            """CREATE TABLE IF NOT EXISTS status_history (
                history_id INT AUTO_INCREMENT PRIMARY KEY,
                application_id INT,
                old_status VARCHAR(30),
                new_status VARCHAR(30),
                changed_on DATE
            )""",
        )
        connection = None
        cursor = None
        try:
            connection = self._connect()
            cursor = connection.cursor()
            for query in queries:
                cursor.execute(query)
            connection.commit()
        except Error as error:
            if connection:
                connection.rollback()
            raise RuntimeError("Unable to prepare core tables: " + str(error)) from error
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def execute(self, query, values=(), fetch=False, many=False):
        connection = None
        cursor = None
        try:
            connection = self._connect()
            cursor = connection.cursor()
            if many:
                cursor.executemany(query, values)
            else:
                cursor.execute(query, values)
            result = cursor.fetchall() if fetch else cursor.lastrowid
            connection.commit()
            return result
        except Error as error:
            if connection:
                connection.rollback()
            raise RuntimeError("Database error: " + str(error)) from error
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def fetch_one(self, query, values=()):
        rows = self.execute(query, values, fetch=True)
        return rows[0] if rows else None


db = DatabaseManager()