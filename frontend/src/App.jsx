import React, { useState, useEffect } from 'react';
import { api } from './services/api';
import { 
  Vote, Lock, Shield, Activity, Award, Users, CheckCircle2, 
  XCircle, Plus, Trash2, Edit, BarChart3, LogOut, RefreshCw, 
  Play, Pause, Square, UserCheck, FileText, Layers, X, Info
} from 'lucide-react';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('home'); // home, login, register, voter_dashboard, admin_dashboard, results
  const [user, setUser] = useState(null); // { user_type, username/voter_id, ... }
  const [loading, setLoading] = useState(true);
  const [assemblies, setAssemblies] = useState([]);
  
  // Flash / Notification State
  const [notification, setNotification] = useState(null); // { type: 'success'|'error', message }

  // Auth Inputs
  const [loginType, setLoginType] = useState('voter'); // voter, admin
  const [loginVoterId, setLoginVoterId] = useState('');
  const [loginVoterName, setLoginVoterName] = useState('');
  const [loginAdminUser, setLoginAdminUser] = useState('');
  const [loginAdminPass, setLoginAdminPass] = useState('');

  // Register Inputs
  const [regVoterId, setRegVoterId] = useState('');
  const [regName, setRegName] = useState('');
  const [regAge, setRegAge] = useState('');
  const [regGender, setRegGender] = useState('Male');
  const [regAssemblyId, setRegAssemblyId] = useState('');
  const [regMobile, setRegMobile] = useState('');

  // Voter Dashboard State
  const [voterDashboardData, setVoterDashboardData] = useState(null);
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  // Admin Dashboard State
  const [adminDashboardData, setAdminDashboardData] = useState(null);
  const [showCandidateModal, setShowCandidateModal] = useState(false);
  const [modalMode, setModalMode] = useState('add'); // add, edit
  const [editingCandidateId, setEditingCandidateId] = useState(null);
  
  // Candidate Modal Inputs
  const [candName, setCandName] = useState('');
  const [candParty, setCandParty] = useState('');
  const [candAssemblyId, setCandAssemblyId] = useState('');
  const [candSymbol, setCandSymbol] = useState('');
  const [candSerialNo, setCandSerialNo] = useState('');

  // Public Results State
  const [publicResultsData, setPublicResultsData] = useState(null);
  const [selectedResultsAssembly, setSelectedResultsAssembly] = useState('');
  const [selectedAssemblyDetail, setSelectedAssemblyDetail] = useState(null);
  const [cmNameInput, setCmNameInput] = useState('');

  // Auto-clear notifications
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  // Check Session on mount
  useEffect(() => {
    checkSession();
    fetchAssemblies();
  }, []);

  const showFlash = (type, message) => {
    setNotification({ type, message });
  };

  const checkSession = async () => {
    try {
      const data = await api.getSession();
      if (data.logged_in) {
        setUser(data.user);
        if (data.user.user_type === 'admin') {
          setCurrentPage('admin_dashboard');
          fetchAdminDashboard();
        } else if (data.user.user_type === 'voter') {
          setCurrentPage('voter_dashboard');
          fetchVoterDashboard();
        }
      } else {
        setUser(null);
        if (currentPage === 'voter_dashboard' || currentPage === 'admin_dashboard') {
          setCurrentPage('home');
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchAssemblies = async () => {
    try {
      const data = await api.getAssemblies();
      setAssemblies(data.assemblies);
      if (data.assemblies.length > 0) {
        setRegAssemblyId(data.assemblies[0].assembly_id);
        setCandAssemblyId(data.assemblies[0].assembly_id);
      }
    } catch (err) {
      showFlash('error', 'Failed to fetch constituencies');
    }
  };

  const handleLogout = async () => {
    try {
      await api.logout();
      setUser(null);
      setVoterDashboardData(null);
      setAdminDashboardData(null);
      setCurrentPage('home');
      showFlash('success', 'Logged out successfully');
    } catch (err) {
      showFlash('error', err.message || 'Logout failed');
    }
  };

  // Auth Operations
  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const credentials = loginType === 'admin' 
        ? { user_type: 'admin', username: loginAdminUser, password: loginAdminPass }
        : { user_type: 'voter', voter_id: loginVoterId, full_name: loginVoterName };

      const data = await api.login(credentials);
      if (data.success) {
        setUser(data.user);
        showFlash('success', 'Logged in successfully!');
        if (data.user.user_type === 'admin') {
          setCurrentPage('admin_dashboard');
          fetchAdminDashboard();
        } else {
          setCurrentPage('voter_dashboard');
          fetchVoterDashboard();
        }
        // Reset login inputs
        setLoginVoterId('');
        setLoginVoterName('');
        setLoginAdminUser('');
        setLoginAdminPass('');
      }
    } catch (err) {
      showFlash('error', err.message || 'Authentication failed');
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      const voterData = {
        voter_id: regVoterId,
        name: regName,
        age: parseInt(regAge),
        gender: regGender,
        constituency_id: parseInt(regAssemblyId),
        mobile: regMobile
      };
      const data = await api.registerVoter(voterData);
      if (data.success) {
        showFlash('success', data.message);
        // Reset form
        setRegVoterId('');
        setRegName('');
        setRegAge('');
        setRegMobile('');
        setCurrentPage('login');
      }
    } catch (err) {
      showFlash('error', err.message || 'Registration failed');
    }
  };

  // Voter dashboard logic
  const fetchVoterDashboard = async () => {
    try {
      const data = await api.getVoterDashboard();
      setVoterDashboardData(data);
    } catch (err) {
      showFlash('error', 'Failed to load voter dashboard');
    }
  };

  const handleCastVote = async () => {
    if (!selectedCandidate) {
      showFlash('error', 'Please select a candidate to vote');
      return;
    }
    try {
      const data = await api.castVote(selectedCandidate);
      if (data.success) {
        showFlash('success', data.message);
        setSelectedCandidate(null);
        fetchVoterDashboard();
      }
    } catch (err) {
      showFlash('error', err.message || 'Error casting vote');
    }
  };

  // Admin dashboard logic
  const fetchAdminDashboard = async () => {
    try {
      const data = await api.getAdminDashboard();
      setAdminDashboardData(data);
      if (data.government?.chief_minister) {
        setCmNameInput(data.government.chief_minister);
      }
    } catch (err) {
      showFlash('error', 'Failed to load admin dashboard');
    }
  };

  const handleApproveVoter = async (voterId) => {
    try {
      const data = await api.approveVoter(voterId);
      showFlash('success', data.message);
      fetchAdminDashboard();
    } catch (err) {
      showFlash('error', 'Failed to approve voter');
    }
  };

  const handleRejectVoter = async (voterId) => {
    try {
      const data = await api.rejectVoter(voterId);
      showFlash('success', data.message);
      fetchAdminDashboard();
    } catch (err) {
      showFlash('error', 'Failed to reject voter');
    }
  };

  const handleApproveCandidate = async (candidateId) => {
    try {
      const data = await api.approveCandidate(candidateId);
      showFlash('success', data.message);
      fetchAdminDashboard();
    } catch (err) {
      showFlash('error', 'Failed to approve candidate');
    }
  };

  const handleRejectCandidate = async (candidateId) => {
    try {
      const data = await api.rejectCandidate(candidateId);
      showFlash('success', data.message);
      fetchAdminDashboard();
    } catch (err) {
      showFlash('error', 'Failed to reject candidate');
    }
  };

  const handleElectionControl = async (action) => {
    try {
      let data;
      if (action === 'start') data = await api.startElection();
      else if (action === 'pause') data = await api.pauseElection();
      else if (action === 'end') data = await api.endElection();
      else if (action === 'calculate') data = await api.calculateResults();
      else if (action === 'declare') data = await api.declareResults();
      
      showFlash('success', data.message);
      fetchAdminDashboard();
    } catch (err) {
      showFlash('error', err.message || `Failed to perform: ${action}`);
    }
  };

  const handleCMSubmit = async (e) => {
    e.preventDefault();
    try {
      const data = await api.assignCM(cmNameInput);
      showFlash('success', data.message);
      fetchAdminDashboard();
    } catch (err) {
      showFlash('error', err.message || 'Failed to assign Chief Minister');
    }
  };

  // Candidate CRUD Modal
  const openAddCandidateModal = () => {
    setModalMode('add');
    setCandName('');
    setCandParty('BJP');
    if (assemblies.length > 0) setCandAssemblyId(assemblies[0].assembly_id);
    setCandSymbol('🌸');
    setCandSerialNo('');
    setShowCandidateModal(true);
  };

  const openEditCandidateModal = (cand) => {
    setModalMode('edit');
    setEditingCandidateId(cand.candidate_id);
    setCandName(cand.candidate_name);
    setCandParty(cand.party_name);
    setCandAssemblyId(cand.assembly_id);
    setCandSymbol(cand.symbol);
    setCandSerialNo(cand.candidate_serial_no || '');
    setShowCandidateModal(true);
  };

  const handleCandidateSubmit = async (e) => {
    e.preventDefault();
    try {
      const candData = {
        name: candName,
        party: candParty,
        constituency_id: parseInt(candAssemblyId),
        symbol: candSymbol,
        candidate_serial_no: candSerialNo ? parseInt(candSerialNo) : null
      };

      let data;
      if (modalMode === 'add') {
        data = await api.addCandidate(candData);
      } else {
        data = await api.editCandidate(editingCandidateId, candData);
      }

      showFlash('success', data.message);
      setShowCandidateModal(false);
      fetchAdminDashboard();
    } catch (err) {
      showFlash('error', err.message || 'Candidate operation failed');
    }
  };

  const handleDeleteCandidate = async (candidateId) => {
    if (!window.confirm('Are you sure you want to delete this candidate?')) return;
    try {
      const data = await api.deleteCandidate(candidateId);
      showFlash('success', data.message);
      fetchAdminDashboard();
    } catch (err) {
      showFlash('error', err.message || 'Failed to delete candidate');
    }
  };

  // Public Results logic
  const fetchPublicResults = async () => {
    try {
      const data = await api.getPublicResults();
      setPublicResultsData(data);
      if (data.assemblies?.length > 0) {
        setSelectedResultsAssembly(data.assemblies[0].assembly_id);
        fetchAssemblyDetail(data.assemblies[0].assembly_id);
      }
    } catch (err) {
      showFlash('error', 'Failed to load results');
    }
  };

  const fetchAssemblyDetail = async (assemblyId) => {
    if (!assemblyId) return;
    try {
      const data = await api.getPublicResultDetail(assemblyId);
      setSelectedAssemblyDetail(data);
    } catch (err) {
      showFlash('error', 'Failed to load constituency results');
    }
  };

  // Auto-switch results assembly detail
  useEffect(() => {
    if (currentPage === 'results' && selectedResultsAssembly) {
      fetchAssemblyDetail(selectedResultsAssembly);
    }
  }, [selectedResultsAssembly]);

  if (loading) {
    return (
      <div style={{
        display: 'flex', justifyContent: 'center', alignItems: 'center', 
        height: '100vh', flexDirection: 'column', gap: '1rem', background: '#0b0f19', color: '#fff'
      }}>
        <RefreshCw style={{ animation: 'spin 2s linear infinite' }} size={40} />
        <p style={{ fontFamily: 'Plus Jakarta Sans', fontWeight: 600 }}>Connecting to Secured ECI Platform...</p>
      </div>
    );
  }

  return (
    <div className="app-container">
      {/* Navigation Header */}
      <nav className="navbar">
        <div className="nav-brand" style={{ cursor: 'pointer' }} onClick={() => setCurrentPage('home')}>
          <Shield size={28} style={{ color: '#06b6d4' }} />
          <span>ECI Secure Voting</span>
        </div>
        
        <div className="nav-links">
          <button className={`nav-btn ${currentPage === 'home' ? 'active' : ''}`} onClick={() => setCurrentPage('home')}>Home</button>
          <button className={`nav-btn ${currentPage === 'results' ? 'active' : ''}`} onClick={() => { setCurrentPage('results'); fetchPublicResults(); }}>Results</button>
          
          {user ? (
            <>
              {user.user_type === 'admin' ? (
                <button className={`nav-btn ${currentPage === 'admin_dashboard' ? 'active' : ''}`} onClick={() => { setCurrentPage('admin_dashboard'); fetchAdminDashboard(); }}>Admin Panel</button>
              ) : (
                <button className={`nav-btn ${currentPage === 'voter_dashboard' ? 'active' : ''}`} onClick={() => { setCurrentPage('voter_dashboard'); fetchVoterDashboard(); }}>Voter Panel</button>
              )}
              <button className="nav-btn-primary" style={{ background: '#ef4444', display: 'flex', alignItems: 'center', gap: '0.5rem' }} onClick={handleLogout}>
                <LogOut size={16} /> Logout
              </button>
            </>
          ) : (
            <>
              <button className={`nav-btn ${currentPage === 'register' ? 'active' : ''}`} onClick={() => setCurrentPage('register')}>Register</button>
              <button className="nav-btn-primary" onClick={() => setCurrentPage('login')}>Sign In</button>
            </>
          )}
        </div>
      </nav>

      {/* Global Notifications */}
      {notification && (
        <div style={{ padding: '0 2rem', marginTop: '1.5rem', width: '100%', maxWidth: '1280px', margin: '1.5rem auto 0 auto' }}>
          <div className={`alert alert-${notification.type}`}>
            {notification.type === 'success' ? <CheckCircle2 size={20} /> : <XCircle size={20} />}
            <span>{notification.message}</span>
          </div>
        </div>
      )}

      {/* 1. Landing Page / Home */}
      {currentPage === 'home' && (
        <>
          <div className="hero">
            <div className="hero-tagline">ECI Blockchain Voting Simulation</div>
            <h1 className="hero-title">Karnataka Assembly Election 2026</h1>
            <p className="hero-desc">
              Experience the secure, tamper-proof multi-constituency digital voting system. Powered by simulated cryptography, localized assembly routing, and decentralized blockchain ledger simulation for maximum transparency.
            </p>
            <div className="hero-actions">
              {!user ? (
                <>
                  <button className="btn-lg btn-primary" onClick={() => setCurrentPage('login')}>
                    <Vote size={20} /> Cast Your Vote
                  </button>
                  <button className="btn-lg btn-outline" onClick={() => setCurrentPage('register')}>
                    <UserCheck size={20} /> Voter Registration
                  </button>
                </>
              ) : (
                <button className="btn-lg btn-primary" onClick={() => user.user_type === 'admin' ? setCurrentPage('admin_dashboard') : setCurrentPage('voter_dashboard')}>
                  Go to Dashboard
                </button>
              )}
            </div>
          </div>

          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon"><Lock size={24} /></div>
              <h3 className="feature-title">SHA-256 Vote Security</h3>
              <p className="feature-desc">All votes are parsed through a SHA-256 cryptographic hashing layout to mask voter details and prevent casting logs manipulation.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon"><Layers size={24} /></div>
              <h3 className="feature-title">Blockchain Audit Ledger</h3>
              <p className="feature-desc">Every single vote cast generates an immutable block in our ECI blockchain simulation, verified by previous hashes.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon"><Activity size={24} /></div>
              <h3 className="feature-title">Real-Time Visualization</h3>
              <p className="feature-desc">Instantly track election voter turnouts, vote counts, and winner seat distributions constituency-wise once declared.</p>
            </div>
          </div>
        </>
      )}

      {/* 2. Authentication Login Page */}
      {currentPage === 'login' && (
        <div className="auth-wrapper">
          <div className="auth-card">
            <div className="auth-header">
              <h2 className="auth-title">Welcome Back</h2>
              <p className="auth-desc">Sign in to ECI secure election vault</p>
            </div>

            <div className="auth-tabs">
              <button className={`auth-tab ${loginType === 'voter' ? 'active' : ''}`} onClick={() => setLoginType('voter')}>Voter</button>
              <button className={`auth-tab ${loginType === 'admin' ? 'active' : ''}`} onClick={() => setLoginType('admin')}>ECI Admin</button>
            </div>

            <form onSubmit={handleLogin}>
              {loginType === 'voter' ? (
                <>
                  <div className="form-group">
                    <label className="form-label">Voter ID</label>
                    <input className="form-input" type="text" placeholder="e.g. RSB1000001" value={loginVoterId} onChange={(e) => setLoginVoterId(e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Full Name</label>
                    <input className="form-input" type="text" placeholder="Your Registered Name" value={loginVoterName} onChange={(e) => setLoginVoterName(e.target.value)} required />
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.8rem', padding: '0.5rem 0' }}>
                    <Info size={16} />
                    <span>Format: RSB followed by 7 digits. (e.g. RSB1000001)</span>
                  </div>
                </>
              ) : (
                <>
                  <div className="form-group">
                    <label className="form-label">Username</label>
                    <input className="form-input" type="text" placeholder="Admin username" value={loginAdminUser} onChange={(e) => setLoginAdminUser(e.target.value)} required />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Password</label>
                    <input className="form-input" type="password" placeholder="Admin password" value={loginAdminPass} onChange={(e) => setLoginAdminPass(e.target.value)} required />
                  </div>
                </>
              )}

              <button className="form-submit-btn" type="submit">Sign In</button>
            </form>
          </div>
        </div>
      )}

      {/* 3. Voter Registration Page */}
      {currentPage === 'register' && (
        <div className="auth-wrapper">
          <div className="auth-card" style={{ maxWidth: '550px' }}>
            <div className="auth-header">
              <h2 className="auth-title">Voter Registration</h2>
              <p className="auth-desc">Register yourself to the official Karnataka voter roll</p>
            </div>

            <form onSubmit={handleRegister}>
              <div className="form-group">
                <label className="form-label">Requested Voter ID (7-digit unique string)</label>
                <input className="form-input" type="text" placeholder="e.g. RSB1234567" value={regVoterId} onChange={(e) => setRegVoterId(e.target.value)} required />
              </div>
              
              <div className="form-group">
                <label className="form-label">Full Name</label>
                <input className="form-input" type="text" placeholder="As shown on national records" value={regName} onChange={(e) => setRegName(e.target.value)} required />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div className="form-group">
                  <label className="form-label">Age</label>
                  <input className="form-input" type="number" min="18" placeholder="Must be >= 18" value={regAge} onChange={(e) => setRegAge(e.target.value)} required />
                </div>
                <div className="form-group">
                  <label className="form-label">Gender</label>
                  <select className="form-select" value={regGender} onChange={(e) => setRegGender(e.target.value)}>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Constituency Assembly</label>
                <select className="form-select" value={regAssemblyId} onChange={(e) => setRegAssemblyId(e.target.value)} required>
                  {assemblies.map(a => (
                    <option key={a.assembly_id} value={a.assembly_id}>{a.name} ({a.district})</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Mobile Number</label>
                <input className="form-input" type="tel" placeholder="10-digit number" value={regMobile} onChange={(e) => setRegMobile(e.target.value)} required />
              </div>

              <button className="form-submit-btn" type="submit">Submit Registration</button>
            </form>
          </div>
        </div>
      )}

      {/* 4. Voter Dashboard */}
      {currentPage === 'voter_dashboard' && voterDashboardData && (
        <div className="dashboard-container">
          <div className="dashboard-header">
            <div className="welcome-text">
              <h1>Welcome, {voterDashboardData.voter.full_name}</h1>
              <p>Constituency: <strong style={{ color: '#3b82f6' }}>{voterDashboardData.voter.assembly_name}</strong> | ID: <code>{voterDashboardData.voter.voter_id}</code></p>
            </div>
            <div>
              {voterDashboardData.has_voted ? (
                <span className="badge badge-success">Vote Cast Successfully</span>
              ) : voterDashboardData.election.status === 'started' ? (
                <span className="badge badge-info">Election Active</span>
              ) : voterDashboardData.election.status === 'paused' ? (
                <span className="badge badge-warning">Election Paused</span>
              ) : (
                <span className="badge badge-danger">Election Closed</span>
              )}
            </div>
          </div>

          <div className="dashboard-grid">
            {/* Left Main Dashboard */}
            <div>
              <div className="widget-card">
                <h3 className="widget-title"><Vote size={20} /> Secure Voting Console</h3>
                
                {voterDashboardData.has_voted ? (
                  <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
                    <CheckCircle2 size={64} style={{ color: '#10b981', marginBottom: '1.5rem' }} />
                    <h2 style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }}>Your Vote is Cryptographically Encrypted!</h2>
                    <p style={{ color: 'var(--text-secondary)', maxWidth: '500px', margin: '0 auto' }}>
                      Thank you for participating. Your ballot has been secured using SHA-256 and appended to the election simulation ledger. You cannot cast another vote.
                    </p>
                  </div>
                ) : voterDashboardData.election.status !== 'started' ? (
                  <div style={{ textAlign: 'center', padding: '3rem 1rem', color: 'var(--text-secondary)' }}>
                    <Info size={48} style={{ color: 'var(--accent-yellow)', marginBottom: '1.5rem' }} />
                    <h2>Voting Booth is Currently Closed</h2>
                    <p style={{ marginTop: '0.5rem' }}>The Election Commission has either not started the voting cycle or has paused it. Please check back later.</p>
                  </div>
                ) : (
                  <div>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
                      Select your candidate representing <strong style={{ color: '#fff' }}>{voterDashboardData.voter.assembly_name}</strong> and click "Cast Ballot" to securely register your vote.
                    </p>

                    {voterDashboardData.candidates.length === 0 ? (
                      <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)' }}>
                        No approved candidates available for this constituency.
                      </div>
                    ) : (
                      <>
                        <div className="candidates-grid">
                          {voterDashboardData.candidates.map(cand => (
                            <div 
                              key={cand.candidate_id} 
                              className={`candidate-item ${selectedCandidate === cand.candidate_id ? 'selected' : ''}`}
                              onClick={() => setSelectedCandidate(cand.candidate_id)}
                            >
                              <div className="candidate-symbol">{cand.symbol}</div>
                              <div className="candidate-name">{cand.candidate_name}</div>
                              <div className="candidate-party">{cand.party_name}</div>
                            </div>
                          ))}
                        </div>

                        <div className="vote-action-bar">
                          <button className="btn-lg btn-primary" onClick={handleCastVote} disabled={!selectedCandidate}>
                            Confirm & Cast Ballot
                          </button>
                        </div>
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Right Panel: Blockchain Audit Trail */}
            <div>
              <div className="widget-card">
                <h3 className="widget-title"><Layers size={20} /> Blockchain Ledger Log</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '1rem' }}>
                  Simulated audit block stream for Karnataka Assembly election logs.
                </p>
                <div className="blockchain-timeline">
                  {voterDashboardData.blockchain?.length === 0 ? (
                    <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                      Blockchain empty. Genesis block pending.
                    </div>
                  ) : (
                    voterDashboardData.blockchain.map(block => (
                      <div key={block.index} className="blockchain-node">
                        <div className="blockchain-node-header">
                          <span>BLOCK #{block.index}</span>
                          <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{block.timestamp.split('.')[0]}</span>
                        </div>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem', color: 'var(--text-secondary)' }}>
                          <div>Voter Hash: <code>{block.voter_id ? 'Appended (Encrypted)' : 'Genesis'}</code></div>
                          <div>Candidate Ref: <code>{block.candidate_id ? `CAN_ID_${block.candidate_id}` : 'N/A'}</code></div>
                          <div className="blockchain-hash">Hash: <code>{block.hash.substring(0, 16)}...</code></div>
                          <div className="blockchain-hash">Prev: <code>{block.previous_hash.substring(0, 16)}...</code></div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 5. Admin Dashboard */}
      {currentPage === 'admin_dashboard' && adminDashboardData && (
        <div className="dashboard-container">
          <div className="dashboard-header">
            <div className="welcome-text">
              <h1>ECI Commission Hub</h1>
              <p>Logged in as: <strong>Admin Control</strong></p>
            </div>
            <div>
              {adminDashboardData.election.status === 'started' ? (
                <span className="badge badge-success">Voting Cycle Active</span>
              ) : adminDashboardData.election.status === 'paused' ? (
                <span className="badge badge-warning">Voting Cycle Paused</span>
              ) : adminDashboardData.election.status === 'ended' ? (
                <span className="badge badge-danger">Voting Ended</span>
              ) : (
                <span className="badge badge-info">Preparation Mode</span>
              )}
            </div>
          </div>

          {/* Stats Bar */}
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon blue"><Users size={24} /></div>
              <div>
                <div className="stat-value">{adminDashboardData.total_voters}</div>
                <div className="stat-label">Approved Voters</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon purple"><Vote size={24} /></div>
              <div>
                <div className="stat-value">{adminDashboardData.total_votes}</div>
                <div className="stat-label">Ballots Cast</div>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon cyan"><BarChart3 size={24} /></div>
              <div>
                <div className="stat-value">{adminDashboardData.total_constituencies}</div>
                <div className="stat-label">Constituencies</div>
              </div>
            </div>
          </div>

          {/* Ruling CM Panel */}
          {adminDashboardData.government?.winning_party && adminDashboardData.election.result_declared && (
            <div className="cm-card">
              <div>
                <div className="cm-title">Government Formation Projection</div>
                <div className="cm-name">{adminDashboardData.government.winning_party} formed government</div>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                  Seats won: <strong>{adminDashboardData.government.seats_won}</strong> / 224 | Majority: {adminDashboardData.government.majority_obtained ? 'Obtained' : 'Coalition Needed'}
                </p>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <div>
                  <div className="cm-title" style={{ textAlign: 'right' }}>Designated Chief Minister</div>
                  <div className="cm-name" style={{ fontSize: '1.25rem', textAlign: 'right', color: '#8b5cf6' }}>{adminDashboardData.government.chief_minister || 'Not Assigned'}</div>
                </div>
                
                <form onSubmit={handleCMSubmit} style={{ display: 'flex', gap: '0.5rem' }}>
                  <input 
                    type="text" 
                    className="form-input" 
                    placeholder="Assign CM Name..." 
                    style={{ padding: '0.5rem', width: '160px' }} 
                    value={cmNameInput}
                    onChange={(e) => setCmNameInput(e.target.value)}
                  />
                  <button type="submit" className="btn-sm btn-info" style={{ padding: '0.5rem 0.75rem' }}>Assign</button>
                </form>
              </div>
            </div>
          )}

          {/* Control Center Widgets */}
          <div className="dashboard-grid">
            <div>
              {/* Election Controller */}
              <div className="widget-card">
                <h3 className="widget-title"><Activity size={20} /> Election Controller</h3>
                <div className="control-panel">
                  <button className="control-btn" style={{ background: '#10b981', color: '#fff' }} onClick={() => handleElectionControl('start')} disabled={adminDashboardData.election.status === 'started'}>
                    <Play size={16} /> Start Election
                  </button>
                  <button className="control-btn" style={{ background: '#f59e0b', color: '#fff' }} onClick={() => handleElectionControl('pause')} disabled={adminDashboardData.election.status !== 'started'}>
                    <Pause size={16} /> Pause Election
                  </button>
                  <button className="control-btn" style={{ background: '#ef4444', color: '#fff' }} onClick={() => handleElectionControl('end')} disabled={adminDashboardData.election.status === 'ended' || adminDashboardData.election.status === 'not_started'}>
                    <Square size={16} /> End Election
                  </button>
                  
                  <button className="control-btn" style={{ background: '#8b5cf6', color: '#fff' }} onClick={() => handleElectionControl('calculate')} disabled={adminDashboardData.election.status !== 'ended'}>
                    <RefreshCw size={16} /> Calculate Results
                  </button>
                  <button className="control-btn" style={{ background: '#06b6d4', color: '#fff' }} onClick={() => handleElectionControl('declare')} disabled={adminDashboardData.election.result_declared}>
                    <FileText size={16} /> Declare Results
                  </button>
                </div>
                <div style={{ display: 'flex', gap: '1rem', color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                  <span>Results Declared: <strong>{adminDashboardData.election.result_declared ? 'YES' : 'NO'}</strong></span>
                </div>
              </div>

              {/* Voter Registration Approvals */}
              <div className="widget-card">
                <h3 className="widget-title"><UserCheck size={20} /> Pending Voter Approvals ({adminDashboardData.pending_voters.length})</h3>
                {adminDashboardData.pending_voters.length === 0 ? (
                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem' }}>No voter registration requests are currently pending approval.</p>
                ) : (
                  <div className="table-wrapper">
                    <table className="table">
                      <thead>
                        <tr>
                          <th>Voter ID</th>
                          <th>Name</th>
                          <th>Age</th>
                          <th>Assembly</th>
                          <th>Mobile</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {adminDashboardData.pending_voters.map(v => (
                          <tr key={v.voter_id}>
                            <td><code>{v.voter_id}</code></td>
                            <td>{v.full_name}</td>
                            <td>{v.age}</td>
                            <td>{v.constituency_name}</td>
                            <td>{v.mobile}</td>
                            <td>
                              <div className="table-actions">
                                <button className="btn-sm btn-success" onClick={() => handleApproveVoter(v.voter_id)}>Approve</button>
                                <button className="btn-sm btn-danger" onClick={() => handleRejectVoter(v.voter_id)}>Reject</button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>

            {/* Right Widget: Candidates ECI management */}
            <div>
              <div className="widget-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <h3 className="widget-title" style={{ margin: 0, border: 0 }}><Award size={20} /> Candidates Manager</h3>
                  <button className="btn-sm btn-info" style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }} onClick={openAddCandidateModal}>
                    <Plus size={14} /> Add
                  </button>
                </div>
                
                <div style={{ maxHeight: '500px', overflowY: 'auto', paddingRight: '0.25rem' }}>
                  {adminDashboardData.candidates.length === 0 ? (
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>No candidates enrolled in the system.</p>
                  ) : (
                    adminDashboardData.candidates.map(cand => (
                      <div key={cand.candidate_id} style={{
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center', 
                        padding: '0.75rem', background: 'rgba(255, 255, 255, 0.02)', border: '1px solid var(--border-color)',
                        borderRadius: '10px', marginBottom: '0.5rem'
                      }}>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <span style={{ fontSize: '1.5rem' }}>{cand.symbol}</span>
                            <div>
                              <strong style={{ fontSize: '0.95rem' }}>{cand.candidate_name}</strong>
                              <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                                {cand.party_name} | {cand.constituency_name}
                              </div>
                            </div>
                          </div>
                        </div>
                        <div style={{ display: 'flex', gap: '0.25rem' }}>
                          <button className="btn-sm btn-warning" style={{ padding: '0.3rem' }} onClick={() => openEditCandidateModal(cand)}><Edit size={14} /></button>
                          <button className="btn-sm btn-danger" style={{ padding: '0.3rem' }} onClick={() => handleDeleteCandidate(cand.candidate_id)}><Trash2 size={14} /></button>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 6. Public Results View */}
      {currentPage === 'results' && publicResultsData && (
        <div className="dashboard-container" style={{ maxWidth: '960px' }}>
          <div className="results-header">
            <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem' }}>Elections Result Center</h1>
            <p style={{ color: 'var(--text-secondary)' }}>Official visualizer for declared assembly polls</p>
          </div>

          {/* Main Results State */}
          {!publicResultsData.election.result_declared ? (
            <div style={{ textAlign: 'center', padding: '4rem 2rem', background: 'var(--glass-bg)', borderRadius: '20px', border: '1px solid var(--glass-border)' }}>
              <Info size={64} style={{ color: 'var(--accent-yellow)', marginBottom: '1.5rem' }} />
              <h2>Results Are Not Declared Yet</h2>
              <p style={{ color: 'var(--text-secondary)', marginTop: '0.5rem', maxWidth: '500px', margin: '0.5rem auto 0 auto' }}>
                The voting phase is either active or calculation processes have not been finalized by the Election Commission of India. Keep checking back.
              </p>
            </div>
          ) : (
            <>
              {/* Show ruling CM and seat charts */}
              {publicResultsData.government?.winning_party && (
                <div className="cm-card" style={{ marginBottom: '3rem' }}>
                  <div>
                    <div className="cm-title"> ruling government formed</div>
                    <div className="cm-name" style={{ fontSize: '1.75rem' }}>{publicResultsData.government.winning_party} Party</div>
                    <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '0.25rem' }}>
                      Seats secured: <strong>{publicResultsData.government.seats_won}</strong> (Majority: 113)
                    </p>
                  </div>
                  <div>
                    <div className="cm-title" style={{ textAlign: 'right' }}>Elected Chief Minister</div>
                    <div className="cm-name" style={{ color: '#06b6d4' }}>{publicResultsData.government.chief_minister || 'To be announced'}</div>
                  </div>
                </div>
              )}

              {/* State level Party Seat distribution charts */}
              {publicResultsData.seat_distribution?.length > 0 && (
                <div className="widget-card" style={{ marginBottom: '3rem' }}>
                  <h3 className="widget-title"><BarChart3 size={20} /> Assembly Seat Distribution (Total 224)</h3>
                  <div className="chart-bar-container">
                    {publicResultsData.seat_distribution.map((item, idx) => {
                      const pct = Math.min(100, (item.seats_won / 224) * 100);
                      return (
                        <div key={idx} className="chart-bar-item">
                          <div className="chart-bar-label">
                            <span>{item.party}</span>
                            <strong>{item.seats_won} Seats ({roundVal(pct)}%)</strong>
                          </div>
                          <div className="chart-bar-bg">
                            <div 
                              className="chart-bar-fill" 
                              style={{ 
                                width: `${pct}%`,
                                background: item.party === 'BJP' ? '#f97316' : item.party === 'INC' ? '#3b82f6' : '#8b5cf6'
                              }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Constituency wise detail viewer */}
              <div className="widget-card">
                <h3 className="widget-title">Constituency Detailed Breakdown</h3>
                <div className="form-group" style={{ marginBottom: '2rem', maxWidth: '400px' }}>
                  <label className="form-label">Select Constituency Assembly</label>
                  <select 
                    className="form-select" 
                    value={selectedResultsAssembly}
                    onChange={(e) => setSelectedResultsAssembly(e.target.value)}
                  >
                    {publicResultsData.assemblies.map(a => (
                      <option key={a.assembly_id} value={a.assembly_id}>{a.name}</option>
                    ))}
                  </select>
                </div>

                {selectedAssemblyDetail && (
                  <div>
                    {selectedAssemblyDetail.result_declared ? (
                      <>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
                          <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                            <div className="cm-title" style={{ fontSize: '0.75rem' }}>Total Votes Polled</div>
                            <div style={{ fontSize: '1.75rem', fontWeight: 800 }}>{selectedAssemblyDetail.total_votes}</div>
                          </div>
                          <div style={{ padding: '1rem', background: 'rgba(255,255,255,0.02)', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                            <div className="cm-title" style={{ fontSize: '0.75rem' }}>Voter Turnout</div>
                            <div style={{ fontSize: '1.75rem', fontWeight: 800 }}>{selectedAssemblyDetail.turnout_pct || 'N/A'}%</div>
                          </div>
                        </div>

                        <div className="table-wrapper">
                          <table className="table">
                            <thead>
                              <tr>
                                <th>Position</th>
                                <th>Candidate</th>
                                <th>Party</th>
                                <th>Votes Secured</th>
                                <th>Share %</th>
                              </tr>
                            </thead>
                            <tbody>
                              {selectedAssemblyDetail.results.map((cand, index) => {
                                const share = selectedAssemblyDetail.total_votes > 0 
                                  ? roundVal((cand.votes / selectedAssemblyDetail.total_votes) * 100)
                                  : 0;
                                return (
                                  <tr key={index}>
                                    <td>
                                      {index === 0 ? (
                                        <span className="badge badge-success" style={{ padding: '0.25rem 0.5rem' }}>Winner</span>
                                      ) : (
                                        <span>#{index + 1}</span>
                                      )}
                                    </td>
                                    <td>
                                      <span style={{ marginRight: '0.5rem', fontSize: '1.25rem' }}>{cand.symbol}</span>
                                      <strong>{cand.candidate_name}</strong>
                                    </td>
                                    <td>{cand.party_name}</td>
                                    <td>{cand.votes}</td>
                                    <td>{share}%</td>
                                  </tr>
                                );
                              })}
                            </tbody>
                          </table>
                        </div>
                      </>
                    ) : (
                      <p style={{ color: 'var(--text-secondary)' }}>Results details unavailable for this segment.</p>
                    )}
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      )}

      {/* CANDIDATE CRUD MODAL */}
      {showCandidateModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h2>{modalMode === 'add' ? 'Add Candidate' : 'Edit Candidate'}</h2>
              <button className="modal-close" onClick={() => setShowCandidateModal(false)}><X size={20} /></button>
            </div>

            <form onSubmit={handleCandidateSubmit}>
              <div className="form-group">
                <label className="form-label">Candidate Name</label>
                <input type="text" className="form-input" value={candName} onChange={(e) => setCandName(e.target.value)} required />
              </div>
              <div className="form-group">
                <label className="form-label">Party Affiliation</label>
                <select className="form-select" value={candParty} onChange={(e) => setCandParty(e.target.value)}>
                  <option value="BJP">BJP</option>
                  <option value="INC">INC</option>
                  <option value="AAP">AAP</option>
                  <option value="NPP">NPP</option>
                  <option value="IND">Independent (IND)</option>
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Constituency Assembly</label>
                <select className="form-select" value={candAssemblyId} onChange={(e) => setCandAssemblyId(e.target.value)}>
                  {assemblies.map(a => (
                    <option key={a.assembly_id} value={a.assembly_id}>{a.name} ({a.district})</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label className="form-label">Election Symbol Icon</label>
                <input type="text" className="form-input" placeholder="e.g. 🌸, 🖐️, 🔥" value={candSymbol} onChange={(e) => setCandSymbol(e.target.value)} required />
              </div>
              <div className="form-group">
                <label className="form-label">Candidate Serial Number (Optional)</label>
                <input type="number" className="form-input" placeholder="Leave blank to auto-increment" value={candSerialNo} onChange={(e) => setCandSerialNo(e.target.value)} />
              </div>

              <button type="submit" className="form-submit-btn" style={{ marginTop: '1.5rem' }}>
                {modalMode === 'add' ? 'Register Candidate' : 'Save Changes'}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

// Utility Helper
function roundVal(val) {
  return Math.round((val + Number.EPSILON) * 100) / 100;
}

export default App;
