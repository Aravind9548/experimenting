import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [genre, setGenre] = useState('');
  const [artist, setArtist] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [currentSong, setCurrentSong] = useState(null);

  // Load favorites from localStorage on app start
  useEffect(() => {
    const storedFavorites = localStorage.getItem('favorites');
    if (storedFavorites) {
      setFavorites(JSON.parse(storedFavorites));
    }
  }, []);

  // Save to localStorage whenever favorites change
  useEffect(() => {
    localStorage.setItem('favorites', JSON.stringify(favorites));
  }, [favorites]);

  const handleRecommend = async () => {
    if (!genre && !artist) return;
    
    setLoading(true);
    try {
      const response = await fetch(`http://127.0.0.1:5000/recommend?genre=${genre}&artist=${artist}`);
      const data = await response.json();
      
      // Add an ID to each song for tracking purposes
      const enhancedData = data.map((song, index) => ({
        ...song,
        id: `song-${Date.now()}-${index}`
      }));
      
      setRecommendations(enhancedData);
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveToFavorites = (song) => {
    if (!favorites.find(fav => fav.id === song.id)) {
      setFavorites([...favorites, song]);
    }
  };

  const removeFromFavorites = (songId) => {
    const updated = favorites.filter(fav => fav.id !== songId);
    setFavorites(updated);
  };

  const openPreviewModal = (song) => {
    setCurrentSong(song);
    setShowModal(true);
  };

  const closePreviewModal = () => {
    setCurrentSong(null);
    setShowModal(false);
  };

  const extractYouTubeQuery = (url) => {
    const searchParams = new URL(url).searchParams;
    return searchParams.get('search_query') || '';
  };

  const getEmbedUrl = (searchUrl) => {
    const query = extractYouTubeQuery(searchUrl);
    return `https://www.youtube.com/embed?videoseries?search_query=${query}&autoplay=1`;
  };

  return (
    <div className="App">
      <header className="app-header">
        <div className="logo-container">
          <img src="/api/placeholder/40/40" alt="headphones" className="app-logo" />
          <h1>Music Recommender</h1>
        </div>
      </header>

      <div className="search-container">
        <input
          type="text"
          placeholder="Enter Genre"
          value={genre}
          onChange={e => setGenre(e.target.value)}
          className="search-input"
        />
        <input
          type="text"
          placeholder="Enter Artist"
          value={artist}
          onChange={e => setArtist(e.target.value)}
          className="search-input"
        />
        <button 
          className="recommend-button"
          onClick={handleRecommend}
          disabled={loading}
        >
          {loading ? 'Searching...' : 'Recommend'}
        </button>
      </div>

      <div className="content-section">
        <div className="song-section">
          <h2 className="section-title">
            <span className="music-icon">♫</span> Recommended Songs
          </h2>
          
          {loading ? (
            <div className="loading-indicator">
              <div className="spinner"></div>
              <p>Finding music for you...</p>
            </div>
          ) : recommendations.length > 0 ? (
            <div className="song-list">
              {recommendations.map((song) => (
                <div className="song-item" key={song.id}>
                  <div className="song-details">
                    <div className="song-title">{song.track_name}</div>
                    <div className="song-artist">by {song.artists}</div>
                    <div className="song-genre">Genre: {song.track_genre}</div>
                  </div>
                  <div className="song-actions">
                    <a 
                      href={song.youtube_url} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="preview-link"
                      onClick={(e) => {
                        e.preventDefault();
                        openPreviewModal(song);
                      }}
                    >
                      ▶ Preview on YouTube
                    </a>
                    <button 
                      className="save-button"
                      onClick={() => saveToFavorites(song)}
                    >
                      ❤️ Save
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="empty-message">No recommendations yet. Try entering a genre or artist!</p>
          )}
        </div>

        {favorites.length > 0 && (
          <div className="song-section">
            <h2 className="section-title">
              <span className="star-icon">⭐</span> Favorite Songs
            </h2>
            <div className="song-list">
              {favorites.map((fav) => (
                <div className="song-item" key={fav.id}>
                  <div className="song-details">
                    <div className="song-title">{fav.track_name}</div>
                    <div className="song-artist">by {fav.artists}</div>
                    <div className="song-genre">Genre: {fav.track_genre}</div>
                  </div>
                  <div className="song-actions">
                    <a 
                      href={fav.youtube_url} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      className="preview-link"
                      onClick={(e) => {
                        e.preventDefault();
                        openPreviewModal(fav);
                      }}
                    >
                      ▶ Preview on YouTube
                    </a>
                    <button 
                      className="remove-button"
                      onClick={() => removeFromFavorites(fav.id)}
                    >
                      🗑️ Remove
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {showModal && currentSong && (
        <div className="modal-overlay" onClick={closePreviewModal}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={closePreviewModal}>×</button>
            <iframe
              src={getEmbedUrl(currentSong.youtube_url)}
              title={`${currentSong.track_name} by ${currentSong.artists}`}
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
              className="youtube-frame"
            ></iframe>
            <div className="modal-song-details">
              <h3>{currentSong.track_name}</h3>
              <p>by {currentSong.artists}</p>
              <p>Genre: {currentSong.track_genre}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;