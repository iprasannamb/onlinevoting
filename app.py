"""
Karnataka Assembly Election System - Multi-Constituency Voting Platform
Main Flask Application
"""

import hashlib
import json
import random
import sqlite3
import re
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'
# Session configuration
app.permanent_session_lifetime = timedelta(hours=1)

# Database configuration
DATABASE = 'voting_system.db'

# Election configuration
ELECTION_TYPE = "Karnataka Assembly Election"
TOTAL_CONSTITUENCIES = 224
MAJORITY_SEATS = 113

# Party symbols mapping
PARTY_SYMBOLS = {
    'BJP': '🌸',
    'INC': '🖐️',
    'NPP': '🌺'
}

# Default symbols for other parties
DEFAULT_SYMBOLS = ['⭐', '🔥', '💧', '🌊', '🌈', '🦅', '🦁', '🐘']

# Blockchain class for vote simulation
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_block(previous_hash='0')
    
    def create_block(self, voter_id=None, candidate_id=None, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.now()),
            'voter_id': voter_id,
            'candidate_id': candidate_id,
            'hash': '',
            'previous_hash': previous_hash or self.chain[-1]['hash'] if self.chain else '0'
        }
        
        # Create hash for the block
        block_string = json.dumps(block, sort_keys=True).encode()
        block['hash'] = hashlib.sha256(block_string).hexdigest()
        
        self.chain.append(block)
        return block
    
    def get_chain(self):
        return self.chain

# Initialize blockchain
blockchain = Blockchain()

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables for multi-constituency system"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Create assemblies table (modern schema compatible with MySQL schema file)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assemblies (
            assembly_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            district TEXT,
            state TEXT,
            total_voters INTEGER DEFAULT 0
        )
    ''')
    
    # Create admin table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    ''')
    
    # Create voters table (with approval and verification fields)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voters (
            voter_id TEXT PRIMARY KEY,
            full_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT,
            assembly_id INTEGER NOT NULL,
            mobile TEXT,
            has_voted BOOLEAN DEFAULT 0,
            verified_status BOOLEAN DEFAULT 0,
            approval_status TEXT DEFAULT 'Pending',
            FOREIGN KEY (assembly_id) REFERENCES assemblies(assembly_id)
        )
    ''')
    
    # Create candidates table (admin-managed)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            candidate_id INTEGER PRIMARY KEY AUTOINCREMENT,
            candidate_serial_no INTEGER,
            candidate_name TEXT NOT NULL,
            party_name TEXT NOT NULL,
            assembly_id INTEGER,
            symbol TEXT,
            verified_by_eci BOOLEAN DEFAULT 1,
            added_by_admin BOOLEAN DEFAULT 1,
            votes_count INTEGER DEFAULT 0,
            FOREIGN KEY (assembly_id) REFERENCES assemblies(assembly_id)
        )
    ''')
    
    # Create votes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS votes (
            vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id TEXT NOT NULL,
            candidate_id INTEGER NOT NULL,
            assembly_id INTEGER NOT NULL,
            encrypted_vote TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (voter_id) REFERENCES voters(voter_id),
            FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id),
            FOREIGN KEY (assembly_id) REFERENCES assemblies(assembly_id)
        )
    ''')
    
    # Create results table for assembly-wise results
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS results (
            result_id INTEGER PRIMARY KEY AUTOINCREMENT,
            assembly_id INTEGER NOT NULL,
            candidate_id INTEGER NOT NULL,
            votes INTEGER NOT NULL,
            position INTEGER NOT NULL,
            declared BOOLEAN DEFAULT 0,
            FOREIGN KEY (assembly_id) REFERENCES assemblies(assembly_id),
            FOREIGN KEY (candidate_id) REFERENCES candidates(candidate_id)
        )
    ''')
    
    # Create government table for ruling party information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS government (
            id INTEGER PRIMARY KEY DEFAULT 1,
            election_type TEXT NOT NULL,
            winning_party TEXT,
            seats_won INTEGER DEFAULT 0,
            majority_obtained BOOLEAN DEFAULT 0,
            chief_minister TEXT,
            government_formed BOOLEAN DEFAULT 0,
            declared BOOLEAN DEFAULT 0
        )
    ''')
    
    # Create election table (updated)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS election (
            id INTEGER PRIMARY KEY DEFAULT 1,
            election_type TEXT DEFAULT 'Karnataka Assembly Election',
            status TEXT DEFAULT 'not_started',
            result_declared BOOLEAN DEFAULT 0,
            total_assemblies INTEGER DEFAULT 224
        )
    ''')
    
    # Create blockchain table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS blockchain (
            block_id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_data TEXT NOT NULL
        )
    ''')
    
    # Insert default admin if not exists
    cursor.execute('SELECT * FROM admin WHERE username = ?', ('admin',))
    if not cursor.fetchone():
        cursor.execute('INSERT INTO admin (username, password) VALUES (?, ?)',
                      ('admin', hashlib.sha256('admin123'.encode()).hexdigest()))
    
    # Insert default election status if not exists
    cursor.execute('SELECT * FROM election')
    if not cursor.fetchone():
        cursor.execute('INSERT INTO election (election_type, status, result_declared, total_assemblies) VALUES (?, ?, ?, ?)',
                      (ELECTION_TYPE, 'not_started', 0, TOTAL_CONSTITUENCIES))
    
    # Insert default government record if not exists
    cursor.execute('SELECT * FROM government')
    if not cursor.fetchone():
        cursor.execute('INSERT INTO government (election_type) VALUES (?)', (ELECTION_TYPE,))
    
    conn.commit()
    conn.close()

# Decorators for authentication
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'admin':
            flash('Admin access required!', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def voter_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'voter':
            flash('Voter access required!', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def candidate_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_type' not in session or session['user_type'] != 'candidate':
            flash('Candidate access required!', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/voter_register')
def voter_register():
    """Voter registration page"""
    # Get all constituencies for dropdown
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM assemblies ORDER BY name')
    constituencies = cursor.fetchall()
    conn.close()
    return render_template('voter_register.html', constituencies=constituencies)

@app.route('/voter_register_submit', methods=['POST'])
def voter_register_submit():
    """Handle voter registration"""
    voter_id = request.form.get('voter_id')
    name = request.form.get('name')
    age = request.form.get('age')
    gender = request.form.get('gender') or None
    assembly_id = request.form.get('constituency_id')
    mobile = request.form.get('mobile') or None
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO voters (voter_id, full_name, age, gender, assembly_id, mobile, approval_status, verified_status)
            VALUES (?, ?, ?, ?, ?, ?, 'Pending', 0)
        ''', (voter_id, name, age, gender, assembly_id, mobile))
        conn.commit()
        flash('Voter registration successful! Wait for admin approval.', 'success')
    except sqlite3.IntegrityError:
        flash('Voter ID already exists!', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('voter_register'))

@app.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    """Handle authentication"""
    user_type = request.form.get('user_type')
    
    if user_type == 'admin':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admin WHERE username = ?', (username,))
        admin = cursor.fetchone()
        conn.close()
        
        if admin and admin['password'] == hashlib.sha256(password.encode()).hexdigest():
            session['user_type'] = 'admin'
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!', 'error')
            return redirect(url_for('login'))
    
    elif user_type == 'voter':
        voter_id = request.form.get('voter_id')
        full_name = request.form.get('full_name') or ''

        # Validate voter ID format: must match ^RSB\d{7}$
        if not voter_id or not re.fullmatch(r'^RSB\d{7}$', voter_id):
            flash('Invalid Voter ID Format', 'error')
            return redirect(url_for('login'))

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT v.*, a.name as assembly_name, a.assembly_id as assembly_id
            FROM voters v
            JOIN assemblies a ON v.assembly_id = a.assembly_id
            WHERE v.voter_id = ?
        ''', (voter_id,))
        voter = cursor.fetchone()
        conn.close()

        if voter:
            # Check name match (case-insensitive)
            if full_name.strip() and full_name.strip().lower() != (voter['full_name'] or '').lower():
                flash('Voter name does not match our records.', 'error')
                return redirect(url_for('login'))

            # Check if voter is approved and verified
            if (voter['approval_status'] or '').lower() != 'approved' or not voter['verified_status']:
                flash('Voter not approved/verified yet! Please wait for admin approval.', 'error')
                return redirect(url_for('login'))

            # Create session
            session.permanent = True
            session['user_type'] = 'voter'
            session['voter_id'] = voter['voter_id']
            session['voter_name'] = voter['full_name']
            session['assembly_id'] = voter['assembly_id']
            session['assembly_name'] = voter['assembly_name']
            flash('Login successful!', 'success')
            return redirect(url_for('voter_dashboard'))
        else:
            flash('Invalid Voter ID!', 'error')
            return redirect(url_for('login'))
    
    elif user_type == 'candidate':
        # Candidate accounts cannot login. Candidates are added and managed only by Admin/ECI officials.
        flash('Candidate portal is disabled. Candidates are verified and added by ECI/Admin only.', 'error')
        return redirect(url_for('login'))
    
    return redirect(url_for('login'))

@app.route('/verify_otp')
def verify_otp():
    """OTP verification page"""
    if 'temp_voter_id' not in session:
        return redirect(url_for('login'))
    return render_template('verify_otp.html')

@app.route('/verify_otp_submit', methods=['POST'])
def verify_otp_submit():
    """Verify OTP and login voter"""
    if 'temp_voter_id' not in session:
        return redirect(url_for('login'))
    
    otp = request.form.get('otp')
    voter_id = session['temp_voter_id']
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM voters WHERE voter_id = ? AND otp = ?', (voter_id, otp))
    voter = cursor.fetchone()
    conn.close()
    
    if voter:
        # Get voter details with assembly
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT v.*, a.name as constituency_name, a.assembly_id as assembly_id FROM voters v JOIN assemblies a ON v.assembly_id = a.assembly_id WHERE v.voter_id = ?', (voter_id,))
        voter_details = cursor.fetchone()
        conn.close()
        
        session['user_type'] = 'voter'
        session['voter_id'] = voter_id
        session['voter_name'] = voter_details['full_name']
        session['assembly_id'] = voter_details['assembly_id']
        session['constituency_name'] = voter_details['constituency_name']
        session.pop('temp_voter_id', None)
        session.pop('temp_constituency', None)
        flash('Login successful!', 'success')
        return redirect(url_for('voter_dashboard'))
    else:
        flash('Invalid OTP!', 'error')
        return redirect(url_for('verify_otp'))

@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) as count FROM voters WHERE LOWER(approval_status) = 'approved'")
    total_voters = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM votes')
    total_votes = cursor.fetchone()['count']
    
    cursor.execute('SELECT COUNT(*) as count FROM assemblies')
    total_constituencies = cursor.fetchone()['count']
    
    cursor.execute('SELECT c.*, a.name as constituency_name FROM candidates c JOIN assemblies a ON c.assembly_id = a.assembly_id')
    candidates = cursor.fetchall()
    
    cursor.execute("SELECT v.*, a.name as constituency_name FROM voters v JOIN assemblies a ON v.assembly_id = a.assembly_id WHERE LOWER(v.approval_status) = 'pending'")
    pending_voters = cursor.fetchall()
    
    cursor.execute('SELECT * FROM election WHERE id = 1')
    election = cursor.fetchone()
    
    # Get seat distribution if results are declared
    seat_distribution = []
    if election['result_declared']:
        cursor.execute('''
            SELECT c.party_name as party, COUNT(*) as seats_won
            FROM results r
            JOIN candidates c ON r.candidate_id = c.candidate_id
            WHERE r.position = 1
            GROUP BY c.party_name
            ORDER BY seats_won DESC
        ''')
        seat_distribution = cursor.fetchall()

    # Get assemblies for admin candidate management
    cursor.execute('SELECT * FROM assemblies ORDER BY name')
    constituencies = cursor.fetchall()
    
    conn.close()
    
    return render_template('admin_dashboard.html', 
                         total_voters=total_voters,
                         total_votes=total_votes,
                         total_constituencies=total_constituencies,
                         candidates=candidates,
                         pending_voters=pending_voters,
                         election=election,
                         seat_distribution=seat_distribution,
                         constituencies=constituencies,
                         election_type=ELECTION_TYPE)

@app.route('/voter_dashboard')
@voter_required
def voter_dashboard():
    """Voter dashboard"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if voter has already voted
    cursor.execute('SELECT has_voted FROM voters WHERE voter_id = ?', 
                  (session['voter_id'],))
    has_voted = cursor.fetchone()['has_voted']
    
    # Get election status
    cursor.execute('SELECT status, election_type FROM election WHERE id = 1')
    election = cursor.fetchone()
    
    # Get approved/verified candidates from voter's assembly only
    cursor.execute('SELECT * FROM candidates WHERE verified_by_eci = 1 AND assembly_id = ?', 
                  (session['assembly_id'],))
    candidates = cursor.fetchall()
    
    # Get assembly information
    cursor.execute('SELECT * FROM assemblies WHERE assembly_id = ?', 
                  (session['assembly_id'],))
    constituency = cursor.fetchone()
    
    conn.close()
    
    return render_template('voter_dashboard.html',
                         has_voted=has_voted,
                         election=election,
                         candidates=candidates,
                         constituency=constituency)

# Candidate self-registration and candidate portal removed.
# Candidates must be added/managed by Admin only (see admin candidate management routes below).


@app.route('/add_candidate', methods=['POST'])
@admin_required
def add_candidate():
    """Admin: Add a verified candidate manually"""
    name = request.form.get('name')
    party = request.form.get('party')
    assembly_id = request.form.get('constituency_id')
    symbol = request.form.get('symbol') or (PARTY_SYMBOLS.get(party) or random.choice(DEFAULT_SYMBOLS))
    serial_no = request.form.get('candidate_serial_no') or None
    verified = 1 if request.form.get('verified') in ('1', 'on', 'true', 'yes') else 1

    conn = get_db()
    cursor = conn.cursor()
    try:
        # Assign a serial number if not provided
        if not serial_no:
            cursor.execute('SELECT COALESCE(MAX(candidate_serial_no), 0) as maxsn FROM candidates')
            serial_no = cursor.fetchone()['maxsn'] + 1

        cursor.execute('''
            INSERT INTO candidates (candidate_serial_no, candidate_name, party_name, assembly_id, symbol, verified_by_eci, votes_count)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        ''', (serial_no, name, party, assembly_id, symbol, verified))
        conn.commit()
        flash('Candidate added successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash('Error adding candidate.', 'error')
    finally:
        conn.close()
    return redirect(url_for('admin_dashboard'))


@app.route('/edit_candidate/<candidate_id>', methods=['POST'])
@admin_required
def edit_candidate(candidate_id):
    """Admin: Edit candidate details"""
    name = request.form.get('name')
    party = request.form.get('party')
    assembly_id = request.form.get('constituency_id')
    symbol = request.form.get('symbol')
    verified = 1 if request.form.get('verified') in ('1', 'on', 'true', 'yes') else 0
    serial_no = request.form.get('candidate_serial_no') or None

    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE candidates SET candidate_name = ?, party_name = ?, assembly_id = ?, symbol = ?, verified_by_eci = ?, candidate_serial_no = ?
            WHERE candidate_id = ?
        ''', (name, party, assembly_id, symbol, verified, serial_no, candidate_id))
        conn.commit()
        flash('Candidate updated successfully!', 'success')
    except Exception:
        conn.rollback()
        flash('Error updating candidate.', 'error')
    finally:
        conn.close()
    return redirect(url_for('admin_dashboard'))


@app.route('/delete_candidate/<candidate_id>')
@admin_required
def delete_candidate(candidate_id):
    """Admin: Delete candidate"""
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM candidates WHERE candidate_id = ?', (candidate_id,))
        conn.commit()
        flash('Candidate removed successfully!', 'success')
    except Exception:
        conn.rollback()
        flash('Error removing candidate.', 'error')
    finally:
        conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/vote', methods=['POST'])
@voter_required
def vote():
    """Handle voting with constituency validation"""
    candidate_id = request.form.get('candidate_id')
    voter_id = session['voter_id']
    assembly_id = session['assembly_id']
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if voter has already voted
    cursor.execute('SELECT has_voted FROM voters WHERE voter_id = ?', (voter_id,))
    has_voted = cursor.fetchone()['has_voted']
    
    if has_voted:
        flash('You have already voted!', 'error')
        conn.close()
        return redirect(url_for('voter_dashboard'))
    
    # Check election status
    cursor.execute('SELECT status FROM election WHERE id = 1')
    election_status = cursor.fetchone()['status']
    
    if election_status != 'started':
        flash('Election is not active!', 'error')
        conn.close()
        return redirect(url_for('voter_dashboard'))
    
    # Verify candidate belongs to voter's constituency
    cursor.execute('SELECT * FROM candidates WHERE candidate_id = ? AND assembly_id = ? AND verified_by_eci = 1', 
                  (candidate_id, assembly_id))
    candidate = cursor.fetchone()
    
    if not candidate:
        flash('Invalid candidate for your constituency!', 'error')
        conn.close()
        return redirect(url_for('voter_dashboard'))
    
    try:
        # Create encrypted vote
        vote_data = f"{voter_id}_{candidate_id}_{assembly_id}_{datetime.now()}"
        encrypted_vote = hashlib.sha256(vote_data.encode()).hexdigest()
        
        # Insert vote with constituency
        cursor.execute('''
            INSERT INTO votes (voter_id, candidate_id, assembly_id, encrypted_vote)
            VALUES (?, ?, ?, ?)
        ''', (voter_id, candidate_id, assembly_id, encrypted_vote))
        
        # Update candidate vote count
        cursor.execute('''
            UPDATE candidates SET votes_count = votes_count + 1
            WHERE candidate_id = ?
        ''', (candidate_id,))
        
        # Mark voter as has_voted
        cursor.execute('''
            UPDATE voters SET has_voted = 1 WHERE voter_id = ?
        ''', (voter_id,))
        
        # Add to blockchain
        previous_hash = blockchain.chain[-1]['hash'] if blockchain.chain else '0'
        blockchain.create_block(voter_id, candidate_id, previous_hash)
        
        # Store blockchain in database
        block_data = json.dumps(blockchain.chain[-1])
        cursor.execute('INSERT INTO blockchain (block_data) VALUES (?)', (block_data,))
        
        conn.commit()
        flash('Vote cast successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash('Error casting vote!', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('voter_dashboard'))

@app.route('/start_election')
@admin_required
def start_election():
    """Start election"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE election SET status = "started" WHERE id = 1')
    conn.commit()
    conn.close()
    flash('Election started!', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/pause_election')
@admin_required
def pause_election():
    """Pause election"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE election SET status = "paused" WHERE id = 1')
    conn.commit()
    conn.close()
    flash('Election paused!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/end_election')
@admin_required
def end_election():
    """End election"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE election SET status = "ended" WHERE id = 1')
    conn.commit()
    conn.close()
    flash('Election ended!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/declare_results')
@admin_required
def declare_results():
    """Declare results"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE election SET result_declared = 1 WHERE id = 1')
    conn.commit()
    conn.close()
    flash('Results declared!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/approve_candidate/<candidate_id>')
@admin_required
def approve_candidate(candidate_id):
    """Approve candidate"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE candidates SET verified_by_eci = 1 WHERE candidate_id = ?', 
                  (candidate_id,))
    conn.commit()
    conn.close()
    flash('Candidate approved!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/reject_candidate/<candidate_id>')
@admin_required
def reject_candidate(candidate_id):
    """Reject candidate"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE candidates SET verified_by_eci = 0 WHERE candidate_id = ?', 
                  (candidate_id,))
    conn.commit()
    conn.close()
    flash('Candidate rejected!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/approve_voter/<voter_id>')
@admin_required
def approve_voter(voter_id):
    """Approve voter"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE voters SET approval_status = 'Approved', verified_status = 1 WHERE voter_id = ?", 
                  (voter_id,))
    conn.commit()
    conn.close()
    flash('Voter approved!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/reject_voter/<voter_id>')
@admin_required
def reject_voter(voter_id):
    """Reject voter"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE voters SET approval_status = 'Rejected', verified_status = 0 WHERE voter_id = ?", 
                  (voter_id,))
    conn.commit()
    conn.close()
    flash('Voter rejected!', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/calculate_results')
@admin_required
def calculate_results():
    """Calculate constituency-wise results and government formation"""
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        # Get all assemblies
        cursor.execute('SELECT * FROM assemblies')
        constituencies = cursor.fetchall()
        
        # Clear existing results
        cursor.execute('DELETE FROM results')
        
        # Calculate results for each constituency
        for constituency in constituencies:
            assembly_id = constituency['assembly_id']
            
            # Get candidates with votes for this assembly
            cursor.execute('''
                SELECT c.candidate_id, c.candidate_name as name, c.party_name as party, COALESCE(c.votes_count, 0) as votes
                FROM candidates c
                WHERE c.assembly_id = ? AND c.verified_by_eci = 1
                ORDER BY votes DESC
            ''', (assembly_id,))
            
            candidates_results = cursor.fetchall()
            
            # Insert results with positions
            for position, candidate in enumerate(candidates_results, 1):
                cursor.execute('''
                    INSERT INTO results (assembly_id, candidate_id, votes, position, declared)
                    VALUES (?, ?, ?, ?, 1)
                ''', (assembly_id, candidate['candidate_id'], candidate['votes'], position))
        
        # Calculate party-wise seat distribution
        cursor.execute('''
            SELECT c.party_name as party, COUNT(*) as seats_won
            FROM results r
            JOIN candidates c ON r.candidate_id = c.candidate_id
            WHERE r.position = 1
            GROUP BY c.party_name
            ORDER BY seats_won DESC
        ''')
        
        party_seats = cursor.fetchall()
        
        # Determine winning party and government formation
        winning_party = None
        majority_obtained = False
        chief_minister = None
        
        if party_seats:
            winning_party = party_seats[0]['party']
            seats_won = party_seats[0]['seats_won']
            
            if seats_won >= MAJORITY_SEATS:
                majority_obtained = True
                chief_minister = "To be announced"  # Admin can update this
        
        # Update government table
        cursor.execute('''
            UPDATE government 
            SET winning_party = ?, seats_won = ?, majority_obtained = ?, 
                chief_minister = ?, government_formed = ?
            WHERE id = 1
        ''', (winning_party, party_seats[0]['seats_won'] if party_seats else 0, 
              majority_obtained, chief_minister, majority_obtained))
        
        conn.commit()
        flash('Results calculated successfully!', 'success')
        
    except Exception as e:
        conn.rollback()
        flash('Error calculating results!', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/assign_cm', methods=['POST'])
@admin_required
def assign_cm():
    """Assign Chief Minister"""
    cm_name = request.form.get('cm_name')
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('UPDATE government SET chief_minister = ? WHERE id = 1', (cm_name,))
        conn.commit()
        flash('Chief Minister assigned successfully!', 'success')
    except Exception as e:
        conn.rollback()
        flash('Error assigning Chief Minister!', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('admin_dashboard'))

@app.route('/results')
def results():
    """Public result selection page for any visitor"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT assembly_id, name FROM assemblies ORDER BY name')
    assemblies = cursor.fetchall()
    conn.close()
    return render_template('results_selection.html', assemblies=assemblies)

@app.route('/result/<int:assembly_id>')
def result_detail(assembly_id):
    """Display result details for a single constituency"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT result_declared, election_type, status FROM election WHERE id = 1')
    election = cursor.fetchone()
    cursor.execute('SELECT * FROM assemblies WHERE assembly_id = ?', (assembly_id,))
    assembly = cursor.fetchone()

    if not assembly:
        conn.close()
        flash('Constituency not found.', 'error')
        return redirect(url_for('results'))

    if not election['result_declared']:
        conn.close()
        return render_template('result_detail.html', assembly=assembly, election=election, result_declared=False)

    cursor.execute('''
        SELECT r.position, r.votes, c.candidate_name, c.party_name, c.symbol
        FROM results r
        JOIN candidates c ON r.candidate_id = c.candidate_id
        WHERE r.assembly_id = ?
        ORDER BY r.position ASC
        LIMIT 2
    ''', (assembly_id,))
    top_candidates = cursor.fetchall()

    winner = top_candidates[0] if top_candidates else None
    runner_up = top_candidates[1] if len(top_candidates) > 1 else None

    cursor.execute('SELECT COUNT(*) as total_votes FROM votes WHERE assembly_id = ?', (assembly_id,))
    total_votes = cursor.fetchone()['total_votes']
    total_voters = assembly['total_voters'] or 0
    turnout_pct = round((total_votes / total_voters) * 100, 2) if total_voters else None
    winner_pct = round((winner['votes'] / total_votes) * 100, 2) if winner and total_votes else 0

    conn.close()
    return render_template('result_detail.html',
                           assembly=assembly,
                           election=election,
                           result_declared=True,
                           winner=winner,
                           runner_up=runner_up,
                           total_votes=total_votes,
                           turnout_pct=turnout_pct,
                           winner_pct=winner_pct)

@app.route('/api/results')
def api_results():
    """API endpoint for party-wise seat distribution (for Chart.js)"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if results are declared
    cursor.execute('SELECT result_declared FROM election WHERE id = 1')
    result_declared = cursor.fetchone()['result_declared']
    
    if not result_declared:
        return jsonify({'error': 'Results not declared'})
    
    # Get party-wise seat distribution
    cursor.execute('''
        SELECT c.party_name as party, COUNT(*) as seats_won
        FROM results r
        JOIN candidates c ON r.candidate_id = c.candidate_id
        WHERE r.position = 1
        GROUP BY c.party_name
        ORDER BY seats_won DESC
    ''')
    party_seats = cursor.fetchall()
    
    conn.close()
    
    return jsonify({
        'parties': [dict(p) for p in party_seats]
    })

@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
