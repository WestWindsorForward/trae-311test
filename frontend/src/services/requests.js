import api from './api';

export const requestsAPI = {
  // Service requests
  getRequests: async (params = {}) => {
    const response = await api.get('/requests', { params });
    return response.data;
  },

  getRequest: async (id) => {
    const response = await api.get(`/requests/${id}`);
    return response.data;
  },

  createRequest: async (requestData) => {
    const response = await api.post('/requests', requestData);
    return response.data;
  },

  updateRequest: async (id, requestData) => {
    const response = await api.put(`/requests/${id}`, requestData);
    return response.data;
  },

  assignRequest: async (id, staffId) => {
    const response = await api.post(`/requests/${id}/assign`, { staff_id: staffId });
    return response.data;
  },

  updateRequestStatus: async (id, status) => {
    const response = await api.post(`/requests/${id}/status`, { status });
    return response.data;
  },

  // Attachments
  uploadAttachment: async (requestId, file, description = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (description) {
      formData.append('description', description);
    }
    
    const response = await api.post(`/requests/${requestId}/attachments`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getAttachments: async (requestId) => {
    const response = await api.get(`/requests/${requestId}/attachments`);
    return response.data;
  },

  // Comments
  createComment: async (requestId, commentData) => {
    const response = await api.post(`/requests/${requestId}/comments`, commentData);
    return response.data;
  },

  getComments: async (requestId, params = {}) => {
    const response = await api.get(`/requests/${requestId}/comments`, { params });
    return response.data;
  },
};