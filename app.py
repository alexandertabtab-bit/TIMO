import streamlit as st
import pandas as pd
import os
import base64
from datetime import date
import plotly.graph_objects as go

DATA_FILE = "life_chart_data.csv"
MED_CHANGE_FILE = "med_changes.csv"
LITHIUM_FILE = "lithium_tests.csv"
REELS_FILE = "reels.csv"
LITHIUM_INTERVAL_DAYS = 182  # ~6 months
BACKGROUND_IMAGE = "assets/background.jpg"

st.set_page_config(page_title="Life Chart Tracker", layout="wide", page_icon="🌙")


def inject_background():
    if not os.path.exists(BACKGROUND_IMAGE):
        return
    with open(BACKGROUND_IMAGE, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] {{
            background-image: linear-gradient(rgba(250,248,245,0.93), rgba(250,248,245,0.93)),
                               url("data:image/jpeg;base64,{b64}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        [data-testid="stHeader"] {{
            background-color: rgba(250, 248, 245, 0.6) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_background()

COLUMNS = [
    "date", "mood_rating", "sleep_hours", "sleep_quality", "irritability",
    "ultradian_cycling", "cycling_notes", "medications", "med_adherence",
    "ate_meals", "ed_status", "purging", "factors",
    "life_events", "caffeine", "nicotine", "alcohol", "other_substance",
    "notes", "caregiver_notes",
]

FACTOR_OPTIONS = [
    "Poor sleep", "Work stress", "Family conflict", "Travel",
    "Medication change", "Substance use", "Hormonal", "Other",
]

MED_CHANGE_COLUMNS = ["date", "change_description"]
REELS_COLUMNS = ["title", "url", "category", "added_by"]

MOOD_LABELS = {
    -4: "Severe / incapacitating depression", -3: "Marked depression",
    -2: "Moderate depression", -1: "Mild depression", 0: "Stable / euthymic",
    1: "Mild hypomania", 2: "Moderate hypomania", 3: "Marked mania",
    4: "Severe / incapacitating mania",
}

SLEEP_QUALITY_HOURS = {"Good": 8.0, "Normal": 6.5, "Bad": 4.0}


def load_data() -> pd.DataFrame:
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE, parse_dates=["date"])
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = None
        return df[COLUMNS]
    return pd.DataFrame(columns=COLUMNS)


def save_entry(entry: dict) -> pd.DataFrame:
    """Full overwrite of a date's row — used by the full entry form."""
    df = load_data()
    df = df[df["date"] != entry["date"]]
    df = pd.concat([df, pd.DataFrame([entry])], ignore_index=True)
    df = df.sort_values("date")
    df.to_csv(DATA_FILE, index=False)
    return df


def upsert_entry(entry_date, partial: dict) -> pd.DataFrame:
    """Update only the given fields for a date, preserving whatever else
    is already logged for that day (so a simplified check-in doesn't wipe
    out fields entered elsewhere for the same date)."""
    df = load_data()
    ts = pd.Timestamp(entry_date)
    existing = df[df["date"] == ts]
    if existing.empty:
        row = {c: None for c in COLUMNS}
        row["date"] = ts
    else:
        row = existing.iloc[0].to_dict()
    row.update(partial)
    df = df[df["date"] != ts]
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df = df.sort_values("date")
    df.to_csv(DATA_FILE, index=False)
    return df


def load_lithium_tests() -> pd.DataFrame:
    if os.path.exists(LITHIUM_FILE):
        return pd.read_csv(LITHIUM_FILE, parse_dates=["date"])
    return pd.DataFrame(columns=["date", "result", "notes"])


def save_lithium_test(test_date, result, notes) -> pd.DataFrame:
    df = load_lithium_tests()
    df = pd.concat(
        [df, pd.DataFrame([{"date": pd.Timestamp(test_date), "result": result, "notes": notes}])],
        ignore_index=True,
    )
    df = df.sort_values("date")
    df.to_csv(LITHIUM_FILE, index=False)
    return df


def lithium_banner():
    tests = load_lithium_tests()
    if tests.empty:
        return
    last = tests.sort_values("date").iloc[-1]
    next_due = last["date"] + pd.Timedelta(days=LITHIUM_INTERVAL_DAYS)
    days_left = (next_due - pd.Timestamp.today()).days
    if days_left < 0:
        st.error(f"Lithium level check is overdue — was due {next_due.date()} ({-days_left} days ago).")
    elif days_left <= 14:
        st.warning(f"Lithium level check due soon: {next_due.date()} ({days_left} days).")
    else:
        st.info(f"Next lithium level check due: {next_due.date()} ({days_left} days).")


def load_med_changes() -> pd.DataFrame:
    if os.path.exists(MED_CHANGE_FILE):
        return pd.read_csv(MED_CHANGE_FILE, parse_dates=["date"])
    return pd.DataFrame(columns=MED_CHANGE_COLUMNS)


def save_med_change(entry_date, description) -> pd.DataFrame:
    df = load_med_changes()
    df = pd.concat(
        [df, pd.DataFrame([{"date": pd.Timestamp(entry_date), "change_description": description}])],
        ignore_index=True,
    )
    df = df.sort_values("date")
    df.to_csv(MED_CHANGE_FILE, index=False)
    return df


def load_reels() -> pd.DataFrame:
    if os.path.exists(REELS_FILE):
        return pd.read_csv(REELS_FILE)
    return pd.DataFrame(columns=REELS_COLUMNS)


def save_reel(title, url, category, added_by) -> pd.DataFrame:
    df = load_reels()
    df = pd.concat(
        [df, pd.DataFrame([{"title": title, "url": url, "category": category, "added_by": added_by}])],
        ignore_index=True,
    )
    df.to_csv(REELS_FILE, index=False)
    return df


def mood_sign(m):
    if m > 0:
        return "hypomania/mania"
    if m < 0:
        return "depression"
    return "stable"


def detect_episodes(df: pd.DataFrame):
    """Group consecutive same-direction mood days into episodes.
    Returns (completed_episodes, ongoing_episode). Purely descriptive —
    no forecasting, just grouping what already happened."""
    df = df.sort_values("date").reset_index(drop=True)
    episodes = []
    if df.empty:
        return episodes, None
    current_sign, start, prev_date = None, None, None
    for _, row in df.iterrows():
        s = mood_sign(row["mood_rating"])
        if s != current_sign:
            if current_sign is not None and current_sign != "stable":
                episodes.append({"type": current_sign, "start": start, "end": prev_date,
                                  "days": (prev_date - start).days + 1})
            current_sign, start = s, row["date"]
        prev_date = row["date"]
    ongoing = None
    if current_sign is not None and current_sign != "stable":
        ongoing = {"type": current_sign, "start": start, "end": prev_date,
                   "days": (prev_date - start).days + 1}
    return episodes, ongoing


def render_mood_chart(df, med_changes, show_table):
    df = df.sort_values("date")
    colors = ["#d62728" if m > 0 else ("#1f77b4" if m < 0 else "#2ca02c") for m in df["mood_rating"]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["date"], y=df["mood_rating"], mode="lines+markers",
        marker=dict(color=colors, size=9), line=dict(color="lightgray"), name="Mood",
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    for _, mc in med_changes.iterrows():
        fig.add_vline(x=mc["date"], line_dash="dot", line_color="orange")
    fig.update_layout(
        title="Mood over time (red = mania, blue = depression, orange line = medication change)",
        yaxis=dict(range=[-4.5, 4.5], title="Mood rating"), xaxis_title="Date", height=420,
    )
    st.plotly_chart(fig, use_container_width=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=df["date"], y=df["sleep_hours"], marker_color="#9467bd"))
    fig2.update_layout(title="Sleep over time", yaxis_title="Hours (est. if logged as quality)", height=280)
    st.plotly_chart(fig2, use_container_width=True)

    cycling_days = df[df["ultradian_cycling"] == True]  # noqa: E712
    if not cycling_days.empty:
        st.warning(f"{len(cycling_days)} day(s) with same-day mood switching flagged.")

    if show_table:
        st.subheader("All entries")
        st.dataframe(df, use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV", csv, "life_chart_data.csv", "text/csv")


st.title("Life Chart Tracker")
st.caption(
    "Based on the NIMH Life Chart Method — a logging and pattern tool, not a "
    "diagnostic or forecasting one. Comparisons are to his own logged history, "
    "never a prediction of the future."
)

lithium_banner()

view = st.sidebar.radio("View", ["Your view (full)", "His view (simple)"])
st.sidebar.caption(
    "UI separation, not real security — anyone with access to this device or "
    "the CSV files can see everything either way."
)
full_view = view.startswith("Your")

if full_view:
    with st.sidebar.expander("Lithium level tests"):
        lt_date = st.date_input("Test date", value=date.today(), key="lithium_date")
        lt_result = st.selectbox("Result", ["Stable / in range", "Out of range", "Pending"], key="lithium_result")
        lt_notes = st.text_input("Notes (optional)", key="lithium_notes")
        if st.button("Log lithium test"):
            save_lithium_test(lt_date, lt_result, lt_notes)
            st.success("Logged. Next check calculated at ~6 months from this date.")

if full_view:
    tab_entry, tab_chart, tab_patterns, tab_factors, tab_summary = st.tabs(
        ["Daily Entry", "Life Chart", "Episode Patterns", "Factors", "Doctor Summary"]
    )
else:
    tab_entry, tab_chart, tab_reels = st.tabs(["Check-in", "My Mood Chart", "Reels"])

# ---------------------------------------------------------------- Entry tab
with tab_entry:
    if full_view:
        st.subheader("Today's entry")
        entry_date = st.date_input("Date", value=date.today())

        st.markdown("**Mood rating**")
        mood = st.slider("−4 severe depression → 0 stable → +4 severe mania", -4, 4, 0)
        st.caption(f"Selected: {MOOD_LABELS[mood]}")

        col_a, col_b = st.columns(2)
        with col_a:
            sleep_hours = st.number_input("Hours of sleep last night", min_value=0.0, max_value=24.0, value=7.0, step=0.5)
        with col_b:
            irritability = st.slider("Irritability (0 none → 4 severe)", 0, 4, 0)

        ultradian = st.checkbox("Mood switched more than once today (ultradian cycling)")
        cycling_notes = ""
        if ultradian:
            cycling_notes = st.text_input("Notes on the switching — roughly when, how many times")

        st.markdown("**Medications**")
        med_col1, med_col2 = st.columns([2, 1])
        with med_col1:
            medications = st.text_input("What was taken today")
        with med_col2:
            med_adherence = st.selectbox("Adherence", ["As prescribed", "Missed a dose", "N/A"])

        with st.expander("Log a medication or dose change (only on days it happens)"):
            change_desc = st.text_input("What changed", key="med_change_desc")
            if st.button("Save medication change"):
                if change_desc.strip():
                    save_med_change(entry_date, change_desc.strip())
                    st.success("Medication change logged.")
                else:
                    st.warning("Add a description before saving.")

        st.markdown("**Eating**")
        e_col1, e_col2 = st.columns(2)
        with e_col1:
            ate_meals = st.selectbox("Meals today", ["All meals", "Skipped 1 meal", "Skipped most/all meals"])
        with e_col2:
            ed_status = st.selectbox("ED status today", ["Stable", "Not stable"])
        purging = False
        if ed_status == "Not stable":
            purging = st.checkbox("Purging occurred today")

        factors = st.multiselect(
            "Possible contributing factors today (tagging only, not a conclusion)", FACTOR_OPTIONS,
        )
        life_events = st.text_area("Life events today (anything disruptive, stressful, or notable)")

        st.markdown("**Substances**")
        s_col1, s_col2, s_col3, s_col4 = st.columns(4)
        caffeine = s_col1.checkbox("Caffeine")
        nicotine = s_col2.checkbox("Nicotine")
        alcohol = s_col3.checkbox("Alcohol")
        other_substance = s_col4.text_input("Other")

        notes = st.text_area("Free notes")
        caregiver_notes = st.text_area(
            "Private context notes (only visible in Your view — e.g. "
            "'in Spain this week', 'rough day at work', 'family tension')"
        )

        if st.button("Save entry", type="primary"):
            entry = {
                "date": pd.Timestamp(entry_date), "mood_rating": mood,
                "sleep_hours": sleep_hours, "sleep_quality": None,
                "irritability": irritability, "ultradian_cycling": ultradian,
                "cycling_notes": cycling_notes, "medications": medications,
                "med_adherence": med_adherence, "ate_meals": ate_meals,
                "ed_status": ed_status, "purging": purging,
                "factors": ", ".join(factors), "life_events": life_events,
                "caffeine": caffeine, "nicotine": nicotine, "alcohol": alcohol,
                "other_substance": other_substance, "notes": notes,
                "caregiver_notes": caregiver_notes,
            }
            save_entry(entry)
            st.success(f"Entry saved for {entry_date}")

    else:
        # ---- Simplified check-in for him: three questions, nothing else ----
        st.subheader("Quick check-in")
        entry_date = st.date_input("Date", value=date.today())

        mood_type = st.radio("Mood today", ["Stable", "Depression", "Hypomania"], horizontal=True)
        severity = 0
        if mood_type != "Stable":
            severity = st.slider("How strong? (1 mild → 10 severe)", 1, 10, 5)

        sleep_quality = st.select_slider("Sleep last night", options=["Bad", "Normal", "Good"], value="Normal")

        ed_status = st.radio("Eating today", ["Stable", "Not stable"], horizontal=True)
        purging = False
        if ed_status == "Not stable":
            purging = st.checkbox("Purging occurred today")

        if st.button("Save check-in", type="primary"):
            if mood_type == "Stable":
                mood_rating = 0
            else:
                level = min(4, max(1, round(severity / 2.5)))
                mood_rating = -level if mood_type == "Depression" else level
            upsert_entry(entry_date, {
                "mood_rating": mood_rating,
                "sleep_hours": SLEEP_QUALITY_HOURS[sleep_quality],
                "sleep_quality": sleep_quality,
                "ed_status": ed_status,
                "purging": purging,
            })
            st.success("Saved. That's it — thanks for checking in.")

# ---------------------------------------------------------------- Chart tab
with tab_chart:
    df = load_data()
    med_changes = load_med_changes()
    if df.empty or df["mood_rating"].isna().all():
        st.info("No entries yet.")
    else:
        df_plot = df.dropna(subset=["mood_rating"])
        render_mood_chart(df_plot, med_changes, show_table=full_view)

# ---------------------------------------------------------------- Reels tab
if not full_view:
    with tab_reels:
        st.subheader("Reels")
        reels = load_reels()
        categories = ["All"] + (sorted(reels["category"].unique().tolist()) if not reels.empty else [])
        cat = st.selectbox("Category", categories)
        filtered = reels if cat == "All" or reels.empty else reels[reels["category"] == cat]
        filtered = filtered.reset_index(drop=True)

        if filtered.empty:
            st.info("No reels added yet — add one below.")
        else:
            if "reel_idx" not in st.session_state:
                st.session_state.reel_idx = 0
            if st.session_state.reel_idx >= len(filtered):
                st.session_state.reel_idx = 0
            current = filtered.iloc[st.session_state.reel_idx]
            st.caption(f"{current['category']} · shared by {current['added_by']}")
            st.markdown(f"**{current['title']}**")
            st.video(current["url"])
            c1, c2, c3 = st.columns([1, 1, 1])
            if c1.button("⏮️ Prev"):
                st.session_state.reel_idx = (st.session_state.reel_idx - 1) % len(filtered)
                st.rerun()
            c2.markdown(f"<p style='text-align:center'>{st.session_state.reel_idx + 1}/{len(filtered)}</p>", unsafe_allow_html=True)
            if c3.button("Next ⏭️"):
                st.session_state.reel_idx = (st.session_state.reel_idx + 1) % len(filtered)
                st.rerun()

        with st.expander("➕ Add a reel"):
            r_title = st.text_input("Title")
            r_url = st.text_input("Video URL (YouTube link, etc.)")
            r_cat = st.selectbox("Category", ["Islam", "Science", "Cars", "Other"])
            r_by = st.text_input("Added by", value="")
            if st.button("Add reel"):
                if r_title and r_url:
                    save_reel(r_title, r_url, r_cat, r_by)
                    st.success("Added.")
                    st.rerun()
                else:
                    st.warning("Need a title and URL.")

# ------------------------------------------------------------- Patterns tab
if full_view:
    with tab_patterns:
        df = load_data()
        med_changes = load_med_changes()
        df = df.dropna(subset=["mood_rating"])
        if df.empty:
            st.info("No entries yet.")
        else:
            st.subheader("Episode history (from his own logged data — not a forecast)")
            completed, ongoing = detect_episodes(df)

            if completed:
                ep_df = pd.DataFrame(completed)
                for etype in ep_df["type"].unique():
                    sub = ep_df[ep_df["type"] == etype]
                    st.write(
                        f"**{etype.capitalize()}** — {len(sub)} episode(s), "
                        f"average **{sub['days'].mean():.1f} days**, "
                        f"longest **{sub['days'].max()} days**, shortest **{sub['days'].min()} days**."
                    )
                with st.expander("See all completed episodes"):
                    st.dataframe(ep_df, use_container_width=True)
            else:
                st.info("Not enough completed episodes yet to summarize history.")

            if ongoing:
                hist = [e["days"] for e in completed if e["type"] == ongoing["type"]]
                avg = sum(hist) / len(hist) if hist else None
                st.markdown("---")
                st.subheader("Current stretch")
                if avg:
                    delta = ongoing["days"] - avg
                    st.metric(
                        f"Day {ongoing['days']} of current {ongoing['type']} stretch",
                        f"{ongoing['days']} days",
                        delta=f"{delta:+.1f} vs. his {avg:.1f}-day average",
                        delta_color="inverse",
                    )
                    if ongoing["days"] > max(hist):
                        st.warning(
                            f"This stretch ({ongoing['days']} days) is already longer than "
                            f"any {ongoing['type']} episode on record ({max(hist)} days max). "
                            "Worth mentioning to his prescriber."
                        )
                else:
                    st.metric(f"Day {ongoing['days']} of current {ongoing['type']} stretch", f"{ongoing['days']} days")
                    st.caption("No completed episodes of this type yet to compare against.")
            else:
                st.info("Currently in a stable/euthymic stretch based on the latest entry.")

            if not med_changes.empty:
                st.markdown("---")
                st.subheader("Mood before vs. after logged medication changes")
                mc_sorted = med_changes.sort_values("date").reset_index(drop=True)
                boundaries = [df["date"].min()] + list(mc_sorted["date"]) + [df["date"].max() + pd.Timedelta(days=1)]
                rows = []
                for i in range(len(boundaries) - 1):
                    period = df[(df["date"] >= boundaries[i]) & (df["date"] < boundaries[i + 1])]
                    if not period.empty:
                        label = "Before any logged change" if i == 0 else f"After: {mc_sorted.iloc[i-1]['change_description']}"
                        rows.append({
                            "Period": label, "Days logged": len(period),
                            "Avg mood": round(period["mood_rating"].mean(), 2),
                            "Avg sleep": round(period["sleep_hours"].mean(), 2),
                        })
                st.dataframe(pd.DataFrame(rows), use_container_width=True)
                st.caption("Descriptive only — for discussion with his prescriber, not a conclusion about efficacy.")

# -------------------------------------------------------------- Factors tab
if full_view:
    with tab_factors:
        df = load_data()
        df = df.dropna(subset=["mood_rating"])
        st.subheader("Factor correlations (exploratory — small N, not causal proof)")
        if df.empty:
            st.info("No entries yet.")
        else:
            rows = []
            for factor in FACTOR_OPTIONS:
                tagged = df[df["factors"].fillna("").str.contains(factor)]
                untagged = df[~df["factors"].fillna("").str.contains(factor)]
                if len(tagged) == 0:
                    continue
                rows.append({
                    "Factor": factor,
                    "Days tagged": len(tagged),
                    "Avg severity (tagged)": round(tagged["mood_rating"].abs().mean(), 2),
                    "Avg severity (not tagged)": round(untagged["mood_rating"].abs().mean(), 2) if len(untagged) else None,
                })
            if rows:
                st.dataframe(pd.DataFrame(rows), use_container_width=True)
                st.caption(
                    "Treat any factor with fewer than ~10 tagged days as noise, not a pattern. "
                    "This compares averages — it doesn't prove one causes the other."
                )
            else:
                st.info("No factors tagged yet.")

# -------------------------------------------------------------- Summary tab
if full_view:
    with tab_summary:
        df = load_data()
        df = df.dropna(subset=["mood_rating"])
        if df.empty:
            st.info("No entries yet.")
        else:
            df = df.sort_values("date")
            st.subheader("Summary for a clinical visit")
            window_days = st.slider("Window (days)", 7, 90, 30)
            cutoff = pd.Timestamp.today() - pd.Timedelta(days=window_days)
            recent = df[df["date"] >= cutoff]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Entries", len(recent))
            c2.metric("Avg mood", f"{recent['mood_rating'].mean():.1f}" if len(recent) else "—")
            c3.metric("Avg sleep (hrs)", f"{recent['sleep_hours'].mean():.1f}" if len(recent) else "—")
            c4.metric("Ultradian cycling days", int(recent["ultradian_cycling"].fillna(False).sum()))

            missed = (recent["med_adherence"] == "Missed a dose").sum()
            skipped = (recent["ate_meals"] != "All meals").sum()
            purge_days = int(recent["purging"].fillna(False).sum())

            c5, c6, c7 = st.columns(3)
            c5.metric("Missed medication days", int(missed))
            c6.metric("Days with skipped meal(s)", int(skipped))
            c7.metric("Purging days", purge_days)

            st.markdown("---")
            st.write("**Notable events and notes in this period:**")
            for _, row in recent.iterrows():
                text = " ".join(str(x) for x in [row["life_events"], row["notes"]] if pd.notna(x) and str(x).strip())
                if text:
                    st.write(f"- {row['date'].date()}: {text}")

            st.info("Print this page (Ctrl/Cmd + P) for a clean summary to bring to a doctor, GP, or psychiatrist.")
