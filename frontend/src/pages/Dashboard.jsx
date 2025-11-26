import React from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { requestsAPI } from '../services/requests';
import { useAuth } from '../contexts/AuthContext';
import {
  DocumentTextIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationCircleIcon,
} from '@heroicons/react/24/outline';

const Dashboard = () => {
  const { user } = useAuth();

  const { data: stats, isLoading } = useQuery(
    ['dashboard-stats'],
    async () => {
      const response = await requestsAPI.getRequests({ limit: 1 });
      return response;
    },
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  const getStatusCounts = () => {
    if (!stats?.items) return {};
    
    const counts = {
      submitted: 0,
      under_review: 0,
      assigned: 0,
      in_progress: 0,
      completed: 0,
      rejected: 0,
      closed: 0,
    };

    stats.items.forEach(item => {
      counts[item.status] = (counts[item.status] || 0) + 1;
    });

    return counts;
  };

  const statusCounts = getStatusCounts();

  const quickActions = [
    {
      name: 'New Request',
      description: 'Submit a new service request',
      href: '/requests/new',
      icon: DocumentTextIcon,
      color: 'bg-blue-500',
    },
    {
      name: 'View Requests',
      description: 'Browse all your requests',
      href: '/requests',
      icon: ClockIcon,
      color: 'bg-green-500',
    },
  ];

  if (user?.role !== 'citizen') {
    quickActions.push({
      name: 'Staff Dashboard',
      description: 'Manage assigned requests',
      href: '/requests?filter=assigned',
      icon: CheckCircleIcon,
      color: 'bg-purple-500',
    });
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900">
            Welcome back, {user?.full_name}!
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            Here's what's happening with your service requests.
          </p>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {quickActions.map((action) => (
          <Link
            key={action.name}
            to={action.href}
            className="relative block w-full rounded-lg border-2 border-dashed border-gray-300 p-6 text-center hover:border-gray-400 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
          >
            <action.icon className="mx-auto h-12 w-12 text-gray-400" />
            <span className="mt-2 block text-sm font-semibold text-gray-900">
              {action.name}
            </span>
            <span className="mt-1 block text-sm text-gray-500">
              {action.description}
            </span>
          </Link>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Recent Activity</h2>
        </div>
        <div className="p-6">
          {isLoading ? (
            <div className="text-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p className="mt-2 text-sm text-gray-500">Loading recent activity...</p>
            </div>
          ) : (
            <div className="text-center py-8">
              <ExclamationCircleIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No recent activity</h3>
              <p className="mt-1 text-sm text-gray-500">
                Get started by creating a new service request.
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
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;