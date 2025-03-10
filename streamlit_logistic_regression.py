import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns

# Streamlit UI
st.set_page_config(page_title="logistic regression classifier", layout="wide")

st.title("📊 Logistic Regression Classifier")

# Upload CSV File
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("### Dataset Preview")
    st.dataframe(df.head())

    # Select Features and Target
    target_col = st.selectbox("Select Target Column", df.columns)
    feature_cols = st.multiselect("Select Feature Columns", df.columns.drop(target_col))

    if feature_cols:
        X = df[feature_cols]
        y = df[target_col]

        # Split Data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Standardize Features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        # Train Logistic Regression Model
        model = LogisticRegression()
        model.fit(X_train_scaled, y_train)

        # Make Predictions
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)

        # Display Results
        st.write(f"### ✅ Model Accuracy: {accuracy:.2f}")
        st.write("### 📊 Classification Report")
        st.text(classification_report(y_test, y_pred))

        # Confusion Matrix
        st.write("### 🔍 Confusion Matrix")
        fig, ax = plt.subplots()
        sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt="d", cmap="Blues", ax=ax)
        st.pyplot(fig)

        # Decision Boundary (Only for 2D Features)
        if len(feature_cols) == 2:
            st.write("### 🏞 Decision Boundary")
            x_min, x_max = X_train_scaled[:, 0].min() - 1, X_train_scaled[:, 0].max() + 1
            y_min, y_max = X_train_scaled[:, 1].min() - 1, X_train_scaled[:, 1].max() + 1
            xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100), np.linspace(y_min, y_max, 100))
            Z = model.predict(np.c_[xx.ravel(), yy.ravel()])
            Z = Z.reshape(xx.shape)

            fig, ax = plt.subplots()
            ax.contourf(xx, yy, Z, alpha=0.3)
            scatter = ax.scatter(X_test_scaled[:, 0], X_test_scaled[:, 1], c=y_test, edgecolor="k", cmap="coolwarm")
            plt.xlabel(feature_cols[0])
            plt.ylabel(feature_cols[1])
            st.pyplot(fig)

