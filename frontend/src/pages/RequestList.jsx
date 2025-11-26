import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { requestsAPI } from '../services/requests';
import { useAuth } from '../contexts/AuthContext';
import {
  DocumentTextIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline';

const RequestList = () => {
  const { user } = useAuth();
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({
    status: '',
    category: '',
    priority: '',
    search: '',
  });

  const pageSize = 20;

  const { data, isLoading, error } = useQuery(
    ['requests', page, filters],
    () => requestsAPI.getRequests({
      skip: (page - 1) * pageSize,
      limit: pageSize,
      ...filters,
    }),
    {
      keepPreviousData: true,
    }
  );

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPage(1);
  };

  const clearFilters = () => {
    setFilters({
      status: '',
      category: '',
      priority: '',
      search: '',
    });
    setPage(1);
  };

  const statusOptions = [
    { value: '', label: 'All Statuses' },
    { value: 'submitted', label: 'Submitted' },
    { value: 'under_review', label: 'Under Review' },
    { value: 'assigned', label: 'Assigned' },
    { value: 'in_progress', label: 'In Progress' },
    { value: 'completed', label: 'Completed' },
    { value: 'rejected', label: 'Rejected' },
    { value: 'closed', label: 'Closed' },
  ];

  const categoryOptions = [
    { value: '', label: 'All Categories' },
    { value: 'road_maintenance', label: 'Road Maintenance' },
    { value: 'street_lighting', label: 'Street Lighting' },
    { value: 'traffic_signals', label: 'Traffic Signals' },
    { value: 'park_maintenance', label: 'Park Maintenance' },
    { value: 'waste_management', label: 'Waste Management' },
    { value: 'water_sewer', label: 'Water & Sewer' },
    { value: 'noise_complaint', label: 'Noise Complaint' },
    { value: 'parking_issue', label: 'Parking Issue' },
    { value: 'other', label: 'Other' },
  ];

  const priorityOptions = [
    { value: '', label: 'All Priorities' },
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'urgent', label: 'Urgent' },
  ];

  const getStatusBadgeClass = (status) => {
    return `status-badge status-${status}`;
  };

  const getPriorityBadgeClass = (priority) => {
    return `status-badge priority-${priority}`;
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">Service Requests</h1>
            <Link
              to="/requests/new"
              className="btn-primary"
            >
              <DocumentTextIcon className="w-4 h-4 mr-2 inline" />
              New Request
            </Link>
          </div>
        </div>

        {/* Filters */}
        <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="form-label">Search</label>
              <div className="relative">
                <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search requests..."
                  value={filters.search}
                  onChange={(e) => handleFilterChange('search', e.target.value)}
                  className="form-input pl-10"
                />
              </div>
            </div>
            <div>
              <label className="form-label">Status</label>
              <select
                value={filters.status}
                onChange={(e) => handleFilterChange('status', e.target.value)}
                className="form-input"
              >
                {statusOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="form-label">Category</label>
              <select
                value={filters.category}
                onChange={(e) => handleFilterChange('category', e.target.value)}
                className="form-input"
              >
                {categoryOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="form-label">Priority</label>
              <select
                value={filters.priority}
                onChange={(e) => handleFilterChange('priority', e.target.value)}
                className="form-input"
              >
                {priorityOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
          <div className="mt-4 flex justify-end">
            <button
              onClick={clearFilters}
              className="btn-secondary"
            >
              <FunnelIcon className="w-4 h-4 mr-2 inline" />
              Clear Filters
            </button>
          </div>
        </div>

        {/* Requests List */}
        <div className="px-6 py-4">
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-2 text-sm text-gray-500">Loading requests...</p>
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <p className="text-red-600">Error loading requests: {error.message}</p>
            </div>
          ) : data?.items?.length === 0 ? (
            <div className="text-center py-8">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No requests found</h3>
              <p className="mt-1 text-sm text-gray-500">
                Try adjusting your filters or create a new request.
              </p>
              <div className="mt-6">
                <Link
                  to="/requests/new"
                  className="btn-primary"
                >
                  New Request
                </Link>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {data?.items?.map((request) => (
                <div key={request.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <Link
                        to={`/requests/${request.id}`}
                        className="text-lg font-semibold text-gray-900 hover:text-primary-600"
                      >
                        {request.title}
                      </Link>
                      <p className="mt-1 text-sm text-gray-600 line-clamp-2">
                        {request.description}
                      </p>
                      <div className="mt-2 flex items-center space-x-4 text-sm text-gray-500">
                        <span>ID: #{request.id}</span>
                        <span>Created: {new Date(request.created_at).toLocaleDateString()}</span>
                        {request.assigned_staff_name && (
                          <span>Assigned to: {request.assigned_staff_name}</span>
                        )}
                      </div>
                    </div>
                    <div className="ml-4 flex flex-col items-end space-y-2">
                      <span className={getStatusBadgeClass(request.status)}>
                        {request.status.replace('_', ' ').toUpperCase()}
                      </span>
                      <span className={getPriorityBadgeClass(request.priority)}>
                        {request.priority.toUpperCase()}
                      </span>
                      <span className="status-badge bg-gray-100 text-gray-800">
                        {request.category.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Pagination */}
        {data && data.total > pageSize && (
          <div className="px-6 py-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-700">
                Showing {((page - 1) * pageSize) + 1} to {Math.min(page * pageSize, data.total)} of {data.total} results
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => setPage(page - 1)}
                  disabled={page === 1}
                  className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setPage(page + 1)}
                  disabled={page * pageSize >= data.total}
                  className="px-3 py-1 border border-gray-300 rounded text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RequestList;