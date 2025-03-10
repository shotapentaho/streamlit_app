import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score

# Set page config to full-width layout
st.set_page_config(page_title="🌳 Decision Tree Classifier", layout="wide")

# Upload Dataset
uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

if uploaded_file is not None:
    # Read the CSV file
    df = pd.read_csv(uploaded_file)
    
    
    # Split the screen into two columns
    col1, col2 = st.columns([0.5, 0.5])  # 50-50 split
    
    with col1:
        st.write("### 📊 Preview of Dataset")
        st.write(df.head())

        # Select target column
        target_column = st.selectbox("Select Target Column (Label)", df.columns)

        # Select feature columns
        feature_columns = st.multiselect("Select Feature Columns", [col for col in df.columns if col != target_column])

        if target_column and feature_columns:
            # Prepare Data
            X = df[feature_columns]
            y = df[target_column]
            
            # Split Data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Decision Tree Parameters
            max_depth = st.slider("Select Max Depth of the Tree", 1, 20, 5)
            criterion = st.selectbox("Select Criterion", ["gini", "entropy"])

            # Train Decision Tree
            clf = DecisionTreeClassifier(max_depth=max_depth, criterion=criterion)
            clf.fit(X_train, y_train)

            # Predictions & Accuracy
            y_pred = clf.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            st.write(f"### ✅ Model Accuracy: **{accuracy:.2f}**")
            
    with col2:
        if target_column and feature_columns:
            st.header("🌳 Decision Tree Visualization")
        
            # Plot Decision Tree
            fig, ax = plt.subplots(figsize=(10, 6))
            #plot_tree(clf, feature_names=feature_columns, class_names=str(np.unique(y)), filled=True, rounded=True)
            plot_tree(clf, feature_names=feature_columns, class_names=[str(cls) for cls in np.unique(y)], filled=True, rounded=True)
            
            # Display tree with expander
            with st.expander("🔍 Click to Enlarge Decision Tree"):
                st.pyplot(fig)

        # Make Predictions
        st.write("### 🔍 Choose selection (left), to get tree and then predict!")
        input_data = [st.number_input(f"Enter value for {col}", value=float(X.iloc[0][col])) for col in feature_columns]

        if st.button("Predict"):
            prediction = clf.predict([input_data])
            st.write(f"### 🎯 Predicted Class: **{prediction[0]}**")
