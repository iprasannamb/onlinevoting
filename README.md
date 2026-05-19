# Secure Online Voting System

A comprehensive, secure, and transparent digital voting platform built with Flask, featuring role-based authentication, blockchain simulation, and real-time results visualization.

## 🚀 Features

### Core Features
- **Role-Based Authentication**: Admin, Voter, and Candidate roles with secure login
- **OTP Verification**: Simulated OTP system for voter authentication
- **Secure Voting**: SHA-256 encryption for vote security
- **Blockchain Simulation**: Immutable vote tracking using blockchain concepts
- **Real-time Dashboard**: Live statistics and election control
- **Interactive Results**: Chart.js visualizations with bar and pie charts
- **Responsive Design**: Mobile-friendly Bootstrap UI

### Security Features
- One person, one vote enforcement
- Encrypted vote storage
- SQL injection protection
- Session management
- Input validation
- Blockchain-based audit trail

### User Roles
1. **Election Commission Admin**
   - Manage election process
   - Approve/reject candidates
   - Start/end elections
   - Declare results

2. **Voter**
   - OTP-based authentication
   - Secure voting interface
   - View voting status

3. **Candidate**
   - Registration system
   - Dashboard for results
   - Status tracking

## 📋 Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Modern web browser

## 🛠️ Installation

### Step 1: Clone/Download the Project
```bash
# If using git (not required for this setup)
# git clone <repository-url>

# Or download and extract the ZIP file
# Navigate to the project directory
cd secure_voting_system
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv voting_env

# Activate virtual environment
# On Windows:
voting_env\Scripts\activate

# On macOS/Linux:
source voting_env/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Setup Database
```bash
# Initialize database with sample data
python setup_database.py
```

### Step 5: Run the Application
```bash
python app.py
```

The application will start on `http://localhost:5000`

## 📁 Project Structure

```
secure_voting_system/
├── app.py                 # Main Flask application
├── setup_database.py      # Database initialization script
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── templates/            # HTML templates
│   ├── base.html         # Base template
│   ├── index.html        # Home page
│   ├── login.html        # Login page
│   ├── verify_otp.html   # OTP verification
│   ├── admin_dashboard.html
│   ├── voter_dashboard.html
│   ├── candidate_register.html
│   ├── candidate_dashboard.html
│   └── results.html      # Results page with charts
├── static/               # Static files
│   ├── css/
│   │   └── style.css     # Custom styles
│   └── js/
│       └── script.js     # Custom JavaScript
└── voting_system.db      # SQLite database (created after setup)
```

## 🔐 Default Credentials

### Admin Login
- **Username**: `admin`
- **Password**: `admin123`

### Sample Voters
- **Voter IDs**: `VOT001` to `VOT010`
- **OTP**: Generated dynamically (shown in flash message)

### Sample Candidates
- **Candidate IDs**: `CAN001` to `CAN005`
- **Status**: Pre-approved for demo

## 🎯 Usage Guide

### For Admin
1. Login with admin credentials
2. Approve pending candidates
3. Start the election
4. Monitor voting progress
5. End election and declare results

### For Voters
1. Enter Voter ID (VOT001-VOT010)
2. Note the generated OTP
3. Enter OTP for verification
4. Select candidate and cast vote
5. Vote is encrypted and stored

### For Candidates
1. Register with candidate details
2. Wait for admin approval
3. Login to view dashboard
4. Check results when declared

## 🗄️ Database Schema

### Tables
- **admin**: Admin credentials
- **voters**: Voter information and voting status
- **candidates**: Candidate details and approval status
- **votes**: Encrypted vote records
- **election**: Election status and control
- **blockchain**: Blockchain simulation data

### Key Features
- Foreign key relationships
- Encrypted vote storage
- Status tracking
- Audit trail

## 🎨 Frontend Technologies

- **HTML5**: Semantic markup
- **CSS3**: Modern styling with animations
- **JavaScript**: Interactive features
- **Bootstrap 5**: Responsive framework
- **Font Awesome**: Icon library
- **Chart.js**: Data visualization

## 🔧 Backend Technologies

- **Flask**: Web framework
- **SQLite**: Database
- **Python**: Programming language
- **Werkzeug**: WSGI utilities
- **Jinja2**: Template engine

## 🔒 Security Measures

1. **Password Hashing**: SHA-256 for admin passwords
2. **Vote Encryption**: SHA-256 for vote data
3. **Session Management**: Secure session handling
4. **Input Validation**: Server-side validation
5. **SQL Injection Prevention**: Parameterized queries
6. **Blockchain**: Immutable vote tracking

## 📊 Charts and Visualizations

- **Bar Chart**: Vote distribution per candidate
- **Pie Chart**: Vote percentage breakdown
- **Progress Bars**: Visual vote percentages
- **Real-time Updates**: Live statistics

## 🚀 Running in Production

For production deployment:

1. **Security**
   ```bash
   # Change secret key in app.py
   app.secret_key = 'your-secure-secret-key'
   ```

2. **Database**
   ```bash
   # Use MySQL/PostgreSQL for production
   # Update database configuration
   ```

3. **Web Server**
   ```bash
   # Use production WSGI server
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 app:app
   ```

4. **HTTPS**
   - Configure SSL certificate
   - Update Nginx/Apache configuration

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Kill existing process or change port
   python app.py --port 5001
   ```

2. **Database Error**
   ```bash
   # Reinitialize database
   python setup_database.py
   ```

3. **Import Error**
   ```bash
   # Install missing dependencies
   pip install -r requirements.txt
   ```

4. **Permission Denied**
   ```bash
   # Run as administrator (Windows)
   # or use sudo (Linux/macOS)
   ```

## 📞 Support

For issues and support:
- Check the troubleshooting section
- Review the code comments
- Verify all installation steps

## 📝 License

This project is for educational purposes. Use responsibly and comply with local regulations regarding electronic voting systems.

## 🔄 Version History

- **v1.0.0**: Initial release with all core features
  - Complete voting system
  - Blockchain simulation
  - Real-time results
  - Responsive design

---

**Note**: This is a demonstration system. For real-world elections, additional security measures and independent audits are required.
