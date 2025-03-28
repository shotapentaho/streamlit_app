import streamlit as st
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from minisom import MiniSom

# Streamlit UI
st.set_page_config(page_title="Self-Organizing Maps", layout="wide")
st.title("🧠 Self-Organizing Maps (SOM) Visualization")
st.write("Upload a dataset, process will train a Self-Organizing Map (SOM) to cluster the data.")

# Upload CSV
uploaded_file = st.file_uploader("📂 Upload CSV File", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("📊 Preview of the Data:")
    st.dataframe(df.head())

    # Select features for SOM
    features = st.multiselect("🔢 Select Features for SOM", df.columns, default=df.columns[:3])
    
    if len(features) > 1:
        data = df[features].values
        
        # Convert data to DataFrame (if not already)
        data = pd.DataFrame(data)  

        # Convert all columns to numeric, forcing errors to NaN
        data = data.apply(pd.to_numeric, errors='coerce')

        # Fill NaNs with column mean (optional, or drop NaNs)
        data.fillna(data.mean(), inplace=True)

        # Normalize data
        eps = 1e-8  # Small constant to prevent division by zero
        data = (data - np.min(data, axis=0)) / (np.max(data, axis=0) - np.min(data, axis=0)+ eps)

        # SOM parameters
        x_dim, y_dim = 10, 10  # SOM Grid Size
        som = MiniSom(x_dim, y_dim, len(features), sigma=1.0, learning_rate=0.5)
        som.random_weights_init(data)
        som.train_random(data, 1000)  # Training for 1000 iterations

        weights = som.get_weights()  # ✅ This correctly gets the weight matrix
        # Generate heatmap
        heatmap_data = np.zeros((x_dim, y_dim))
        for i in range(x_dim):
            for j in range(y_dim):
                heatmap_data[i, j] = np.linalg.norm(weights[i, j])

        # Plot heatmap
        st.subheader("🔥 SOM Heatmap")
        fig, ax = plt.subplots(figsize=(6, 6))
        sns.heatmap(heatmap_data, cmap="coolwarm", ax=ax, square=True)
        st.pyplot(fig)

        # Assign clusters
        clusters = np.array([som.winner(x) for x in data])
        df["Cluster"] = [f"({c[0]},{c[1]})" for c in clusters]

        st.subheader("📌 Clustered Data")
        st.dataframe(df)

        # Display cluster count
        st.subheader("📊 Cluster Counts")
        st.bar_chart(df["Cluster"].value_counts())

    else:
        st.warning("⚠ Please select at least two features for SOM.")

else:
    st.info("📂 Please upload a dataset to begin.")
