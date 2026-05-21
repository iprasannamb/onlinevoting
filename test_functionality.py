import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import app
from flask import Flask

def test_voting_functionality():
    try:
        test_client = app.app.test_client()
        
        # Test admin login
        print("Testing admin login...")
        response = test_client.post('/api/login', json={
            'user_type': 'admin',
            'username': 'admin',
            'password': 'admin123'
        })
        print(f"Admin API login status: {response.status_code}, data: {response.get_data(as_text=True)}")
        
        # Test voter login
        print("\nTesting voter API login...")
        response = test_client.post('/api/login', json={
            'user_type': 'voter',
            'voter_id': 'RSB1000001',
            'full_name': 'Ramesh Rao'
        })
        print(f"Voter API login status: {response.status_code}, data: {response.get_data(as_text=True)}")
        
        # Test voter registration API
        print("\nTesting voter registration API...")
        response = test_client.post('/api/register_voter', json={
            'voter_id': 'RSB2000001',
            'name': 'Suresh Kumar',
            'age': 25,
            'gender': 'Male',
            'constituency_id': 1,
            'mobile': '9988776655'
        })
        print(f"Voter registration status: {response.status_code}, data: {response.get_data(as_text=True)}")
        
        # Test public results API
        print("\nTesting public results API...")
        response = test_client.get('/api/public_results')
        print(f"Public results status: {response.status_code}")
        
    except Exception as e:
        print(f"Functionality test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_voting_functionality()
