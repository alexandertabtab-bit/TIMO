import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import base64
import calendar
from datetime import date, datetime

import plotly.graph_objects as go


# ============================================================
# APP CONFIG
# ============================================================

st.set_page_config(
    page_title="Life Chart 🌙",
    page_icon="🌙",
    layout="centered",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "life_chart_data.csv"
LITHIUM_FILE = "lithium_tests.csv"

BACKGROUND_IMAGE = "assets/mosque_background.jpg"

LITHIUM_INTERVAL_DAYS = 182


# ============================================================
# DATA
# ============================================================

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
    "med_adherence"
]


FACTOR_OPTIONS = [

    # Sleep
    "Lack of sleep",
    "Poor quality sleep",
    "Oversleeping",
    "Changed sleep schedule",

    # Nicotine
    "Nicotine deficiency / withdrawal",
    "Nicotine use",
    "Smoking more than usual",
    "Smoking less than usual",

    # Work
    "Problem at work",
    "Work stress",
    "Heavy workload",
    "Conflict with colleague",
    "Conflict with boss",
    "Job uncertainty",

    # Family
    "Family conflict",
    "Family stress",
    "Family pressure",

    # Relationship / social
    "Relationship conflict",
    "Loneliness",
    "Social stress",
    "Argument with someone",
    "Feeling isolated",

    # Mental / emotional
    "Anxiety",
    "Overthinking",
    "Feeling overwhelmed",
    "Stress",
    "Boredom",

    # Physical
    "Physical illness",
    "Pain",
    "Headache / migraine",
    "Fatigue",

    # Medication
    "Missed medication",
    "Medication change",

    # Lifestyle
    "Too much caffeine",
    "Lack of caffeine",
    "Exercise",
    "Lack of exercise",
    "Travel",
    "Change in routine",

    # Positive
    "Good social interaction",
    "Positive event",
    "Relaxation",
    "Good day",

    "Other"
]


# ============================================================
# DAILY QUOTES
# ============================================================

DAILY_QUOTES = [

    (
        "رَبِّ اشْرَحْ لِي صَدْرِي",
        "My Lord, expand for me my chest. — Quran 20:25"
    ),

    (
        "إِنَّ مَعَ الْعُسْرِ يُسْرًا",
        "Indeed, with hardship comes ease. — Quran 94:6"
    ),

    (
        "لَا تَحْزَنْ إِنَّ اللَّهَ مَعَنَا",
        "Do not grieve; indeed Allah is with us. — Quran 9:40"
    ),

    (
        "أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ",
        "Surely in the remembrance of Allah do hearts find comfort. — Quran 13:28"
    ),

    (
        "حَسْبُنَا اللَّهُ وَنِعْمَ الْوَكِيلُ",
        "Allah is sufficient for us, and He is the best disposer of affairs."
    ),

    (
        "وَمَن يَتَوَكَّلْ عَلَى اللَّهِ فَهُوَ حَسْبُهُ",
        "Whoever puts their trust in Allah, He is sufficient for them. — Quran 65:3"
    ),

    (
        "لَا يُكَلِّفُ اللَّهُ نَفْسًا إِلَّا وُسْعَهَا",
        "Allah does not burden a soul beyond what it can bear. — Quran 2:286"
    ),

    (
        "إِنَّ اللَّهَ مَعَ الصَّابِرِينَ",
        "Indeed, Allah is with those who are patient. — Quran 2:153"
    ),

    (
        "وَقُل رَّبِّ زِدْنِي عِلْمًا",
        "My Lord, increase me in knowledge. — Quran 20:114"
    ),

    (
        "فَإِنَّ مَعَ الْعُسْرِ يُسْرًا",
        "So surely with hardship comes ease. — Quran 94:5"
    )
]


# ============================================================
# CSS
# ============================================================

def inject_css():

    st.markdown(
        """
        <style>

        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        header {
            visibility: hidden;
        }

        .block-container {
            max-width: 520px;
            margin: auto;
            padding-top: 15px;
            padding-left: 12px;
            padding-right: 12px;
            padding-bottom: 80px;
        }

        h1 {
            text-align: center;
        }

        .stButton > button {
            width: 100%;
            min-height: 52px;
            border-radius: 18px;
            font-size: 16px;
            font-weight: 600;
        }

        textarea {
            border-radius: 18px !important;
        }

        div[data-baseweb="input"] > div {
            border-radius: 16px;
        }

        div[data-baseweb="select"] > div {
            border-radius: 16px;
        }

        .quote-card {

            background: rgba(255,255,255,0.82);

            backdrop-filter: blur(10px);

            padding: 22px;

            border-radius: 25px;

            margin-bottom: 20px;

            text-align: center;
        }

        .arabic-quote {

            font-size: 27px;

            line-height: 2;

            direction: rtl;

            text-align: center;

            font-family:
                "Noto Naskh Arabic",
                "Amiri",
                serif;

            font-weight: 600;

            margin-bottom: 12px;
        }

        .english-quote {

            font-size: 15px;

            line-height: 1.6;

            text-align: center;

            font-style: italic;

            opacity: 0.85;
        }

        .calendar-day {

            background: rgba(255,255,255,0.82);

            border-radius: 10px;

            padding: 7px;

            min-height: 55px;

            text-align: center;

            font-size: 11px;

            margin: 2px;
        }

        .calendar-header {

            text-align: center;

            font-weight: bold;

            font-size: 11px;

            opacity: 0.8;
        }

        @media (max-width: 600px) {

            .block-container {

                width: 100%;

                padding-left: 8px;

                padding-right: 8px;
            }

            h1 {

                font-size: 27px !important;
            }

            .stButton > button {

                min-height: 55px;

                border-radius: 18px;
            }

        }

        </style>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# BACKGROUND
# ============================================================

def inject_background():

    if not os.path.exists(BACKGROUND_IMAGE):

        return

    with open(
        BACKGROUND_IMAGE,
        "rb"
    ) as image_file:

        encoded = base64.b64encode(
            image_file.read()
        ).decode()

    st.markdown(
        f"""
        <style>

        [data-testid="stAppViewContainer"] {{

            background-image:

                linear-gradient(
                    rgba(10, 20, 15, 0.35),
                    rgba(10, 20, 15, 0.45)
                ),

                url(
                    "data:image/jpeg;base64,{encoded}"
                );

            background-size: cover;

            background-position: center;

            background-attachment: fixed;
        }}

        </style>
        """,
        unsafe_allow_html=True
    )


inject_css()
inject_background()


# ============================================================
# DATA FUNCTIONS
# ============================================================

def load_data():

    if os.path.exists(DATA_FILE):

        df = pd.read_csv(
            DATA_FILE
        )

        df["date"] = pd.to_datetime(
            df["date"]
        )

        for column in COLUMNS:

            if column not in df.columns:

                df[column] = None

        return df[COLUMNS]

    return pd.DataFrame(
        columns=COLUMNS
    )


def save_entry(
    entry_date,
    updates
):

    df = load_data()

    entry_date = pd.Timestamp(
        entry_date
    )

    existing = df[
        df["date"] == entry_date
    ]

    if existing.empty:

        row = {
            column: None
            for column in COLUMNS
        }

        row["date"] = entry_date

    else:

        row = existing.iloc[0].to_dict()

    row.update(updates)

    df = df[
        df["date"] != entry_date
    ]

    new_row = pd.DataFrame(
        [row]
    )

    df = pd.concat(
        [
            df,
            new_row
        ],
        ignore_index=True
    )

    df = df.sort_values(
        "date"
    )

    df.to_csv(
        DATA_FILE,
        index=False
    )


# ============================================================
# DAILY QUOTE
# ============================================================

def render_quote():

    index = (
        date.today().toordinal()
        % len(DAILY_QUOTES)
    )

    arabic, english = DAILY_QUOTES[
        index
    ]

    st.markdown(
        f"""
        <div class="quote-card">

            <div class="arabic-quote">

                {arabic}

            </div>

            <div class="english-quote">

                {english}

            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# MOOD CONVERSION
# ============================================================

def severity_to_mood(
    mood_type,
    severity
):

    if mood_type == "Stable":

        return 0

    level = round(
        severity / 2.5
    )

    level = max(
        1,
        min(4, level)
    )

    if mood_type == "Depression":

        return -level

    return level


# ============================================================
# LITHIUM TRACKER
# ============================================================

def load_lithium():

    if os.path.exists(LITHIUM_FILE):

        df = pd.read_csv(
            LITHIUM_FILE
        )

        df["date"] = pd.to_datetime(
            df["date"]
        )

        return df

    return pd.DataFrame(
        columns=[
            "date",
            "result",
            "notes"
        ]
    )


def save_lithium(
    test_date,
    result,
    notes
):

    df = load_lithium()

    new_row = pd.DataFrame([
        {
            "date": pd.Timestamp(
                test_date
            ),

            "result": result,

            "notes": notes
        }
    ])

    df = pd.concat(
        [
            df,
            new_row
        ],
        ignore_index=True
    )

    df = df.sort_values(
        "date"
    )

    df.to_csv(
        LITHIUM_FILE,
        index=False
    )


def render_lithium_tracker():

    tests = load_lithium()

    st.subheader(
        "💊 Lithium tracker"
    )

    if tests.empty:

        st.info(
            "No lithium test has been logged yet."
        )

        return

    tests = tests.sort_values(
        "date"
    )

    last = tests.iloc[-1]

    last_date = last["date"]

    next_date = (
        last_date
        + pd.Timedelta(
            days=LITHIUM_INTERVAL_DAYS
        )
    )

    days_remaining = (
        next_date
        - pd.Timestamp.today()
    ).days

    col1, col2 = st.columns(2)

    col1.metric(
        "Last test",
        last_date.strftime(
            "%d %b %Y"
        )
    )

    col2.metric(
        "Next test",
        next_date.strftime(
            "%d %b %Y"
        )
    )

    st.write(
        f"**Result:** {last['result']}"
    )

    if pd.notna(
        last["notes"]
    ):

        if str(
            last["notes"]
        ).strip():

            st.caption(
                str(last["notes"])
            )

    if days_remaining < 0:

        st.error(
            f"⚠️ The next lithium test is overdue by {-days_remaining} days."
        )

    elif days_remaining <= 14:

        st.warning(
            f"⚠️ The next lithium test is due in {days_remaining} days."
        )

    else:

        st.success(
            f"Next test is in approximately {days_remaining} days."
        )


# ============================================================
# ED / PURGING CALENDAR
# ============================================================

def render_ed_calendar():

    df = load_data()

    st.subheader(
        "📅 ED & Purging Calendar"
    )

    selected_month = st.date_input(
        "Choose month",
        value=date.today(),
        key="calendar_month"
    )

    year = selected_month.year

    month = selected_month.month

    month_name = calendar.month_name[
        month
    ]

    st.markdown(
        f"### {month_name} {year}"
    )

    if not df.empty:

        df["date"] = pd.to_datetime(
            df["date"]
        )

    cal = calendar.monthcalendar(
        year,
        month
    )

    day_names = [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun"
    ]

    header_cols = st.columns(7)

    for i, day_name in enumerate(
        day_names
    ):

        header_cols[i].markdown(
            f"""
            <div class="calendar-header">
                {day_name}
            </div>
            """,
            unsafe_allow_html=True
        )

    for week in cal:

        cols = st.columns(7)

        for i, day_number in enumerate(
            week
        ):

            if day_number == 0:

                cols[i].write("")

                continue

            current_date = pd.Timestamp(
                year=year,
                month=month,
                day=day_number
            )

            status = ""

            if not df.empty:

                matching = df[
                    df["date"]
                    == current_date
                ]

                if not matching.empty:

                    row = matching.iloc[-1]

                    ed_status = str(
                        row.get(
                            "ed_status",
                            ""
                        )
                    ).lower()

                    purging = row.get(
                        "purging",
                        False
                    )

                    if str(purging).lower() in [
                        "true",
                        "yes",
                        "1"
                    ]:

                        status = "🔴<br>Purging"

                    elif ed_status == "yes":

                        status = "🟡<br>ED"

            cols[i].markdown(
                f"""
                <div class="calendar-day">

                    <b>
                        {day_number}
                    </b>

                    <br>

                    {status}

                </div>
                """,
                unsafe_allow_html=True
            )

    st.caption(
        "🟡 ED active day • 🔴 Purging occurred"
    )


# ============================================================
# MOOD CHART
# ============================================================

def render_mood_chart():

    df = load_data()

    if df.empty:

        st.info(
            "No mood data yet."
        )

        return

    df = df.dropna(
        subset=["mood_rating"]
    )

    if df.empty:

        return

    df = df.sort_values(
        "date"
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["mood_rating"],
            mode="lines+markers",
            marker=dict(
                size=10
            )
        )
    )

    fig.add_hline(
        y=0,
        line_dash="dash"
    )

    fig.update_layout(
        title="Mood over time",
        height=400,
        yaxis=dict(
            range=[-4.5, 4.5]
        ),
        margin=dict(
            l=10,
            r=10,
            t=50,
            b=20
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# FACTOR CHARTS
# ============================================================

def render_factor_charts():

    df = load_data()

    if df.empty:

        st.info(
            "No factor data yet."
        )

        return

    all_factors = []

    for _, row in df.iterrows():

        factors = row.get(
            "factors"
        )

        if pd.isna(factors):

            continue

        for factor in str(
            factors
        ).split(","):

            factor = factor.strip()

            if factor:

                all_factors.append(
                    {
                        "factor": factor,
                        "mood": abs(
                            float(
                                row.get(
                                    "mood_rating",
                                    0
                                )
                            )
                        )
                    }
                )

    if not all_factors:

        st.info(
            "No factors have been logged yet."
        )

        return

    factor_df = pd.DataFrame(
        all_factors
    )

    counts = (
        factor_df["factor"]
        .value_counts()
    )

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=counts.index,
            y=counts.values
        )
    )

    fig.update_layout(
        title="Most common factors",
        height=400,
        xaxis_title="Factor",
        yaxis_title="Times mentioned"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# INSTAGRAM STYLE REELS
# ============================================================

def render_reels():

    # ADD YOUR REELS HERE
    # You only need to put links once.

    reels = [

        {
            "title": "Islamic reminder",
            "url": "",
            "type": "youtube"
        },

        {
            "title": "Motivation",
            "url": "",
            "type": "youtube"
        },

        {
            "title": "A reminder for difficult days",
            "url": "",
            "type": "youtube"
        }
    ]

    valid_reels = []

    for reel in reels:

        if reel["url"].strip():

            valid_reels.append(
                reel
            )

    if not valid_reels:

        st.info(
            "No reels have been added yet. "
            "Add links inside the reels section in app.py."
        )

        return

    reels_html = ""

    for reel in valid_reels:

        url = reel["url"]

        title = reel["title"]

        # YouTube Shorts support

        if "youtube.com" in url:

            if "/shorts/" in url:

                video_id = url.split(
                    "/shorts/"
                )[1].split("?")[0]

                embed_url = (
                    "https://www.youtube.com/embed/"
                    + video_id
                )

            elif "watch?v=" in url:

                video_id = url.split(
                    "watch?v="
                )[1].split("&")[0]

                embed_url = (
                    "https://www.youtube.com/embed/"
                    + video_id
                )

            else:

                embed_url = url

            media = f'''
            <iframe
                src="{embed_url}"
                allowfullscreen
                allow="autoplay; encrypted-media"
            ></iframe>
            '''

        # Direct MP4 support

        elif url.endswith(
            ".mp4"
        ):

            media = f'''
            <video
                controls
                playsinline
                preload="metadata"
            >
                <source
                    src="{url}"
                    type="video/mp4"
                >
            </video>
            '''

        else:

            media = f'''
            <div class="unsupported">

                This video format is not supported.

            </div>
            '''

        reels_html += f'''

        <div class="reel">

            {media}

            <div class="overlay">

                <div class="reel-title">

                    {title}

                </div>

            </div>

        </div>

        '''

    html = f"""

    <html>

    <head>

    <style>

    * {{
        box-sizing: border-box;
    }}

    body {{
        margin: 0;
        background: black;
        overflow: hidden;
    }}

    .feed {{

        height: 100vh;

        overflow-y: scroll;

        scroll-snap-type:
            y mandatory;

        scrollbar-width: none;
    }}

    .feed::-webkit-scrollbar {{
        display: none;
    }}

    .reel {{

        width: 100%;

        height: 100vh;

        position: relative;

        scroll-snap-align: start;

        background: black;
    }}

    iframe,
    video {{

        width: 100%;

        height: 100%;

        border: none;

        object-fit: cover;
    }}

    .overlay {{

        position: absolute;

        bottom: 0;

        left: 0;

        right: 0;

        padding:
            100px 20px 40px 20px;

        color: white;

        background:
            linear-gradient(
                transparent,
                rgba(0,0,0,0.9)
            );
    }}

    .reel-title {{

        font-size: 18px;

        font-weight: bold;

        line-height: 1.5;
    }}

    .unsupported {{

        color: white;

        display: flex;

        align-items: center;

        justify-content: center;

        height: 100%;
    }}

    </style>

    </head>

    <body>

        <div class="feed">

            {reels_html}

        </div>

    </body>

    </html>
    """

    components.html(
        html,
        height=750,
        scrolling=False
    )


# ============================================================
# MAIN APP
# ============================================================

st.title(
    "🌙 Life Chart"
)

render_quote()


view = st.radio(
    "Choose view",
    [
        "👤 His View",
        "🔐 My View"
    ],
    horizontal=True
)


# ============================================================
# HIS VIEW
# ============================================================

if view == "👤 His View":

    tab = st.radio(
        "Navigation",
        [
            "🏠 Check-in",
            "📅 Calendar",
            "🎬 Reels"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )


    # ========================================================
    # CHECK-IN
    # ========================================================

    if tab == "🏠 Check-in":

        st.subheader(
            "Today's check-in 🌙"
        )

        entry_date = st.date_input(
            "Date",
            value=date.today()
        )


        # ----------------------------------------------------
        # MOOD
        # ----------------------------------------------------

        st.markdown(
            "### Mood"
        )

        mood_type = st.radio(
            "How do you feel today?",
            [
                "Stable",
                "Depression",
                "Hypomania"
            ],
            horizontal=True
        )

        mood_severity = 0

        if mood_type == "Depression":

            mood_severity = st.slider(
                "Depression intensity",
                min_value=1,
                max_value=10,
                value=5
            )

        elif mood_type == "Hypomania":

            mood_severity = st.slider(
                "Hypomania intensity",
                min_value=1,
                max_value=10,
                value=5
            )


        # ----------------------------------------------------
        # SLEEP - ALWAYS SEPARATE
        # ----------------------------------------------------

        st.markdown("---")

        st.markdown(
            "### 😴 Sleep"
        )

        sleep_score = st.slider(
            "How was your sleep?",
            min_value=1,
            max_value=10,
            value=5
        )

        if sleep_score <= 2:

            sleep_text = "Very bad"

        elif sleep_score <= 4:

            sleep_text = "Bad"

        elif sleep_score <= 6:

            sleep_text = "Okay"

        elif sleep_score <= 8:

            sleep_text = "Good"

        else:

            sleep_text = "Excellent"

        st.caption(
            f"{sleep_score}/10 — {sleep_text}"
        )


        # ----------------------------------------------------
        # ED STATUS
        # ----------------------------------------------------

        st.markdown("---")

        st.markdown(
            "### ED status"
        )

        ed_status = st.radio(
            "Was your ED active today?",
            [
                "No",
                "Yes"
            ],
            horizontal=True
        )

        purging = False

        if ed_status == "Yes":

            purging_answer = st.radio(
                "Did purging happen today?",
                [
                    "No",
                    "Yes"
                ],
                horizontal=True
            )

            if purging_answer == "Yes":

                purging = True


        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        st.markdown("---")

        if st.button(
            "Save today's check-in 🤍",
            type="primary"
        ):

            mood_rating = severity_to_mood(
                mood_type,
                mood_severity
            )

            save_entry(
                entry_date,
                {
                    "mood_type":
                        mood_type,

                    "mood_rating":
                        mood_rating,

                    "mood_severity":
                        mood_severity,

                    "sleep_score":
                        sleep_score,

                    "ed_status":
                        ed_status,

                    "purging":
                        purging
                }
            )

            st.success(
                "Saved 🤍"
            )


    # ========================================================
    # CALENDAR
    # ========================================================

    elif tab == "📅 Calendar":

        render_ed_calendar()


    # ========================================================
    # REELS
    # ========================================================

    elif tab == "🎬 Reels":

        render_reels()


# ============================================================
# MY VIEW
# ============================================================

else:

    tab = st.radio(
        "Navigation",
        [
            "📝 Entry",
            "📈 Mood",
            "🧩 Factors",
            "📅 Calendar",
            "💊 Lithium"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )


    # ========================================================
    # PRIVATE ENTRY
    # ========================================================

    if tab == "📝 Entry":

        st.subheader(
            "Detailed entry"
        )

        entry_date = st.date_input(
            "Date",
            value=date.today(),
            key="private_date"
        )


        # ----------------------------------------------------
        # MOOD
        # ----------------------------------------------------

        mood = st.slider(
            "Mood",
            min_value=-4,
            max_value=4,
            value=0
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
            4: "Severe hypomania"
        }

        st.caption(
            labels[mood]
        )


        # ----------------------------------------------------
        # SLEEP
        # ----------------------------------------------------

        sleep_score = st.slider(
            "Sleep quality",
            min_value=1,
            max_value=10,
            value=5,
            key="private_sleep"
        )


        # ----------------------------------------------------
        # FACTORS
        # ----------------------------------------------------

        st.markdown("---")

        st.subheader(
            "Factors that may have influenced today"
        )

        selected_factors = st.multiselect(
            "Choose all that apply",
            FACTOR_OPTIONS
        )

        custom_factor = ""

        if "Other" in selected_factors:

            custom_factor = st.text_input(
                "Describe the other factor"
            )

        final_factors = [

            factor

            for factor in selected_factors

            if factor != "Other"
        ]

        if custom_factor.strip():

            final_factors.append(
                custom_factor.strip()
            )

        factors_text = ", ".join(
            final_factors
        )


        # ----------------------------------------------------
        # NOTES
        # ----------------------------------------------------

        notes = st.text_area(
            "Additional notes"
        )


        # ----------------------------------------------------
        # MEDICATION
        # ----------------------------------------------------

        st.markdown("---")

        medications = st.text_input(
            "Medication taken"
        )

        med_adherence = st.selectbox(
            "Medication adherence",
            [
                "As prescribed",
                "Missed a dose",
                "Not applicable"
            ]
        )


        # ----------------------------------------------------
        # ED
        # ----------------------------------------------------

        st.markdown("---")

        ed_status = st.radio(
            "ED active today?",
            [
                "No",
                "Yes"
            ],
            horizontal=True,
            key="private_ed"
        )

        purging = False

        if ed_status == "Yes":

            purging = st.checkbox(
                "Purging occurred today"
            )


        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        if st.button(
            "Save detailed entry",
            type="primary"
        ):

            save_entry(
                entry_date,
                {
                    "mood_rating":
                        mood,

                    "sleep_score":
                        sleep_score,

                    "factors":
                        factors_text,

                    "notes":
                        notes,

                    "medications":
                        medications,

                    "med_adherence":
                        med_adherence,

                    "ed_status":
                        ed_status,

                    "purging":
                        purging
                }
            )

            st.success(
                "Entry saved."
            )


    # ========================================================
    # MOOD
    # ========================================================

    elif tab == "📈 Mood":

        render_mood_chart()


    # ========================================================
    # FACTORS
    # ========================================================

    elif tab == "🧩 Factors":

        render_factor_charts()


    # ========================================================
    # CALENDAR
    # ========================================================

    elif tab == "📅 Calendar":

        render_ed_calendar()


    # ========================================================
    # LITHIUM
    # ========================================================

    elif tab == "💊 Lithium":

        render_lithium_tracker()

        st.markdown("---")

        st.subheader(
            "Log a new lithium test"
        )

        test_date = st.date_input(
            "Test date",
            value=date.today()
        )

        result = st.text_input(
            "Result"
        )

        lithium_notes = st.text_area(
            "Notes"
        )

        if st.button(
            "Save lithium test",
            type="primary"
        ):

            if result.strip():

                save_lithium(
                    test_date,
                    result,
                    lithium_notes
                )

                st.success(
                    "Lithium test saved."
                )

                st.rerun()

            else:

                st.warning(
                    "Please enter the test result."
                )

        tests = load_lithium()

        if not tests.empty:

            st.markdown("---")

            st.subheader(
                "Previous tests"
            )

            st.dataframe(
                tests.sort_values(
                    "date",
                    ascending=False
                ),
                use_container_width=True
            )
