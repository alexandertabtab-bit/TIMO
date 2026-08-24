import base64
import os
from datetime import date
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# File paths
DATA_FILE = "life_chart_data.csv"
REELS_FILE = "reels.csv"
BACKGROUND_IMAGE = "assets/background.jpg"

st.set_page_config(
    page_title="Life Chart & Sanctuary",
    layout="wide",
    page_icon="🌙",
    initial_sidebar_state="collapsed",
)


# --------------------------------------------------------- Styles & Background
def inject_custom_styles():
    bg_css = ""
    if os.path.exists(BACKGROUND_IMAGE):
        with open(BACKGROUND_IMAGE, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        bg_css = f"""
            [data-testid="stAppViewContainer"] {{
                background-image: linear-gradient(rgba(250,248,245,0.92), rgba(250,248,245,0.92)),
                                  url("data:image/jpeg;base64,{b64}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }}
        """
    else:
        bg_css = """
            [data-testid="stAppViewContainer"] {
                background-color: #FAF8F5;
            }
        """

    st.markdown(
        f"""
        <style>
        {bg_css}
        
        /* Mobile-First Layout Optimizations */
        .block-container {{
            padding-top: 1rem !important;
            padding-bottom: 2rem !important;
            max-width: 650px !important;
        }}
        
        /* Instagram Reel Card Style */
        .reel-card {{
            background: #FFFFFF;
            border-radius: 18px;
            padding: 14px;
            margin-bottom: 16px;
            border: 1px solid #E6D8CA;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }}
        .reel-header {{
            font-size: 0.85rem;
            color: #047857;
            font-weight: 700;
            margin-bottom: 6px;
        }}
        .reel-title {{
            font-size: 1.1rem;
            font-weight: 700;
            color: #1F2937;
            margin-bottom: 10px;
        }}
        
        /* Quote Card Style */
        .quote-box {{
            background: linear-gradient(135deg, #F0FDF4 0%, #FFFBEB 100%);
            border-left: 5px solid #D97706;
            border-radius: 12px;
            padding: 14px;
            margin-bottom: 15px;
            color: #1F2937;
        }}
        
        /* Smooth Touch Buttons */
        .stButton>button {{
            width: 100%;
            height: 48px;
            border-radius: 12px;
            font-weight: 700;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_custom_styles()

# --------------------------------------------------------- Data Constants
COLUMNS = [
    "date",
    "mood_rating",
    "sleep_hours",
    "sleep_quality",
    "irritability",
    "ultradian_cycling",
    "ate_meals",
    "ed_status",
    "purging",
    "factors",
    "life_events",
    "notes",
]

FACTOR_OPTIONS = [
    "Poor sleep",
    "Work/Study stress",
    "Family conflict",
    "Travel / Routine change",
    "Medication adjustment",
    "Hormonal changes",
    "Weather / Environment",
    "Physical illness",
    "Social interaction",
    "Other",
]

DEFAULT_REELS = [
    {
        "title": "Surah Al-Fatiha Deep Reflection",
        "url": "https://www.youtube.com/watch?v=2OEL4P1Rz0U",
        "category": "Islam",
        "added_by": "System",
    },
    {
        "title": "The Power of Sabr (Patience)",
        "url": "https://www.youtube.com/watch?v=bn9F19Hi1Lk",
        "category": "Motivation",
        "added_by": "System",
    },
    {
        "title": "Daily Dhikr & Grounding",
        "url": "https://www.youtube.com/watch?v=2OEL4P1Rz0U",
        "category": "Islam",
        "added_by": "System",
    },
]

DAILY_QUOTES = [
    {
        "verse": "« فَإِنَّ مَعَ الْعُسْرِ يُسْرًا »",
        "translation": "'For indeed, with hardship will come ease.' (Quran 94:5)",
    },
    {
        "verse": "« أَلا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ »",
        "translation": "'Unquestionably, by the remembrance of Allah do hearts find rest.' (Quran 13:28)",
    },
    {
        "verse": "« وَاللَّهُ يَعْلَمُ وَأَنتُمْ لا تَعْلَمُونَ »",
        "translation": "'And Allah knows, while you do not know.' (Quran 2:216)",
    },
]


# --------------------------------------------------------- Loaders & Helpers
def load_data() -> pd.DataFrame:
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, parse_dates=["date"])
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = None
        return df[COLUMNS]
    return pd.DataFrame(columns=COLUMNS)


def save_entry(entry: dict):
    df = load_data()
    ts = pd.Timestamp(entry["date"])
    df = df[df["date"] != ts]
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df = df.sort_values("date")
    df.to_csv(DATA_FILE, index=False)


def load_reels() -> pd.DataFrame:
    if os.path.exists(REELS_FILE):
        return pd.read_csv(REELS_FILE)
    df_def = pd.DataFrame(DEFAULT_REELS)
    df_def.to_csv(REELS_FILE, index=False)
    return df_def


def save_reel(title, url, category, added_by):
    df = load_reels()
    new_row = pd.DataFrame(
        [
            {
                "title": title,
                "url": url,
                "category": category,
                "added_by": added_by,
            }
        ]
    )
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(REELS_FILE, index=False)


# --------------------------------------------------------- App Navigation
st.title("🌙 Life Tracker")

view = st.sidebar.radio("Navigation", ["Your View (Observer)", "His View"])
full_view = view.startswith("Your")

# --------------------------------------------------------- YOUR VIEW (OBSERVER)
if full_view:
    tab_entry, tab_factors, tab_chart = st.tabs(
        ["📝 Daily Observation", "📊 Factor Analytics", "📈 Mood Chart"]
    )

    with tab_entry:
        st.subheader("Observe & Track Factors")
        entry_date = st.date_input("Date", value=date.today())

        st.markdown("**Core Observation**")
        mood = st.slider(
            "Mood State (−4 Severe Depression → 0 Stable → +4 Mania)",
            -4,
            4,
            0,
        )
        sleep_hours = st.number_input(
            "Hours Slept Last Night",
            min_value=0.0,
            max_value=24.0,
            value=7.0,
            step=0.5,
        )
        irritability = st.slider("Irritability Level (0 None → 4 High)", 0, 4, 0)
        ultradian = st.checkbox("Multiple mood shifts today (Ultradian)")

        st.markdown("**Influencing Factors Today**")
        factors = st.multiselect(
            "Select all factors that influenced his state today:",
            FACTOR_OPTIONS,
        )

        life_events = st.text_area(
            "Context & Disruptions",
            placeholder="Describe specific triggers, work events, or conflicts...",
        )
        notes = st.text_area(
            "Private Observer Notes",
            placeholder="Notes on behavior, environment, or overall pattern...",
        )

        if st.button("Save Observation Entry", type="primary"):
            entry = {
                "date": pd.Timestamp(entry_date),
                "mood_rating": mood,
                "sleep_hours": sleep_hours,
                "sleep_quality": None,
                "irritability": irritability,
                "ultradian_cycling": ultradian,
                "ate_meals": None,
                "ed_status": None,
                "purging": False,
                "factors": ", ".join(factors),
                "life_events": life_events,
                "notes": notes,
            }
            save_entry(entry)
            st.success(f"Observation logged for {entry_date}")

    with tab_factors:
        st.subheader("Factor Fragmentation & Analytics")
        df = load_data().dropna(subset=["mood_rating"])

        if df.empty or df["factors"].dropna().empty:
            st.info("No factor entries recorded yet.")
        else:
            # Fragment factors into individual tags
            factor_records = []
            for _, row in df.iterrows():
                if pd.notna(row["factors"]) and row["factors"].strip():
                    tags = [
                        f.strip()
                        for f in str(row["factors"]).split(",")
                        if f.strip()
                    ]
                    for tag in tags:
                        factor_records.append(
                            {
                                "date": row["date"],
                                "Factor": tag,
                                "Mood": row["mood_rating"],
                                "Sleep": row["sleep_hours"],
                            }
                        )

            f_df = pd.DataFrame(factor_records)

            if not f_df.empty:
                # Chart 1: Factor Frequency Count
                f_counts = (
                    f_df["Factor"]
                    .value_counts()
                    .reset_index(name="Occurrences")
                )
                fig_count = px.bar(
                    f_counts,
                    x="Factor",
                    y="Occurrences",
                    title="Most Frequent Influencing Factors",
                    color="Occurrences",
                    color_continuous_scale="Viridis",
                )
                st.plotly_chart(fig_count, use_container_width=True)

                # Chart 2: Average Mood Impact per Factor
                f_mood = (
                    f_df.groupby("Factor")["Mood"]
                    .mean()
                    .reset_index(name="Avg Mood")
                )
                fig_mood = px.bar(
                    f_mood,
                    x="Factor",
                    y="Avg Mood",
                    title="Average Mood Impact by Factor (−4 Depressed | +4 Manic)",
                    color="Avg Mood",
                    color_continuous_scale="RdBu",
                )
                fig_mood.add_hline(y=0, line_dash="dash", line_color="gray")
                st.plotly_chart(fig_mood, use_container_width=True)
            else:
                st.info("No tagged factor data found.")

    with tab_chart:
        st.subheader("Mood Timeline")
        df = load_data().dropna(subset=["mood_rating"])
        if not df.empty:
            fig = go.Figure()
            colors = [
                "#d62728" if m > 0 else ("#1f77b4" if m < 0 else "#2ca02c")
                for m in df["mood_rating"]
            ]
            fig.add_trace(
                go.Scatter(
                    x=df["date"],
                    y=df["mood_rating"],
                    mode="lines+markers",
                    marker=dict(color=colors, size=8),
                    line=dict(color="lightgray"),
                )
            )
            fig.add_hline(y=0, line_dash="dash", line_color="gray")
            fig.update_layout(
                yaxis=dict(range=[-4.5, 4.5], title="Mood Rating"), height=350
            )
            st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------------- HIS VIEW (MOBILE INSTAGRAM STYLE)
else:
    tab_checkin, tab_reels = st.tabs(["📝 Quick Check-in", "📱 Reels Feed"])

    with tab_checkin:
        # Display Rotating / Daily Quote
        today_quote = DAILY_QUOTES[date.today().day % len(DAILY_QUOTES)]
        st.markdown(
            f"""
            <div class="quote-box">
                <div style="font-size:1.2rem; font-weight:bold; text-align:right; direction:rtl; margin-bottom:4px;">
                    {today_quote['verse']}
                </div>
                <div style="font-size:0.9rem; color:#047857;">
                    {today_quote['translation']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.subheader("Today's Check-in")
        entry_date = st.date_input("Date", value=date.today())

        mood_type = st.radio(
            "How are you feeling overall today?",
            ["Stable", "Depression", "Hypomania"],
            horizontal=True,
        )

        sleep_quality = st.select_slider(
            "Sleep Last Night",
            options=["Bad", "Normal", "Good"],
            value="Normal",
        )

        ed_status = st.radio(
            "Eating today", ["Stable", "Not stable"], horizontal=True
        )
        purging = False
        if ed_status == "Not stable":
            purging = st.checkbox("Purging occurred today")

        if st.button("Save Check-in", type="primary"):
            mood_val = (
                0
                if mood_type == "Stable"
                else (-2 if mood_type == "Depression" else 2)
            )
            sleep_hours_map = {"Bad": 4.0, "Normal": 7.0, "Good": 8.5}

            entry = {
                "date": pd.Timestamp(entry_date),
                "mood_rating": mood_val,
                "sleep_hours": sleep_hours_map[sleep_quality],
                "sleep_quality": sleep_quality,
                "irritability": 0,
                "ultradian_cycling": False,
                "ate_meals": ed_status,
                "ed_status": ed_status,
                "purging": purging,
                "factors": "",
                "life_events": "",
                "notes": "",
            }
            save_entry(entry)
            st.success("Saved! Thank you for checking in.")

    with tab_reels:
        st.subheader("📱 Curated Reels")
        reels_df = load_reels()

        if reels_df.empty:
            st.info("No reels loaded.")
        else:
            if "reel_idx" not in st.session_state:
                st.session_state.reel_idx = 0

            current = reels_df.iloc[st.session_state.reel_idx]

            # Mobile Instagram Card Container
            st.markdown(
                f"""
                <div class="reel-card">
                    <div class="reel-header">📌 {current['category']} • Added by {current['added_by']}</div>
                    <div class="reel-title">{current['title']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.video(current["url"])

            # Touch Controls
            c1, c2, c3 = st.columns([1, 1, 1])
            if c1.button("⏮️ Prev"):
                st.session_state.reel_idx = (
                    st.session_state.reel_idx - 1
                ) % len(reels_df)
                st.rerun()
            c2.markdown(
                f"<p style='text-align:center; padding-top:10px;'><b>{st.session_state.reel_idx + 1} / {len(reels_df)}</b></p>",
                unsafe_allow_html=True,
            )
            if c3.button("Next ⏭️"):
                st.session_state.reel_idx = (
                    st.session_state.reel_idx + 1
                ) % len(reels_df)
                st.rerun()

        st.markdown("---")
        with st.expander("➕ Add a reel (Optional)"):
            r_title = st.text_input("Title")
            r_url = st.text_input("Video URL")
            r_cat = st.selectbox(
                "Category", ["Islam", "Motivation", "Reminders", "Other"]
            )
            r_by = st.text_input("Added By", value="User")
            if st.button("Add to Feed"):
                if r_title and r_url:
                    save_reel(r_title, r_url, r_cat, r_by)
                    st.success("Added!")
                    st.rerun()
