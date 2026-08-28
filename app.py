from __future__ import annotations

import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from src.live_monitor import LiveMonitor


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(

    page_title="CYBERSENTINEL AI",

    page_icon="🛡️",

    layout="wide",

    initial_sidebar_state="expanded"
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {

        background:
        radial-gradient(
            circle at 90% 0%,
            rgba(0,255,180,.08),
            transparent 25%
        ),
        radial-gradient(
            circle at 10% 100%,
            rgba(0,180,255,.05),
            transparent 25%
        ),
        #05080d;

        color: #d7ffe9;

        font-family:
        Consolas,
        "Courier New",
        monospace;
    }


    section[data-testid="stSidebar"] {

        background:
        linear-gradient(
            180deg,
            #020509,
            #07130e
        );

        border-right:
        1px solid
        rgba(0,255,170,.25);
    }


    .title {

        font-size: 3.2rem;

        font-weight: 900;

        letter-spacing: 9px;

        color: #00ff9d;

        text-shadow:
        0 0 6px #00ff9d,
        0 0 18px #00ff9d,
        0 0 35px rgba(0,255,157,.6);
    }


    .subtitle {

        color: #58e0bc;

        letter-spacing: 3px;

        font-size: .85rem;
    }


    .card {

        background:
        linear-gradient(
            145deg,
            #08130f,
            #030807
        );

        border:
        1px solid
        rgba(0,255,157,.22);

        border-radius: 12px;

        padding: 18px;

        min-height: 125px;

        box-shadow:
        0 0 20px
        rgba(0,255,157,.05);
    }


    .label {

        font-size: .70rem;

        color: #65bca6;

        letter-spacing: 2px;
    }


    .value {

        font-size: 2rem;

        font-weight: 900;

        color: #00ff9d;

        margin-top: 8px;

        text-shadow:
        0 0 12px
        rgba(0,255,157,.4);
    }


    .danger-value {

        color: #ff416d;

        text-shadow:
        0 0 12px
        rgba(255,65,109,.45);
    }


    .cyan-value {

        color: #00d9ff;

        text-shadow:
        0 0 12px
        rgba(0,217,255,.35);
    }


    .online {

        color: #00ff9d;

        font-weight: bold;

        letter-spacing: 2px;
    }


    .offline {

        color: #ffaa00;

        font-weight: bold;

        letter-spacing: 2px;
    }


    .threat {

        background:
        rgba(255,20,70,.08);

        border:
        1px solid
        rgba(255,20,70,.6);

        border-radius: 12px;

        padding: 18px;

        color: #ff5279;

        box-shadow:
        0 0 25px
        rgba(255,20,70,.12);
    }


    .safe {

        background:
        rgba(0,255,157,.04);

        border:
        1px solid
        rgba(0,255,157,.25);

        border-radius: 12px;

        padding: 18px;

        color: #00ff9d;
    }


    .terminal {

        background:
        #010302;

        border:
        1px solid
        rgba(0,255,157,.18);

        border-radius: 10px;

        padding: 16px;

        font-size: .82rem;

        line-height: 1.8;

        max-height: 330px;

        overflow-y: auto;
    }


    .normal-log {

        color: #73d9b5;
    }


    .attack-log {

        color: #ff416d;

        font-weight: bold;
    }


    .time-log {

        color: #4e7669;
    }


    .section {

        color: #00ff9d;

        font-size: .78rem;

        letter-spacing: 3px;

        border-bottom:
        1px solid
        rgba(0,255,157,.15);

        padding-bottom: 7px;

        margin-top: 20px;

        margin-bottom: 12px;
    }


    #MainMenu,
    footer {

        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# INITIALIZE MONITOR
# ============================================================

@st.cache_resource
def get_monitor():

    return LiveMonitor(
        timeout_seconds=5
    )


monitor = get_monitor()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div style="
        font-size:1.35rem;
        font-weight:900;
        letter-spacing:3px;
        color:#00ff9d;">
        ⚡ CYBERSENTINEL 
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")

    st.markdown(
        "### CONTROL CENTER"
    )

    start = st.button(
        "▶ START MONITORING",
        use_container_width=True
    )

    stop = st.button(
        "■ STOP MONITORING",
        use_container_width=True
    )

    clear = st.button(
        "⌫ CLEAR EVENTS",
        use_container_width=True
    )

    st.markdown("---")

    st.markdown(
        "### ENGINE"
    )

    st.code(
        "XGBoost\n"
        "Scapy\n"
        "Npcap\n"
        "Flow Engine\n"
        "Streamlit"
    )

    st.markdown("---")

    st.caption(
        "CYBERSENTINEL AI // LOCAL SECURITY MONITOR"
    )


if start:

    monitor.start()


if stop:

    monitor.stop()


if clear:

    monitor.clear()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="title">CYBERSENTINEL AI</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    '// REAL-TIME NETWORK INTRUSION DETECTION'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# STATUS
# ============================================================

st.markdown(
    '<div class="section">SYSTEM STATUS</div>',
    unsafe_allow_html=True
)

stats = monitor.get_stats()


if stats["running"]:

    st.markdown(
        '<div class="online">'
        '● LIVE MONITORING ACTIVE'
        '</div>',
        unsafe_allow_html=True
    )

else:

    st.markdown(
        '<div class="offline">'
        '● MONITORING STANDBY'
        '</div>',
        unsafe_allow_html=True
    )


# ============================================================
# METRICS
# ============================================================

st.markdown(
    '<div class="section">NETWORK TELEMETRY</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)


with c1:

    st.markdown(
        f"""
        <div class="card">

        <div class="label">
        FLOWS ANALYZED
        </div>

        <div class="value">
        {stats["flows"]:,}
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with c2:

    st.markdown(
        f"""
        <div class="card">

        <div class="label">
        THREATS
        </div>

        <div class="value danger-value">
        {stats["attacks"]:,}
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with c3:

    st.markdown(
        f"""
        <div class="card">

        <div class="label">
        BENIGN
        </div>

        <div class="value">
        {stats["benign"]:,}
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


with c4:

    st.markdown(
        f"""
        <div class="card">

        <div class="label">
        THREAT RATE
        </div>

        <div class="value cyan-value">
        {stats["threat_rate"]:.2f}%
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# LIVE EVENTS
# ============================================================

results = monitor.get_results()

st.markdown(
    '<div class="section">LIVE THREAT TERMINAL</div>',
    unsafe_allow_html=True
)


if results:

    recent = results[-20:]

    logs = ""

    for event in reversed(recent):

        if event["prediction"] == "ATTACK":

            css = "attack-log"

            icon = "🚨"

        else:

            css = "normal-log"

            icon = "✓"


        logs += (

            f'<div class="{css}">'

            f'<span class="time-log">'
            f'[{event["timestamp"]}]'
            f'</span> '

            f'{icon} '

            f'{event["prediction"]} '

            f'| '

            f'{event["source"]} '

            f'→ '

            f'{event["destination"]} '

            f'| '

            f'P(ATTACK)='

            f'{event["probability"]:.2%}'

            f'</div>'
        )


    st.markdown(
        f"""
        <div class="terminal">
        {logs}
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    st.markdown(
        """
        <div class="terminal">

        > CYBERSENTINEL AI INITIALIZED

        <br>

        > XGBoost engine ........ READY

        <br>

        > Flow engine ........... READY

        <br>

        > Packet capture ........ STANDBY

        <br>

        > Waiting for network traffic...

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# LATEST THREAT
# ============================================================

attacks = [
    x for x in results
    if x["prediction"] == "ATTACK"
]


if attacks:

    latest = attacks[-1]

    st.markdown(
        '<div class="section">LATEST THREAT</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class="threat">

        <b>🚨 THREAT DETECTED</b>

        <br><br>

        SOURCE:
        {latest["source"]}

        <br>

        DESTINATION:
        {latest["destination"]}

        <br>

        ATTACK PROBABILITY:
        {latest["probability"]:.2%}

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# CHARTS
# ============================================================

st.markdown(
    '<div class="section">THREAT ANALYTICS</div>',
    unsafe_allow_html=True
)


if results:

    result_df = pd.DataFrame(
        results
    )


    left, right = st.columns(2)


    # --------------------------------------------------------
    # Classification chart
    # --------------------------------------------------------

    with left:

        counts = (
            result_df[
                "prediction"
            ]
            .value_counts()
        )


        fig = go.Figure()


        for category in [
            "NOT ATTACK",
            "ATTACK"
        ]:

            fig.add_trace(
                go.Bar(
                    x=[category],
                    y=[
                        counts.get(
                            category,
                            0
                        )
                    ],
                    name=category
                )
            )


        fig.update_layout(

            title="Traffic Classification",

            template="plotly_dark",

            paper_bgcolor="rgba(0,0,0,0)",

            plot_bgcolor="rgba(0,0,0,0)",

            showlegend=False,

            font=dict(
                family="Consolas"
            )
        )


        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # --------------------------------------------------------
    # Probability timeline
    # --------------------------------------------------------

    with right:

        fig2 = go.Figure()


        fig2.add_trace(
            go.Scatter(

                x=list(
                    range(
                        len(result_df)
                    )
                ),

                y=(
                    result_df[
                        "probability"
                    ] * 100
                ),

                mode="lines+markers",

                name="Threat Probability"
            )
        )


        fig2.update_layout(

            title="Threat Probability",

            template="plotly_dark",

            paper_bgcolor="rgba(0,0,0,0)",

            plot_bgcolor="rgba(0,0,0,0)",

            font=dict(
                family="Consolas"
            ),

            yaxis=dict(
                title="Attack Probability (%)"
            )
        )


        st.plotly_chart(
            fig2,
            use_container_width=True
        )


# ============================================================
# RECENT FLOW TABLE
# ============================================================

st.markdown(
    '<div class="section">RECENT NETWORK FLOWS</div>',
    unsafe_allow_html=True
)


if results:

    table = pd.DataFrame(
        results[-30:]
    )[
        [
            "timestamp",
            "source",
            "destination",
            "prediction",
            "probability"
        ]
    ].copy()


    table["probability"] = (
        table["probability"]
        .mul(100)
        .round(2)
        .astype(str)
        + "%"
    )


    table.columns = [
        "TIME",
        "SOURCE",
        "DESTINATION",
        "PREDICTION",
        "CONFIDENCE"
    ]


    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <br><br>

    <div style="
    text-align:center;
    color:#31574c;
    font-size:.7rem;
    letter-spacing:2px;">

    CYBERSENTINEL AI //
    XGBOOST THREAT INTELLIGENCE //
    LOCAL NETWORK MONITOR

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# AUTO REFRESH
# ============================================================

if monitor.running:

    time.sleep(1)

    st.rerun()