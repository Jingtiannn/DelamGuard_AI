import time
import streamlit as st
import pandas as pd
import plotly.express as px

from logic import (
    classify_three_zone,
    classify_score,
    weighted_stage_score,
    evaluate_demo_stage,
    parameter_weights,
    stage_weights,
    stage_thresholds,
    cumulative_risk_threshold,
)

from ui_helpers import (
    inject_css,
    section_title,
    metric_card,
    highlight_zone,
    status_badge_html,
)
from demo_data import get_demo_lots, get_historical_lot_quality_data

st.set_page_config(page_title="DelamGuard AI", page_icon="⚙️", layout="wide")
inject_css()


# =========================================================
# Demo lots
# =========================================================
demo_lots = get_demo_lots(stage_weights)
historical_lot_quality_data = get_historical_lot_quality_data()
historical_lot_df = pd.DataFrame(historical_lot_quality_data)

# =========================================================
# Helper
# =========================================================

def highlight_risk_class(value):
    if value == "Low":
        return "background-color: #E8FFF1; color: #166534; font-weight: 700;"
    elif value == "Medium":
        return "background-color: #FFF7E6; color: #92400E; font-weight: 700;"
    elif value == "High":
        return "background-color: #FFE8E8; color: #991B1B; font-weight: 700;"
    return ""

def get_stage_parameter_details_from_sim(stage_name, param_values, danger_params):
    target_ranges = {
        "Die Attach": {
            "die_attach_temp": "145–155 °C",
            "bond_force": "18–22 N",
            "epoxy_volume": "95–105",
            "die_attach_void_percent": "<= 5%"
        },
        "Die Attach Cure": {
            "cure_temp": "160–170 °C",
            "cure_time": "50–70 min",
            "cure_ramp_rate": "3–6 °C/min"
        },
        "Moulding": {
            "mold_temp": "170–180 °C",
            "mold_pressure": "75–85 bar",
            "transfer_speed": "0.9–1.1",
            "vacuum_level": "0.4–0.7",
            "mold_void_count": "0–2"
        },
        "Post-Mould Cure": {
            "pmc_temp": "165–175 °C",
            "pmc_time": "80–100 min",
            "cooling_rate": "3–5 °C/min",
            "warpage_mm": "<= 0.10"
        },
        "Solder Reflow": {
            "floor_life_hours": "<= 48 h",
            "moisture_content": "<= 0.30",
            "reflow_peak_temp": "235–250 °C",
            "reflow_ramp_rate": "<= 3.0 °C/s",
            "time_above_liquidus": "60–120 s"
        }
    }
    
    
    
    stage_weight_map = {
        "Die Attach": parameter_weights["die_attach"],
        "Die Attach Cure": parameter_weights["die_attach_cure"],
        "Moulding": parameter_weights["moulding"],
        "Post-Mould Cure": parameter_weights["pmc"],
        "Solder Reflow": parameter_weights["reflow"]
    }

  

    rows = []

    for param, status in danger_params.items():
        normalized_risk = 1.0 if status == "Danger" else 0.5 if status == "Warning" else 0.0
        contribution = normalized_risk * stage_weight_map[stage_name][param]

        current_value = param_values.get(param, "-")

        if isinstance(current_value, (int, float)):
            current_value = f"{current_value:.2f}"

        rows.append([
            param,
            current_value,
            target_ranges[stage_name].get(param, "-"),
            status,
            round(contribution, 2)
        ])

    return pd.DataFrame(
        rows,
        columns=["Parameter", "Current Value", "Target / Range", "Status", "Contribution"]
    )

# =========================================================
# Top Risk Contributors Table Styling
# =========================================================
stage_color_map = {
    "Die Attach": "background-color: #E8F1FF; color: #111827;",
    "Die Attach Cure": "background-color: #F3E8FF; color: #111827;",
    "Moulding": "background-color: #FFF7E6; color: #111827;",
    "Post-Mould Cure": "background-color: #E8FFF1; color: #111827;",
    "Solder Reflow": "background-color: #E0F7FA; color: #111827;",
}

def highlight_stage_row(row):
    return [stage_color_map.get(row["Stage"], "") for _ in row]


# =========================================================
# Session state
# =========================================================
if "sim_running" not in st.session_state:
    st.session_state.sim_running = False
if "sim_index" not in st.session_state:
    st.session_state.sim_index = 0
if "sim_completed" not in st.session_state:
    st.session_state.sim_completed = []
if "sim_cumulative" not in st.session_state:
    st.session_state.sim_cumulative = 0.0
if "sim_lot_name" not in st.session_state:
    st.session_state.sim_lot_name = "Lot A - Safe Lot"
if "has_started" not in st.session_state:
    st.session_state.has_started = False

# =========================================================
# Top controls
# =========================================================
control_left, control_right = st.columns([3, 1])

with control_left:
    demo_lot = st.selectbox(
        "Choose Demo Lot",
        list(demo_lots.keys()),
        key="demo_lot_select",
        label_visibility="collapsed"
    )

with control_right:
    run_simulation = st.button("Run Demo Simulation", use_container_width=True)

if st.session_state.sim_lot_name != demo_lot:
    st.session_state.sim_running = False
    st.session_state.sim_index = 0
    st.session_state.sim_completed = []
    st.session_state.sim_cumulative = 0.0
    st.session_state.sim_lot_name = demo_lot
    st.session_state.has_started = False

if run_simulation:
    st.session_state.sim_running = True
    st.session_state.sim_index = 0
    st.session_state.sim_completed = []
    st.session_state.sim_cumulative = 0.0
    st.session_state.sim_lot_name = demo_lot
    st.session_state.has_started = True

stages = demo_lots[demo_lot]

if not st.session_state.get("has_started", False):
    preview_badge = "PENDING"
elif st.session_state.sim_running:
    preview_badge = "RUNNING"
elif st.session_state.sim_completed:
    preview_badge = st.session_state.sim_completed[0]["badge"]
else:
    preview_badge = "PENDING"


# =========================================================
# Top cards
# =========================================================
top_left, top_right = st.columns([3, 2])

with top_left:
    title_logo_col, title_text_col = st.columns([0.18, 1.82])

    with title_logo_col:
        st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)
        st.image("micron_logo.png", width=90)

    with title_text_col:
        st.markdown("""
        <div class="top-hero">
            <div style="font-size:2rem;font-weight:800;color:#173c8f;">
                DelamGuard AI Monitoring Dashboard
            </div>
            <div style="color:#6b7280;margin-top:4px;">
                Lot-Level Delamination Risk Monitoring for Semiconductor Packaging
            </div>
        </div>
        """, unsafe_allow_html=True)

with top_right:
    st.markdown(f"""
    <div class="top-hero">
        <div style="font-size:0.9rem;color:#6b7280;">Selected Lot</div>
        <div style="font-size:1.15rem;font-weight:700;color:#173c8f;margin-top:6px;">{demo_lot}</div>
        <div style="margin-top:10px;">{status_badge_html(preview_badge)}</div>
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# Show preview before run, or live stage while running
# =========================================================
if st.session_state.sim_running or st.session_state.has_started:
    stage = stages[st.session_state.sim_index]
    completed = st.session_state.sim_completed.copy()
    cumulative_base = st.session_state.sim_cumulative
else:
    stage = None
    completed = []
    cumulative_base = 0.0

if stage is not None:
    stage_name = stage["stage_name"]
    weight = stage["weight"]
    param_values = stage["param_values"]

    danger_params, score, score_class = evaluate_demo_stage(
        stage_name,
        param_values,
        parameter_weights
    )

    cumulative = cumulative_base + (score * weight)
    has_danger = "Danger" in danger_params.values()

    has_danger = "Danger" in danger_params.values()
    stage_threshold = stage_thresholds.get(stage_name, 0.67)
    exceeds_stage_threshold = score >= stage_threshold
    exceeds_cumulative_threshold = cumulative >= cumulative_risk_threshold

    exceeds_cumulative_threshold = cumulative >= cumulative_risk_threshold

    if has_danger:
        danger_list = [p for p, z in danger_params.items() if z == "Danger"]
        status_message = f"STOP: Danger Zone detected. Dangerous parameters: {', '.join(danger_list)}"
        status_type = "error"
        badge = "STOPPED"

    elif exceeds_stage_threshold:
        status_message = f"STOP: Stage risk score {score:.2f} exceeds stage threshold {stage_threshold:.2f}."
        status_type = "error"
        badge = "STOPPED"

    elif exceeds_cumulative_threshold:
        status_message = f"STOP: Running cumulative risk {cumulative:.2f} exceeds cumulative threshold {cumulative_risk_threshold:.2f}."
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
        "threshold": stage_threshold,
        "cumulative_threshold": cumulative_risk_threshold,
        "cumulative": cumulative,
        "param_values": param_values,
        "danger_params": danger_params,
        "status_message": status_message,
        "status_type": status_type,
        "badge": badge
    }

    live_stage_list = [current_stage] + completed
    live_overall_risk = cumulative
    live_overall_class = classify_score(live_overall_risk)

else:
    current_stage = {
        "stage_name": "Not Started",
        "score": 0.0,
        "score_class": "Pending",
        "threshold": 0.0,
        "cumulative_threshold": cumulative_risk_threshold,
        "cumulative": 0.0,
        "param_values": {},
        "danger_params": {},
        "status_message": "Select a lot and click Run Demo Simulation to start.",
        "status_type": "info",
        "badge": "PENDING"
    }

    live_stage_list = []
    live_overall_risk = 0.0
    live_overall_class = "Pending"


live_sensor_rows = []
for rec in live_stage_list:
    for param, zone in rec["danger_params"].items():
        risk = 1.0 if zone == "Danger" else 0.5 if zone == "Warning" else 0.0
        value = rec["param_values"].get(param, "-")

        live_sensor_rows.append([
            rec["stage_name"],
            param,
            value,
            zone,
            risk
        ])

live_sensor_df = pd.DataFrame(
    live_sensor_rows,
    columns=["Stage", "Parameter", "Value", "Zone", "Normalized Risk"]
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
live_contrib_df["Contribution"] = live_contrib_df["Normalized Risk"] * live_contrib_df["Weight"]
live_contrib_df = live_contrib_df.sort_values("Contribution", ascending=False)

top_risk_table_df = live_contrib_df[
    ["Stage", "Parameter", "Value", "Zone", "Contribution"]
].reset_index(drop=True)


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

trend_df = pd.DataFrame(
    trend_records,
    columns=["Stage", "Stage Risk", "Cumulative Risk"]
)

# =========================================================
# Dashboard
# =========================================================
section_title("Executive Overview")
tone_map = {
    "Low": "green",
    "Medium": "yellow",
    "High": "red",
    "Pending": "neutral"
}
active_alerts = len(live_warning_df)

k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(metric_card("Overall Lot Risk", f"{live_overall_risk:.2f}", live_overall_class, tone_map.get(live_overall_class, "neutral")), unsafe_allow_html=True)
with k2:
    cumulative_exceeded = current_stage["cumulative"] >= cumulative_risk_threshold
    cumulative_color = "#dc2626" if cumulative_exceeded else "#198754"
    cumulative_card_class = "metric-card-cumulative-alert" if cumulative_exceeded else "metric-card"

    st.markdown(f"""
    <div class="{cumulative_card_class}">
        <div style="font-size:0.85rem;color:#6b7280;margin-bottom:0.35rem;">
            Running Cumulative Risk
        </div>
        <div style="font-size:1.85rem;font-weight:800;color:{cumulative_color};line-height:1.05;margin-bottom:0.3rem;">
            {current_stage["cumulative"]:.2f}
        </div>
        <div style="font-size:0.9rem;font-weight:600;color:{cumulative_color};">
            Threshold: {cumulative_risk_threshold:.2f}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
with k3:
    st.markdown(metric_card("Current Stage", current_stage["stage_name"], current_stage["score_class"], tone_map.get(current_stage["score_class"], "neutral")), unsafe_allow_html=True)
with k4:
    if current_stage["badge"] == "STOPPED":
        recommended_action = "Review Before Next Stage"
        action_color = "#dc2626"   # red
    elif current_stage["badge"] == "PENDING":
        recommended_action = "Not Started"
        action_color = "#4b5563"   # gray
    else:
        recommended_action = "Continue Process"
        action_color = "#198754"   # green

    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size:0.85rem;color:#6b7280;margin-bottom:0.35rem;">
            Recommended Action
        </div>
        <div style="font-size:1.65rem;font-weight:800;color:{action_color};line-height:1.1;margin-bottom:0.3rem;">
            {recommended_action}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
with k5:
    st.markdown(metric_card("Active Alerts", str(active_alerts), "Requires Attention" if active_alerts > 0 else "No Active Alerts", "red" if active_alerts > 0 else "green"), unsafe_allow_html=True)

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
        threshold_text = f"{stage_thresholds.get(sname, 0.67):.2f}"

        if st.session_state.has_started and sname == current_stage["stage_name"]:
            stage_class_name = "stage-stopped" if current_stage["badge"] == "STOPPED" else "stage-current"
            score_text = f"{current_stage['score']:.2f}"
            class_text = current_stage["score_class"]
            threshold_text = f"{current_stage.get('threshold', stage_thresholds.get(sname, 0.67)):.2f}"

        elif sname in completed_names:
            prev_stage = next(s for s in completed if s["stage_name"] == sname)
            stage_class_name = "stage-complete"
            score_text = f"{prev_stage['score']:.2f}"
            class_text = prev_stage["score_class"]
            threshold_text = f"{prev_stage.get('threshold', stage_thresholds.get(sname, 0.67)):.2f}"

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
            <div style="font-size:0.78rem;color:#6b7280;margin-top:6px;">Threshold: {threshold_text}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 28px;'></div>", unsafe_allow_html=True)

left_col, mid_col, right_col = st.columns([1.0, 1.8, 0.9])

with left_col:
    with st.container(border=True):
        section_title("Running Cumulative Risk Trend")

        if trend_df.empty:
            st.info("Click 'Run Demo Simulation' to view cumulative risk trend.")
        else:
            fig_trend = px.line(
                trend_df,
                x="Stage",
                y="Cumulative Risk",
                markers=True,
                title=""
            )

            fig_trend.update_yaxes(range=[0, 1])

            st.plotly_chart(
                fig_trend,
                use_container_width=True,
                key="running_cumulative_risk_trend"
            )

    with st.container(border=True):
        section_title("Lot Quality Trend")

        fig_lot_trend = px.line(
            historical_lot_df,
            x="Lot ID",
            y="Overall Risk",
            markers=True,
            title=""
        )

        fig_lot_trend.update_yaxes(range=[0, 1])

        fig_lot_trend.add_hline(
            y=0.33,
            line_dash="dash",
            annotation_text="Medium Threshold",
            annotation_position="top left"
        )

        fig_lot_trend.add_hline(
            y=0.66,
            line_dash="dash",
            annotation_text="High Threshold",
            annotation_position="top left"
        )

        st.plotly_chart(
            fig_lot_trend,
            use_container_width=True,
            key="lot_quality_trend_chart"
        )

    with st.container(border=True):
        section_title("Lot Risk Comparison")

        styled_historical_lot_df = (
            historical_lot_df.style
            .map(highlight_risk_class, subset=["Risk Class"])
            .format({"Overall Risk": "{:.2f}"})
        )

        st.dataframe(
            styled_historical_lot_df,
            use_container_width=True,
            hide_index=True
        )


with mid_col:
    with st.container(border=True):
        section_title(f"Key Parameter Monitoring (Current Stage: {current_stage['stage_name']})")

        current_df = get_stage_parameter_details_from_sim(
            current_stage["stage_name"],
            current_stage["param_values"],
            current_stage["danger_params"]
        )

        if current_df is None or current_df.empty:
            st.info("Click 'Run Demo Simulation' to view key parameter monitoring.")
        else:
            st.write(current_df.style.map(highlight_zone, subset=["Status"]))

    with st.container(border=True):
        section_title("Top Risk Contributors")

        if top_risk_table_df.empty:
            st.info("Click 'Run Demo Simulation' to view risk contributors.")
        else:
            display_top_risk_df = top_risk_table_df.rename(columns={
                "Parameter": "Param",
                "Contribution": "Contrib."
            })

            styled_top_risk_df = (
                display_top_risk_df.style
                .apply(highlight_stage_row, axis=1)
                .map(highlight_zone, subset=["Zone"])
                .format({
                    "Value": "{:.2f}",
                    "Contrib.": "{:.2f}"
                })
            )

            st.dataframe(
                styled_top_risk_df,
                use_container_width=True,
                hide_index=True,
                height=380
            )


with right_col:
    with st.container(border=True):
        section_title("Recommended Actions")

        if current_stage["badge"] == "STOPPED":
            st.error("Hold progression to next stage until risk is reduced.")
            st.write("- Review abnormal parameters")
            st.write("- Inspect process profile")
            st.write("- Verify current stage settings")
        elif current_stage["badge"] == "PENDING":
            st.info("Select a lot and click Run Demo Simulation to start.")
            st.write("- Choose demo lot")
            st.write("- Run simulation")
            st.write("- Review stage risk and contributors")
        else:
            st.success("Lot may proceed to next stage.")
            st.write("- Continue monitoring")
            st.write("- Track cumulative trend")
            st.write("- Review warnings if any")

# =========================================================
# Advance simulation
# =========================================================
if st.session_state.sim_running:
    st.session_state.sim_cumulative = cumulative

    if badge == "STOPPED":
        st.session_state.sim_completed.insert(0, current_stage)
        st.session_state.sim_running = False
        time.sleep(0.5)
        st.rerun()

    else:
        if st.session_state.sim_index < len(stages) - 1:
            st.session_state.sim_completed.insert(0, current_stage)
            st.session_state.sim_index += 1
            time.sleep(1)
            st.rerun()

        else:
            st.session_state.sim_completed.insert(0, current_stage)
            st.session_state.sim_running = False
            time.sleep(0.5)
            st.rerun()

else:
    if not st.session_state.has_started:
        st.info("Select a lot and click 'Run Demo Simulation' to start.")
    elif st.session_state.sim_completed:
        final_stage = st.session_state.sim_completed[0]
        if final_stage["badge"] == "STOPPED":
            st.info(f"Simulation stopped. Current cumulative risk = {final_stage['cumulative']:.2f}")
        else:
            st.success(f"Simulation complete. Final cumulative risk = {final_stage['cumulative']:.2f}")