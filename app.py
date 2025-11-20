import streamlit as st
import sqlite3
import pandas as pd
import time
import os

DB_NAME = "log.db"

st.set_page_config(page_title="Networking & Protocols Dashboard", layout="wide")

# Sidebar navigation
st.sidebar.title("📂 Navigation")
page = st.sidebar.radio("Select Page", ["Dashboard", "Settings", "About"])

# Cek apakah database ada
if not os.path.exists(DB_NAME):
    st.warning("Database not found. Please make sure 'log.db' from Week 7–8 exists.")
else:
    # Koneksi ke database
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM system_log", conn)

    # Ubah timestamp jadi datetime (kalau ada)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    if page == "Dashboard":
        st.title("🌐 Interactive Data Center Dashboard")

        # ============================
        # ✅ Auto-refresh / Manual refresh
        # ============================
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("🔄 Refresh Now"):
                st.experimental_rerun()
        with col_r2:
            auto_refresh = st.checkbox("Auto refresh every 5 seconds")
            if auto_refresh:
                time.sleep(5)
                st.experimental_rerun()

        # ============================
        # ✅ Sidebar filters
        #    - Ping Status
        #    - CPU Threshold
        # ============================
        st.sidebar.subheader("🔍 Filters")

        # Ping Status filter
        if "ping_status" in df.columns:
            ping_options = ["All"] + sorted(df["ping_status"].dropna().unique().tolist())
            ping_filter = st.sidebar.selectbox("Ping Status", ping_options, index=0)
        else:
            ping_filter = "All"

        # CPU Threshold filter
        if "cpu" in df.columns:
            cpu_threshold = st.sidebar.slider(
                "Minimum CPU Usage (%)",
                min_value=0,
                max_value=100,
                value=0,
                step=5
            )
        else:
            cpu_threshold = 0

        # ============================
        # ✅ Apply filters to dataframe
        # ============================
        filtered_df = df.copy()

        if "ping_status" in filtered_df.columns and ping_filter != "All":
            filtered_df = filtered_df[filtered_df["ping_status"] == ping_filter]

        if "cpu" in filtered_df.columns:
            filtered_df = filtered_df[filtered_df["cpu"] >= cpu_threshold]

        st.subheader("Filtered Records")
        st.write(f"Showing **{len(filtered_df)}** records after filtering.")
        st.dataframe(filtered_df, use_container_width=True)

        # ============================
        # ✅ Line charts for CPU, Memory, Disk
        # ============================
        st.subheader("📈 Resource Usage Over Time")

        chart_cols = [c for c in ["cpu", "memory", "disk"] if c in filtered_df.columns]

        if len(chart_cols) == 0:
            st.info("No CPU/Memory/Disk columns found in the data.")
        else:
            if "timestamp" in filtered_df.columns:
                chart_df = filtered_df.set_index("timestamp")[chart_cols].sort_index()
            else:
                chart_df = filtered_df[chart_cols]

            st.line_chart(chart_df)

    elif page == "Settings":
        st.title("⚙️ Settings Page")
        st.write("You can add custom configuration or thresholds here.")
        st.markdown("""
        **Examples of what you can configure:**
        - CPU alert threshold (e.g., > 80%)
        - Memory usage warning level
        - Disk usage warning level
        """)
    else:
        st.title("ℹ️ About")
        st.write("This dashboard was developed in Week 10 (Networking & Protocols).")
        st.write("It uses real monitoring data stored in `log.db` from Week 7–8.")

    conn.close()