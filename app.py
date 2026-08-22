import os
from datetime import date, datetime, timedelta
import pandas as pd
import streamlit as st

DATA_FILE = "life_chart_data.csv"
LAB_FILE = "lab_tests.csv"
REELS_FILE = "reels_data.csv"

# Page Configuration - Light Theme with Expanded Sidebar
st.set_page_config(
    page_title="Safe Haven & Tracker",
    page_icon="🕌",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Custom Styling: Bright Light Sandstone, Sunset Gold & Emerald Green Accent
st.markdown(
    """
    <style>
    /* Global Soft Light Sandstone Background */
    [data-testid="stAppViewContainer"], .stApp {
        background-color: #FAF8F5 !important;
        color: #2D241E !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Header Styling */
    [data-testid="stHeader"] {
        background-color: rgba(250, 248, 245, 0.85) !important;
        backdrop-filter: blur(8px);
    }

    /* Soft Warm Sidebar */
    [data-testid="stSidebar"] {
        background-color: #F3ECE4 !important;
        border-right: 1px solid #E6D8CA !important;
    }

    /* Reel Card - Crisp White with Sunset Gold Accent */
    .mobile-reel-card {
        background-color: #FFFFFF !important;
        border: 1px solid #E6D8CA !important;
        border-top: 4px solid #D97706 !important;
        border-radius: 16px;
        padding: 18px;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.04);
    }
    
    /* Emerald Category Badge */
    .reel-badge {
        display: inline-block;
        background-color: #ECFDF5 !important;
        color: #047857 !important;
        border: 1px solid #A7F3D0 !important;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 9999px;
        margin-bottom: 8px;
    }

    /* Sunset Gold Language Badge */
    .reel-lang-badge {
        display: inline-block;
        background-color: #FEF3C7 !important;
        color: #B45309 !important;
        border: 1px solid #FDE68A !important;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 9999px;
        margin-left: 6px;
    }

    /* Islamic Quote Card - Warm Light Gradient */
    .quote-card {
        background: linear-gradient(135deg, #F0FDF4 0%, #FFFBEB 100%) !important;
        border-left: 5px solid #D97706 !important;
        border-right: 1px solid #10B981 !important;
        padding: 18px !important;
        border-radius: 14px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    }
    .quote-title {
        font-size: 1.1em !important;
        font-weight: 700 !important;
        color: #B45309 !important;
    }
    .quote-body {
        font-size: 1.25em !important;
        font-style: italic !important;
        margin-top: 8px !important;
        color: #1F2937 !important;
        line-height: 1.6 !important;
        direction: rtl;
        text-align: right;
    }
    .quote-translation {
        font-size: 0.95em !important;
        color: #047857 !important;
        margin-top: 8px !important;
        direction: ltr;
        text-align: left;
    }

    /* Touch-Optimized Emerald Green Buttons */
    .stButton>button {
        width: 100% !important;
        height: 48px !important;
        border-radius: 12px !important;
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        border: none !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 12px rgba(5, 150, 105, 0.25) !important;
    }
    
    .stButton>button:active {
        transform: scale(0.98);
    }

    /* Video Player Frame */
    [data-testid="stVideo"] {
        border-radius: 14px !important;
        overflow: hidden !important;
        border: 1px solid #E6D8CA;
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
    "ate_meals",
    "restriction_observed",
    "location_tag",
    "trigger_tags",
    "observer_notes",
    "composite_severity",
]

DEFAULT_REELS = [
    {
        "title": "سورة الفاتحة وتفسيرها الميسر | Meaning of Surah Al-Fatiha",
        "url": "https://www.youtube.com/watch?v=2OEL4P1Rz0U",
        "category": "Quran & Tafseer (القرآن والتفسير)",
        "language": "Arabic / English",
        "added_by": "System",
    },
    {
        "title": "The Power of Sabr (Patience) & Trusting Allah's Plan",
        "url": "https://www.youtube.com/watch?v=bn9F19Hi1Lk",
        "category": "Reminders & Grounding (رقائق وتذكير)",
        "language": "English",
        "added_by": "System",
    },
    {
        "title": "فضل الأذكار اليومية وحفظ المسلم | Daily Adhkar Protection",
        "url": "https://www.youtube.com/watch?v=2OEL4P1Rz0U",
        "category": "Hadith & Sunnah (الحديث والسنة)",
        "language": "Arabic",
        "added_by": "System",
    },
]

ISLAMIC_QUOTES = {
    "Depression": {
        "title": "A Reminder of Ease • تذكير باليسر",
        "verse": "« فَإِنَّ مَعَ الْعُسْرِ يُسْرًا • إِنَّ مَعَ الْعُسْرِ يُسْرًا »",
        "translation": "'For indeed, with hardship will come ease. Indeed, with hardship will come ease.' (Quran 94:5-6)",
        "ref": "Take things one moment at a time. Allah does not burden a soul beyond what it can bear.",
    },
    "Hypomania": {
        "title": "A Gentle Grounding • السكينة والاعتدال",
        "verse": "« وَاقْصِدْ فِي مَشْيِكَ وَاغْضُضْ مِن صَوْتِك »",
        "translation": "'And be moderate in your pace...' (Quran 31:19)",
        "ref": "Pause, breathe deeply, and allow your body to move with calm deliberation.",
    },
    "Stable": {
        "title": "A Moment of Peace • طمأنينة القلب",
        "verse": "« أَلا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ »",
        "translation": "'Unquestionably, by the remembrance of Allah do hearts find rest.' (Quran 13:28)",
        "ref": "May your heart remain grounded, thankful, and calm throughout today.",
    },
}

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

def load_reels() -> pd.DataFrame:
    if os.path.exists(REELS_FILE):
        df = pd.read_csv(REELS_FILE)
        if "language" not in df.columns:
            df["language"] = "Bilingual"
        return df
    df_default = pd.DataFrame(DEFAULT_REELS)
    df_default.to_csv(REELS_FILE, index=False)
    return df_default

def save_reel(title: str, url: str, category: str, language: str, added_by: str):
    df = load_reels()
    new_row = pd.DataFrame([{"title": title, "url": url, "category": category, "language": language, "added_by": added_by}])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(REELS_FILE, index=False)

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

# Navigation Menu
st.sidebar.title("🕌 Safe Haven Menu")
view_mode = st.sidebar.radio("Navigation", ["📝 Daily Check-in & Space", "🎥 Islamic Reels Feed", "📊 Observer Analytics"])

# VIEW 1: DAILY CHECK-IN & SPACE
if view_mode == "📝 Daily Check-in & Space":
    df = load_data()
    active_streak, avg_cluster = get_purging_cluster_info(df)

    st.markdown("<h2 style='color: #B45309;'>Daily Sanctuary & Tracking</h2>", unsafe_allow_html=True)

    mood_state = st.radio("Mind & Spirit State Today", ["Depression", "Stable", "Hypomania"], horizontal=True)

    quote = ISLAMIC_QUOTES[mood_state]
    st.markdown(
        f"""
        <div class="quote-card">
            <div class="quote-title">{quote['title']}</div>
            <div class="quote-body">{quote['verse']}</div>
            <div class="quote-translation">{quote['translation']}</div>
            <p style="color:#B45309; font-size:0.85em; margin-top:8px;">{quote['ref']}</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    with st.form("partner_form"):
        entry_date = st.date_input("Date", value=date.today())
        mood_severity = st.slider("Severity level (1 mild → 10 heavy)", 1, 10, 3)

        c1, c2 = st.columns(2)
        sleep_quality = c1.select_slider("Sleep Quality", options=["Bad", "Medium", "Good"], value="Medium")
        sleep_hours = c2.number_input("Hours Slept", min_value=0.0, max_value=24.0, value=7.0, step=0.5)

        purging_today = st.checkbox("Purging occurred today")
        ate_meals = st.selectbox("Meals Today", ["All meals", "Partial meals", "Restricted heavily"])

        if st.form_submit_button("Save Today's Entry"):
            date_str = pd.Timestamp(entry_date).strftime("%Y-%m-%d")
            existing = df[df["date"] == date_str]

            partner_n = existing["partner_notes"].values[0] if not existing.empty and pd.notna(existing["partner_notes"].values[0]) else ""
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
                "ate_meals": ate_meals,
                "restriction_observed": restr,
                "location_tag": loc,
                "trigger_tags": trig,
                "observer_notes": obs_n,
                "composite_severity": comp_sev,
            }
            save_entry(entry)
            st.success("Entry saved gracefully.")
            st.rerun()

# VIEW 2: ISLAMIC REELS FEED
elif view_mode == "🎥 Islamic Reels Feed":
    st.markdown("<h2 style='text-align: center; color: #B45309; margin-bottom: 4px;'>📱 Islamic Reels</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #047857; font-size: 0.9em; font-weight: 500;'>Short Educational Clips & Reminders</p>", unsafe_allow_html=True)

    reels_df = load_reels()

    col_cat, col_lang = st.columns([2, 1])
    with col_cat:
        categories = ["All Categories"] + list(reels_df["category"].unique())
        selected_cat = st.selectbox("Category", categories, label_visibility="collapsed")
    with col_lang:
        languages = ["All Languages", "Arabic", "English", "Arabic / English"]
        selected_lang = st.selectbox("Language", languages, label_visibility="collapsed")

    filtered_reels = reels_df.copy()
    if selected_cat != "All Categories":
        filtered_reels = filtered_reels[filtered_reels["category"] == selected_cat]
    if selected_lang != "All Languages":
        filtered_reels = filtered_reels[filtered_reels["language"] == selected_lang]

    filtered_reels = filtered_reels.reset_index(drop=True)

    if not filtered_reels.empty:
        if "reel_idx" not in st.session_state:
            st.session_state.reel_idx = 0

        if st.session_state.reel_idx >= len(filtered_reels):
            st.session_state.reel_idx = 0

        current_reel = filtered_reels.iloc[st.session_state.reel_idx]

        st.markdown(
            f"""
            <div class="mobile-reel-card">
                <div>
                    <span class="reel-badge">{current_reel['category']}</span>
                    <span class="reel-lang-badge">🌐 {current_reel['language']}</span>
                </div>
                <h3 style="color:#1F2937; margin:6px 0 2px 0; font-size: 1.1rem; line-height:1.4;">{current_reel['title']}</h3>
                <p style="color:#6B7280; font-size:0.8rem; margin:0;">Shared by: {current_reel['added_by']}</p>
            </div>
        """,
            unsafe_allow_html=True,
        )

        st.video(current_reel["url"])

        c_prev, c_count, c_next = st.columns([1, 1, 1])
        with c_prev:
            if st.button("⏮️ Prev"):
                st.session_state.reel_idx = (st.session_state.reel_idx - 1) % len(filtered_reels)
                st.rerun()
        with c_count:
            st.markdown(f"<p style='text-align:center; margin-top:12px; font-weight:bold; color:#B45309;'>{st.session_state.reel_idx + 1} / {len(filtered_reels)}</p>", unsafe_allow_html=True)
        with c_next:
            if st.button("Next ⏭️"):
                st.session_state.reel_idx = (st.session_state.reel_idx + 1) % len(filtered_reels)
                st.rerun()

    else:
        st.info("No videos found matching these filters.")

    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("➕ Share a New Islamic Reel / Video"):
        with st.form("add_reel_form"):
            r_title = st.text_input("Title (العنوان)", placeholder="e.g., Tafseer of Ayatul Kursi")
            r_url = st.text_input("Video Link", placeholder="YouTube Shorts or Video URL")
            r_cat = st.selectbox("Topic Category", ["Quran & Tafseer (القرآن والتفسير)", "Hadith & Sunnah (الحديث والسنة)", "Reminders & Grounding (رقائق وتذكير)", "Fiqh & Daily Life (الفقه والأحكام)"])
            r_lang = st.selectbox("Language (اللغة)", ["Arabic", "English", "Arabic / English"])
            r_author = st.text_input("Your Name / Note", value="Partner")

            if st.form_submit_button("Add Reel to Feed"):
                if r_title and r_url:
                    save_reel(r_title, r_url, r_cat, r_lang, r_author)
                    st.success("Video added to the feed!")
                    st.rerun()
                else:
                    st.warning("Please enter both a title and a valid URL.")

# VIEW 3: OBSERVER ANALYTICS
else:
    pin = st.sidebar.text_input("Passkey", type="password")
    if pin != "1234" and pin != "":
        st.error("Access restricted.")
        st.stop()

    st.markdown("<h2 style='color: #B45309;'>Observer Dashboard</h2>", unsafe_allow_html=True)
    df = load_data()

    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No data recorded yet.")
