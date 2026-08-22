iimport os
from datetime import date, datetime, timedelta
import pandas as pd
import streamlit as st
st.set_page_config(page_title="Safe Haven & Tracker", layout="wide", initial_sidebar_state="expanded")

# Custom Warm Theme Styling for Partner View
st.markdown(
    """
    <style>
    .quote-card {
        background-color: #2D3748;
        border-left: 5px solid #D69E2E;
        padding: 18px;
        border-radius: 8px;
        margin-bottom: 20px;
        color: #EDF2F7;
    }
    .quote-title {
        font-size: 1.1em;
        font-weight: bold;
        color: #ECC94B;
    }
    .quote-body {
        font-size: 1.05em;
        font-style: italic;
        margin-top: 6px;
    }
    .cluster-banner {
        background-color: #742A2A;
        color: #FFF5F5;
        padding: 12px;
        border-radius: 6px;
        margin-top: 10px;
        font-weight: bold;
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
        "title": "A Reminder of Ease",
        "verse": "« فَإِنَّ مَعَ الْعُسْرِ يُسْرًا • إِنَّ مَعَ الْعُسْرِ يُسْرًا »",
        "translation": "'For indeed, with hardship will come ease. Indeed, with hardship will come ease.' (Quran 94:5-6)",
        "ref": "Remember that your worth is non-negotiable, and taking things one moment at a time is more than enough today.",
    },
    "Hypomania": {
        "title": "A Gentle Grounding",
        "verse": "« وَاقْصِدْ فِي مَشْيِكَ وَاغْضُضْ مِن صَوْتِكَ »",
        "translation": "'And be moderate in your pace and lower your voice...' (Quran 31:19)",
        "ref": "Pause, take a deep breath, and let your body move at a calm, deliberate rhythm.",
    },
    "Stable": {
        "title": "A Moment of Peace",
        "verse": "« لَئِن شَكَرْتُمْ لأَزِيدَنَّكُمْ »",
        "translation": "'If you are grateful, I will surely increase you in favor...' (Quran 14:7)",
        "ref": "May your heart remain grounded, peaceful, and filled with tranquility today.",
    },
}

MATH_SCIENCE_BYTES = [
    "**The Beauty of Euler's Identity:** $e^{i\\pi} + 1 = 0$ combines five of the most fundamental constants in mathematics into one elegant relationship.",
    "**Cosmological Curiosity:** Light from the cosmic microwave background has been traveling for over 13.8 billion years to reach detectors today.",
    "**Fibonacci in Nature:** The spiraling pattern of sunflower seeds follows Fibonacci sequence ratios to maximize spatial efficiency.",
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


def get_purging_cluster_info(df: pd.DataFrame):
    """Calculates active purging cluster streak and historical average duration."""
    if df.empty or "purging" not in df.columns:
        return 0, 0.0

    df_sorted = df.sort_values("date").reset_index(drop=True)
    df_sorted["purging"] = df_sorted["purging"].fillna(False).astype(bool)

    # Active cluster check
    active_streak = 0
    for i in range(len(df_sorted) - 1, -1, -1):
        if df_sorted.loc[i, "purging"]:
            active_streak += 1
        else:
            break

    # Historical cluster calculation
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
view_mode = st.sidebar.radio("View", ["Partner View (Daily Space)", "Observer View (Analytics & Context)"])

# ---------------------------------------------------------------- PARTNER VIEW
if view_mode == "Partner View (Daily Space)":
    df = load_data()
    active_streak, avg_cluster = get_purging_cluster_info(df)

    st.title("Daily Check-in")

    # Quick Mood Selection for Dynamic Quote
    mood_state = st.radio("How is your mind feeling today?", ["Depression", "Stable", "Hypomania"], horizontal=True)

    # Render Mood-Adaptive Quran Card
    quote = ISLAMIC_QUOTES[mood_state]
    st.markdown(
        f"""
        <div class="quote-card">
            <div class="quote-title">{quote['title']}</div>
            <div class="quote-body">{quote['verse']}</div>
            <p style="margin-top:8px; margin-bottom:4px;">{quote['translation']}</p>
            <small style="color:#A0AEC0;">{quote['ref']}</small>
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

        partner_notes = st.text_area("Anything on your mind? (Optional)", placeholder="Write anything you'd like to drop off here...")

        if st.form_submit_button("Save Entry", type="primary"):
            date_str = pd.Timestamp(entry_date).strftime("%Y-%m-%d")
            existing = df[df["date"] == date_str]

            # Preserve Observer fields if already set
            ate = existing["ate_meals"].values[0] if not existing.empty else "All meals"
            restr = existing["restriction_observed"].values[0] if not existing.empty else False
            loc = existing["location_tag"].values[0] if not existing.empty else "Home"
            trig = existing["trigger_tags"].values[0] if not existing.empty else ""
            obs_n = existing["observer_notes"].values[0] if not existing.empty else ""

            # Calculate composite severity for observer side
            comp_sev = mood_severity * 1.0 + (2.0 if purging_today else 0.0)

            entry = {
                "date": entry_date,
                "mood_type": mood_state,
                "mood_severity": mood_severity,
                "sleep_quality": sleep_quality,
                "sleep_hours": sleep_hours,
                "purging": purging_today,
                "partner_notes": partner_notes,
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

    # Active Purging Cluster Indicator (Low Invasive Banner)
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

    # Comfort & Micro-Learning Hub
    st.markdown("---")
    st.subheader("Comfort & Learning Corner")
    tab_math, tab_history = st.tabs(["Math & Science Bytes", "Your Logged History"])

    with tab_math:
        for b in MATH_SCIENCE_BYTES:
            st.markdown(f"- {b}")

    with tab_history:
        if not df.empty:
            st.dataframe(df[["date", "mood_type", "mood_severity", "sleep_quality", "sleep_hours", "partner_notes"]].sort_values("date", ascending=False), use_container_width=True)

# ---------------------------------------------------------------- OBSERVER VIEW
else:
    pin = st.sidebar.text_input("Observer Passkey", type="password")
    if pin != "1234" and pin != "":  # Replace 1234 with your preferred pin
        st.error("Access restricted.")
        st.stop()

    st.title("Observer Control & Predictive Dashboard")
    tab1, tab2, tab3 = st.tabs(["Meal & Context Logger", "Predictive Risk & Triggers", "Lithium Lab Countdown"])

    # --- TAB 1: Meal & Context Entry
    with tab1:
        st.subheader("Log Meal Intake & Observer Context")
        df = load_data()

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

    # --- TAB 2: Predictive Risk & Trigger Correlations
    with tab2:
        df = load_data()
        if df.empty:
            st.info("No logs available yet.")
        else:
            df["date"] = pd.to_datetime(df["date"])
            df = df.sort_values("date")

            st.subheader("Trigger-to-Restriction Lag & Probability Engine")

            # 24-48h Trigger Lag Calculation
            df["has_trigger"] = df["trigger_tags"].apply(lambda x: True if pd.notna(x) and len(str(x)) > 0 else False)
            df["restr_next_48h"] = df["restriction_observed"].shift(-1).fillna(False) | df["restriction_observed"].shift(-2).fillna(False)

            trigger_days = df[df["has_trigger"]]
            if not trigger_days.empty:
                prob = (trigger_days["restr_next_48h"].sum() / len(trigger_days)) * 100
                st.metric("Probability of ED Restriction within 48h of a Trigger", f"{prob:.1f}%")
            else:
                st.info("Logging more trigger tags will activate the 48h restriction probability engine.")

            st.markdown("---")
            st.subheader("Factor Severity Correlations (Statistical Floor n ≥ 10)")

            trig_rows = []
            for _, row in df.iterrows():
                if pd.notna(row["trigger_tags"]) and row["trigger_tags"]:
                    for t in str(row["trigger_tags"]).split(","):
                        trig_rows.append({"Trigger": t, "Severity": row["composite_severity"]})

            if trig_rows:
                tdf = pd.DataFrame(trig_rows)
                summary = tdf.groupby("Trigger").agg(Logged_Days=("Severity", "count"), Raw_Avg_Severity=("Severity", "mean")).reset_index()

                summary["Confidence"] = summary["Logged_Days"].apply(lambda n: "Established Pattern" if n >= 10 else f"Low Sample Size (n={n})")
                summary["Average Severity"] = summary.apply(lambda r: round(r["Raw_Avg_Severity"], 2) if r["Logged_Days"] >= 10 else "N/A (n < 10)", axis=1)

                st.dataframe(summary[["Trigger", "Logged_Days", "Average Severity", "Confidence"]].sort_values("Logged_Days", ascending=False), use_container_width=True)

    # --- TAB 3: Lithium Lab Countdown
    with tab3:
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
