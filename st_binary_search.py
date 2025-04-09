import streamlit as st

def binary_search(arr, target):
    left, right = 0, len(arr) - 1
    steps = []

    while left <= right:
        mid = (left + right) // 2
        steps.append(f"Checking middle index {mid} → {arr[mid]}")
        if arr[mid] == target:
            steps.append(f"✅ Found {target} at index {mid}")
            return mid, steps
        elif arr[mid] < target:
            steps.append(f"{target} > {arr[mid]} → Search right half")
            left = mid + 1
        else:
            steps.append(f"{target} < {arr[mid]} → Search left half")
            right = mid - 1

    steps.append("❌ Not found")
    return -1, steps

# Streamlit UI
st.set_page_config(page_title="Binary Search Demo", layout="centered")
st.title("🔍 Binary Search Visualizer")

# Input
arr_input = st.text_input("Enter sorted numbers (comma-separated)", "1, 3, 5, 7, 9, 11, 13")
target = st.number_input("Enter number to search", step=1)

# Parse array
try:
    arr = [int(x.strip()) for x in arr_input.split(',')]
    arr.sort()  # Ensure sorted
except:
    st.error("Please enter valid integers separated by commas.")
    arr = []

if st.button("Search"):
    if not arr:
        st.warning("Please provide a sorted list of numbers.")
    else:
        index, steps = binary_search(arr, int(target))
        
        st.subheader("🔄 Search Steps")
        for step in steps:
            st.write(step)
        
        if index != -1:
            st.success(f"🎯 Number {target} found at index {index}")
        else:
            st.error("🔎 Number not found in the list.")
