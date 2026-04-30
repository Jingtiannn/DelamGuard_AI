import time
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from logic import (
    classify_three_zone,
    classify_score,
    weighted_stage_score,
    parameter_weights,
    stage_weights,
)
from ui_helpers import (
    inject_css,
    section_title,
    metric_card,
    highlight_zone,
    status_badge_html,
)
from demo_data import get_demo_lots

st.set_page_config(page_title="DelamGuard AI", page_icon="⚙️", layout="wide")
inject_css()

# =========================================================
# Header
# =========================================================
st.markdown('<div class="main-title">DelamGuard AI Monitoring Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="main-subtitle">Lot-Level Delamination Risk Monitoring for Semiconductor Packaging</div>',
    unsafe_allow_html=True
)

# =========================================================
# Sidebar
# =========================================================
st.sidebar.title("DelamGuard AI")
st.sidebar.markdown("### Live Lot Simulation")

with st.sidebar.expander("Stage 1: Die Attach", expanded=False):
    die_attach_temp = st.slider("die_attach_temp (°C)", 130.0, 170.0, 150.0, 0.1)
    bond_force = st.slider("bond_force (N)", 10.0, 30.0, 20.0, 0.1)
    epoxy_volume = st.slider("epoxy_volume", 80.0, 120.0, 100.0, 0.1)
    die_attach_void_percent = st.slider("die_attach_void_percent (%)", 0.0, 20.0, 3.0, 0.1)

with st.sidebar.expander("Stage 2: Die Attach Cure", expanded=False):
    cure_temp = st.slider("cure_temp (°C)", 140.0, 190.0, 165.0, 0.1)
    cure_time = st.slider("cure_time (min)", 20.0, 120.0, 60.0, 1.0)
    cure_ramp_rate = st.slider("cure_ramp_rate (°C/min)", 1.0, 10.0, 5.0, 0.1)

with st.sidebar.expander("Stage 3: Moulding", expanded=False):
    mold_temp = st.slider("mold_temp (°C)", 160.0, 190.0, 175.0, 0.1)
    mold_pressure = st.slider("mold_pressure (bar)", 50.0, 100.0, 80.0, 0.1)
    transfer_speed = st.slider("transfer_speed", 0.5, 2.0, 1.0, 0.1)
    vacuum_level = st.slider("vacuum_level", 0.0, 1.0, 0.5, 0.01)
    mold_void_count = st.slider("mold_void_count", 0, 20, 2, 1)

with st.sidebar.expander("Stage 4: Post-Mould Cure", expanded=False):
    pmc_temp = st.slider("pmc_temp (°C)", 140.0, 190.0, 170.0, 0.1)
    pmc_time = st.slider("pmc_time (min)", 30.0, 180.0, 90.0, 1.0)
    cooling_rate = st.slider("cooling_rate (°C/min)", 1.0, 10.0, 4.0, 0.1)
    warpage_mm = st.slider("warpage_mm", 0.0, 0.5, 0.08, 0.01)

with st.sidebar.expander("Stage 5: Solder Reflow", expanded=False):
    floor_life_hours = st.slider("floor_life_hours", 0.0, 200.0, 24.0, 1.0)
    moisture_content = st.slider("moisture_content", 0.0, 1.0, 0.25, 0.01)
    reflow_peak_temp = st.slider("reflow_peak_temp (°C)", 220.0, 270.0, 245.0, 0.1)
    reflow_ramp_rate = st.slider("reflow_ramp_rate (°C/s)", 0.5, 5.0, 2.5, 0.1)
    time_above_liquidus = st.slider("time_above_liquidus (s)", 30.0, 200.0, 90.0, 1.0)

# =========================================================
# Parameter classification
# =========================================================
da_temp_zone, da_temp_risk = classify_three_zone(die_attach_temp, 145, 155, 140, 160, "both")
bond_force_zone, bond_force_risk = classify_three_zone(bond_force, 18, 22, 15, 25, "both")
epoxy_volume_zone, epoxy_volume_risk = classify_three_zone(epoxy_volume, 95, 105, 90, 110, "both")
da_void_zone, da_void_risk = classify_three_zone(die_attach_void_percent, 0, 5, 5, 10, "high")

cure_temp_zone, cure_temp_risk = classify_three_zone(cure_temp, 160, 170, 150, 180, "both")
cure_time_zone, cure_time_risk = classify_three_zone(cure_time, 50, 70, 40, 90, "both")
cure_ramp_zone, cure_ramp_risk = classify_three_zone(cure_ramp_rate, 3, 6, 2, 8, "both")

mold_temp_zone, mold_temp_risk = classify_three_zone(mold_temp, 170, 180, 165, 185, "both")
mold_pressure_zone, mold_pressure_risk = classify_three_zone(mold_pressure, 75, 85, 65, 90, "both")
transfer_speed_zone, transfer_speed_risk = classify_three_zone(transfer_speed, 0.9, 1.1, 0.7, 1.3, "both")
vacuum_zone, vacuum_risk = classify_three_zone(vacuum_level, 0.4, 0.7, 0.2, 0.8, "both")
mold_void_zone, mold_void_risk = classify_three_zone(mold_void_count, 0, 2, 3, 5, "high")

pmc_temp_zone, pmc_temp_risk = classify_three_zone(pmc_temp, 165, 175, 155, 185, "both")
pmc_time_zone, pmc_time_risk = classify_three_zone(pmc_time, 80, 100, 60, 120, "both")
cooling_zone, cooling_risk = classify_three_zone(cooling_rate, 3, 5, 2, 7, "both")
warpage_zone, warpage_risk = classify_three_zone(warpage_mm, 0, 0.10, 0.10, 0.20, "high")

floor_life_zone, floor_life_risk = classify_three_zone(floor_life_hours, 0, 48, 49, 72, "high")
moisture_zone, moisture_risk = classify_three_zone(moisture_content, 0, 0.30, 0.31, 0.50, "high")
peak_temp_zone, peak_temp_risk = classify_three_zone(reflow_peak_temp, 235, 250, 251, 260, "high")
reflow_ramp_zone, reflow_ramp_risk = classify_three_zone(reflow_ramp_rate, 0, 3.0, 3.0, 3.5, "high")
tal_zone, tal_risk = classify_three_zone(time_above_liquidus, 60, 120, 121, 150, "high")

# =========================================================
# Stage scores
# =========================================================
die_attach_score = weighted_stage_score(
    {
        "die_attach_temp": da_temp_risk,
        "bond_force": bond_force_risk,
        "epoxy_volume": epoxy_volume_risk,
        "die_attach_void_percent": da_void_risk
    },
    parameter_weights["die_attach"]
)

die_attach_cure_score = weighted_stage_score(
    {
        "cure_temp": cure_temp_risk,
        "cure_time": cure_time_risk,
        "cure_ramp_rate": cure_ramp_risk
    },
    parameter_weights["die_attach_cure"]
)

moulding_score = weighted_stage_score(
    {
        "mold_temp": mold_temp_risk,
        "mold_pressure": mold_pressure_risk,
        "transfer_speed": transfer_speed_risk,
        "vacuum_level": vacuum_risk,
        "mold_void_count": mold_void_risk
    },
    parameter_weights["moulding"]
)

pmc_score = weighted_stage_score(
    {
        "pmc_temp": pmc_temp_risk,
        "pmc_time": pmc_time_risk,
        "cooling_rate": cooling_risk,
        "warpage_mm": warpage_risk
    },
    parameter_weights["pmc"]
)

reflow_score = weighted_stage_score(
    {
        "floor_life_hours": floor_life_risk,
        "moisture_content": moisture_risk,
        "reflow_peak_temp": peak_temp_risk,
        "reflow_ramp_rate": reflow_ramp_risk,
        "time_above_liquidus": tal_risk
    },
    parameter_weights["reflow"]
)

overall_risk = (
    stage_weights["die_attach"] * die_attach_score +
    stage_weights["die_attach_cure"] * die_attach_cure_score +
    stage_weights["moulding"] * moulding_score +
    stage_weights["pmc"] * pmc_score +
    stage_weights["reflow"] * reflow_score
)

die_attach_class = classify_score(die_attach_score)
die_attach_cure_class = classify_score(die_attach_cure_score)
moulding_class = classify_score(moulding_score)
pmc_class = classify_score(pmc_score)
reflow_class = classify_score(reflow_score)
overall_class = classify_score(overall_risk)

demo_lots = get_demo_lots(stage_weights)

# =========================================================
# Helper for current stage parameter table
# =========================================================
def get_stage_parameter_details(stage_name):
    if stage_name == "Die Attach":
        return pd.DataFrame([
            ["die_attach_temp", die_attach_temp, "145–155 °C", da_temp_zone, parameter_weights["die_attach"]["die_attach_temp"] * da_temp_risk],
            ["bond_force", bond_force, "18–22 N", bond_force_zone, parameter_weights["die_attach"]["bond_force"] * bond_force_risk],
            ["epoxy_volume", epoxy_volume, "95–105", epoxy_volume_zone, parameter_weights["die_attach"]["epoxy_volume"] * epoxy_volume_risk],
            ["die_attach_void_percent", die_attach_void_percent, "<= 5%", da_void_zone, parameter_weights["die_attach"]["die_attach_void_percent"] * da_void_risk],
        ], columns=["Parameter", "Current Value", "Target / Range", "Status", "Contribution"])

    elif stage_name == "Die Attach Cure":
        return pd.DataFrame([
            ["cure_temp", cure_temp, "160–170 °C", cure_temp_zone, parameter_weights["die_attach_cure"]["cure_temp"] * cure_temp_risk],
            ["cure_time", cure_time, "50–70 min", cure_time_zone, parameter_weights["die_attach_cure"]["cure_time"] * cure_time_risk],
            ["cure_ramp_rate", cure_ramp_rate, "3–6 °C/min", cure_ramp_zone, parameter_weights["die_attach_cure"]["cure_ramp_rate"] * cure_ramp_risk],
        ], columns=["Parameter", "Current Value", "Target / Range", "Status", "Contribution"])

    elif stage_name == "Moulding":
        return pd.DataFrame([
            ["mold_temp", mold_temp, "170–180 °C", mold_temp_zone, parameter_weights["moulding"]["mold_temp"] * mold_temp_risk],
            ["mold_pressure", mold_pressure, "75–85 bar", mold_pressure_zone, parameter_weights["moulding"]["mold_pressure"] * mold_pressure_risk],
            ["transfer_speed", transfer_speed, "0.9–1.1", transfer_speed_zone, parameter_weights["moulding"]["transfer_speed"] * transfer_speed_risk],
            ["vacuum_level", vacuum_level, "0.4–0.7", vacuum_zone, parameter_weights["moulding"]["vacuum_level"] * vacuum_risk],
            ["mold_void_count", mold_void_count, "0–2", mold_void_zone, parameter_weights["moulding"]["mold_void_count"] * mold_void_risk],
        ], columns=["Parameter", "Current Value", "Target / Range", "Status", "Contribution"])

    elif stage_name == "Post-Mould Cure":
        return pd.DataFrame([
            ["pmc_temp", pmc_temp, "165–175 °C", pmc_temp_zone, parameter_weights["pmc"]["pmc_temp"] * pmc_temp_risk],
            ["pmc_time", pmc_time, "80–100 min", pmc_time_zone, parameter_weights["pmc"]["pmc_time"] * pmc_time_risk],
            ["cooling_rate", cooling_rate, "3–5 °C/min", cooling_zone, parameter_weights["pmc"]["cooling_rate"] * cooling_risk],
            ["warpage_mm", warpage_mm, "<= 0.10", warpage_zone, parameter_weights["pmc"]["warpage_mm"] * warpage_risk],
        ], columns=["Parameter", "Current Value", "Target / Range", "Status", "Contribution"])

    elif stage_name == "Solder Reflow":
        return pd.DataFrame([
            ["floor_life_hours", floor_life_hours, "<= 48 h", floor_life_zone, parameter_weights["reflow"]["floor_life_hours"] * floor_life_risk],
            ["moisture_content", moisture_content, "<= 0.30", moisture_zone, parameter_weights["reflow"]["moisture_content"] * moisture_risk],
            ["reflow_peak_temp", reflow_peak_temp, "235–250 °C", peak_temp_zone, parameter_weights["reflow"]["reflow_peak_temp"] * peak_temp_risk],
            ["reflow_ramp_rate", reflow_ramp_rate, "<= 3.0 °C/s", reflow_ramp_zone, parameter_weights["reflow"]["reflow_ramp_rate"] * reflow_ramp_risk],
            ["time_above_liquidus", time_above_liquidus, "60–120 s", tal_zone, parameter_weights["reflow"]["time_above_liquidus"] * tal_risk],
        ], columns=["Parameter", "Current Value", "Target / Range", "Status", "Contribution"])

    return pd.DataFrame(columns=["Parameter", "Current Value", "Target / Range", "Status", "Contribution"])

# =========================================================
# Live Lot Simulation only
# =========================================================
section_title("Live Lot Simulation")
st.markdown(
    '<div class="small-note">This page simulates preset lots stage by stage using the same scoring logic in a dashboard-style layout.</div>',
    unsafe_allow_html=True
)

demo_lot = st.selectbox(
    "Choose Demo Lot",
    [
        "Lot A - Safe Lot",
        "Lot B - Caution Lot",
        "Lot C - High Stage Risk",
        "Lot D - Danger Zone Lot"
    ]
)

_, button_col = st.columns([3, 1])
with button_col:
    run_simulation = st.button("Run Demo Simulation", use_container_width=True)

# Session state
if "sim_running" not in st.session_state:
    st.session_state.sim_running = False
if "sim_index" not in st.session_state:
    st.session_state.sim_index = 0
if "sim_completed" not in st.session_state:
    st.session_state.sim_completed = []
if "sim_cumulative" not in st.session_state:
    st.session_state.sim_cumulative = 0.0
if "sim_lot_name" not in st.session_state:
    st.session_state.sim_lot_name = demo_lot

if run_simulation or st.session_state.sim_lot_name != demo_lot:
    st.session_state.sim_running = True
    st.session_state.sim_index = 0
    st.session_state.sim_completed = []
    st.session_state.sim_cumulative = 0.0
    st.session_state.sim_lot_name = demo_lot

stages = demo_lots[demo_lot]
placeholder = st.empty()

if st.session_state.sim_running:
    stage = stages[st.session_state.sim_index]

    stage_name = stage["stage_name"]
    score = stage["score"]
    score_class = stage["score_class"]
    weight = stage["weight"]
    danger_params = stage["danger_params"]

    cumulative = st.session_state.sim_cumulative + (score * weight)
    has_danger = "Danger" in danger_params.values()

    if has_danger:
        danger_list = [p for p, z in danger_params.items() if z == "Danger"]
        status_message = f"STOP: Danger Zone detected. Dangerous parameters: {', '.join(danger_list)}"
        status_type = "error"
        badge = "STOPPED"
    elif score_class == "High":
        status_message = "STOP: Stage risk is HIGH. Process halted for engineering review."
        status_type = "error"
        badge = "STOPPED"
    else:
        status_message = "Stage cleared. Lot can proceed to next stage."
        status_type = "success"
        badge = "PASSED"

    current_stage = {
        "stage_name": stage_name,
        "score": score,
        "score_class": score_class,
        "cumulative": cumulative,
        "danger_params": danger_params,
        "status_message": status_message,
        "status_type": status_type,
        "badge": badge
    }

    completed = st.session_state.sim_completed.copy()
    live_stage_list = [current_stage] + completed
    live_overall_risk = cumulative
    live_overall_class = classify_score(live_overall_risk)

    live_sensor_rows = []
    for rec in live_stage_list:
        for param, zone in rec["danger_params"].items():
            risk = 1.0 if zone == "Danger" else 0.5 if zone == "Warning" else 0.0
            live_sensor_rows.append([rec["stage_name"], param, zone, risk])

    live_sensor_df = pd.DataFrame(
        live_sensor_rows,
        columns=["Stage", "Parameter", "Zone", "Normalized Risk"]
    )

    live_warning_df = live_sensor_df[live_sensor_df["Zone"] != "Normal"]

    live_stage_df = pd.DataFrame({
        "Stage": [rec["stage_name"] for rec in live_stage_list],
        "Score": [rec["score"] for rec in live_stage_list],
        "Class": [rec["score_class"] for rec in live_stage_list]
    })

    weight_lookup = {
        "die_attach_temp": parameter_weights["die_attach"]["die_attach_temp"],
        "bond_force": parameter_weights["die_attach"]["bond_force"],
        "epoxy_volume": parameter_weights["die_attach"]["epoxy_volume"],
        "die_attach_void_percent": parameter_weights["die_attach"]["die_attach_void_percent"],
        "cure_temp": parameter_weights["die_attach_cure"]["cure_temp"],
        "cure_time": parameter_weights["die_attach_cure"]["cure_time"],
        "cure_ramp_rate": parameter_weights["die_attach_cure"]["cure_ramp_rate"],
        "mold_temp": parameter_weights["moulding"]["mold_temp"],
        "mold_pressure": parameter_weights["moulding"]["mold_pressure"],
        "transfer_speed": parameter_weights["moulding"]["transfer_speed"],
        "vacuum_level": parameter_weights["moulding"]["vacuum_level"],
        "mold_void_count": parameter_weights["moulding"]["mold_void_count"],
        "pmc_temp": parameter_weights["pmc"]["pmc_temp"],
        "pmc_time": parameter_weights["pmc"]["pmc_time"],
        "cooling_rate": parameter_weights["pmc"]["cooling_rate"],
        "warpage_mm": parameter_weights["pmc"]["warpage_mm"],
        "floor_life_hours": parameter_weights["reflow"]["floor_life_hours"],
        "moisture_content": parameter_weights["reflow"]["moisture_content"],
        "reflow_peak_temp": parameter_weights["reflow"]["reflow_peak_temp"],
        "reflow_ramp_rate": parameter_weights["reflow"]["reflow_ramp_rate"],
        "time_above_liquidus": parameter_weights["reflow"]["time_above_liquidus"],
    }

    live_contrib_df = live_sensor_df.copy()
    live_contrib_df["Weight"] = live_contrib_df["Parameter"].map(weight_lookup)
    live_contrib_df["Weighted Contribution"] = live_contrib_df["Normalized Risk"] * live_contrib_df["Weight"]
    live_contrib_df = live_contrib_df.sort_values("Weighted Contribution", ascending=False)

    trend_records = []
    running_risk = 0.0
    ordered_stage_list = list(reversed(live_stage_list))

    for rec in ordered_stage_list:
        if rec["stage_name"] == "Die Attach":
            w = stage_weights["die_attach"]
        elif rec["stage_name"] == "Die Attach Cure":
            w = stage_weights["die_attach_cure"]
        elif rec["stage_name"] == "Moulding":
            w = stage_weights["moulding"]
        elif rec["stage_name"] == "Post-Mould Cure":
            w = stage_weights["pmc"]
        elif rec["stage_name"] == "Solder Reflow":
            w = stage_weights["reflow"]
        else:
            w = 0.0

        running_risk += rec["score"] * w
        trend_records.append({
            "Stage": rec["stage_name"],
            "Stage Risk": rec["score"],
            "Cumulative Risk": running_risk
        })

    trend_df = pd.DataFrame(trend_records)

    with placeholder.container():
        # top summary
        left_header, right_header = st.columns([3, 2])

        with left_header:
            st.markdown("""
            <div class="top-hero">
                <div style="font-size:2rem;font-weight:800;color:#173c8f;">DelamGuard AI Monitoring Dashboard</div>
                <div style="color:#6b7280;margin-top:4px;">Lot-Level Delamination Risk Monitoring for Semiconductor Packaging</div>
            </div>
            """, unsafe_allow_html=True)

        with right_header:
            st.markdown(f"""
            <div class="top-hero">
                <div style="font-size:0.9rem;color:#6b7280;">Selected Lot</div>
                <div style="font-size:1.15rem;font-weight:700;color:#173c8f;margin-top:6px;">{demo_lot}</div>
                <div style="margin-top:10px;">{status_badge_html(current_stage['badge'])}</div>
            </div>
            """, unsafe_allow_html=True)

        # KPI row
        section_title("Executive Overview")
        tone_map = {"Low": "green", "Medium": "yellow", "High": "red"}
        active_alerts = len(live_warning_df)

        k1, k2, k3, k4, k5 = st.columns(5)
        with k1:
            st.markdown(metric_card("Overall Lot Risk", f"{live_overall_risk:.2f}", live_overall_class, tone_map.get(live_overall_class, "neutral")), unsafe_allow_html=True)
        with k2:
            st.markdown(metric_card("Running Cumulative Risk", f"{current_stage['cumulative']:.2f}", "Live Update", "yellow" if current_stage["cumulative"] > 0.33 else "green"), unsafe_allow_html=True)
        with k3:
            st.markdown(metric_card("Current Stage", current_stage["stage_name"], current_stage["score_class"], tone_map.get(current_stage["score_class"], "neutral")), unsafe_allow_html=True)
        with k4:
            recommended_action = "Review Before Next Stage" if current_stage["badge"] == "STOPPED" else "Continue Process"
            st.markdown(metric_card("Recommended Action", recommended_action, "", "red" if current_stage["badge"] == "STOPPED" else "green"), unsafe_allow_html=True)
        with k5:
            st.markdown(metric_card("Active Alerts", str(active_alerts), "Requires Attention" if active_alerts > 0 else "No Active Alerts", "red" if active_alerts > 0 else "green"), unsafe_allow_html=True)

        # Stage progress
        section_title("Stage-by-Stage Progress")
        all_stage_names = [
            "Die Attach",
            "Die Attach Cure",
            "Moulding",
            "Post-Mould Cure",
            "Solder Reflow"
        ]
        completed_names = [s["stage_name"] for s in completed]
        stage_cols = st.columns(5)

        for i, sname in enumerate(all_stage_names):
            with stage_cols[i]:
                if sname == current_stage["stage_name"]:
                    stage_class_name = "stage-stopped" if current_stage["badge"] == "STOPPED" else "stage-current"
                    score_text = f"{current_stage['score']:.2f}"
                    class_text = current_stage["score_class"]
                elif sname in completed_names:
                    prev_stage = next(s for s in completed if s["stage_name"] == sname)
                    stage_class_name = "stage-complete"
                    score_text = f"{prev_stage['score']:.2f}"
                    class_text = prev_stage["score_class"]
                else:
                    stage_class_name = "stage-pending"
                    score_text = "—"
                    class_text = "Pending"

                st.markdown(f"""
                <div class="stage-box {stage_class_name}">
                    <div style="font-size:0.85rem;color:#6b7280;">Stage {i+1}</div>
                    <div style="font-size:1rem;font-weight:700;color:#173c8f;margin-top:4px;">{sname}</div>
                    <div style="font-size:1.9rem;font-weight:800;color:#173c8f;margin-top:10px;">{score_text}</div>
                    <div style="font-size:0.9rem;color:#6b7280;margin-top:4px;">{class_text}</div>
                </div>
                """, unsafe_allow_html=True)

        # Main analytics row
        left_col, mid_col, right_col = st.columns([1.2, 1.5, 1.0])

        with left_col:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            section_title("Running Cumulative Risk Trend")
            fig_trend = px.line(
                trend_df,
                x="Stage",
                y="Cumulative Risk",
                markers=True,
                title=""
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with mid_col:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            section_title(f"Key Parameter Monitoring (Current Stage: {current_stage['stage_name']})")
            current_df = get_stage_parameter_details(current_stage["stage_name"]).copy()
            current_df["Contribution"] = current_df["Contribution"].round(2)
            st.write(current_df.style.map(highlight_zone, subset=["Status"]))
            st.markdown('</div>', unsafe_allow_html=True)

        with right_col:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            section_title("Top Risk Contributors")
            st.dataframe(live_contrib_df.head(5), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            section_title("Recommended Actions")
            if current_stage["badge"] == "STOPPED":
                st.error("Hold progression to next stage until risk is reduced.")
                st.write("- Review abnormal parameters")
                st.write("- Inspect process profile")
                st.write("- Verify current stage settings")
            else:
                st.success("Lot may proceed to the next stage.")
                st.write("- Continue monitoring")
                st.write("- Track cumulative trend")
                st.write("- Review warnings if any")
            st.markdown('</div>', unsafe_allow_html=True)

        # Current stage
        section_title("Current Stage")
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown(
            f"### {current_stage['stage_name']} {status_badge_html(current_stage['badge'])}",
            unsafe_allow_html=True
        )
        c1, c2, c3 = st.columns(3)
        c1.metric("Stage Risk", f"{current_stage['score']:.2f}")
        c2.metric("Stage Class", current_stage["score_class"])
        c3.metric("Cumulative Risk", f"{current_stage['cumulative']:.2f}")
        current_param_df = get_stage_parameter_details(current_stage["stage_name"]).copy()
        current_param_df["Contribution"] = current_param_df["Contribution"].round(2)
        st.write(current_param_df.style.map(highlight_zone, subset=["Status"]))
        if current_stage["status_type"] == "error":
            st.error(current_stage["status_message"])
        else:
            st.success(current_stage["status_message"])
        st.markdown('</div>', unsafe_allow_html=True)

        # Previous stages
        for prev in completed:
            st.markdown('<div class="panel-card">', unsafe_allow_html=True)
            st.markdown(
                f"### {prev['stage_name']} {status_badge_html(prev['badge'])}",
                unsafe_allow_html=True
            )
            p1, p2, p3 = st.columns(3)
            p1.metric("Stage Risk", f"{prev['score']:.2f}")
            p2.metric("Stage Class", prev["score_class"])
            p3.metric("Cumulative Risk", f"{prev['cumulative']:.2f}")
            prev_df = pd.DataFrame({
                "Parameter": list(prev["danger_params"].keys()),
                "Zone": list(prev["danger_params"].values())
            })
            st.write(prev_df.style.map(highlight_zone, subset=["Zone"]))
            if prev["status_type"] == "error":
                st.error(prev["status_message"])
            else:
                st.success(prev["status_message"])
            st.markdown('</div>', unsafe_allow_html=True)

        # Lower sections
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        section_title("Live Dashboard")
        live_dashboard_df = pd.DataFrame({
            "Stage": [rec["stage_name"] for rec in live_stage_list],
            "Score": [rec["score"] for rec in live_stage_list],
            "Class": [rec["score_class"] for rec in live_stage_list],
            "Status": [rec["badge"] for rec in live_stage_list]
        })
        st.dataframe(live_dashboard_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        section_title("Live Parameter Status")
        st.write(live_sensor_df.style.map(highlight_zone, subset=["Zone"]))
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        section_title("Warning Parameters")
        if live_warning_df.empty:
            st.success("No warning or danger parameters currently active.")
        else:
            st.write(live_warning_df.style.map(highlight_zone, subset=["Zone"]))
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        section_title("Stage-by-Stage Risk")
        fig_stage = px.bar(
            live_stage_df,
            x="Stage",
            y="Score",
            color="Class",
            text="Score",
            title=""
        )
        st.plotly_chart(fig_stage, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        section_title("Top Current Risk Contributors")
        fig_contrib = px.bar(
            live_contrib_df.head(10),
            x="Parameter",
            y="Weighted Contribution",
            color="Stage",
            title=""
        )
        st.plotly_chart(fig_contrib, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        section_title("Historical Trend")
        fig_trend_2 = px.line(
            trend_df,
            x="Stage",
            y="Cumulative Risk",
            markers=True,
            title=""
        )
        st.plotly_chart(fig_trend_2, use_container_width=True)
        st.dataframe(trend_df, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Threshold strip
        st.markdown("""
        <div class="threshold-strip">
            <div style="display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;">
                <div style="font-weight:700;color:#173c8f;">Risk Category Thresholds</div>
                <div style="display:flex;gap:24px;flex-wrap:wrap;">
                    <div><span style="color:#198754;font-weight:700;">● Low Risk</span> <span style="color:#6b7280;">0.00 – 0.33</span></div>
                    <div><span style="color:#d97706;font-weight:700;">● Medium Risk</span> <span style="color:#6b7280;">0.34 – 0.66</span></div>
                    <div><span style="color:#dc2626;font-weight:700;">● High Risk</span> <span style="color:#6b7280;">0.67 – 1.00</span></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Update simulation state
    st.session_state.sim_cumulative = cumulative

    if badge == "STOPPED":
        st.session_state.sim_completed.insert(0, current_stage)
        st.session_state.sim_running = False
        st.info(f"Simulation stopped early. Current cumulative risk = {cumulative:.2f}")
    else:
        if st.session_state.sim_index < len(stages) - 1:
            st.session_state.sim_completed.insert(0, current_stage)
            st.session_state.sim_index += 1
            time.sleep(1)
            st.rerun()
        else:
            st.session_state.sim_completed.insert(0, current_stage)
            st.session_state.sim_running = False
            st.success(f"Simulation complete. Final cumulative risk = {cumulative:.2f}")
else:
    st.info("Click 'Run Demo Simulation' to start the live lot simulation.")