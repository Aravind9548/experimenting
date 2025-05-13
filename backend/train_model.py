import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import pickle

# Load data
df = pd.read_csv('clustered_data.csv')

# Select numeric features for clustering
features = df.select_dtypes(include=['float64', 'int64'])

# Normalize
scaler = StandardScaler()
scaled = scaler.fit_transform(features)

# Train KMeans
kmeans = KMeans(n_clusters=10, random_state=42)
kmeans.fit(scaled)

# Save model
with open('kmeans_model.pkl', 'wb') as f:
    pickle.dump(kmeans, f)

# Save scaler too
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
