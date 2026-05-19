import sqlite3

def check_database():
    try:
        conn = sqlite3.connect('voting_system.db')
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
        tables = cursor.fetchall()
        print('Tables:', [table[0] for table in tables])
        
        # Check admin table
        cursor.execute('SELECT * FROM admin')
        admin = cursor.fetchall()
        print('Admin records:', admin)
        
        # Check voters table
        cursor.execute('SELECT COUNT(*) FROM voters')
        voter_count = cursor.fetchone()[0]
        print('Voter count:', voter_count)
        
        # Check candidates table
        cursor.execute('SELECT COUNT(*) FROM candidates')
        candidate_count = cursor.fetchone()[0]
        print('Candidate count:', candidate_count)
        
        # Check election table
        cursor.execute('SELECT * FROM election')
        election = cursor.fetchone()
        print('Election status:', election)
        
        conn.close()
        print("Database check completed successfully!")
        
    except Exception as e:
        print(f"Database error: {e}")

if __name__ == '__main__':
    check_database()
