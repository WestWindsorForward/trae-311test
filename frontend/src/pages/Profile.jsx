import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const Profile = () => {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);

  if (!user) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-600">Loading profile...</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="btn-secondary"
            >
              {isEditing ? 'Cancel' : 'Edit Profile'}
            </button>
          </div>
        </div>

        <div className="px-6 py-6">
          <div className="space-y-6">
            <div>
              <label className="form-label">Full Name</label>
              <input
                type="text"
                defaultValue={user.full_name}
                disabled={!isEditing}
                className="form-input disabled:bg-gray-50"
              />
            </div>

            <div>
              <label className="form-label">Email Address</label>
              <input
                type="email"
                defaultValue={user.email}
                disabled
                className="form-input disabled:bg-gray-50"
              />
              <p className="mt-1 text-sm text-gray-500">
                Email address cannot be changed.
              </p>
            </div>

            <div>
              <label className="form-label">Phone Number</label>
              <input
                type="tel"
                defaultValue={user.phone || ''}
                disabled={!isEditing}
                className="form-input disabled:bg-gray-50"
              />
            </div>

            <div>
              <label className="form-label">Role</label>
              <input
                type="text"
                value={user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                disabled
                className="form-input disabled:bg-gray-50"
              />
            </div>

            <div>
              <label className="form-label">Account Status</label>
              <input
                type="text"
                value={user.is_active ? 'Active' : 'Inactive'}
                disabled
                className="form-input disabled:bg-gray-50"
              />
            </div>

            <div>
              <label className="form-label">Member Since</label>
              <input
                type="text"
                value={new Date(user.created_at).toLocaleDateString()}
                disabled
                className="form-input disabled:bg-gray-50"
              />
            </div>
          </div>

          {isEditing && (
            <div className="mt-6 flex justify-end space-x-4">
              <button
                onClick={() => setIsEditing(false)}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  // TODO: Implement profile update
                  toast.success('Profile updated successfully!');
                  setIsEditing(false);
                }}
                className="btn-primary"
              >
                Save Changes
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Profile;