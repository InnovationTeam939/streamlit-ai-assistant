import psycopg2
from psycopg2.extras import RealDictCursor
import logging
from contextlib import contextmanager
from dotenv import load_dotenv
import os

logger = logging.getLogger(__name__)
load_dotenv()

class DatabaseDriver:
    """Database driver for PostgreSQL connection."""
    
    def __init__(self):
        self.connection_string = os.getenv("DATABASE_URL")

    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context manager."""
        conn = None
        try:
            logger.info("Establishing database connection...")
            conn = psycopg2.connect(
                self.connection_string,
                cursor_factory=RealDictCursor,
                connect_timeout=30,
                sslmode='require'
            )
            logger.info("Database connection established successfully")
            yield conn
        except psycopg2.Error as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
                logger.info("Database connection closed")
    
    def test_connection(self):
        """Test database connection."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return True, "Connection successful"
        except Exception as e:
            return False, str(e)
    
    def get_table_info(self):
        """Get information about tables in the database."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = cursor.fetchall()
                return [table['table_name'] for table in tables]
        except Exception as e:
            logger.error(f"Error getting table info: {str(e)}")
            return []
    
    def get_column_info(self, table_name):
        """Get column information for a specific table."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = %s AND table_schema = 'public'
                    ORDER BY ordinal_position
                """, (table_name,))
                columns = cursor.fetchall()
                return columns
        except Exception as e:
            logger.error(f"Error getting column info: {str(e)}")
            return []