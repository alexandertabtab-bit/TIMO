import streamlit as st
import pandas as pd
import os
import base64
from datetime import date
import plotly.graph_objects as go


# ============================================================
# CONFIG
# ============================================================

DATA_FILE = "life_chart_data.csv"
MED_CHANGE_FILE = "med_changes.csv"
LITHIUM_FILE = "lithium_tests.csv"
REELS_FILE = "reels.csv"

LITHIUM_INTERVAL_DAYS = 182

# Change this if your mosque image has another name
BACKGROUND_IMAGE = "assets/background.jpg"


st.set_page_config(
    page_title="Life Chart Tracker",
    layout="centered",
    page_icon="🌙",
    initial_sidebar_state="collapsed",
)


# ============================================================
# BACKGROUND
# ============================================================

def inject_background():

    if not os.path.exists(BACKGROUND_IMAGE):
        return

    extension = os.path.splitext(BACKGROUND_IMAGE)[1].lower()

    if extension == ".png":
        mime = "image/png"
    elif extension == ".webp":
        mime = "image/webp"
    else:
        mime = "image/jpeg"

    with open(BACKGROUND_IMAGE, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()

    st.markdown(
        f"""
        <style>

        [data-testid="stAppViewContainer"] {{
            background-image:
                linear-gradient(
                    rgba(250, 248, 245, 0.55),
                    rgba(250, 248, 245, 0.65)
                ),
                url("data:{mime};base64,{b64}");

            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# MOBILE / INSTAGRAM STYLE
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
            max-width: 600px;
            padding-top: 1rem;
            padding-bottom: 6rem;
            padding-left: 14px;
            padding-right: 14px;
        }

        .stButton > button {
            width: 100%;
            min-height: 52px;
            border-radius: 18px;
            font-size: 16px;
            font-weight: 600;
        }

        textarea {
            border-radius: 16px !important;
        }

        div[data-baseweb="input"] > div {
            border-radius: 16px;
        }

        .quote-card {
            background: rgba(255,255,255,0.80);
            backdrop-filter: blur(12px);
            border-radius: 24px;
            padding: 22px;
            margin-bottom: 18px;
            text-align: center;
        }

        .arabic-quote {
            font-size: 24px;
            line-height: 1.8;
            direction: rtl;
            margin-bottom: 12px;
        }

        .english-quote {
            font-size: 15px;
            line-height: 1.5;
            font-style: italic;
            opacity: 0.8;
        }

        .calendar-day {
            background: rgba(255,255,255,0.82);
            border-radius: 12px;
            padding: 10px;
            min-height: 72px;
            text-align: center;
            font-size: 13px;
        }

        .purging-day {
            background: rgba(255,220,220,0.9);
        }

        .ed-day {
            background: rgba(255,240,210,0.9);
        }

        .reel-container {
            background: rgba(0,0,0,0.90);
            border-radius: 24px;
            overflow: hidden;
            margin-bottom: 12px;
        }

        @media (max-width: 768px) {

            .block-container {
                padding-left: 10px;
                padding-right: 10px;
            }

            h1 {
                font-size: 27px !important;
            }

            .stButton > button {
                min-height: 56px;
            }

        }

        </style>
        """,
        unsafe_allow_html=True,
    )


inject_css()
inject_background()


# ============================================================
# DATA COLUMNS
# ============================================================

COLUMNS = [
    "date",
    "mood_rating",
    "mood_severity",
    "sleep_hours",
    "sleep_quality",

    "irritability",
    "ultradian_cycling",
    "cycling_notes",

    "medications",
    "med_adherence",

    "ate_meals",
    "ed_status",
    "purging",

    "factors",
    "life_events",

    "caffeine",
    "nicotine",
    "alcohol",
    "other_substance",

    "notes",
    "caregiver_notes",
]


MED_CHANGE_COLUMNS = [
    "date",
    "change_description",
]


REELS_COLUMNS = [
    "title",
    "url",
    "category",
    "added_by",
]


MOOD_LABELS = {
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


SLEEP_QUALITY_HOURS = {
    "Very bad": 3.0,
    "Bad": 4.5,
    "Okay": 6.0,
    "Good": 7.5,
    "Excellent": 9.0,
}


# ============================================================
# DAILY ISLAMIC QUOTES
# ============================================================

DAILY_QUOTES = [

    (
        "إِنَّ مَعَ الْعُسْرِ يُسْرًا",
        "Indeed, with hardship comes ease. — Quran 94:6"
    ),

    (
        "لَا يُكَلِّفُ اللَّهُ نَفْسًا إِلَّا وُسْعَهَا",
        "Allah does not burden a soul beyond what it can bear. — Quran 2:286"
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
        "لَا تَحْزَنْ إِنَّ اللَّهَ مَعَنَا",
        "Do not grieve; indeed Allah is with us. — Quran 9:40"
    ),

    (
        "إِنَّ اللَّهَ مَعَ الصَّابِرِينَ",
        "Indeed, Allah is with those who are patient. — Quran 2:153"
    ),

    (
        "رَبِّ اشْرَحْ لِي صَدْرِي",
        "My Lord, expand for me my chest. — Quran 20:25"
    ),

    (
        "مَنْ صَبَرَ ظَفِرَ",
        "Whoever is patient will succeed."
    ),

]


def get_daily_quote():

    index = date.today().toordinal() % len(DAILY_QUOTES)

    return DAILY_QUOTES[index]


def render_daily_quote():

    arabic, english = get_daily_quote()

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
        unsafe_allow_html=True,
    )


# ============================================================
# DATA FUNCTIONS
# ============================================================

def load_data():

    if os.path.exists(DATA_FILE):

        df = pd.read_csv(
            DATA_FILE,
            parse_dates=["date"]
        )

        for col in COLUMNS:

            if col not in df.columns:
                df[col] = None

        return df[COLUMNS]

    return pd.DataFrame(columns=COLUMNS)


def save_entry(entry):

    df = load_data()

    entry_date = pd.Timestamp(entry["date"])

    df = df[df["date"] != entry_date]

    df = pd.concat(
        [
            df,
            pd.DataFrame([entry])
        ],
        ignore_index=True
    )

    df = df.sort_values("date")

    df.to_csv(
        DATA_FILE,
        index=False
    )

    return df


def upsert_entry(entry_date, partial):

    df = load_data()

    ts = pd.Timestamp(entry_date)

    existing = df[df["date"] == ts]

    if existing.empty:

        row = {
            c: None
            for c in COLUMNS
        }

        row["date"] = ts

    else:

        row = existing.iloc[0].to_dict()

    row.update(partial)

    df = df[df["date"] != ts]

    df = pd.concat(
        [
            df,
            pd.DataFrame([row])
        ],
        ignore_index=True
    )

    df = df.sort_values("date")

    df.to_csv(
        DATA_FILE,
        index=False
    )

    return df


# ============================================================
# LITHIUM TRACKER
# ============================================================

def load_lithium_tests():

    if os.path.exists(LITHIUM_FILE):

        return pd.read_csv(
            LITHIUM_FILE,
            parse_dates=["date"]
        )

    return pd.DataFrame(
        columns=[
            "date",
            "result",
            "notes"
        ]
    )


def save_lithium_test(
    test_date,
    result,
    notes
):

    df = load_lithium_tests()

    new_row = pd.DataFrame([
        {
            "date": pd.Timestamp(test_date),
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

    df = df.sort_values("date")

    df.to_csv(
        LITHIUM_FILE,
        index=False
    )

    return df


def render_lithium_tracker():

    st.subheader("💊 Lithium tracker")

    tests = load_lithium_tests()

    if tests.empty:

        st.info(
            "No lithium test logged yet."
        )

    else:

        last = tests.sort_values(
            "date"
        ).iloc[-1]

        last_date = last["date"]

        next_due = (
            last_date
            + pd.Timedelta(
                days=LITHIUM_INTERVAL_DAYS
            )
        )

        days_left = (
            next_due
            - pd.Timestamp.today()
        ).days

        col1, col2 = st.columns(2)

        col1.metric(
            "Last test",
            str(last_date.date())
        )

        col2.metric(
            "Next test",
            str(next_due.date())
        )

        st.write(
            f"**Last result:** {last['result']}"
        )

        if pd.notna(last["notes"]):

            if str(last["notes"]).strip():

                st.caption(
                    str(last["notes"])
                )

        if days_left < 0:

            st.error(
                f"⚠️ Overdue by {-days_left} days"
            )

        elif days_left <= 14:

            st.warning(
                f"⚠️ Due in {days_left} days"
            )

        else:

            st.success(
                f"Next check in approximately {days_left} days"
            )


# ============================================================
# MEDICATION CHANGES
# ============================================================

def load_med_changes():

    if os.path.exists(MED_CHANGE_FILE):

        return pd.read_csv(
            MED_CHANGE_FILE,
            parse_dates=["date"]
        )

    return pd.DataFrame(
        columns=MED_CHANGE_COLUMNS
    )


def save_med_change(
    entry_date,
    description
):

    df = load_med_changes()

    df = pd.concat(
        [
            df,
            pd.DataFrame([
                {
                    "date": pd.Timestamp(entry_date),
                    "change_description": description
                }
            ])
        ],
        ignore_index=True
    )

    df = df.sort_values("date")

    df.to_csv(
        MED_CHANGE_FILE,
        index=False
    )


# ============================================================
# REELS
# ============================================================

def load_reels():

    if os.path.exists(REELS_FILE):

        return pd.read_csv(REELS_FILE)

    return pd.DataFrame(
        columns=REELS_COLUMNS
    )


def save_reel(
    title,
    url,
    category,
    added_by
):

    df = load_reels()

    df = pd.concat(
        [
            df,
            pd.DataFrame([
                {
                    "title": title,
                    "url": url,
                    "category": category,
                    "added_by": added_by
                }
            ])
        ],
        ignore_index=True
    )

    df.to_csv(
        REELS_FILE,
        index=False
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

    level = min(
        4,
        max(
            1,
            round(severity / 2.5)
        )
    )

    if mood_type == "Depression":

        return -level

    return level


# ============================================================
# MOOD CHART
# ============================================================

def render_mood_chart(
    df,
    med_changes
):

    if df.empty:

        st.info("No entries yet.")

        return

    df = df.sort_values("date")

    colors = []

    for mood in df["mood_rating"]:

        if mood > 0:
            colors.append("#9b59b6")

        elif mood < 0:
            colors.append("#3498db")

        else:
            colors.append("#2ecc71")

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["mood_rating"],
            mode="lines+markers",
            marker=dict(
                color=colors,
                size=10
            ),
            line=dict(
                color="lightgray"
            )
        )
    )

    fig.add_hline(
        y=0,
        line_dash="dash"
    )

    if not med_changes.empty:

        for _, mc in med_changes.iterrows():

            fig.add_vline(
                x=mc["date"],
                line_dash="dot"
            )

    fig.update_layout(
        title="Mood over time",
        yaxis=dict(
            range=[-4.5, 4.5]
        ),
        height=420
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# ED / PURGING CALENDAR
# ============================================================

def render_ed_calendar():

    df = load_data()

    if df.empty:

        st.info(
            "No ED or purging days logged yet."
        )

        return

    df["date"] = pd.to_datetime(
        df["date"]
    )

    df = df.sort_values("date")

    st.subheader("📅 ED & purging calendar")

    st.caption(
        "🟡 ED unstable   🔴 Purging"
    )

    start_date = df["date"].min().date()

    end_date = max(
        date.today(),
        df["date"].max().date()
    )

    all_days = pd.date_range(
        start=start_date,
        end=end_date,
        freq="D"
    )

    rows = []

    for day in all_days:

        row = df[
            df["date"].dt.date
            == day.date()
        ]

        status = ""

        if not row.empty:

            latest = row.iloc[-1]

            ed_status = str(
                latest.get(
                    "ed_status",
                    ""
                )
            )

            purging = latest.get(
                "purging",
                False
            )

            if purging == True:

                status = "🔴 Purging"

            elif ed_status.lower() in [
                "yes",
                "not stable",
                "unstable"
            ]:

                status = "🟡 ED"

        rows.append({
            "Date": day.date(),
            "Status": status
        })

    calendar_df = pd.DataFrame(rows)

    calendar_df["Week"] = (
        pd.to_datetime(
            calendar_df["Date"]
        )
        .dt.isocalendar()
        .week
        .astype(int)
    )

    calendar_df["Day"] = (
        pd.to_datetime(
            calendar_df["Date"]
        )
        .dt.day_name()
    )

    weeks = calendar_df["Week"].unique()

    for week in weeks:

        week_df = calendar_df[
            calendar_df["Week"] == week
        ]

        cols = st.columns(7)

        ordered_days = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday"
        ]

        for i, day_name in enumerate(ordered_days):

            day_row = week_df[
                week_df["Day"] == day_name
            ]

            if not day_row.empty:

                day_data = day_row.iloc[0]

                day_number = pd.Timestamp(
                    day_data["Date"]
                ).day

                status = day_data["Status"]

                cols[i].markdown(
                    f"""
                    <div class="calendar-day">
                        <b>{day_number}</b><br>
                        {status}
                    </div>
                    """,
                    unsafe_allow_html=True
                )


# ============================================================
# FACTOR CHARTS FOR PRIVATE VIEW
# ============================================================

def render_factor_chart():

    df = load_data()

    df = df.dropna(
        subset=["mood_rating"]
    )

    if df.empty:

        st.info("No data yet.")

        return

    factor_rows = []

    for _, row in df.iterrows():

        factors = str(
            row.get(
                "factors",
                ""
            )
        )

        if factors == "nan":
            continue

        for factor in factors.split(","):

            factor = factor.strip()

            if factor:

                factor_rows.append({
                    "Factor": factor,
                    "Severity": abs(
                        row["mood_rating"]
                    )
                })

    if not factor_rows:

        st.info(
            "No factors logged."
        )

        return

    factor_df = pd.DataFrame(
        factor_rows
    )

    counts = (
        factor_df["Factor"]
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
        height=350
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# TITLE
# ============================================================

st.title("🌙 Life Chart")

render_daily_quote()


# ============================================================
# VIEW SELECTOR
# ============================================================

view = st.radio(
    "View",
    [
        "👤 His view",
        "🔐 Your view"
    ],
    horizontal=True
)


full_view = (
    view == "🔐 Your view"
)


# ============================================================
# HIS VIEW
# ============================================================

if not full_view:

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


    # --------------------------------------------------------
    # CHECK-IN
    # --------------------------------------------------------

    if tab == "🏠 Check-in":

        st.subheader(
            "Today's check-in 🌙"
        )

        entry_date = st.date_input(
            "Date",
            value=date.today()
        )


        # MOOD

        mood_type = st.radio(
            "Mood today",
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
                1,
                10,
                5
            )

            st.caption(
                f"{mood_severity}/10"
            )

        elif mood_type == "Hypomania":

            mood_severity = st.slider(
                "Hypomania intensity",
                1,
                10,
                5
            )

            st.caption(
                f"{mood_severity}/10"
            )


        # SLEEP
        # ALWAYS SEPARATE

        st.markdown("---")

        st.subheader(
            "Sleep 😴"
        )

        sleep_spectrum = st.slider(
            "How was your sleep?",
            1,
            10,
            5
        )

        if sleep_spectrum <= 2:
            sleep_quality = "Very bad"

        elif sleep_spectrum <= 4:
            sleep_quality = "Bad"

        elif sleep_spectrum <= 6:
            sleep_quality = "Okay"

        elif sleep_spectrum <= 8:
            sleep_quality = "Good"

        else:
            sleep_quality = "Excellent"

        st.caption(
            f"Sleep: {sleep_spectrum}/10 — {sleep_quality}"
        )


        # ED STATUS

        st.markdown("---")

        st.subheader(
            "ED status"
        )

        ed_problem = st.radio(
            "Was your ED active today?",
            [
                "No",
                "Yes"
            ],
            horizontal=True
        )

        purging = False

        if ed_problem == "Yes":

            purging_answer = st.radio(
                "Did purging happen today?",
                [
                    "No",
                    "Yes"
                ],
                horizontal=True
            )

            purging = (
                purging_answer == "Yes"
            )


        # SAVE

        if st.button(
            "Save check-in 🤍",
            type="primary"
        ):

            mood_rating = severity_to_mood(
                mood_type,
                mood_severity
            )

            sleep_hours = (
                sleep_spectrum / 10
            ) * 10

            upsert_entry(
                entry_date,
                {

                    "mood_rating":
                        mood_rating,

                    "mood_severity":
                        mood_severity,

                    "sleep_hours":
                        sleep_hours,

                    "sleep_quality":
                        sleep_quality,

                    "ed_status":
                        ed_problem,

                    "purging":
                        purging,

                }
            )

            st.success(
                "Saved 🤍"
            )


    # --------------------------------------------------------
    # CALENDAR
    # --------------------------------------------------------

    elif tab == "📅 Calendar":

        render_ed_calendar()


    # --------------------------------------------------------
    # REELS
    # --------------------------------------------------------

    elif tab == "🎬 Reels":

        st.subheader(
            "For You"
        )

        reels = load_reels()

        if reels.empty:

            st.info(
                "No reels available yet."
            )

        else:

            if "reel_idx" not in st.session_state:

                st.session_state.reel_idx = 0

            current_index = (
                st.session_state.reel_idx
                % len(reels)
            )

            current = reels.iloc[
                current_index
            ]

            st.markdown(
                """
                <div class="reel-container">
                """,
                unsafe_allow_html=True
            )

            st.video(
                current["url"]
            )

            st.markdown(
                """
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown(
                f"### {current['title']}"
            )

            st.caption(
                f"{current['category']}"
            )

            st.caption(
                f"{current_index + 1} / {len(reels)}"
            )

            col1, col2 = st.columns(2)

            if col1.button(
                "⬆ Previous"
            ):

                st.session_state.reel_idx -= 1

                st.rerun()

            if col2.button(
                "⬇ Next"
            ):

                st.session_state.reel_idx += 1

                st.rerun()


# ============================================================
# YOUR PRIVATE VIEW
# ============================================================

else:

    tab = st.radio(
        "Navigation",
        [
            "📝 Entry",
            "📈 Chart",
            "🧩 Factors",
            "📅 ED Calendar",
            "💊 Lithium",
            "📋 Summary"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )


    # --------------------------------------------------------
    # ENTRY
    # --------------------------------------------------------

    if tab == "📝 Entry":

        st.subheader(
            "Detailed entry"
        )

        entry_date = st.date_input(
            "Date",
            value=date.today(),
            key="private_date"
        )

        mood = st.slider(
            "Mood",
            -4,
            4,
            0
        )

        st.caption(
            MOOD_LABELS[mood]
        )

        sleep_hours = st.number_input(
            "Hours of sleep",
            0.0,
            24.0,
            7.0,
            0.5
        )

        ultradian = st.checkbox(
            "Mood switched multiple times today"
        )

        cycling_notes = ""

        if ultradian:

            cycling_notes = st.text_input(
                "Notes on mood switching"
            )


        # MEDICATION

        medications = st.text_input(
            "Medication taken"
        )

        med_adherence = st.selectbox(
            "Adherence",
            [
                "As prescribed",
                "Missed a dose",
                "N/A"
            ]
        )

        with st.expander(
            "Log medication change"
        ):

            change_desc = st.text_input(
                "What changed?"
            )

            if st.button(
                "Save medication change"
            ):

                if change_desc.strip():

                    save_med_change(
                        entry_date,
                        change_desc.strip()
                    )

                    st.success(
                        "Saved."
                    )


        # ED

        st.markdown("---")

        ed_status = st.radio(
            "ED active today?",
            [
                "No",
                "Yes"
            ],
            horizontal=True
        )

        purging = False

        if ed_status == "Yes":

            purging = st.checkbox(
                "Purging occurred today"
            )


        # FACTORS

        factors = st.text_area(
            "Factors / life events"
        )

        notes = st.text_area(
            "Notes"
        )

        caregiver_notes = st.text_area(
            "Private context notes"
        )


        if st.button(
            "Save detailed entry",
            type="primary"
        ):

            entry = {

                "date":
                    pd.Timestamp(entry_date),

                "mood_rating":
                    mood,

                "mood_severity":
                    None,

                "sleep_hours":
                    sleep_hours,

                "sleep_quality":
                    None,

                "irritability":
                    None,

                "ultradian_cycling":
                    ultradian,

                "cycling_notes":
                    cycling_notes,

                "medications":
                    medications,

                "med_adherence":
                    med_adherence,

                "ate_meals":
                    None,

                "ed_status":
                    ed_status,

                "purging":
                    purging,

                "factors":
                    factors,

                "life_events":
                    factors,

                "caffeine":
                    None,

                "nicotine":
                    None,

                "alcohol":
                    None,

                "other_substance":
                    None,

                "notes":
                    notes,

                "caregiver_notes":
                    caregiver_notes,

            }

            save_entry(entry)

            st.success(
                "Entry saved."
            )


    # --------------------------------------------------------
    # CHART
    # --------------------------------------------------------

    elif tab == "📈 Chart":

        df = load_data()

        df = df.dropna(
            subset=["mood_rating"]
        )

        med_changes = load_med_changes()

        render_mood_chart(
            df,
            med_changes
        )


    # --------------------------------------------------------
    # FACTORS
    # --------------------------------------------------------

    elif tab == "🧩 Factors":

        render_factor_chart()


    # --------------------------------------------------------
    # ED CALENDAR
    # --------------------------------------------------------

    elif tab == "📅 ED Calendar":

        render_ed_calendar()


    # --------------------------------------------------------
    # LITHIUM
    # --------------------------------------------------------

    elif tab == "💊 Lithium":

        render_lithium_tracker()

        st.markdown("---")

        st.subheader(
            "Log a lithium test"
        )

        test_date = st.date_input(
            "Test date",
            value=date.today(),
            key="lithium_date"
        )

        result = st.selectbox(
            "Result",
            [
                "Stable / in range",
                "Out of range",
                "Pending"
            ]
        )

        notes = st.text_area(
            "Notes",
            key="lithium_notes"
        )

        if st.button(
            "Log lithium test"
        ):

            save_lithium_test(
                test_date,
                result,
                notes
            )

            st.success(
                "Lithium test logged."
            )

            st.rerun()


        tests = load_lithium_tests()

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


    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    elif tab == "📋 Summary":

        df = load_data()

        df = df.dropna(
            subset=["mood_rating"]
        )

        if df.empty:

            st.info(
                "No entries yet."
            )

        else:

            window_days = st.slider(
                "Window (days)",
                7,
                90,
                30
            )

            cutoff = (
                pd.Timestamp.today()
                - pd.Timedelta(
                    days=window_days
                )
            )

            recent = df[
                df["date"] >= cutoff
            ]

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Entries",
                len(recent)
            )

            col2.metric(
                "Average mood",
                f"{recent['mood_rating'].mean():.1f}"
                if len(recent)
                else "—"
            )

            col3.metric(
                "Average sleep",
                f"{recent['sleep_hours'].mean():.1f} h"
                if len(recent)
                else "—"
            )

            st.markdown("---")

            st.subheader(
                "Recent notes"
            )

            for _, row in recent.iterrows():

                texts = []

                for column in [
                    "life_events",
                    "notes"
                ]:

                    value = row.get(
                        column
                    )

                    if pd.notna(value):

                        if str(value).strip():

                            texts.append(
                                str(value)
                            )

                if texts:

                    st.write(
                        f"**{row['date'].date()}**"
                    )

                    st.write(
                        " — ".join(texts)
                    )

                    st.markdown("---")
