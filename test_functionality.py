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
        response = test_client.post('/authenticate', data={
            'user_type': 'admin',
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        print(f"Admin login status: {response.status_code}")
        
        # Test voter OTP generation
        print("\nTesting voter OTP generation...")
        response = test_client.post('/authenticate', data={
            'user_type': 'voter',
            'voter_id': 'VOT001'
        }, follow_redirects=True)
        print(f"Voter OTP generation status: {response.status_code}")
        
        # Test candidate registration
        print("\nTesting candidate registration...")
        response = test_client.post('/candidate_register_submit', data={
            'candidate_id': 'TEST001',
            'name': 'Test Candidate',
            'party': 'TEST',
            'password': 'test123'
        }, follow_redirects=True)
        print(f"Candidate registration status: {response.status_code}")
        
        # Test results API
        print("\nTesting results API...")
        with test_client.session_transaction() as sess:
            sess['user_type'] = 'admin'
        
        response = test_client.get('/api/results')
        print(f"Results API status: {response.status_code}")
        
        print("\nFunctionality tests completed!")
        
    except Exception as e:
        print(f"Functionality test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_voting_functionality()
