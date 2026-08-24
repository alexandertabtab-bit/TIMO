import streamlit as st
import pandas as pd
import os
import base64
import re
from datetime import date
from collections import Counter
import plotly.graph_objects as go


# ============================================================
# CONFIG
# ============================================================

DATA_FILE = "life_chart_data.csv"
MED_CHANGE_FILE = "med_changes.csv"
LITHIUM_FILE = "lithium_tests.csv"
REELS_FILE = "reels.csv"

LITHIUM_INTERVAL_DAYS = 182

# IMPORTANT:
# Put your mosque image here:
# your-project/
# ├── app.py
# └── assets/
#     └── mosque.jpg
BACKGROUND_IMAGE = "assets/mosque.jpg"


st.set_page_config(
    page_title="Life Chart",
    page_icon="🌙",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# ============================================================
# MOBILE / INSTAGRAM STYLE
# ============================================================

def inject_css():
    st.markdown(
        """
        <style>

        /* ---------------- GENERAL ---------------- */

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
            max-width: 650px;
            padding-top: 1rem;
            padding-bottom: 6rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        /* ---------------- BUTTONS ---------------- */

        .stButton > button {
            width: 100%;
            min-height: 50px;
            border-radius: 16px;
            font-size: 16px;
            font-weight: 600;
        }

        /* ---------------- INPUTS ---------------- */

        textarea {
            border-radius: 16px !important;
        }

        div[data-baseweb="input"] > div {
            border-radius: 14px;
        }

        div[data-baseweb="select"] > div {
            border-radius: 14px;
        }

        /* ---------------- CARDS ---------------- */

        .app-card {
            background: rgba(255, 255, 255, 0.82);
            backdrop-filter: blur(12px);
            padding: 20px;
            border-radius: 24px;
            margin-bottom: 18px;
        }

        .quote-card {
            background: rgba(255, 255, 255, 0.78);
            backdrop-filter: blur(12px);
            padding: 22px;
            border-radius: 24px;
            margin-bottom: 20px;
            text-align: center;
        }

        .quote-title {
            font-size: 13px;
            opacity: 0.65;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .quote-text {
            font-size: 18px;
            line-height: 1.6;
            font-style: italic;
        }

        .reel-card {
            background: rgba(255,255,255,0.85);
            padding: 15px;
            border-radius: 22px;
            margin-bottom: 15px;
        }

        /* ---------------- TITLES ---------------- */

        h1 {
            text-align: center;
            font-size: 30px !important;
        }

        /* ---------------- MOBILE ---------------- */

        @media (max-width: 768px) {

            .block-container {
                padding-left: 12px;
                padding-right: 12px;
                padding-top: 0.7rem;
            }

            h1 {
                font-size: 27px !important;
            }

            h2 {
                font-size: 22px !important;
            }

            .stButton > button {
                min-height: 52px;
                border-radius: 17px;
            }

        }

        </style>
        """,
        unsafe_allow_html=True,
    )


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
                    rgba(250,248,245,0.55),
                    rgba(250,248,245,0.65)
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


inject_css()
inject_background()


# ============================================================
# DATA STRUCTURE
# ============================================================

COLUMNS = [
    "date",
    "mood_rating",
    "sleep_hours",
    "sleep_quality",

    # Keeping these in the database so old CSV files still work
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
    "Bad": 4.0,
    "Normal": 6.5,
    "Good": 8.0,
}


# ============================================================
# DAILY QUOTES
# ============================================================

DAILY_QUOTES = [
    "Indeed, with hardship comes ease. — Quran 94:6",
    "Allah does not burden a soul beyond what it can bear. — Quran 2:286",
    "So remember Me; I will remember you. — Quran 2:152",
    "And whoever puts their trust in Allah, then He alone is sufficient for them. — Quran 65:3",
    "Do not lose hope, nor be sad. — Quran 3:139",
    "Perhaps you dislike something which is good for you. — Quran 2:216",
    "And He is with you wherever you are. — Quran 57:4",
    "Verily, in the remembrance of Allah do hearts find rest. — Quran 13:28",
]


def get_daily_quote():
    index = date.today().toordinal() % len(DAILY_QUOTES)
    return DAILY_QUOTES[index]


# ============================================================
# FACTOR DETECTION
# ============================================================

FACTOR_KEYWORDS = {

    "Poor sleep": [
        "bad sleep",
        "slept badly",
        "didn't sleep",
        "did not sleep",
        "insomnia",
        "couldn't sleep",
        "could not sleep",
        "tired",
        "exhausted",
        "no sleep",
    ],

    "Work stress": [
        "work",
        "job",
        "boss",
        "deadline",
        "meeting",
        "office",
        "coworker",
        "colleague",
    ],

    "Family conflict": [
        "family",
        "parents",
        "mother",
        "father",
        "argument with family",
        "fight with family",
    ],

    "Relationship stress": [
        "relationship",
        "partner",
        "girlfriend",
        "boyfriend",
        "argument",
        "fight",
        "breakup",
    ],

    "Travel": [
        "travel",
        "trip",
        "flight",
        "airport",
        "journey",
    ],

    "Exercise": [
        "gym",
        "walk",
        "walking",
        "exercise",
        "workout",
        "running",
    ],

    "Social": [
        "friends",
        "friend",
        "party",
        "social",
        "people",
        "conversation",
    ],

    "Stress": [
        "stress",
        "stressed",
        "stressful",
        "overwhelmed",
        "pressure",
    ],

    "Good day": [
        "happy",
        "good day",
        "great day",
        "relaxed",
        "peaceful",
        "calm",
        "fun",
    ],

    "Illness / physical health": [
        "sick",
        "ill",
        "pain",
        "headache",
        "migraine",
        "doctor",
        "hospital",
    ],

}


def extract_factors(text):

    if not text or not str(text).strip():
        return []

    text_lower = str(text).lower()

    found = []

    for factor, keywords in FACTOR_KEYWORDS.items():

        for keyword in keywords:

            if keyword in text_lower:

                found.append(factor)
                break

    return list(dict.fromkeys(found))


def fragment_text(text):

    if not text or not str(text).strip():
        return []

    fragments = re.split(
        r"[.,;!?]|\band\b|\bbut\b|\bthen\b",
        str(text),
        flags=re.IGNORECASE,
    )

    cleaned = []

    for fragment in fragments:

        fragment = fragment.strip()

        if len(fragment) > 2:
            cleaned.append(fragment)

    return cleaned


# ============================================================
# DATA FUNCTIONS
# ============================================================

def load_data():

    if os.path.exists(DATA_FILE):

        df = pd.read_csv(
            DATA_FILE,
            parse_dates=["date"],
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
            pd.DataFrame([entry]),
        ],
        ignore_index=True,
    )

    df = df.sort_values("date")

    df.to_csv(
        DATA_FILE,
        index=False,
    )

    return df


def upsert_entry(entry_date, partial):

    df = load_data()

    ts = pd.Timestamp(entry_date)

    existing = df[df["date"] == ts]

    if existing.empty:

        row = {
            column: None
            for column in COLUMNS
        }

        row["date"] = ts

    else:

        row = existing.iloc[0].to_dict()

    row.update(partial)

    df = df[df["date"] != ts]

    df = pd.concat(
        [
            df,
            pd.DataFrame([row]),
        ],
        ignore_index=True,
    )

    df = df.sort_values("date")

    df.to_csv(
        DATA_FILE,
        index=False,
    )

    return df


# ============================================================
# MEDICATION CHANGES
# ============================================================

def load_med_changes():

    if os.path.exists(MED_CHANGE_FILE):

        return pd.read_csv(
            MED_CHANGE_FILE,
            parse_dates=["date"],
        )

    return pd.DataFrame(
        columns=MED_CHANGE_COLUMNS
    )


def save_med_change(entry_date, description):

    df = load_med_changes()

    new_row = pd.DataFrame([
        {
            "date": pd.Timestamp(entry_date),
            "change_description": description,
        }
    ])

    df = pd.concat(
        [df, new_row],
        ignore_index=True,
    )

    df = df.sort_values("date")

    df.to_csv(
        MED_CHANGE_FILE,
        index=False,
    )


# ============================================================
# LITHIUM
# ============================================================

def load_lithium_tests():

    if os.path.exists(LITHIUM_FILE):

        return pd.read_csv(
            LITHIUM_FILE,
            parse_dates=["date"],
        )

    return pd.DataFrame(
        columns=[
            "date",
            "result",
            "notes",
        ]
    )


def save_lithium_test(
    test_date,
    result,
    notes,
):

    df = load_lithium_tests()

    new_row = pd.DataFrame([
        {
            "date": pd.Timestamp(test_date),
            "result": result,
            "notes": notes,
        }
    ])

    df = pd.concat(
        [df, new_row],
        ignore_index=True,
    )

    df = df.sort_values("date")

    df.to_csv(
        LITHIUM_FILE,
        index=False,
    )


def lithium_banner():

    tests = load_lithium_tests()

    if tests.empty:
        return

    last = tests.sort_values(
        "date"
    ).iloc[-1]

    next_due = (
        last["date"]
        + pd.Timedelta(
            days=LITHIUM_INTERVAL_DAYS
        )
    )

    days_left = (
        next_due
        - pd.Timestamp.today()
    ).days

    if days_left < 0:

        st.error(
            f"⚠️ Lithium level check overdue. "
            f"Due: {next_due.date()}"
        )

    elif days_left <= 14:

        st.warning(
            f"⚠️ Lithium level check due soon: "
            f"{next_due.date()}"
        )

    else:

        st.info(
            f"Next lithium check: "
            f"{next_due.date()}"
        )


# ============================================================
# REELS
# ============================================================

def load_reels():

    if os.path.exists(REELS_FILE):

        return pd.read_csv(
            REELS_FILE
        )

    return pd.DataFrame(
        columns=REELS_COLUMNS
    )


def save_reel(
    title,
    url,
    category,
    added_by,
):

    df = load_reels()

    new_row = pd.DataFrame([
        {
            "title": title,
            "url": url,
            "category": category,
            "added_by": added_by,
        }
    ])

    df = pd.concat(
        [df, new_row],
        ignore_index=True,
    )

    df.to_csv(
        REELS_FILE,
        index=False,
    )


# ============================================================
# MOOD CONVERSION
# ============================================================

def severity_to_mood(
    mood_type,
    severity,
):

    if mood_type == "Stable":
        return 0

    level = min(
        4,
        max(
            1,
            round(severity / 2.5),
        )
    )

    if mood_type == "Depression":
        return -level

    if mood_type == "Hypomania":
        return level

    return 0


# ============================================================
# MOOD CHART
# ============================================================

def render_mood_chart(
    df,
    med_changes=None,
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
                size=10,
            ),
            line=dict(
                color="lightgray"
            ),
            name="Mood",
        )
    )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray",
    )

    if med_changes is not None:

        if not med_changes.empty:

            for _, change in med_changes.iterrows():

                fig.add_vline(
                    x=change["date"],
                    line_dash="dot",
                )

    fig.update_layout(
        title="My mood over time",
        yaxis=dict(
            range=[-4.5, 4.5],
            title="Mood",
        ),
        xaxis_title="Date",
        height=400,
        margin=dict(
            l=10,
            r=10,
            t=50,
            b=10,
        ),
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# ============================================================
# FACTOR CHARTS
# ============================================================

def get_factor_dataframe(df):

    all_factors = []

    for _, row in df.iterrows():

        factors = str(
            row.get("factors", "")
        )

        if factors == "nan":
            continue

        factor_list = [
            factor.strip()
            for factor in factors.split(",")
            if factor.strip()
        ]

        for factor in factor_list:

            all_factors.append({
                "factor": factor,
                "mood": row["mood_rating"],
                "severity": abs(
                    row["mood_rating"]
                ),
            })

    if not all_factors:

        return pd.DataFrame(
            columns=[
                "factor",
                "mood",
                "severity",
            ]
        )

    return pd.DataFrame(
        all_factors
    )


def render_factor_charts(df):

    factor_df = get_factor_dataframe(df)

    if factor_df.empty:

        st.info(
            "No factors detected yet."
        )

        return

    # ---------------------------
    # MOST COMMON FACTORS
    # ---------------------------

    counts = (
        factor_df["factor"]
        .value_counts()
        .reset_index()
    )

    counts.columns = [
        "Factor",
        "Days",
    ]

    fig1 = go.Figure()

    fig1.add_trace(
        go.Bar(
            x=counts["Factor"],
            y=counts["Days"],
        )
    )

    fig1.update_layout(
        title="Most common influences",
        xaxis_title="Factor",
        yaxis_title="Days mentioned",
        height=350,
        margin=dict(
            l=10,
            r=10,
            t=50,
            b=70,
        ),
    )

    st.plotly_chart(
        fig1,
        use_container_width=True,
    )

    # ---------------------------
    # AVERAGE MOOD SEVERITY
    # ---------------------------

    severity = (
        factor_df
        .groupby("factor")["severity"]
        .mean()
        .sort_values(
            ascending=False
        )
        .reset_index()
    )

    fig2 = go.Figure()

    fig2.add_trace(
        go.Bar(
            x=severity["factor"],
            y=severity["severity"],
        )
    )

    fig2.update_layout(
        title="Average mood intensity when mentioned",
        xaxis_title="Factor",
        yaxis_title="Average intensity",
        height=350,
        margin=dict(
            l=10,
            r=10,
            t=50,
            b=70,
        ),
    )

    st.plotly_chart(
        fig2,
        use_container_width=True,
    )

    st.caption(
        "These charts show patterns in logged data. "
        "They do not prove that a factor caused a mood change."
    )


# ============================================================
# APP HEADER
# ============================================================

st.title("🌙 Life Chart")

st.caption(
    "A personal mood and pattern tracker."
)


# ============================================================
# VIEW SELECTOR
# ============================================================

view = st.radio(
    "View",
    [
        "👤 My check-in",
        "🔐 Private view",
    ],
    horizontal=True,
)


his_view = (
    view == "👤 My check-in"
)


# ============================================================
# HIS VIEW
# ============================================================

if his_view:

    # --------------------------------------------------------
    # DAILY QUOTE
    # --------------------------------------------------------

    st.markdown(
        f"""
        <div class="quote-card">

        <div class="quote-title">
        🌙 Daily reminder
        </div>

        <div class="quote-text">
        {get_daily_quote()}
        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    his_tab = st.radio(
        "Navigation",
        [
            "🏠 Check-in",
            "📈 My patterns",
            "🎬 Reels",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )


    # ========================================================
    # CHECK-IN
    # ========================================================

    if his_tab == "🏠 Check-in":

        st.subheader(
            "How are you today?"
        )

        entry_date = st.date_input(
            "Date",
            value=date.today(),
        )

        # ---------------------------
        # MOOD
        # ---------------------------

        mood_type = st.radio(
            "Mood today",
            [
                "Stable",
                "Depression",
                "Hypomania",
            ],
            horizontal=True,
        )

        severity = 0

        # IMPORTANT:
        # Severity only appears when
        # Depression or Hypomania is selected

        if mood_type == "Depression":

            severity = st.slider(
                "How strong is the depression?",
                min_value=1,
                max_value=10,
                value=5,
                step=1,
            )

            st.caption(
                f"Depression intensity: {severity}/10"
            )

        elif mood_type == "Hypomania":

            severity = st.slider(
                "How strong is the hypomania?",
                min_value=1,
                max_value=10,
                value=5,
                step=1,
            )

            st.caption(
                f"Hypomania intensity: {severity}/10"
            )


        # ---------------------------
        # SLEEP
        # ---------------------------

        sleep_quality = st.select_slider(
            "How was your sleep?",
            options=[
                "Bad",
                "Normal",
                "Good",
            ],
            value="Normal",
        )


        # ---------------------------
        # FACTORS
        # ---------------------------

        st.markdown("---")

        st.subheader(
            "What influenced your day?"
        )

        factors_text = st.text_area(
            "Write anything that affected your mood today",
            placeholder=(
                "For example:\n"
                "Work was stressful, I didn't sleep well, "
                "but I went for a walk and felt better."
            ),
            height=160,
            label_visibility="collapsed",
        )

        # Automatically detect factors
        detected_factors = extract_factors(
            factors_text
        )

        # Fragment the written text
        fragments = fragment_text(
            factors_text
        )

        if detected_factors:

            st.caption(
                "Detected influences: "
                + " • ".join(
                    detected_factors
                )
            )

        # Optional custom factor
        custom_factors = st.text_input(
            "Anything else? (optional)",
            placeholder=(
                "Add your own factor..."
            ),
        )

        final_factors = (
            detected_factors.copy()
        )

        if custom_factors.strip():

            custom_list = [
                x.strip()
                for x in custom_factors.split(",")
                if x.strip()
            ]

            final_factors.extend(
                custom_list
            )

        # Remove duplicates
        final_factors = list(
            dict.fromkeys(
                final_factors
            )
        )


        # ---------------------------
        # SAVE
        # ---------------------------

        if st.button(
            "Save today's check-in 🤍",
            type="primary",
        ):

            mood_rating = severity_to_mood(
                mood_type,
                severity,
            )

            upsert_entry(
                entry_date,
                {

                    "mood_rating": mood_rating,

                    "sleep_hours":
                        SLEEP_QUALITY_HOURS[
                            sleep_quality
                        ],

                    "sleep_quality":
                        sleep_quality,

                    "factors":
                        ", ".join(
                            final_factors
                        ),

                    "life_events":
                        factors_text,

                    "notes":
                        " | ".join(
                            fragments
                        ),
                },
            )

            st.success(
                "Saved 🤍"
            )


    # ========================================================
    # HIS PATTERNS
    # ========================================================

    elif his_tab == "📈 My patterns":

        df = load_data()

        df = df.dropna(
            subset=["mood_rating"]
        )

        if df.empty:

            st.info(
                "No entries yet."
            )

        else:

            render_mood_chart(df)

            st.markdown("---")

            st.subheader(
                "What seems to influence my mood?"
            )

            render_factor_charts(df)


    # ========================================================
    # REELS
    # ========================================================

    elif his_tab == "🎬 Reels":

        st.subheader(
            "For You 🎬"
        )

        reels = load_reels()

        if reels.empty:

            st.info(
                "No reels added yet."
            )

        else:

            categories = (
                ["All"]
                + sorted(
                    reels[
                        "category"
                    ].dropna().unique().tolist()
                )
            )

            category = st.selectbox(
                "Category",
                categories,
            )

            if category == "All":

                filtered = reels.copy()

            else:

                filtered = reels[
                    reels["category"]
                    == category
                ].copy()

            filtered = (
                filtered
                .reset_index(drop=True)
            )

            if "reel_idx" not in st.session_state:

                st.session_state.reel_idx = 0

            if (
                st.session_state.reel_idx
                >= len(filtered)
            ):

                st.session_state.reel_idx = 0

            current = filtered.iloc[
                st.session_state.reel_idx
            ]

            st.markdown(
                f"""
                <div class="reel-card">

                <h3>
                {current["title"]}
                </h3>

                <p>
                {current["category"]}
                </p>

                </div>
                """,
                unsafe_allow_html=True,
            )

            st.video(
                current["url"]
            )

            col1, col2 = st.columns(2)

            if col1.button(
                "← Previous"
            ):

                st.session_state.reel_idx = (
                    st.session_state.reel_idx
                    - 1
                ) % len(filtered)

                st.rerun()

            if col2.button(
                "Next →"
            ):

                st.session_state.reel_idx = (
                    st.session_state.reel_idx
                    + 1
                ) % len(filtered)

                st.rerun()


# ============================================================
# PRIVATE VIEW
# ============================================================

else:

    lithium_banner()

    private_tab = st.radio(
        "Navigation",
        [
            "📝 Entry",
            "📈 Life Chart",
            "🧩 Factors",
            "💊 Medication",
            "📋 Summary",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )


    # ========================================================
    # PRIVATE ENTRY
    # ========================================================

    if private_tab == "📝 Entry":

        st.subheader(
            "Detailed entry"
        )

        entry_date = st.date_input(
            "Date",
            value=date.today(),
            key="private_date",
        )

        mood = st.slider(
            "Mood",
            min_value=-4,
            max_value=4,
            value=0,
        )

        st.caption(
            MOOD_LABELS[mood]
        )

        sleep_hours = st.number_input(
            "Hours of sleep",
            min_value=0.0,
            max_value=24.0,
            value=7.0,
            step=0.5,
        )

        ultradian = st.checkbox(
            "Mood switched multiple times today"
        )

        cycling_notes = ""

        if ultradian:

            cycling_notes = st.text_input(
                "Notes about switching"
            )

        st.markdown("---")

        st.subheader(
            "Medications"
        )

        medications = st.text_input(
            "What was taken today"
        )

        med_adherence = st.selectbox(
            "Adherence",
            [
                "As prescribed",
                "Missed a dose",
                "N/A",
            ],
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
                        change_desc.strip(),
                    )

                    st.success(
                        "Medication change saved."
                    )

        st.markdown("---")

        st.subheader(
            "Eating"
        )

        ate_meals = st.selectbox(
            "Meals today",
            [
                "All meals",
                "Skipped 1 meal",
                "Skipped most/all meals",
            ],
        )

        ed_status = st.selectbox(
            "ED status",
            [
                "Stable",
                "Not stable",
            ],
        )

        purging = False

        if ed_status == "Not stable":

            purging = st.checkbox(
                "Purging occurred"
            )

        st.markdown("---")

        factors_text = st.text_area(
            "Factors / life events"
        )

        detected_factors = extract_factors(
            factors_text
        )

        notes = st.text_area(
            "Notes"
        )

        caregiver_notes = st.text_area(
            "Private context notes"
        )

        if st.button(
            "Save detailed entry",
            type="primary",
        ):

            entry = {

                "date":
                    pd.Timestamp(entry_date),

                "mood_rating":
                    mood,

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
                    ate_meals,

                "ed_status":
                    ed_status,

                "purging":
                    purging,

                "factors":
                    ", ".join(
                        detected_factors
                    ),

                "life_events":
                    factors_text,

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


    # ========================================================
    # LIFE CHART
    # ========================================================

    elif private_tab == "📈 Life Chart":

        df = load_data()

        df = df.dropna(
            subset=["mood_rating"]
        )

        med_changes = load_med_changes()

        render_mood_chart(
            df,
            med_changes,
        )


    # ========================================================
    # FACTORS
    # ========================================================

    elif private_tab == "🧩 Factors":

        df = load_data()

        df = df.dropna(
            subset=["mood_rating"]
        )

        st.subheader(
            "Patterns and influences"
        )

        render_factor_charts(df)


    # ========================================================
    # MEDICATION
    # ========================================================

    elif private_tab == "💊 Medication":

        st.subheader(
            "Lithium monitoring"
        )

        test_date = st.date_input(
            "Test date",
            value=date.today(),
            key="lithium_date",
        )

        result = st.selectbox(
            "Result",
            [
                "Stable / in range",
                "Out of range",
                "Pending",
            ],
        )

        lithium_notes = st.text_area(
            "Notes"
        )

        if st.button(
            "Log lithium test"
        ):

            save_lithium_test(
                test_date,
                result,
                lithium_notes,
            )

            st.success(
                "Lithium test logged."
            )

        st.markdown("---")

        tests = load_lithium_tests()

        if not tests.empty:

            st.dataframe(
                tests,
                use_container_width=True,
            )


    # ========================================================
    # SUMMARY
    # ========================================================

    elif private_tab == "📋 Summary":

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
                "Window",
                min_value=7,
                max_value=90,
                value=30,
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
                len(recent),
            )

            avg_mood = (
                recent["mood_rating"]
                .mean()
            )

            col2.metric(
                "Average mood",
                f"{avg_mood:.1f}"
                if not pd.isna(avg_mood)
                else "—",
            )

            avg_sleep = (
                recent["sleep_hours"]
                .mean()
            )

            col3.metric(
                "Average sleep",
                f"{avg_sleep:.1f} h"
                if not pd.isna(avg_sleep)
                else "—",
            )

            st.markdown("---")

            st.subheader(
                "Recent notes"
            )

            for _, row in recent.iterrows():

                text_parts = []

                if pd.notna(
                    row["life_events"]
                ):

                    if str(
                        row["life_events"]
                    ).strip():

                        text_parts.append(
                            str(
                                row["life_events"]
                            )
                        )

                if pd.notna(
                    row["notes"]
                ):

                    if str(
                        row["notes"]
                    ).strip():

                        text_parts.append(
                            str(
                                row["notes"]
                            )
                        )

                if text_parts:

                    st.write(
                        f"**{row['date'].date()}**"
                    )

                    st.write(
                        " — ".join(
                            text_parts
                        )
                    )

                    st.markdown("---")
