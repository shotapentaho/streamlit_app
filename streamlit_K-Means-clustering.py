import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Set Streamlit Page Configuration
st.set_page_config(page_title="K-Means Clustering", layout="wide")

# Title
st.title("🔍 K-Means Clustering with Streamlit")

# Upload CSV File
uploaded_file = st.file_uploader("📂 Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    # Read CSV
    df = pd.read_csv(uploaded_file)
    
    # Split the screen into two columns
    col1, col2 = st.columns([0.5, 0.5])  # 50-50 split
    
    with col1:
        # Show dataset preview
        st.write("### 📊 Data Preview")
        st.write(df.head(100))

        # Select Features for Clustering
        selected_columns = st.multiselect("🔹 Select Features for Clustering", df.columns)

        if selected_columns:
            X = df[selected_columns]
            
            # Standardize Features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)

            # Select Number of Clusters
            k = st.slider("🔢 Select Number of Clusters (K)", min_value=2, max_value=10, value=3)

            # Apply K-Means Clustering
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(X_scaled)
            df["Cluster"] = clusters  # Assign cluster labels to dataset

            # Display Clustered Data
            st.write("### 📌 Clustered Data")
            st.write(df.head())

            # Cluster Centers
            st.write("### 📍 Cluster Centers")
            st.write(pd.DataFrame(kmeans.cluster_centers_, columns=selected_columns))
    with col2:
            # Plot Clusters (if at least 2 selected features)
            if len(selected_columns) >= 2:
                st.write("### 📊 Cluster Visualization")

                fig, ax = plt.subplots(figsize=(8, 6))
                sns.scatterplot(x=X[selected_columns[0]], y=X[selected_columns[1]], hue=df["Cluster"], palette="viridis", s=100)
                plt.xlabel(selected_columns[0])
                plt.ylabel(selected_columns[1])
                plt.title("K-Means Clustering Visualization")
                plt.legend(title="Cluster")
                st.pyplot(fig)

