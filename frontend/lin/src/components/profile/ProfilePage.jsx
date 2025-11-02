import React, { useState, useEffect, useRef } from 'react';
import EditableField from './EditableField'; 

// --- Icons ---
const EditPictureIcon = () => ( <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" d="M6.827 6.175A2.31 2.31 0 015.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 00-1.134-.175 2.31 2.31 0 01-1.64-1.055l-.822-1.316a2.192 2.192 0 00-1.736-1.039 48.774 48.774 0 00-5.232 0 2.192 2.192 0 00-1.736 1.039l-.821 1.316z" /><path strokeLinecap="round" strokeLinejoin="round" d="M16.5 12.75a4.5 4.5 0 11-9 0 4.5 4.5 0 019 0zM18.75 10.5h.008v.008h-.008V10.5z" /></svg>);

// The base URL for your API.
const BASE_URL = 'http://127.0.0.1:8000';

function ProfilePage() {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const fileInputRef = useRef(null); // Ref for the hidden file input

    // Function to fetch the user profile
    const fetchUserProfile = async () => {
        try {
            const response = await fetch(`${BASE_URL}/users/me`);
            if (!response.ok) {
                throw new Error(`Network response was not ok: ${response.statusText}`);
            }
            const result = await response.json();
            if (result.success) {
                setProfile(result.data);
            } else {
                throw new Error(result.message || 'Failed to get user profile.');
            }
        } catch (e) {
            console.error("Failed to fetch user profile:", e);
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    // Fetch data on component mount
    useEffect(() => {
        fetchUserProfile();
    }, []);

    // Function to handle saving an updated field
    const handleUpdateProfile = async (fieldName, newValue) => {
        const originalProfile = { ...profile };
        setProfile(prev => ({ ...prev, [fieldName]: newValue }));

        try {
            const response = await fetch(`${BASE_URL}/users/me`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ [fieldName]: newValue }),
            });
            const result = await response.json();
            if (!result.success) {
                throw new Error(result.error.message || 'Failed to update profile.');
            }
            // Update state with the final confirmed data from the server
            setProfile(result.data);
        } catch (e) {
            console.error("API update error:", e);
            alert(`An error occurred: ${e.message}`);
            setProfile(originalProfile); // Revert on error
        }
    };

    // NEW: Function to handle file selection and trigger upload
    const handleFileChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            handleUploadPicture(file);
        }
    };

    // NEW: Function to upload the profile picture
    const handleUploadPicture = async (file) => {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(`${BASE_URL}/users/me/avatar`, {
                method: 'POST',
                body: formData,
            });
            const result = await response.json();
            if (result.success) {
                // Update the profile state with the new picture URL
                setProfile(result.data);
            } else {
                throw new Error(result.error.message || 'Failed to upload picture.');
            }
        } catch (e) {
            console.error("Upload error:", e);
            alert(`Upload failed: ${e.message}`);
        }
    };


    if (loading) return <div className="loading-message">Loading Profile...</div>;
    if (error) return <div className="loading-message" style={{color: 'red'}}>Error: {error}</div>;
    if (!profile) return <div className="loading-message">No profile data found.</div>;
    
    const profilePictureUrl = profile.profile_picture_url 
        ? `${BASE_URL}${profile.profile_picture_url}`
        : 'https://placehold.co/128x128/e2e8f0/64748b?text=User';

    return (
        <main className="profile-page-main">
            <header className="profile-header">
                {/* NEW: Container for picture and upload button */}
                <div className="profile-picture-container">
                    <img 
                        src={profilePictureUrl} 
                        alt="User Profile" 
                        className="profile-picture"
                        onError={(e) => { 
                            e.target.onerror = null; 
                            e.target.src=`https://placehold.co/128x128/e2e8f0/64748b?text=${profile.first_name[0] || 'U'}`; 
                        }}
                    />
                    <div className="profile-picture-overlay"></div>
                    <input 
                        type="file" 
                        ref={fileInputRef} 
                        onChange={handleFileChange}
                        style={{ display: 'none' }}
                        accept="image/png, image/jpeg, image/gif, image/webp"
                    />
                    <button 
                        className="profile-picture-edit-button"
                        onClick={() => fileInputRef.current.click()}
                    >
                        <EditPictureIcon />
                    </button>
                </div>

                <div className="profile-header-info">
                    <h2>{`${profile.first_name || ''} ${profile.last_name || ''}`}</h2>
                    <p>{profile.email}</p>
                </div>
            </header>

            <div className="profile-content">
                <div className="profile-info-card">
                    <div className="profile-card-header">
                        <h3>Personal Information</h3>
                    </div>
                    <div className="profile-details-grid">
                        <div className="profile-detail-item">
                            <label>First Name</label>
                            <EditableField fieldName="first_name" initialValue={profile.first_name || ''} onSave={handleUpdateProfile} />
                        </div>
                         <div className="profile-detail-item">
                            <label>Last Name</label>
                            <EditableField fieldName="last_name" initialValue={profile.last_name || ''} onSave={handleUpdateProfile} />
                        </div>
                        <div className="profile-detail-item">
                            <label>Username</label>
                            <EditableField fieldName="username" initialValue={profile.username} onSave={handleUpdateProfile} />
                        </div>
                         <div className="profile-detail-item">
                            <label>Email</label>
                            <span>{profile.email}</span>
                        </div>
                         <div className="profile-detail-item">
                            <label>Timezone</label>
                             <EditableField fieldName="timezone" initialValue={profile.timezone} onSave={handleUpdateProfile} />
                        </div>
                         <div className="profile-detail-item">
                            <label>Account Verified</label>
                            <span>{profile.is_verified ? 'Yes' : 'No'}</span>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}

export default ProfilePage;
