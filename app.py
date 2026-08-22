import os
from datetime import date, datetime, timedelta
import pandas as pd
import streamlit as st

DATA_FILE = "life_chart_data.csv"
LAB_FILE = "lab_tests.csv"

st.set_page_config(
    page_title="Safe Haven & Tracker",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Deep Islamic Sunset Theme (Dusk Gold & Amber Warmth)
st.markdown(
    """
    <style>
    /* Force overall app background */
    [data-testid="stAppViewContainer"], .stApp {
        background-color: #140F0D !important;
        color: #EBDCCB !important;
    }
    
    [data-testid="stHeader"] {
        background-color: rgba(20, 15, 13, 0.8) !important;
    }

    [data-testid="stSidebar"] {
        background-color: #1C1512 !important;
        border-right: 1px solid #3B2E26 !important;
    }

    /* Sunset Warm Gold Quotes & Cards */
    .quote-card {
        background: linear-gradient(135deg, #2D221A 0%, #1A130E 100%) !important;
        border-left: 5px solid #E5A93C !important;
        border-top: 1px solid #4A382A !important;
        border-right: 1px solid #4A382A !important;
        border-bottom: 1px solid #4A382A !important;
        padding: 22px !important;
        border-radius: 12px !important;
        margin-bottom: 24px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.6) !important;
    }
    .quote-title {
        font-size: 1.25em !important;
        font-weight: 700 !important;
        color: #FACC15 !important;
    }
    .quote-body {
        font-size: 1.35em !important;
        font-style: italic !important;
        margin-top: 10px !important;
        color: #FFFDF9 !important;
        line-height: 1.6 !important;
    }
    .quote-translation {
        font-size: 1.05em !important;
        color: #E2C99B !important;
        margin-top: 8px !important;
    }
    .quote-ref {
        font-size: 0.9em !important;
        color: #A89885 !important;
    }
    
    /* Cluster Banner */
    .cluster-banner {
        background: linear-gradient(90deg, #4A1A1A 0%, #2D0F0F 100%) !important;
        color: #FFDADA !important;
        border-left: 4px solid #E57373 !important;
        padding: 14px 18px !important;
        border-radius: 8px !important;
        margin-top: 15px !important;
        font-weight: 600 !important;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #E5A93C 0%, #B88214 100%) !important;
        color: #12100E !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
    }
    
    /* Tables and Containers */
    [data-testid="stDataFrame"] {
        background-color: #1C1512 !important;
        border-radius: 8px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

COLUMNS = [
    "date",
    "mood_type",
    "mood_severity",
    "sleep_quality",
    "sleep_hours",
    "purging",
    "partner_notes",
    # Observer Fields
    "ate_meals",
    "restriction_observed",
    "location_tag",
    "trigger_tags",
    "observer_notes",
    "composite_severity",
]

LAB_COLUMNS = ["date", "lab_type", "result_value", "notes", "next_due_date"]

# Mood-Adaptive Islamic Quote Bank
ISLAMIC_QUOTES = {
    "Depression": {
        "title": "A Reminder of Ease • تذكير باليسر",
        "verse": "« فَإِنَّ مَعَ الْعُسْرِ يُسْرًا • إِنَّ مَعَ الْعُسْرِ يُسْرًا »",
        "translation": "'For indeed, with hardship will come ease. Indeed, with hardship will come ease.' (Quran 94:5-6)",
        "ref": "Remember that your worth is non-negotiable, and taking things one moment at a time is more than enough today.",
    },
    "Hypomania": {
        "title": "A Gentle Grounding • السكينة والاعتدال",
        "verse": "« وَاقْصِدْ فِي مَشْيِكَ وَاغْضُضْ مِن صَوْتِك »",
        "translation": "'And be moderate in your pace and lower your voice...' (Quran 31:19)",
        "ref": "Pause, take a deep breath, and let your body move at a calm, deliberate rhythm.",
    },
    "Stable": {
        "title": "A Moment of Peace • طمأنينة القلب",
        "verse": "« لَئِن شَكَرْتُمْ لأَزِيدَنَّكُمْ »",
        "translation": "'If you are grateful, I will surely increase you in favor...' (Quran 14:7)",
        "ref": "May your heart remain grounded, peaceful, and filled with tranquility today.",
    },
}

MATH_SCIENCE_BYTES = [
    "**The Beauty of Euler's Identity:** $e^{i\\pi} + 1 = 0$ combines five fundamental constants into one elegant balance.",
    "**Cosmological Light:** Cosmic microwave background radiation has traveled over 13.8 billion years through space to reach detectors.",
    "**Fibonacci Efficiency:** Sunflower seed spirals follow Fibonacci ratios to minimize spatial overlap.",
]


# ---------------------------------------------------------------- Data Helpers
def load_data() -> pd.DataFrame:
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = None
    else:
        df = pd.DataFrame(columns=COLUMNS)
    return df


def save_entry(entry: dict):
    df = load_data()
    entry_date_str = pd.Timestamp(entry["date"]).strftime("%Y-%m-%d")
    entry["date"] = entry_date_str
    df = df[df["date"] != entry_date_str]
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df = df.sort_values("date")
    df.to_csv(DATA_FILE, index=False)


def get_timeframe_data(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    if df.empty or "date" not in df.columns:
        return df

    df_filtered = df.copy()
    df_filtered["date_dt"] = pd.to_datetime(df_filtered["date"])
    today = pd.Timestamp.today().normalize()

    if timeframe == "Weekly (Last 7 Days)":
        start_date = today - timedelta(days=7)
        df_filtered = df_filtered[df_filtered["date_dt"] >= start_date]
    elif timeframe == "Monthly (Last 30 Days)":
        start_date = today - timedelta(days=30)
        df_filtered = df_filtered[df_filtered["date_dt"] >= start_date]
    elif timeframe == "Yearly (Last 365 Days)":
        start_date = today - timedelta(days=365)
        df_filtered = df_filtered[df_filtered["date_dt"] >= start_date]

    return df_filtered.drop(columns=["date_dt"]).sort_values("date", ascending=False)


def get_purging_cluster_info(df: pd.DataFrame):
    if df.empty or "purging" not in df.columns:
        return 0, 0.0

    df_sorted = df.sort_values("date").reset_index(drop=True)
    df_sorted["purging"] = df_sorted["purging"].fillna(False).astype(bool)

    active_streak = 0
    for i in range(len(df_sorted) - 1, -1, -1):
        if df_sorted.loc[i, "purging"]:
            active_streak += 1
        else:
            break

    clusters = []
    current_cluster = 0
    for val in df_sorted["purging"]:
        if val:
            current_cluster += 1
        else:
            if current_cluster > 0:
                clusters.append(current_cluster)
                current_cluster = 0
    if current_cluster > 0:
        clusters.append(current_cluster)

    avg_cluster = sum(clusters) / len(clusters) if clusters else 0.0
    return active_streak, round(avg_cluster, 1)


def load_labs() -> pd.DataFrame:
    if os.path.exists(LAB_FILE):
        return pd.read_csv(LAB_FILE)
    return pd.DataFrame(columns=LAB_COLUMNS)


# ---------------------------------------------------------------- Sidebar Access Mode
st.sidebar.title("Navigation")
view_mode = st.sidebar.radio("Select View Mode", ["Partner View (Daily Space)", "Observer View (Analytics & Context)"])

# ---------------------------------------------------------------- PARTNER VIEW
if view_mode == "Partner View (Daily Space)":
    df = load_data()
    active_streak, avg_cluster = get_purging_cluster_info(df)

    st.title("Daily Check-in")

    mood_state = st.radio("How is your mind feeling today?", ["Depression", "Stable", "Hypomania"], horizontal=True)

    quote = ISLAMIC_QUOTES[mood_state]
    st.markdown(
        f"""
        <div class="quote-card">
            <div class="quote-title">{quote['title']}</div>
            <div class="quote-body">{quote['verse']}</div>
            <div class="quote-translation">{quote['translation']}</div>
            <div class="quote-ref">{quote['ref']}</div>
        </div>
    """,
        unsafe_allow_html=True,
    )

    with st.form("partner_form"):
        entry_date = st.date_input("Date", value=date.today())

        st.markdown("**Severity Level**")
        mood_severity = st.slider("Severity rating (1 minimal impact → 10 overwhelming)", 1, 10, 3)

        st.markdown("**Sleep & Rest**")
        col1, col2 = st.columns(2)
        sleep_quality = col1.select_slider("Sleep Quality", options=["Bad", "Medium", "Good"], value="Medium")
        sleep_hours = col2.number_input("Hours Slept", min_value=0.0, max_value=24.0, value=7.0, step=0.5)

        st.markdown("**Physical Check-in**")
        purging_today = st.checkbox("Purging occurred today")

        if st.form_submit_button("Save Entry", type="primary"):
            date_str = pd.Timestamp(entry_date).strftime("%Y-%m-%d")
            existing = df[df["date"] == date_str]

            partner_n = existing["partner_notes"].values[0] if not existing.empty and pd.notna(existing["partner_notes"].values[0]) else ""
            ate = existing["ate_meals"].values[0] if not existing.empty else "All meals"
            restr = existing["restriction_observed"].values[0] if not existing.empty else False
            loc = existing["location_tag"].values[0] if not existing.empty else "Home"
            trig = existing["trigger_tags"].values[0] if not existing.empty else ""
            obs_n = existing["observer_notes"].values[0] if not existing.empty else ""

            comp_sev = mood_severity * 1.0 + (2.0 if purging_today else 0.0)

            entry = {
                "date": entry_date,
                "mood_type": mood_state,
                "mood_severity": mood_severity,
                "sleep_quality": sleep_quality,
                "sleep_hours": sleep_hours,
                "purging": purging_today,
                "partner_notes": partner_n,
                "ate_meals": ate,
                "restriction_observed": restr,
                "location_tag": loc,
                "trigger_tags": trig,
                "observer_notes": obs_n,
                "composite_severity": comp_sev,
            }
            save_entry(entry)
            st.success("Saved gently.")
            st.rerun()

    if purging_today or active_streak > 0:
        st.markdown(
            f"""
            <div class="cluster-banner">
                Active Purging Cluster: Day {active_streak}
                <br><span style="font-weight:normal; font-size:0.9em;">(Historical baseline average: ~{avg_cluster} days. Remember to hydrate and rest.)</span>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.subheader("History & Comfort Hub")
    tab_history, tab_math = st.tabs(["Logged History Tables", "Math & Science Bytes"])

    with tab_history:
        timeframe = st.selectbox(
            "Filter History Timeframe",
            ["Weekly (Last 7 Days)", "Monthly (Last 30 Days)", "Yearly (Last 365 Days)", "All Time"],
            key="partner_timeframe",
        )
        filtered_df = get_timeframe_data(df, timeframe)

        if not filtered_df.empty:
            st.dataframe(
                filtered_df[["date", "mood_type", "mood_severity", "sleep_quality", "sleep_hours", "purging"]],
                use_container_width=True,
            )
        else:
            st.info("No records found for this timeframe.")

    with tab_math:
        for b in MATH_SCIENCE_BYTES:
            st.markdown(f"- {b}")

# ---------------------------------------------------------------- OBSERVER VIEW
else:
    pin = st.sidebar.text_input("Observer Passkey", type="password")
    if pin != "1234" and pin != "":  # Passkey check
        st.error("Access restricted.")
        st.stop()

    st.title("Observer Control & Predictive Dashboard")
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Meal & Context Logger", "Timeframe Data Table", "Predictive Risk & Triggers", "Lithium Lab Countdown"]
    )

    df = load_data()

    # --- TAB 1: Meal & Context Entry
    with tab1:
        st.subheader("Log Meal Intake & Observer Context")

        target_date = st.date_input("Entry Date to Append Context", value=date.today())
        target_str = target_date.strftime("%Y-%m-%d")
        existing_row = df[df["date"] == target_str]

        curr_ate = existing_row["ate_meals"].values[0] if not existing_row.empty and pd.notna(existing_row["ate_meals"].values[0]) else "All meals"
        curr_restr = bool(existing_row["restriction_observed"].values[0]) if not existing_row.empty and pd.notna(existing_row["restriction_observed"].values[0]) else False
        curr_loc = existing_row["location_tag"].values[0] if not existing_row.empty and pd.notna(existing_row["location_tag"].values[0]) else "Home"
        curr_trig = existing_row["trigger_tags"].values[0].split(",") if not existing_row.empty and pd.notna(existing_row["trigger_tags"].values[0]) and existing_row["trigger_tags"].values[0] else []
        curr_obs = existing_row["observer_notes"].values[0] if not existing_row.empty and pd.notna(existing_row["observer_notes"].values[0]) else ""

        with st.form("observer_context_form"):
            st.markdown("**Meal Status (Logged via Conversations)**")
            ate_meals = st.selectbox("Meals Logged", ["All meals", "Skipped 1 meal", "Skipped most/all meals"], index=["All meals", "Skipped 1 meal", "Skipped most/all meals"].index(curr_ate))
            restriction_observed = st.checkbox("Restriction behavior observed", value=curr_restr)

            st.markdown("**Environmental Context**")
            location_tag = st.selectbox("Current Location", ["Home", "Spain / Travel", "Work Trip", "Family Visit"], index=0)
            trigger_tags = st.multiselect("Active Triggers", ["Family Conflict", "Sleep Disruption", "Travel Stress", "Work Load", "Social Overstimulation"], default=[t for t in curr_trig if t in ["Family Conflict", "Sleep Disruption", "Travel Stress", "Work Load", "Social Overstimulation"]])
            observer_notes = st.text_area("Private Notes (Conversations, bad work days, hidden stressors)", value=curr_obs)

            if st.form_submit_button("Update Observer Records"):
                if existing_row.empty:
                    base_entry = {c: None for c in COLUMNS}
                    base_entry["date"] = target_str
                    base_entry["mood_type"] = "Stable"
                    base_entry["mood_severity"] = 1
                    base_entry["sleep_quality"] = "Medium"
                    base_entry["sleep_hours"] = 7.0
                    base_entry["purging"] = False
                else:
                    base_entry = existing_row.to_dict(orient="records")[0]

                base_entry["ate_meals"] = ate_meals
                base_entry["restriction_observed"] = restriction_observed
                base_entry["location_tag"] = location_tag
                base_entry["trigger_tags"] = ",".join(trigger_tags)
                base_entry["observer_notes"] = observer_notes

                save_entry(base_entry)
                st.success("Observer context appended successfully.")

    # --- TAB 2: Timeframe Data Tables (Weekly, Monthly, Yearly)
    with tab2:
        st.subheader("Complete Records by Timeframe")
        timeframe_obs = st.selectbox(
            "Select Time Window",
            ["Weekly (Last 7 Days)", "Monthly (Last 30 Days)", "Yearly (Last 365 Days)", "All Time"],
            key="obs_timeframe",
        )
        obs_filtered = get_timeframe_data(df, timeframe_obs)

        if not obs_filtered.empty:
            st.dataframe(obs_filtered, use_container_width=True)
        else:
            st.info("No logs available for this timeframe.")

    # --- TAB 3: Predictive Risk & Trigger Correlations
    with tab3:
        if df.empty:
            st.info("No logs available yet.")
        else:
            df_sorted = df.copy()
            df_sorted["date"] = pd.to_datetime(df_sorted["date"])
            df_sorted = df_sorted.sort_values("date")

            st.subheader("Trigger-to-Restriction Lag & Probability Engine")

            df_sorted["has_trigger"] = df_sorted["trigger_tags"].apply(lambda x: True if pd.notna(x) and len(str(x)) > 0 else False)
            df_sorted["restr_next_48h"] = df_sorted["restriction_observed"].shift(-1).fillna(False) | df_sorted["restriction_observed"].shift(-2).fillna(False)

            trigger_days = df_sorted[df_sorted["has_trigger"]]
            if not trigger_days.empty:
                prob = (trigger_days["restr_next_48h"].sum() / len(trigger_days)) * 100
                st.metric("Probability of ED Restriction within 48h of a Trigger", f"{prob:.1f}%")
            else:
                st.info("Logging more trigger tags will activate the 48h restriction probability engine.")

            st.markdown("---")
            st.subheader("Factor Severity Correlations (Statistical Floor n ≥ 10)")

            trig_rows = []
            for _, row in df_sorted.iterrows():
                if pd.notna(row["trigger_tags"]) and row["trigger_tags"]:
                    for t in str(row["trigger_tags"]).split(","):
                        trig_rows.append({"Trigger": t, "Severity": row["composite_severity"]})

            if trig_rows:
                tdf = pd.DataFrame(trig_rows)
                summary = tdf.groupby("Trigger").agg(Logged_Days=("Severity", "count"), Raw_Avg_Severity=("Severity", "mean")).reset_index()

                summary["Confidence"] = summary["Logged_Days"].apply(lambda n: "Established Pattern" if n >= 10 else f"Low Sample Size (n={n})")
                summary["Average Severity"] = summary.apply(lambda r: round(r["Raw_Avg_Severity"], 2) if r["Logged_Days"] >= 10 else "N/A (n < 10)", axis=1)

                st.dataframe(summary[["Trigger", "Logged_Days", "Average Severity", "Confidence"]].sort_values("Logged_Days", ascending=False), use_container_width=True)

    # --- TAB 4: Lithium Lab Countdown
    with tab4:
        st.subheader("Serum Lithium & Clinical Schedule")
        labs_df = load_labs()

        if not labs_df.empty:
            labs_df["date"] = pd.to_datetime(labs_df["date"])
            labs_df["next_due_date"] = pd.to_datetime(labs_df["next_due_date"])
            latest = labs_df.sort_values("date").iloc[-1]
            days_left = (latest["next_due_date"] - pd.Timestamp.today()).days

            c1, c2, c3 = st.columns(3)
            c1.metric("Latest Level", f"{latest['result_value']} mmol/L")
            c2.metric("Last Lab Date", latest["date"].strftime("%Y-%m-%d"))
            c3.metric("Next Test Due (6-Month Window)", latest["next_due_date"].strftime("%Y-%m-%d"), delta=f"{days_left} days left", delta_color="normal" if days_left > 30 else "inverse")

            st.dataframe(labs_df.sort_values("date", ascending=False), use_container_width=True)
        else:
            st.warning("No lab records found.")
