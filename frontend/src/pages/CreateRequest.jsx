import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useMutation } from 'react-query';
import { requestsAPI } from '../services/requests';
import toast from 'react-hot-toast';
import MapPicker from '../components/MapPicker';

const CreateRequest = () => {
  const navigate = useNavigate();
  const { register, handleSubmit, formState: { errors }, setValue } = useForm();
  const [isSubmitting, setIsSubmitting] = useState(false);

  const createRequestMutation = useMutation(
    (data) => requestsAPI.createRequest(data),
    {
      onSuccess: (data) => {
        toast.success('Request created successfully!');
        navigate(`/requests/${data.id}`);
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Failed to create request');
        setIsSubmitting(false);
      },
    }
  );

  const onSubmit = async (data) => {
    setIsSubmitting(true);
    createRequestMutation.mutate(data);
  };

  const categoryOptions = [
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
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'urgent', label: 'Urgent' },
  ];

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-900">Create Service Request</h1>
          <p className="mt-1 text-sm text-gray-600">
            Submit a new service request to the township.
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="px-6 py-6 space-y-6">
          <div>
            <label htmlFor="title" className="form-label">
              Title *
            </label>
            <input
              {...register('title', {
                required: 'Title is required',
                minLength: {
                  value: 3,
                  message: 'Title must be at least 3 characters',
                },
                maxLength: {
                  value: 200,
                  message: 'Title must not exceed 200 characters',
                },
              })}
              type="text"
              className="form-input"
              placeholder="Brief description of the issue"
            />
            {errors.title && (
              <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="category" className="form-label">
              Category *
            </label>
            <select
              {...register('category', {
                required: 'Category is required',
              })}
              className="form-input"
            >
              <option value="">Select a category</option>
              {categoryOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {errors.category && (
              <p className="mt-1 text-sm text-red-600">{errors.category.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="priority" className="form-label">
              Priority *
            </label>
            <select
              {...register('priority', {
                required: 'Priority is required',
              })}
              className="form-input"
            >
              <option value="">Select a priority</option>
              {priorityOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
            {errors.priority && (
              <p className="mt-1 text-sm text-red-600">{errors.priority.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="description" className="form-label">
              Description *
            </label>
            <textarea
              {...register('description', {
                required: 'Description is required',
                minLength: {
                  value: 10,
                  message: 'Description must be at least 10 characters',
                },
                maxLength: {
                  value: 2000,
                  message: 'Description must not exceed 2000 characters',
                },
              })}
              rows={4}
              className="form-input"
              placeholder="Please provide a detailed description of the issue..."
            />
            {errors.description && (
              <p className="mt-1 text-sm text-red-600">{errors.description.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="address" className="form-label">
              Location/Address
            </label>
            <input
              {...register('address')}
              type="text"
              className="form-input"
              placeholder="Street address or location description (optional)"
            />
          </div>

          <div>
            <label className="form-label">Map Location</label>
            <MapPicker
              value={null}
              onChange={(latlng) => {
                const { lat, lng } = latlng
                setValue('latitude', lat)
                setValue('longitude', lng)
              }}
            />
            <div className="grid grid-cols-2 gap-4 mt-2">
              <input {...register('latitude')} type="number" step="any" className="form-input" placeholder="Latitude" />
              <input {...register('longitude')} type="number" step="any" className="form-input" placeholder="Longitude" />
            </div>
          </div>

          <div className="flex items-center">
            <input
              {...register('is_anonymous')}
              type="checkbox"
              className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
            />
            <label htmlFor="is_anonymous" className="ml-2 block text-sm text-gray-900">
              Submit this request anonymously
            </label>
          </div>

          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => navigate('/requests')}
              className="btn-secondary"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="btn-primary"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Creating...' : 'Create Request'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateRequest;
