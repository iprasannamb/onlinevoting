const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

async function request(path, options = {}) {
  const url = `${BASE_URL}${path}`;
  
  // Setup credentials and headers
  options.credentials = 'include';
  options.headers = {
    ...options.headers,
  };
  
  if (options.body && !(options.body instanceof FormData)) {
    options.headers['Content-Type'] = 'application/json';
    if (typeof options.body === 'object') {
      options.body = JSON.stringify(options.body);
    }
  }

  try {
    const response = await fetch(url, options);
    
    // Attempt to parse JSON response
    let data = null;
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      data = await response.json();
    } else {
      data = { message: await response.text() };
    }
    
    if (!response.ok) {
      throw new Error(data.error || data.message || `Request failed with status ${response.status}`);
    }
    
    return data;
  } catch (error) {
    console.error(`API Error on ${path}:`, error);
    throw error;
  }
}

export const api = {
  // Session
  getSession: () => request('/api/session'),
  logout: () => request('/api/logout', { method: 'POST' }),
  
  // Auth
  login: (credentials) => request('/api/login', {
    method: 'POST',
    body: credentials
  }),
  registerVoter: (voterData) => request('/api/register_voter', {
    method: 'POST',
    body: voterData
  }),
  
  // Public Data
  getAssemblies: () => request('/api/assemblies'),
  getPublicResults: () => request('/api/public_results'),
  getPublicResultDetail: (assemblyId) => request(`/api/public_results/${assemblyId}`),
  
  // Voter Panel
  getVoterDashboard: () => request('/api/voter/dashboard'),
  castVote: (candidateId) => request('/api/vote', {
    method: 'POST',
    body: { candidate_id: candidateId }
  }),
  
  // Admin Panel
  getAdminDashboard: () => request('/api/admin/dashboard'),
  approveVoter: (voterId) => request(`/api/admin/approve_voter/${voterId}`, { method: 'POST' }),
  rejectVoter: (voterId) => request(`/api/admin/reject_voter/${voterId}`, { method: 'POST' }),
  
  approveCandidate: (candidateId) => request(`/api/admin/approve_candidate/${candidateId}`, { method: 'POST' }),
  rejectCandidate: (candidateId) => request(`/api/admin/reject_candidate/${candidateId}`, { method: 'POST' }),
  
  addCandidate: (candidateData) => request('/api/admin/add_candidate', {
    method: 'POST',
    body: candidateData
  }),
  editCandidate: (candidateId, candidateData) => request(`/api/admin/edit_candidate/${candidateId}`, {
    method: 'POST',
    body: candidateData
  }),
  deleteCandidate: (candidateId) => request(`/api/admin/delete_candidate/${candidateId}`, {
    method: 'DELETE'
  }),
  
  // Election Process
  startElection: () => request('/api/admin/election/start', { method: 'POST' }),
  pauseElection: () => request('/api/admin/election/pause', { method: 'POST' }),
  endElection: () => request('/api/admin/election/end', { method: 'POST' }),
  calculateResults: () => request('/api/admin/election/calculate_results', { method: 'POST' }),
  declareResults: () => request('/api/admin/election/declare_results', { method: 'POST' }),
  assignCM: (cmName) => request('/api/admin/assign_cm', {
    method: 'POST',
    body: { cm_name: cmName }
  })
};
