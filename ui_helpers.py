# ui_helpers.py
import streamlit as st


def inject_css():
    st.markdown("""
    <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(124, 58, 237, 0.35), transparent 35%),
                radial-gradient(circle at bottom right, rgba(88, 28, 135, 0.35), transparent 30%),
                linear-gradient(135deg, #050008 0%, #120024 70%, #000000 100%);

        .main-title {
            font-size: 2.2rem;
            font-weight: 800;
            color: #173c8f;
            margin-bottom: 0.2rem;
        }

        .main-subtitle {
            font-size: 1rem;
            color: #5c6b82;
            margin-bottom: 1rem;
        }

        .section-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.65rem;
        }

        .metric-card {
            background: white;
            border: 1px solid #dbe4f0;
            border-radius: 18px;
            padding: 16px;
            min-height: 110px;
            box-shadow: 0 6px 18px rgba(31, 51, 89, 0.06);
        }

        .metric-label {
            font-size: 0.85rem;
            color: #6b7280 !important;
            margin-bottom: 0.35rem;
        }

        .metric-value {
            font-size: 1.85rem;
            font-weight: 800;
            color: #173c8f !important;
            line-height: 1.05;
            margin-bottom: 0.3rem;
        }

        .metric-sub {
            font-size: 0.9rem;
            font-weight: 600;
            color: #4b5563 !important;
        }

        .pill-green { color: #198754 !important; }
        .pill-yellow { color: #d97706 !important; }
        .pill-red { color: #dc2626 !important; }
        .pill-blue { color: #2563eb !important; }
        .pill-neutral { color: #4b5563 !important; }

        .panel-card {
            background: white;
            border: 1px solid #dbe4f0;
            border-radius: 18px;
            padding: 16px;
            box-shadow: 0 6px 18px rgba(31, 51, 89, 0.06);
            margin-bottom: 1rem;
        }

        .stage-box {
            background: white;
            border-radius: 16px;
            padding: 14px;
            min-height: 120px;
            border: 1px solid #dbe4f0;
            box-shadow: 0 4px 14px rgba(31, 51, 89, 0.05);
        }

        .stage-box * {
            color: inherit;
        }

        .stage-complete { border: 2px solid #22c55e; }
        .stage-current { border: 2px solid #2563eb; }
        .stage-stopped { border: 2px solid #dc2626; }
        .stage-pending { border: 1px solid #d1d5db; opacity: 0.8; }

        .threshold-strip {
            background: white;
            border: 1px solid #dbe4f0;
            border-radius: 16px;
            padding: 14px 18px;
            box-shadow: 0 6px 18px rgba(31, 51, 89, 0.06);
            margin-top: 0.75rem;
        }

        .top-hero {
            background: white;
            border: 1px solid #dbe4f0;
            border-radius: 20px;
            padding: 18px 22px;
            box-shadow: 0 8px 22px rgba(31, 51, 89, 0.07);
            margin-bottom: 1rem;
        }

        .small-note {
            color: #6b7280;
            font-size: 0.9rem;
        }

        /* Only Streamlit form labels outside cards should be white */
        label {
            color: #ffffff !important;
        }

        /* Selectbox / dropdown text */
        div[data-baseweb="select"] > div {
            color: #ffffff !important;
            background-color: #111827 !important;
            border: 1px solid rgba(255,255,255,0.25) !important;
        }

        div[data-baseweb="select"] span {
            color: #ffffff !important;
        }

        /* Button text */
        .stButton button {
            color: #ffffff !important;
            background-color: #111827 !important;
            border: 1px solid rgba(255,255,255,0.25) !important;
        }

        .stAlert {
            color: inherit !important;
        }

        * {
            scrollbar-width: none !important;
            -ms-overflow-style: none !important;
        }

        *::-webkit-scrollbar {
            display: none !important;
            width: 0px !important;
            height: 0px !important;
        }
    </style>
    """, unsafe_allow_html=True)


def section_title(text):
    st.markdown(
        f'<div class="section-title">{text}</div>',
        unsafe_allow_html=True
    )


def metric_card(label, value, subtext="", tone="green"):
    tone_color = {
        "green": "#198754",
        "yellow": "#d97706",
        "red": "#dc2626",
        "blue": "#2563eb",
        "neutral": "#4b5563",
    }.get(tone, "#4b5563")

    return f"""
    <div class="metric-card">
        <div class="metric-label" style="color:#6b7280 !important;">{label}</div>
        <div class="metric-value" style="color:#173c8f !important;">{value}</div>
        <div class="metric-sub" style="color:{tone_color} !important;">{subtext}</div>
    </div>
    """


def highlight_zone(val):
    if val == "Danger":
        return "background-color: #fee2e2; color: #991b1b; font-weight: bold;"
    elif val == "Warning":
        return "background-color: #fef3c7; color: #92400e; font-weight: bold;"
    elif val == "Normal":
        return "background-color: #dcfce7; color: #166534; font-weight: bold;"
    return ""


def status_badge_html(status):
    if status == "PASSED":
        return '<span style="color:#166534; background-color:#dcfce7; padding:4px 9px; border-radius:999px; font-weight:bold;">PASSED</span>'
    elif status == "STOPPED":
        return '<span style="color:#991b1b; background-color:#fee2e2; padding:4px 9px; border-radius:999px; font-weight:bold;">STOPPED</span>'
    elif status == "PENDING":
        return '<span style="color:#4b5563; background-color:#e5e7eb; padding:4px 9px; border-radius:999px; font-weight:bold;">PENDING</span>'
    return ""