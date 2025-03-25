import streamlit as st
import numpy as np

# Initialize the game board in session state
if "board" not in st.session_state:
    st.session_state.board = np.full((3, 3), "", dtype=str)
    st.session_state.current_player = "X"

# Function to check for a winner
def check_winner(board):
    for row in board:
        if all(cell == row[0] and cell != "" for cell in row):
            return row[0]

    for col in board.T:
        if all(cell == col[0] and cell != "" for cell in col):
            return col[0]

    if all(board[i, i] == board[0, 0] and board[i, i] != "" for i in range(3)):
        return board[0, 0]
    
    if all(board[i, 2 - i] == board[0, 2] and board[i, 2 - i] != "" for i in range(3)):
        return board[0, 2]

    if "" not in board:
        return "Draw"
    
    return None

# Streamlit UI
st.title("🎯 Tic-Tac-Toe")

winner = check_winner(st.session_state.board)

if winner:
    st.success(f"🎉 {winner} wins!" if winner != "Draw" else "🤝 It's a Draw!")
    if st.button("Restart Game"):
        st.session_state.board = np.full((3, 3), "", dtype=str)
        st.session_state.current_player = "X"
        st.experimental_rerun()
else:
    st.write(f"**Current Player:** {st.session_state.current_player}")

    cols = st.columns(3)
    for i in range(3):
        for j in range(3):
            if st.session_state.board[i, j] == "":
                if cols[j].button(" ", key=f"{i}-{j}"):
                    st.session_state.board[i, j] = st.session_state.current_player
                    st.session_state.current_player = "O" if st.session_state.current_player == "X" else "X"
                    st.experimental_rerun()
            else:
                cols[j].write(f"**{st.session_state.board[i, j]}**")

