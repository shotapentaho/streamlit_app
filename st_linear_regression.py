import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Streamlit Page Configuration
st.set_page_config(page_title="Linear Regression App", layout="wide")

# Title
st.title("📈 Linear Regression on CSV Data")

# File Upload
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # Show dataset
    st.write("### 📊 Data Preview")
    st.write(df.head())

    # Select Features & Target
    target_column = st.selectbox("Select Target Column (Y)", df.columns)
    feature_columns = st.multiselect("Select Feature Columns (X)", [col for col in df.columns if col != target_column])

    if target_column and feature_columns:
        X = df[feature_columns]
        y = df[target_column]

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Train Model
        model = LinearRegression()
        model.fit(X_train, y_train)

        # Predictions
        y_pred = model.predict(X_test)

        # Metrics
        mse = mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        # Display Results
        st.write(f"### ✅ Model Performance")
        st.write(f"📉 Mean Squared Error (MSE): {mse:.2f}")
        st.write(f"📈 R² Score: {r2:.2f}")

        # Plot Results
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(y_test, y_pred, color="blue", alpha=0.5)
        ax.plot(y_test, y_test, color="red", linestyle="dashed", label="Perfect Fit")
        ax.set_xlabel("Actual Values")
        ax.set_ylabel("Predicted Values")
        ax.set_title("Actual vs. Predicted Values")
        ax.legend()
        st.pyplot(fig)

        # Show Predictions
        predictions_df = pd.DataFrame({"Actual": y_test, "Predicted": y_pred})
        st.write("### 🔍 Predictions", predictions_df.head())

