import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score, classification_report, ConfusionMatrixDisplay

# Streamlit App Title
st.title("📊 SVM: Support Vector Machine Classifier for CSV Data")

# File Upload
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("### Preview of Uploaded Data:")
    st.write(df.head())

    # Select Target Column
    target_column = st.selectbox("Select Target Column (Label)", df.columns)

    # Handle Missing Values
    if st.checkbox("Drop missing values"):
        df = df.dropna()

    # Encode Categorical Target Column (if necessary)
    if df[target_column].dtype == "object":
        le = LabelEncoder()
        df[target_column] = le.fit_transform(df[target_column])

    # Select Features (All Columns Except Target)
    X = df.drop(columns=[target_column])
    y = df[target_column]

    # Convert Categorical Features (One-Hot Encoding)
    X = pd.get_dummies(X, drop_first=True)

    # Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Scale Features
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Sidebar Hyperparameter Selection
    st.sidebar.header("SVM Hyperparameters")
    kernel = st.sidebar.selectbox("Kernel", ["linear", "rbf", "poly", "sigmoid"])
    C = st.sidebar.slider("C (Regularization)", 0.01, 10.0, 1.0)
    gamma = st.sidebar.slider("Gamma (for rbf/poly)", 0.01, 1.0, 0.1)

    # Train SVM Model
    svm_model = SVC(kernel=kernel, C=C, gamma=gamma)
    svm_model.fit(X_train, y_train)

    # Model Evaluation
    y_pred = svm_model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    st.write(f"### Model Accuracy: **{accuracy:.2f}**")
    
    # Display Classification Report
    st.subheader("Classification Report")
    st.text(classification_report(y_test, y_pred))

    # Confusion Matrix
    st.subheader("Confusion Matrix")
    fig, ax = plt.subplots()
    ConfusionMatrixDisplay.from_estimator(svm_model, X_test, y_test, ax=ax)
    st.pyplot(fig)

    # PCA for Decision Boundary Visualization
    if X.shape[1] > 2:
        st.subheader("PCA Reduced 2D Decision Boundary")
        pca = PCA(n_components=2)
        X_reduced = pca.fit_transform(X)

        svm_reduced = SVC(kernel=kernel, C=C, gamma=gamma)
        svm_reduced.fit(X_reduced, y)

        x_min, x_max = X_reduced[:, 0].min() - 1, X_reduced[:, 0].max() + 1
        y_min, y_max = X_reduced[:, 1].min() - 1, X_reduced[:, 1].max() + 1
        xx, yy = np.meshgrid(np.linspace(x_min, x_max, 100), np.linspace(y_min, y_max, 100))
        
        Z = svm_reduced.predict(np.c_[xx.ravel(), yy.ravel()])
        Z = Z.reshape(xx.shape)

        fig, ax = plt.subplots()
        ax.contourf(xx, yy, Z, alpha=0.3)
        scatter = ax.scatter(X_reduced[:, 0], X_reduced[:, 1], c=y, edgecolors="k", cmap=plt.cm.Set1)
        ax.set_xlabel("PCA Feature 1")
        ax.set_ylabel("PCA Feature 2")
        ax.legend(handles=scatter.legend_elements()[0], labels=list(set(y)))
        st.pyplot(fig)

