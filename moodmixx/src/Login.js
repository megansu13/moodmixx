import React from 'react';
import spotifyLogo from "./Spotify_Logo_RGB_White.png"; 

function Login() {
  const handleLogin = () => {
    window.location.href =
      "/authorize";  // Adjust if your Flask app is on a different base URL
  };

  return (
    <div className="app">
      <h1 className="moodmixx-title">welcome to moodmixx!</h1>
      <button className="spotify-login-button" onClick={handleLogin}>
        <img src={spotifyLogo} alt="Spotify logo" />
        login
      </button>
    </div>
  );
}

export default Login;
