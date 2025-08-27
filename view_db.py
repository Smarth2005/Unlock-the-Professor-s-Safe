import sqlite3
import pandas as pd
import streamlit as st

st.title("📊 Game Results Leaderboard")

conn = sqlite3.connect("game_results.db")

tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)

if not tables.empty:
    table_name = "results"
    df = pd.read_sql_query(f"SELECT * FROM {table_name};", conn)

    st.write("### All Results")
    st.dataframe(df)

    if "puzzles_solved" in df.columns:
        leaderboard = df.sort_values(by="puzzles_solved", ascending=False)
        st.write("### 🏆 Leaderboard")
        st.dataframe(leaderboard)

    if st.button("🗑️ Reset Leaderboard"):
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name};")
        conn.commit()
        st.success("Leaderboard has been cleared ✅")
else:
    st.warning("⚠ No tables found in database.")

conn.close()
