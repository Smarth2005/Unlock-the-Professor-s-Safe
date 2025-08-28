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

    # ----------------- Reset Leaderboard Section -----------------
    st.write("### Manage Leaderboard")

    if st.button("🗑️ Reset Leaderboard"):
        # When the button is clicked, set a flag in the session state
        st.session_state.confirm_delete = True

    # Check if the confirmation flag is set
    if 'confirm_delete' in st.session_state and st.session_state.confirm_delete:
        st.warning("**Are you sure you want to delete ALL results? This action cannot be undone.**")
        
        col1, col2, _ = st.columns([1, 1, 5])

        with col1:
            if st.button("✅ Yes, Clear All", type="primary"):
                try:
                    # Perform the delete operation
                    supabase.table("results").delete().neq("id", 0).execute()
                    st.success("Leaderboard has been cleared!")
                    
                    # Unset the confirmation flag and rerun
                    del st.session_state.confirm_delete
                    st.rerun()

                except Exception as e:
                    st.error(f"Failed to clear leaderboard: {e}")
                    del st.session_state.confirm_delete # Also unset on failure

        with col2:
            if st.button("❌ Cancel"):
                # If cancelled, just unset the flag and rerun
                del st.session_state.confirm_delete
                st.rerun()

else:
    st.warning("⚠ No data found in database.")
