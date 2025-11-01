from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
import hdbscan
import numpy as np

app = FastAPI(title="Trend Detector")


class Docs(BaseModel):
    texts: list[str]


@app.post("/clusters")
def clusters(data: Docs):
    vec = TfidfVectorizer(max_df=0.9, min_df=2, ngram_range=(1, 2))
    X = vec.fit_transform(data.texts)
    
    clusterer = hdbscan.HDBSCAN(min_cluster_size=2, gen_min_span_tree=True)
    clusterer.fit(X)
    
    labels = clusterer.labels_.tolist()
    
    # To get top terms, we need to calculate cluster centroids manually
    # HDBSCAN does not provide centroids directly
    
    unique_labels = set(labels)
    clusters_out = []
    terms = vec.get_feature_names_out()

    for cluster_id in unique_labels:
        if cluster_id == -1:  # Skip noise points
            continue
        
        # Get all points in the current cluster
        indices = [i for i, label in enumerate(labels) if label == cluster_id]
        cluster_points = X[indices]
        
        # Calculate the centroid of the cluster
        centroid = np.mean(cluster_points, axis=0)
        
        # Get top terms from the centroid
        # The centroid is a dense vector, so we need to convert it to an array
        centroid_array = centroid.A.flatten()
        top_terms_indices = centroid_array.argsort()[-8:][::-1]
        top_terms = [terms[i] for i in top_terms_indices]
        
        clusters_out.append({"cluster": cluster_id, "top_terms": top_terms})

    return {"labels": labels, "clusters": clusters_out}
