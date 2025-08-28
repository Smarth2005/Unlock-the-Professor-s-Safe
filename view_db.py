import pandas as pd
import streamlit as st
from supabase import create_client, Client

st.title("📊 Game Results Leaderboard")

# ----------------- Supabase Setup -----------------
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ----------------- Fetch Results -----------------
response = supabase.table("results").select("*").execute()
data = response.data

if data:
    df = pd.DataFrame(data)

    st.write("### All Results")
    st.dataframe(df)

    if "puzzles_solved" in df.columns:
        # Leaderboard sorted: highest puzzles_solved, then fastest time
        sort_cols = ["puzzles_solved"]
        ascending = [False]

        if "total_time_seconds" in df.columns:
            sort_cols.append("total_time_seconds")
            ascending.append(True)

        leaderboard = df.sort_values(by=sort_cols, ascending=ascending)

        st.write("### 🏆 Leaderboard")
        st.dataframe(leaderboard)

    # ----------------- Reset Leaderboard -----------------
    if st.button("🗑️ Reset Leaderboard"):
        st.warning("This will delete ALL results!")
        confirm = st.checkbox("Yes, clear the leaderboard")
        if confirm:
            supabase.table("results").delete().execute()

            st.success("Leaderboard has been cleared ✅")
else:
    st.warning("⚠ No data found in database.")
