"""
Database Setup Script for Karnataka Assembly Election System
This script initializes the database with Karnataka constituencies and sample data
"""

import sqlite3
import hashlib
import random

def setup_database():
    """Setup database with Karnataka constituencies and sample data"""
    # Import app to initialize database schema and ensure tables exist
    import app
    app.init_db()
    
    conn = sqlite3.connect('voting_system.db')
    cursor = conn.cursor()
    
    # Drop existing tables to force fresh schema creation on re-seed
    cursor.execute('DROP TABLE IF EXISTS votes')
    cursor.execute('DROP TABLE IF EXISTS results')
    cursor.execute('DROP TABLE IF EXISTS voters')
    cursor.execute('DROP TABLE IF EXISTS candidates')
    cursor.execute('DROP TABLE IF EXISTS government')
    cursor.execute('DROP TABLE IF EXISTS election')
    cursor.execute('DROP TABLE IF EXISTS assemblies')
    cursor.execute('DROP TABLE IF EXISTS admin')
    cursor.execute('DROP TABLE IF EXISTS blockchain')
    conn.commit()
    conn.close()
    
    # Re-create tables with current application schema
    app.init_db()
    conn = sqlite3.connect('voting_system.db')
    cursor = conn.cursor()
    
    # Insert Karnataka assemblies (224 constituencies from provided list)
    constituency_names = [
        'Nippani','Chikkodi-Sadalga','Athani','Kagwad','Kudachi','Raybag','Hukkeri','Arabhavi','Gokak','Yemkanmardi',
        'Belagavi Uttar','Belagavi Dakshin','Belagavi Rural','Khanapur','Kittur','Bailhongal','Saundatti Yellamma','Ramdurg',
        'Mudhol','Terdal','Jamkhandi','Bilgi','Badami','Bagalkot','Hungund','Muddebihal','Devar Hippargi','Basavana Bagewadi',
        'Babaleshwar','Bijapur City','Nagthan','Indi','Sindgi','Afzalpur','Jewargi','Shorapur','Shahapur','Yadgir','Gurmitkal',
        'Chittapur','Sedam','Chincholi','Gulbarga Rural','Gulbarga Dakshin','Gulbarga Uttar','Aland','Basavakalyan','Homnabad',
        'Bidar South','Bidar','Bhalki','Aurad','Raichur Rural','Raichur','Manvi','Devadurga','Lingsugur','Sindhanur','Maski',
        'Kushtagi','Kanakagiri','Gangawati','Yelburga','Koppal','Shirahatti','Gadag','Ron','Nargund','Navalgund','Kundgol',
        'Dharwad','Hubli-Dharwad East','Hubli-Dharwad Central','Hubli-Dharwad West','Kalghatgi','Haliyal','Karwar','Kumta',
        'Bhatkal','Sirsi','Yellapur','Hangal','Shiggaon','Haveri','Byadgi','Hirekerur','Ranebennur','Hadagalli','Hagaribommanahalli',
        'Vijayanagara','Kampli','Siruguppa','Bellary','Bellary City','Sandur','Kudligi','Molakalmuru','Challakere','Chitradurga',
        'Hiriyur','Hosadurga','Holalkere','Jagalur','Harapanahalli','Harihar','Davanagere North','Davanagere South','Mayakonda',
        'Channagiri','Honnali','Shimoga Rural','Bhadravati','Shimoga','Tirthahalli','Shikaripura','Sorab','Sagar','Byndoor',
        'Kundapura','Udupi','Kapu','Karkal','Sringeri','Mudigere','Chikmagalur','Tarikere','Kadur','Chiknayakanhalli','Tiptur',
        'Turuvekere','Kunigal','Tumkur City','Tumkur Rural','Koratagere','Gubbi','Sira','Pavagada','Madhugiri','Gauribidanur','Bagepalli',
        'Chikkaballapur','Sidlaghatta','Chintamani','Srinivaspur','Mulbagal','Kolar Gold Field','Bangarapet','Kolar','Malur','Yelahanka',
        'K.R. Pura','Byatarayanapura','Yeshwanthapura','Rajarajeshwarinagar','Dasarahalli','Mahalakshmi Layout','Malleshwaram','Hebbal',
        'Pulakeshinagar','Sarvagnanagar','C.V. Raman Nagar','Shivajinagar','Shanti Nagar','Gandhi Nagar','Rajaji Nagar','Govindraj Nagar',
        'Vijay Nagar','Chamrajpet','Chickpet','Basavanagudi','Padmanabhanagar','B.T.M Layout','Jayanagar','Mahadevapura','Bommanahalli',
        'Bangalore South','Anekal','Hosakote','Devanahalli','Doddaballapur','Nelamangala','Magadi','Ramanagaram','Kanakapura','Channapatna',
        'Malavalli','Maddur','Melukote','Mandya','Srirangapatna','Nagamangala','Krishnarajpet','Shravanabelagola','Arsikere','Belur','Hassan',
        'Holenarasipur','Arkalgud','Sakleshpur','Belthangady','Moodabidri','Mangalore City North','Mangalore City South','Mangalore','Bantval',
        'Puttur','Sullia','Madikeri','Virajpet','Piriyapatna','Krishnarajanagara','Hunsur','Heggadadevankote','Nanjangud','Chamundeshwari',
        'Krishnaraja','Chamaraja','Narasimharaja','Varuna','T. Narasipur','Hanur','Kollegal','Chamarajanagar','Gundlupet'
    ]

    cursor.executemany('INSERT INTO assemblies (name, district, state, total_voters) VALUES (?, ?, ?, ?)', 
                       [(name, name, 'Karnataka', 75000) for name in constituency_names])
    
    # Insert admin user if not already created by app.init_db()
    cursor.execute('INSERT OR IGNORE INTO admin (username, password) VALUES (?, ?)',
                  ('admin', hashlib.sha256('admin123'.encode()).hexdigest()))
    
    # Insert sample demo voters with new RSB ID format
    sample_voters = [
        ('RSB1000001', 'Ramesh Rao', 34, 'Male', 176, '9876543210', 0, 1, 'Approved'),
        ('RSB1000002', 'Anitha Shetty', 29, 'Female', 120, '9876501234', 0, 1, 'Approved'),
        ('RSB1000003', 'Nikhil Kumar', 27, 'Male', 1, '9876509876', 0, 1, 'Approved'),
        ('RSB1000004', 'Priya Nair', 31, 'Female', 9, '9876512345', 0, 1, 'Approved')
    ]
    
    cursor.executemany('INSERT INTO voters (voter_id, full_name, age, gender, assembly_id, mobile, has_voted, verified_status, approval_status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', 
                       sample_voters)
    
    # Insert sample candidates with assembly assignment
    sample_candidates = [
        # Assembly 1 candidates
        (1, 'Narendra Modi', 'BJP', 1, '🌸', 1),
        (2, 'Rahul Gandhi', 'INC', 1, '🖐️', 1),
        (3, 'Arvind Kejriwal', 'AAP', 1, '🔥', 1),

        # Assembly 6 candidates
        (4, 'Amit Shah', 'BJP', 6, '🌸', 1),
        (5, 'Sonia Gandhi', 'INC', 6, '🖐️', 1),
        (6, 'Manish Sisodia', 'AAP', 6, '🔥', 1),

        # Assembly 7 candidates
        (7, 'Nitin Gadkari', 'BJP', 7, '🌸', 1),
        (8, 'Priyanka Gandhi', 'INC', 7, '🖐️', 1),
        (9, 'Raghav Chadha', 'AAP', 7, '🔥', 1),

        # Assembly 8 candidates
        (10, 'Jagat Prakash Nadda', 'BJP', 8, '🌸', 1),
        (11, 'Mallikarjun Kharge', 'INC', 8, '🖐️', 1),
        (12, 'Atishi Marlena', 'AAP', 8, '🔥', 1),

        # Assembly 9 candidates
        (13, 'Smriti Irani', 'BJP', 9, '🌸', 1),
        (14, 'Adhir Ranjan Chowdhury', 'INC', 9, '🖐️', 1),
        (15, 'Sanjay Singh', 'AAP', 9, '🔥', 1),

        # Additional assembly coverage for demo
        (16, 'Piyush Goyal', 'BJP', 10, '🌸', 1),
        (17, 'Suresh Prabhu', 'INC', 10, '🖐️', 1),
        (18, 'Shazia Ilmi', 'AAP', 10, '🔥', 1),
        (19, 'Dushyant Chautala', 'BJP', 11, '🌸', 1),
        (20, 'Mallikarjun Kharge', 'INC', 11, '🖐️', 1),
        (21, 'Raghuvinder Singh', 'AAP', 11, '🔥', 1),
        (22, 'Rajnath Singh', 'BJP', 12, '🌸', 1),
        (23, 'Deepender Hooda', 'INC', 12, '🖐️', 1),
        (24, 'Ritu Khanduri', 'AAP', 12, '🔥', 1)
    ]
    
    cursor.executemany('INSERT INTO candidates (candidate_serial_no, candidate_name, party_name, assembly_id, symbol, verified_by_eci) VALUES (?, ?, ?, ?, ?, ?)', 
                       sample_candidates)
    
    # Insert election status if not already created by app.init_db()
    cursor.execute('INSERT OR IGNORE INTO election (election_type, status, result_declared, total_assemblies) VALUES (?, ?, ?, ?)',
                  ('Karnataka Assembly Election', 'not_started', 0, 224))
    
    # Insert government record if not already created by app.init_db()
    cursor.execute('INSERT OR IGNORE INTO government (election_type) VALUES (?)', ('Karnataka Assembly Election',))
    
    conn.commit()
    conn.close()
    print("Karnataka Assembly Election Database setup completed successfully!")
    print("Data inserted:")
    print("- Admin: username='admin', password='admin123'")
    print("- 224 Karnataka assemblies")
    print("- 4 sample voters (with Karnataka voter IDs)")
    print("- 10 sample candidates (assigned to assemblies)")
    print("- Election type: Karnataka Assembly Election")
    print("- Total assemblies: 224")
    print("- Majority seats: 113")

if __name__ == '__main__':
    setup_database()
