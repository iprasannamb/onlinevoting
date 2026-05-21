import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import app
from flask import Flask

def test_app():
    try:
        # Test Flask app creation
        print("Testing Flask app...")
        test_client = app.app.test_client()
        
        # Test main API routes
        routes = [
            '/api/session',
            '/api/assemblies',
            '/api/public_results'
        ]
        
        for route in routes:
            try:
                response = test_client.get(route)
                print(f"Route {route}: {response.status_code}")
            except Exception as e:
                print(f"Error on route {route}: {e}")
        
        # Test database connection
        print("\nTesting database connection...")
        conn = app.get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM voters')
        count = cursor.fetchone()[0]
        print(f"Database connection OK, voter count: {count}")
        conn.close()
        
        # Test blockchain
        print("\nTesting blockchain...")
        blockchain = app.blockchain
        print(f"Blockchain initialized with {len(blockchain.chain)} blocks")
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_app()
