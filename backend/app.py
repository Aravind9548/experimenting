from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os
from flask_cors import CORS

# Initialize Flask app
app = app = Flask(__name__, static_folder='build', static_url_path='/')

CORS(app)  # Enable CORS for all routes

# Load dataset
df = pd.read_csv('clustered_data.csv')
df.fillna('', inplace=True)

# Define features for recommendation
features = ['danceability', 'energy', 'acousticness', 'instrumentalness', 'valence', 'tempo']

# Preprocess data
scaler = StandardScaler()
X = scaler.fit_transform(df[features])

# Train KMeans model
kmeans = KMeans(n_clusters=10, random_state=42)
df['cluster'] = kmeans.fit_predict(X)

# Create a feature matrix for similarity calculation
feature_matrix = X
@app.route("/api/placeholder/<int:w>/<int:h>")
def placeholder(w, h):
    return jsonify({"message": f"Placeholder {w}x{h}"})

@app.route("/recommend", methods=["GET"])
def recommend():
    genre = request.args.get("genre", "").lower()
    artist = request.args.get("artist", "").lower()
    
    # Track processing time and status
    print(f"Processing recommendation request for genre: {genre}, artist: {artist}")
    
    try:
        # Initial filtering based on user input
        if genre and artist:
            filtered_df = df[(df['track_genre'].str.lower().str.contains(genre, na=False)) & 
                            (df['artists'].str.lower().str.contains(artist, na=False))]
            
            # If no direct matches, try finding songs from the same genre cluster
            if len(filtered_df) < 5:
                genre_matches = df[df['track_genre'].str.lower().str.contains(genre, na=False)]
                if len(genre_matches) > 0:
                    # Find clusters that contain this genre
                    genre_clusters = genre_matches['cluster'].unique()
                    # Get songs from those clusters
                    cluster_matches = df[df['cluster'].isin(genre_clusters)]
                    # Prioritize songs that match the artist if available
                    artist_matches = cluster_matches[cluster_matches['artists'].str.lower().str.contains(artist, na=False)]
                    if len(artist_matches) > 0:
                        filtered_df = pd.concat([filtered_df, artist_matches]).drop_duplicates()
                    else:
                        filtered_df = pd.concat([filtered_df, cluster_matches.sample(min(10, len(cluster_matches)))]).drop_duplicates()
        
        elif genre:
            filtered_df = df[df['track_genre'].str.lower().str.contains(genre, na=False)]
            
            # If still too few results, find similar genres based on audio features
            if len(filtered_df) < 5:
                # Get average features for this genre
                genre_matches = df[df['track_genre'].str.lower().str.contains(genre, na=False)]
                if len(genre_matches) > 0:
                    genre_clusters = genre_matches['cluster'].unique()
                    filtered_df = pd.concat([filtered_df, df[df['cluster'].isin(genre_clusters)].sample(min(10, len(df[df['cluster'].isin(genre_clusters)])))]).drop_duplicates()
        
        elif artist:
            filtered_df = df[df['artists'].str.lower().str.contains(artist, na=False)]
            
            # If too few results, find artists with similar style
            if len(filtered_df) < 5:
                artist_matches = df[df['artists'].str.lower().str.contains(artist, na=False)]
                if len(artist_matches) > 0:
                    artist_clusters = artist_matches['cluster'].unique()
                    filtered_df = pd.concat([filtered_df, df[df['cluster'].isin(artist_clusters)].sample(min(10, len(df[df['cluster'].isin(artist_clusters)])))]).drop_duplicates()
        
        else:
            # If no inputs provided, return popular songs from random clusters
            random_clusters = np.random.choice(df['cluster'].unique(), 3, replace=False)
            filtered_df = df[df['cluster'].isin(random_clusters)].sample(min(10, len(df[df['cluster'].isin(random_clusters)])))
        
        # Ensure we have results
        if len(filtered_df) == 0:
            # Return some general popular songs if no matches
            filtered_df = df.sample(10)
        
        # Limit to top 10 results
        top_results = filtered_df.head(10)
        
        # Format recommendations as JSON
        recommendations = []
        for _, row in top_results.iterrows():
            # Create a more accurate YouTube search query
            clean_title = row['track_name'].replace("'", "").replace('"', '')
            clean_artist = row['artists'].replace("'", "").replace('"', '')
            query = f"{clean_artist} {clean_title} official"
            youtube_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
            
            # Add track information including audio features
            track_info = {
                "track_name": row['track_name'],
                "artists": row['artists'],
                "track_genre": row['track_genre'],
                "youtube_url": youtube_url,
                "audio_features": {
                    "danceability": float(row['danceability']) if 'danceability' in row else 0,
                    "energy": float(row['energy']) if 'energy' in row else 0,
                    "acousticness": float(row['acousticness']) if 'acousticness' in row else 0,
                    "instrumentalness": float(row['instrumentalness']) if 'instrumentalness' in row else 0,
                    "valence": float(row['valence']) if 'valence' in row else 0,
                    "tempo": float(row['tempo']) if 'tempo' in row else 0
                }
            }
            recommendations.append(track_info)
        
        print(f"Found {len(recommendations)} recommendations")
        return jsonify(recommendations)
        
    except Exception as e:
        print(f"Error processing recommendation: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Add health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "ok", "message": "Music Recommender API is running"})

# Serve React frontend
@app.route('/')
@app.route('/<path:path>')
def serve_react(path=''):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    print("Starting Music Recommender API...")
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)