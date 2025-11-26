import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { requestsAPI } from '../services/requests';
import { useAuth } from '../contexts/AuthContext';
import toast from 'react-hot-toast';

const RequestDetail = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [newComment, setNewComment] = useState('');
  const [isInternalComment, setIsInternalComment] = useState(false);
  const [uploadingFile, setUploadingFile] = useState(null);

  const { data: request, isLoading, error } = useQuery(
    ['request', id],
    () => requestsAPI.getRequest(id),
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  const { data: attachments } = useQuery(
    ['request-attachments', id],
    () => requestsAPI.getAttachments(id),
    {
      enabled: !!id,
    }
  );

  const { data: comments } = useQuery(
    ['request-comments', id],
    () => requestsAPI.getComments(id, { include_internal: user?.role !== 'citizen' }),
    {
      enabled: !!id,
    }
  );

  const createCommentMutation = useMutation(
    (data) => requestsAPI.createComment(id, data),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['request-comments', id]);
        setNewComment('');
        toast.success('Comment added successfully!');
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Failed to add comment');
      },
    }
  );

  const uploadAttachmentMutation = useMutation(
    (file) => requestsAPI.uploadAttachment(id, file),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['request-attachments', id]);
        setUploadingFile(null);
        toast.success('File uploaded successfully!');
      },
      onError: (error) => {
        toast.error(error.response?.data?.detail || 'Failed to upload file');
        setUploadingFile(null);
      },
    }
  );

  const handleAddComment = (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    createCommentMutation.mutate({
      content: newComment,
      is_internal: isInternalComment,
    });
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploadingFile(file);
    uploadAttachmentMutation.mutate(file);
  };

  const getStatusBadgeClass = (status) => {
    return `status-badge status-${status}`;
  };

  const getPriorityBadgeClass = (priority) => {
    return `status-badge priority-${priority}`;
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Error loading request: {error.message}</p>
      </div>
    );
  }

  if (!request) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">Request not found</p>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Request Header */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{request.title}</h1>
              <p className="mt-1 text-sm text-gray-600">Request #{request.id}</p>
            </div>
            <div className="flex flex-col items-end space-y-2">
              <span className={getStatusBadgeClass(request.status)}>
                {request.status.replace('_', ' ').toUpperCase()}
              </span>
              <span className={getPriorityBadgeClass(request.priority)}>
                {request.priority.toUpperCase()}
              </span>
            </div>
          </div>
        </div>

        <div className="px-6 py-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Category</h3>
              <p className="mt-1 text-sm text-gray-900 capitalize">
                {request.category.replace('_', ' ')}
              </p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Created</h3>
              <p className="mt-1 text-sm text-gray-900">
                {new Date(request.created_at).toLocaleDateString()}
              </p>
            </div>
            {request.assigned_staff_name && (
              <div>
                <h3 className="text-sm font-medium text-gray-500">Assigned To</h3>
                <p className="mt-1 text-sm text-gray-900">{request.assigned_staff_name}</p>
              </div>
            )}
            {request.address && (
              <div>
                <h3 className="text-sm font-medium text-gray-500">Location</h3>
                <p className="mt-1 text-sm text-gray-900">{request.address}</p>
              </div>
            )}
          </div>

          <div className="mt-4">
            <h3 className="text-sm font-medium text-gray-500">Description</h3>
            <p className="mt-1 text-sm text-gray-900 whitespace-pre-wrap">
              {request.description}
            </p>
          </div>
        </div>
      </div>

      {/* Attachments */}
      {attachments && attachments.length > 0 && (
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-medium text-gray-900">Attachments</h2>
          </div>
          <div className="px-6 py-4">
            <div className="space-y-2">
              {attachments.map((attachment) => (
                <div key={attachment.id} className="flex items-center justify-between p-3 border border-gray-200 rounded">
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {attachment.original_filename}
                    </p>
                    <p className="text-xs text-gray-500">
                      {attachment.file_size} bytes • {attachment.mime_type}
                    </p>
                    {attachment.description && (
                      <p className="text-xs text-gray-600 mt-1">{attachment.description}</p>
                    )}
                  </div>
                  <div className="flex items-center space-x-2">
                    {attachment.is_scanned === 1 && (
                      <span className="text-xs text-green-600">✓ Clean</span>
                    )}
                    {attachment.is_scanned === 2 && (
                      <span className="text-xs text-red-600">⚠ Infected</span>
                    )}
                    {attachment.is_scanned === 0 && (
                      <span className="text-xs text-yellow-600">⟳ Scanning</span>
                    )}
                    <a
                      href={`/uploads/${attachment.filename}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-primary-600 hover:text-primary-500"
                    >
                      Download
                    </a>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* File Upload */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Add Attachment</h2>
        </div>
        <div className="px-6 py-4">
          <div className="flex items-center space-x-4">
            <input
              type="file"
              onChange={handleFileUpload}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
              disabled={uploadAttachmentMutation.isLoading}
            />
            {uploadAttachmentMutation.isLoading && (
              <span className="text-sm text-gray-500">Uploading...</span>
            )}
          </div>
        </div>
      </div>

      {/* Comments */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Comments</h2>
        </div>
        <div className="px-6 py-4">
          {/* Add Comment */}
          <form onSubmit={handleAddComment} className="mb-6">
            <div>
              <label htmlFor="comment" className="form-label">
                Add Comment
              </label>
              <textarea
                id="comment"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                rows={3}
                className="form-input"
                placeholder="Add a comment..."
              />
            </div>
            {user?.role !== 'citizen' && (
              <div className="mt-2">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={isInternalComment}
                    onChange={(e) => setIsInternalComment(e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Internal comment (staff only)</span>
                </label>
              </div>
            )}
            <div className="mt-4">
              <button
                type="submit"
                disabled={!newComment.trim() || createCommentMutation.isLoading}
                className="btn-primary"
              >
                {createCommentMutation.isLoading ? 'Adding...' : 'Add Comment'}
              </button>
            </div>
          </form>

          {/* Comments List */}
          {comments && comments.length > 0 ? (
            <div className="space-y-4">
              {comments.map((comment) => (
                <div key={comment.id} className="border-l-4 border-gray-200 pl-4">
                  <div className="flex items-start justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{comment.author_name}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(comment.created_at).toLocaleString()}
                      </p>
                    </div>
                    {comment.is_internal && (
                      <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                        Internal
                      </span>
                    )}
                  </div>
                  <p className="mt-2 text-sm text-gray-700 whitespace-pre-wrap">
                    {comment.content}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No comments yet. Be the first to comment!</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default RequestDetail;