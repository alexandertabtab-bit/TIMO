import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import os
import base64
import calendar
import json
import re
import xml.etree.ElementTree as ET
from urllib.request import urlopen, Request
from datetime import date

# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="Life Chart 🌙",
    page_icon="🌙",
    layout="centered",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "life_chart_data.csv"
LITHIUM_FILE = "lithium_tests.csv"
SETTINGS_FILE = "app_settings.json"
BACKGROUND_IMAGE = "assets/mosque_background.jpg"

LITHIUM_INTERVAL_DAYS = 182

COLUMNS = [
    "date",
    "mood_type",
    "mood_rating",
    "mood_severity",
    "sleep_score",
    "ed_status",
    "purging",
    "factors",
    "notes",
    "medications",
    "med_adherence",
]

FACTOR_OPTIONS = [
    "Lack of sleep",
    "Poor quality sleep",
    "Oversleeping",
    "Changed sleep schedule",
    "Nicotine deficiency / withdrawal",
    "Nicotine use",
    "Smoking more than usual",
    "Smoking less than usual",
    "Work stress",
    "Heavy workload",
    "Problem at work",
    "Conflict with colleague",
    "Conflict with boss",
    "Job uncertainty",
    "Financial stress",
    "Family conflict",
    "Family stress",
    "Family pressure",
    "Relationship conflict",
    "Loneliness",
    "Social stress",
    "Argument with someone",
    "Feeling isolated",
    "Anxiety",
    "Overthinking",
    "Feeling overwhelmed",
    "Stress",
    "Boredom",
    "Physical illness",
    "Pain",
    "Headache / migraine",
    "Fatigue",
    "Missed medication",
    "Medication change",
    "Too much caffeine",
    "Lack of caffeine",
    "Exercise",
    "Lack of exercise",
    "Travel",
    "Change in routine",
    "Good social interaction",
    "Positive event",
    "Relaxation",
    "Good day",
    "Other",
]

# Arabic only, as requested
DAILY_QUOTES = [
    "رَبِّ اشْرَحْ لِي صَدْرِي",
    "إِنَّ مَعَ الْعُسْرِ يُسْرًا",
    "لَا تَحْزَنْ إِنَّ اللَّهَ مَعَنَا",
    "أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ",
    "حَسْبُنَا اللَّهُ وَنِعْمَ الْوَكِيلُ",
    "وَمَن يَتَوَكَّلْ عَلَى اللَّهِ فَهُوَ حَسْبُهُ",
    "لَا يُكَلِّفُ اللَّهُ نَفْسًا إِلَّا وُسْعَهَا",
    "إِنَّ اللَّهَ مَعَ الصَّابِرِينَ",
    "وَقُل رَّبِّ زِدْنِي عِلْمًا",
    "فَإِنَّ مَعَ الْعُسْرِ يُسْرًا",
]

# ============================================================
# DESIGN
# ============================================================

def inject_design():
    st.markdown("""
    <style>
    #MainMenu, footer, header {visibility:hidden;}

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(rgba(7, 22, 15, 0.46), rgba(7, 22, 15, 0.62));
    }

    .stApp {
        color: #1d261f;
    }

    .block-container {
        max-width: 520px !important;
        margin: auto !important;
        padding: 14px 12px 80px !important;
    }

    h1, h2, h3, p, label, .stMarkdown {
        color: #172119 !important;
    }

    .app-title {
        background: rgba(248, 246, 238, 0.94);
        border-radius: 26px;
        padding: 14px 20px;
        text-align: center;
        font-size: 34px;
        font-weight: 800;
        margin-bottom: 12px;
        box-shadow: 0 8px 24px rgba(0,0,0,.22);
    }

    .quote-box {
        background: rgba(248, 246, 238, 0.96);
        border-radius: 26px;
        padding: 26px 20px;
        margin: 0 0 14px 0;
        box-shadow: 0 8px 24px rgba(0,0,0,.22);
        border: 1px solid rgba(255,255,255,.55);
    }

    .arabic-text {
        direction: rtl;
        unicode-bidi: plaintext;
        text-align: center;
        font-size: 28px;
        line-height: 2.05;
        font-family: "Noto Naskh Arabic", "Amiri", "Tahoma", serif;
        font-weight: 700;
        color: #173d2b !important;
    }

    div[data-testid="stRadio"] {
        background: rgba(248,246,238,.94);
        border-radius: 20px;
        padding: 8px 12px;
        box-shadow: 0 6px 18px rgba(0,0,0,.18);
        margin-bottom: 12px;
    }

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    textarea {
        background: rgba(250,249,245,.98) !important;
        border-radius: 16px !important;
        color: #172119 !important;
    }

    .stSlider {
        background: rgba(248,246,238,.94);
        padding: 12px 14px 4px;
        border-radius: 18px;
        box-shadow: 0 6px 18px rgba(0,0,0,.15);
    }

    [data-testid="stMetric"] {
        background: rgba(248,246,238,.95);
        border-radius: 18px;
        padding: 12px;
    }

    .stButton > button {
        width: 100%;
        min-height: 50px;
        border-radius: 18px;
        font-weight: 700;
        font-size: 16px;
    }

    .content-card {
        background: rgba(248,246,238,.96);
        border-radius: 24px;
        padding: 18px;
        box-shadow: 0 8px 24px rgba(0,0,0,.20);
        margin-bottom: 12px;
    }

    .calendar-day {
        background: rgba(248,246,238,.96);
        color: #172119 !important;
        border-radius: 10px;
        min-height: 58px;
        padding: 7px 2px;
        text-align: center;
        font-size: 11px;
        margin: 2px 0;
    }

    .calendar-head {
        background: rgba(248,246,238,.90);
        color: #172119 !important;
        border-radius: 8px;
        text-align: center;
        font-weight: 700;
        font-size: 11px;
        padding: 5px 1px;
        margin-bottom: 3px;
    }

    .reels-wrap {
        background: #000;
        border-radius: 26px;
        overflow: hidden;
        box-shadow: 0 8px 26px rgba(0,0,0,.28);
    }

    @media (max-width: 600px) {
        .block-container {
            max-width: 100% !important;
            padding-left: 8px !important;
            padding-right: 8px !important;
        }
        .app-title {font-size: 29px;}
        .arabic-text {font-size: 25px;}
    }
    </style>
    """, unsafe_allow_html=True)


def inject_background():
    if not os.path.exists(BACKGROUND_IMAGE):
        return
    with open(BACKGROUND_IMAGE, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    st.markdown(f"""
    <style>
    [data-testid="stAppViewContainer"] {{
        background-image:
            linear-gradient(rgba(7,22,15,.40), rgba(7,22,15,.60)),
            url("data:image/jpeg;base64,{encoded}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    </style>
    """, unsafe_allow_html=True)


inject_design()
inject_background()

# ============================================================
# DATA
# ============================================================

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = None
        return df[COLUMNS]
    return pd.DataFrame(columns=COLUMNS)


def save_entry(entry_date, updates):
    df = load_data()
    entry_date = pd.Timestamp(entry_date)
    existing = df[df["date"] == entry_date]

    if existing.empty:
        row = {col: None for col in COLUMNS}
        row["date"] = entry_date
    else:
        row = existing.iloc[0].to_dict()

    row.update(updates)
    df = df[df["date"] != entry_date]
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df = df.sort_values("date")
    df.to_csv(DATA_FILE, index=False)


# ============================================================
# LITHIUM
# ============================================================

def load_lithium():
    if os.path.exists(LITHIUM_FILE):
        df = pd.read_csv(LITHIUM_FILE)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        return df
    return pd.DataFrame(columns=["date", "result", "notes"])


def save_lithium(test_date, result, notes):
    df = load_lithium()
    row = pd.DataFrame([{
        "date": pd.Timestamp(test_date),
        "result": result,
        "notes": notes,
    }])
    df = pd.concat([df, row], ignore_index=True)
    df = df.sort_values("date")
    df.to_csv(LITHIUM_FILE, index=False)


def render_lithium():
    st.subheader("💊 Lithium tracker")
    tests = load_lithium()

    if not tests.empty:
        tests = tests.dropna(subset=["date"]).sort_values("date")
        if not tests.empty:
            last = tests.iloc[-1]
            next_date = last["date"] + pd.Timedelta(days=LITHIUM_INTERVAL_DAYS)
            days_left = (next_date.normalize() - pd.Timestamp.today().normalize()).days

            c1, c2 = st.columns(2)
            c1.metric("Last test", last["date"].strftime("%d %b %Y"))
            c2.metric("Next test", next_date.strftime("%d %b %Y"))

            st.markdown(f"**Last result:** {last['result']}")
            if pd.notna(last.get("notes")) and str(last["notes"]).strip():
                st.caption(str(last["notes"]))

            if days_left < 0:
                st.error(f"Overdue by {-days_left} days.")
            elif days_left <= 14:
                st.warning(f"Due in {days_left} days.")
            else:
                st.success(f"Next test in approximately {days_left} days.")
    else:
        st.info("No lithium test has been logged yet.")

    with st.expander("➕ Log a lithium test"):
        test_date = st.date_input("Test date", value=date.today(), key="lt_date")
        result = st.text_input("Result", key="lt_result")
        notes = st.text_area("Notes", key="lt_notes")
        if st.button("Save lithium test", type="primary"):
            if result.strip():
                save_lithium(test_date, result.strip(), notes)
                st.success("Saved.")
                st.rerun()
            else:
                st.warning("Please enter the result.")

    if not tests.empty:
        with st.expander("Previous tests"):
            st.dataframe(
                tests.sort_values("date", ascending=False),
                use_container_width=True,
                hide_index=True,
            )


# ============================================================
# SETTINGS + YOUTUBE PLAYLIST
# ============================================================

def load_settings():
    default = {"youtube_playlist": ""}
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            default.update(saved)
        except Exception:
            pass
    return default


def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, ensure_ascii=False, indent=2)


def extract_playlist_id(text):
    text = (text or "").strip()
    if not text:
        return ""
    match = re.search(r"[?&]list=([^&]+)", text)
    if match:
        return match.group(1)
    if text.startswith(("PL", "UU", "LL", "RD")) and " " not in text:
        return text
    return ""


@st.cache_data(ttl=900, show_spinner=False)
def get_playlist_videos(playlist_id):
    if not playlist_id:
        return []

    feed_url = (
        "https://www.youtube.com/feeds/videos.xml?playlist_id="
        + playlist_id
    )

    try:
        request = Request(
            feed_url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urlopen(request, timeout=10) as response:
            xml_data = response.read()

        root = ET.fromstring(xml_data)
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "yt": "http://www.youtube.com/xml/schemas/2015",
        }

        videos = []
        for entry in root.findall("atom:entry", ns):
            title = entry.findtext("atom:title", default="Video", namespaces=ns)
            video_id = entry.findtext("yt:videoId", default="", namespaces=ns)
            if video_id:
                videos.append({
                    "title": title,
                    "video_id": video_id,
                })
        return videos
    except Exception:
        return []


def render_playlist_settings():
    st.subheader("🎬 Reels playlist")

    settings = load_settings()

    st.write(
        "Paste your YouTube playlist link once. "
        "After that, add as many videos or Shorts as you want to the playlist "
        "on YouTube. The app will load them automatically."
    )

    playlist = st.text_input(
        "YouTube playlist link",
        value=settings.get("youtube_playlist", ""),
        placeholder="https://www.youtube.com/playlist?list=...",
    )

    if st.button("Save playlist", type="primary"):
        playlist_id = extract_playlist_id(playlist)
        if playlist_id:
            settings["youtube_playlist"] = playlist
            save_settings(settings)
            get_playlist_videos.clear()
            st.success("Playlist saved. New videos added to that playlist will appear automatically.")
        else:
            st.warning("Please paste a valid YouTube playlist link containing ?list=...")


def render_reels():
    settings = load_settings()
    playlist_id = extract_playlist_id(settings.get("youtube_playlist", ""))
    videos = get_playlist_videos(playlist_id)

    if not playlist_id:
        st.info("No playlist has been set yet. Open My View → 🎬 Reels Setup and paste the playlist link once.")
        return

    if not videos:
        st.warning(
            "The playlist could not be loaded right now. "
            "Make sure the playlist is public or unlisted and contains videos."
        )
        return

    cards = []
    for video in videos:
        embed = (
            "https://www.youtube.com/embed/"
            + video["video_id"]
            + "?playsinline=1&rel=0"
        )
        cards.append(f"""
        <section class="reel">
            <iframe
                src="{embed}"
                title="{video['title'].replace('"', '&quot;')}"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
                allowfullscreen>
            </iframe>
            <div class="caption">{video['title']}</div>
        </section>
        """)

    html = f"""
    <html>
    <head>
    <style>
    * {{ box-sizing: border-box; }}
    body {{
        margin: 0;
        background: #000;
        overflow: hidden;
        font-family: Arial, sans-serif;
    }}
    .feed {{
        height: 100vh;
        overflow-y: auto;
        scroll-snap-type: y mandatory;
        scrollbar-width: none;
        -webkit-overflow-scrolling: touch;
    }}
    .feed::-webkit-scrollbar {{ display: none; }}
    .reel {{
        height: 100vh;
        width: 100%;
        position: relative;
        scroll-snap-align: start;
        background: #000;
    }}
    iframe {{
        width: 100%;
        height: 100%;
        border: 0;
    }}
    .caption {{
        position: absolute;
        left: 0;
        right: 0;
        bottom: 0;
        padding: 80px 18px 28px;
        color: white;
        font-size: 17px;
        font-weight: 700;
        background: linear-gradient(transparent, rgba(0,0,0,.9));
        pointer-events: none;
    }}
    </style>
    </head>
    <body>
        <div class="feed">
            {''.join(cards)}
        </div>
    </body>
    </html>
    """

    st.markdown('<div class="reels-wrap">', unsafe_allow_html=True)
    components.html(html, height=720, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# QUOTE
# ============================================================

def render_quote():
    quote = DAILY_QUOTES[date.today().toordinal() % len(DAILY_QUOTES)]
    # Plain Streamlit markdown, no literal HTML tags can appear to the user.
    st.markdown(
        f'<div class="quote-box"><div class="arabic-text" dir="rtl">{quote}</div></div>',
        unsafe_allow_html=True,
    )


# ============================================================
# HELPERS
# ============================================================

def severity_to_mood(mood_type, severity):
    if mood_type == "Stable":
        return 0
    level = max(1, min(4, round(float(severity) / 2.5)))
    return -level if mood_type == "Depression" else level


def render_calendar():
    df = load_data()
    st.subheader("📅 ED & Purging Calendar")

    selected = st.date_input(
        "Month",
        value=date.today(),
        key="calendar_month",
    )

    year, month = selected.year, selected.month
    st.markdown(f"### {calendar.month_name[month]} {year}")

    headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cols = st.columns(7)
    for i, name in enumerate(headers):
        cols[i].markdown(
            f'<div class="calendar-head">{name}</div>',
            unsafe_allow_html=True,
        )

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")

    for week in calendar.monthcalendar(year, month):
        cols = st.columns(7)
        for i, day_num in enumerate(week):
            if day_num == 0:
                cols[i].write("")
                continue

            current = pd.Timestamp(year=year, month=month, day=day_num)
            label = ""

            match = df[df["date"] == current] if not df.empty else pd.DataFrame()

            if not match.empty:
                row = match.iloc[-1]
                purge_value = str(row.get("purging", "")).lower()
                ed_value = str(row.get("ed_status", "")).lower()

                if purge_value in ["true", "yes", "1"]:
                    label = "🔴<br>Purging"
                elif ed_value == "yes":
                    label = "🟡<br>ED"

            cols[i].markdown(
                f'<div class="calendar-day"><b>{day_num}</b><br>{label}</div>',
                unsafe_allow_html=True,
            )

    st.caption("🟡 ED active day   •   🔴 Purging occurred")


def render_mood_chart():
    df = load_data().dropna(subset=["mood_rating"])
    if df.empty:
        st.info("No mood data yet.")
        return

    df = df.sort_values("date")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["mood_rating"],
        mode="lines+markers",
        marker=dict(size=9),
        name="Mood",
    ))
    fig.add_hline(y=0, line_dash="dash")
    fig.update_layout(
        title="Mood over time",
        yaxis=dict(range=[-4.5, 4.5], title="Mood"),
        height=400,
        margin=dict(l=20, r=20, t=55, b=25),
        paper_bgcolor="rgba(248,246,238,.96)",
        plot_bgcolor="rgba(248,246,238,.96)",
    )
    st.plotly_chart(fig, use_container_width=True)


def render_factor_charts():
    df = load_data().dropna(subset=["factors"])
    if df.empty:
        st.info("No factors have been logged yet.")
        return

    rows = []
    for _, row in df.iterrows():
        for factor in str(row["factors"]).split(","):
            factor = factor.strip()
            if factor:
                rows.append({"factor": factor})

    if not rows:
        st.info("No factors have been logged yet.")
        return

    factor_df = pd.DataFrame(rows)
    counts = factor_df["factor"].value_counts().head(15)

    fig = go.Figure(go.Bar(
        x=counts.values,
        y=counts.index,
        orientation="h",
    ))
    fig.update_layout(
        title="Most common factors",
        height=max(360, len(counts) * 38),
        margin=dict(l=20, r=20, t=55, b=25),
        paper_bgcolor="rgba(248,246,238,.96)",
        plot_bgcolor="rgba(248,246,238,.96)",
        yaxis=dict(autorange="reversed"),
    )
    st.plotly_chart(fig, use_container_width=True)


# ============================================================
# APP
# ============================================================

st.markdown('<div class="app-title">🌙 Life Chart</div>', unsafe_allow_html=True)
render_quote()

view = st.radio(
    "View",
    ["👤 His View", "🔐 My View"],
    horizontal=True,
    label_visibility="collapsed",
)

# ============================================================
# HIS VIEW
# ============================================================

if view == "👤 His View":
    tab = st.radio(
        "Navigation",
        ["🏠 Check-in", "📅 Calendar", "🎬 Reels"],
        horizontal=True,
        label_visibility="collapsed",
        key="his_nav",
    )

    if tab == "🏠 Check-in":
        st.subheader("Today's check-in 🌙")

        entry_date = st.date_input(
            "Date",
            value=date.today(),
            key="his_date",
        )

        st.markdown("### Mood")
        mood_type = st.radio(
            "How do you feel today?",
            ["Stable", "Depression", "Hypomania"],
            horizontal=True,
            key="his_mood_type",
        )

        mood_severity = 0
        if mood_type == "Depression":
            mood_severity = st.slider(
                "Depression intensity",
                1, 10, 5,
                key="depression_severity",
            )
        elif mood_type == "Hypomania":
            mood_severity = st.slider(
                "Hypomania intensity",
                1, 10, 5,
                key="hypomania_severity",
            )

        st.markdown("### 😴 Sleep")
        sleep_score = st.slider(
            "How was your sleep?",
            1, 10, 5,
            key="his_sleep",
        )

        sleep_labels = {
            range(1, 3): "Very bad",
            range(3, 5): "Bad",
            range(5, 7): "Okay",
            range(7, 9): "Good",
            range(9, 11): "Excellent",
        }
        sleep_text = next(
            label for values, label in sleep_labels.items()
            if sleep_score in values
        )
        st.caption(f"{sleep_score}/10 — {sleep_text}")

        st.markdown("### ED status")
        ed_status = st.radio(
            "Was your ED active today?",
            ["No", "Yes"],
            horizontal=True,
            key="his_ed",
        )

        purging = False
        if ed_status == "Yes":
            purging = st.radio(
                "Did purging happen today?",
                ["No", "Yes"],
                horizontal=True,
                key="his_purging",
            ) == "Yes"

        if st.button("Save today's check-in 🤍", type="primary"):
            save_entry(entry_date, {
                "mood_type": mood_type,
                "mood_rating": severity_to_mood(mood_type, mood_severity),
                "mood_severity": mood_severity,
                "sleep_score": sleep_score,
                "ed_status": ed_status,
                "purging": purging,
            })
            st.success("Saved 🤍")

    elif tab == "📅 Calendar":
        render_calendar()

    else:
        render_reels()


# ============================================================
# MY VIEW
# ============================================================

else:
    tab = st.radio(
        "Navigation",
        ["📝 Entry", "📈 Mood", "🧩 Factors", "📅 Calendar", "💊 Lithium", "🎬 Reels Setup"],
        horizontal=True,
        label_visibility="collapsed",
        key="my_nav",
    )

    if tab == "📝 Entry":
        st.subheader("Detailed entry")

        entry_date = st.date_input(
            "Date",
            value=date.today(),
            key="my_date",
        )

        mood = st.slider(
            "Mood",
            -4, 4, 0,
            key="my_mood",
        )

        labels = {
            -4: "Severe depression",
            -3: "Marked depression",
            -2: "Moderate depression",
            -1: "Mild depression",
            0: "Stable",
            1: "Mild hypomania",
            2: "Moderate hypomania",
            3: "Marked hypomania",
            4: "Severe hypomania",
        }
        st.caption(labels[mood])

        sleep_score = st.slider(
            "Sleep quality",
            1, 10, 5,
            key="my_sleep",
        )

        st.subheader("Factors that may have influenced today")
        selected = st.multiselect(
            "Choose all that apply",
            FACTOR_OPTIONS,
            key="my_factors",
        )

        other = ""
        if "Other" in selected:
            other = st.text_input(
                "Describe the other factor",
                key="my_other_factor",
            )

        final_factors = [x for x in selected if x != "Other"]
        if other.strip():
            final_factors.append(other.strip())

        notes = st.text_area(
            "Additional notes",
            key="my_notes",
        )

        st.markdown("### Medication")
        medications = st.text_input(
            "Medication taken",
            key="my_medications",
        )
        med_adherence = st.selectbox(
            "Medication adherence",
            ["As prescribed", "Missed a dose", "Not applicable"],
            key="my_adherence",
        )

        st.markdown("### ED status")
        ed_status = st.radio(
            "ED active today?",
            ["No", "Yes"],
            horizontal=True,
            key="my_ed",
        )

        purging = False
        if ed_status == "Yes":
            purging = st.checkbox(
                "Purging occurred today",
                key="my_purging",
            )

        if st.button("Save detailed entry", type="primary"):
            save_entry(entry_date, {
                "mood_rating": mood,
                "sleep_score": sleep_score,
                "factors": ", ".join(final_factors),
                "notes": notes,
                "medications": medications,
                "med_adherence": med_adherence,
                "ed_status": ed_status,
                "purging": purging,
            })
            st.success("Entry saved.")

    elif tab == "📈 Mood":
        render_mood_chart()

    elif tab == "🧩 Factors":
        render_factor_charts()

    elif tab == "📅 Calendar":
        render_calendar()

    elif tab == "💊 Lithium":
        render_lithium()

    else:
        render_playlist_settings()
