import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

st.set_page_config(page_title="DelamGuard AI", page_icon="⚙️", layout="wide")


# =========================================================
# Helper functions
# =========================================================
def classify_three_zone(value, normal_min, normal_max, warning_min, warning_max, direction="both"):
    if direction == "both":
        if normal_min <= value <= normal_max:
            return "Normal", 0.0
        elif warning_min <= value <= warning_max:
            return "Warning", 0.5
        else:
            return "Danger", 1.0

    elif direction == "high":
        if value <= normal_max:
            return "Normal", 0.0
        elif value <= warning_max:
            return "Warning", 0.5
        else:
            return "Danger", 1.0

    elif direction == "low":
        if value >= normal_min:
            return "Normal", 0.0
        elif value >= warning_min:
            return "Warning", 0.5
        else:
            return "Danger", 1.0


def classify_score(score):
    if score <= 0.33:
        return "Low"
    elif score <= 0.66:
        return "Medium"
    else:
        return "High"


def weighted_stage_score(risk_dict, weight_dict):
    return sum(risk_dict[k] * weight_dict[k] for k in risk_dict)


# =========================================================
# Weights
# =========================================================
parameter_weights = {
    "die_attach": {
        "die_attach_temp": 0.20,
        "bond_force": 0.20,
        "epoxy_volume": 0.20,
        "die_attach_void_percent": 0.40
    },
    "die_attach_cure": {
        "cure_temp": 0.35,
        "cure_time": 0.35,
        "cure_ramp_rate": 0.30
    },
    "moulding": {
        "mold_temp": 0.20,
        "mold_pressure": 0.20,
        "transfer_speed": 0.15,
        "vacuum_level": 0.15,
        "mold_void_count": 0.30
    },
    "pmc": {
        "pmc_temp": 0.20,
        "pmc_time": 0.20,
        "cooling_rate": 0.20,
        "warpage_mm": 0.40
    },
    "reflow": {
        "floor_life_hours": 0.15,
        "moisture_content": 0.20,
        "reflow_peak_temp": 0.25,
        "reflow_ramp_rate": 0.20,
        "time_above_liquidus": 0.20
    }
}

stage_weights = {
    "die_attach": 0.20,
    "die_attach_cure": 0.15,
    "moulding": 0.25,
    "pmc": 0.15,
    "reflow": 0.25
}


# =========================================================
# Sidebar navigation
# =========================================================
st.sidebar.title("DelamGuard AI")

page = st.sidebar.radio(
    "Navigation",
    [
        "Live Lot Simulation",
        "Overview & Live Dashboard",
        
    ]
)

# =========================================================
# Sidebar inputs
# =========================================================
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


# =========================================================
# Decision logic
# =========================================================
danger_flags = {
    "Die Attach": "Danger" in [da_temp_zone, bond_force_zone, epoxy_volume_zone, da_void_zone],
    "Die Attach Cure": "Danger" in [cure_temp_zone, cure_time_zone, cure_ramp_zone],
    "Moulding": "Danger" in [mold_temp_zone, mold_pressure_zone, transfer_speed_zone, vacuum_zone, mold_void_zone],
    "Post-Mould Cure": "Danger" in [pmc_temp_zone, pmc_time_zone, cooling_zone, warpage_zone],
    "Solder Reflow": "Danger" in [floor_life_zone, moisture_zone, peak_temp_zone, reflow_ramp_zone, tal_zone]
}

high_stage_flags = {
    "Die Attach": die_attach_class == "High",
    "Die Attach Cure": die_attach_cure_class == "High",
    "Moulding": moulding_class == "High",
    "Post-Mould Cure": pmc_class == "High",
    "Solder Reflow": reflow_class == "High"
}

if any(danger_flags.values()):
    final_action = "Immediate Hold / Halt"
    final_reason = "At least one parameter entered the Danger Zone."
elif any(high_stage_flags.values()):
    final_action = "Hold for Engineering Review"
    final_reason = "No danger-zone trigger, but at least one stage risk is High."
else:
    if overall_class == "Low":
        final_action = "Continue"
        final_reason = "Overall lot risk is Low."
    elif overall_class == "Medium":
        final_action = "Continue with Caution / Review"
        final_reason = "Overall lot risk is Medium."
    else:
        final_action = "Hold / Review"
        final_reason = "Overall lot risk is High."


# =========================================================
# Page content
# =========================================================
st.title("⚙️ DelamGuard AI")
st.subheader("Explainable Lot-Level Delamination Risk Dashboard")

if page == "Overview & Live Dashboard":
    st.header("Overview & Live Dashboard")

    st.write(
        "This page combines the overall lot summary, stage-by-stage risk, live parameter status, "
        "and what-if simulation. Adjust the sidebar inputs to see the risk and decision update in real time."
    )

    # -------------------------------------------------
    # Top summary
    # -------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Lot Risk", f"{overall_risk:.2f}")
    c2.metric("Overall Risk Class", overall_class)
    c3.metric("Final Action", final_action)
    c4.metric("Decision Basis", final_reason)

    if final_action == "Immediate Hold / Halt":
        st.error(final_reason)
    elif final_action in ["Hold for Engineering Review", "Hold / Review"]:
        st.warning(final_reason)
    elif final_action == "Continue with Caution / Review":
        st.info(final_reason)
    else:
        st.success(final_reason)

    st.divider()

    # -------------------------------------------------
    # Overall gauge
    # -------------------------------------------------
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=overall_risk * 100,
        title={"text": "Overall Delamination Risk (%)"},
        gauge={
            "axis": {"range": [0, 100]},
            "steps": [
                {"range": [0, 33], "color": "#d4edda"},
                {"range": [33, 66], "color": "#fff3cd"},
                {"range": [66, 100], "color": "#f8d7da"}
            ]
        }
    ))
    st.plotly_chart(fig_gauge, use_container_width=True)

    st.divider()

    # -------------------------------------------------
    # Stage-by-stage risk
    # -------------------------------------------------
    st.subheader("Stage-by-Stage Risk")

    stage_df = pd.DataFrame({
        "Stage": ["Die Attach", "Die Attach Cure", "Moulding", "Post-Mould Cure", "Solder Reflow"],
        "Score": [die_attach_score, die_attach_cure_score, moulding_score, pmc_score, reflow_score],
        "Class": [die_attach_class, die_attach_cure_class, moulding_class, pmc_class, reflow_class]
    })

    fig_stage = px.bar(
        stage_df,
        x="Stage",
        y="Score",
        color="Class",
        text="Score",
        title="Stage-Level Delamination Risk"
    )
    st.plotly_chart(fig_stage, use_container_width=True)

    s1, s2, s3, s4, s5 = st.columns(5)
    s1.metric("Die Attach", f"{die_attach_score:.2f}", die_attach_class)
    s2.metric("DA Cure", f"{die_attach_cure_score:.2f}", die_attach_cure_class)
    s3.metric("Moulding", f"{moulding_score:.2f}", moulding_class)
    s4.metric("PMC", f"{pmc_score:.2f}", pmc_class)
    s5.metric("Reflow", f"{reflow_score:.2f}", reflow_class)

    st.divider()

    # -------------------------------------------------
    # Live parameter status
    # -------------------------------------------------
    st.subheader("Live Parameter Status")

    sensor_df = pd.DataFrame([
        ["Die Attach", "die_attach_temp", die_attach_temp, da_temp_zone, da_temp_risk],
        ["Die Attach", "bond_force", bond_force, bond_force_zone, bond_force_risk],
        ["Die Attach", "epoxy_volume", epoxy_volume, epoxy_volume_zone, epoxy_volume_risk],
        ["Die Attach", "die_attach_void_percent", die_attach_void_percent, da_void_zone, da_void_risk],

        ["Die Attach Cure", "cure_temp", cure_temp, cure_temp_zone, cure_temp_risk],
        ["Die Attach Cure", "cure_time", cure_time, cure_time_zone, cure_time_risk],
        ["Die Attach Cure", "cure_ramp_rate", cure_ramp_rate, cure_ramp_zone, cure_ramp_risk],

        ["Moulding", "mold_temp", mold_temp, mold_temp_zone, mold_temp_risk],
        ["Moulding", "mold_pressure", mold_pressure, mold_pressure_zone, mold_pressure_risk],
        ["Moulding", "transfer_speed", transfer_speed, transfer_speed_zone, transfer_speed_risk],
        ["Moulding", "vacuum_level", vacuum_level, vacuum_zone, vacuum_risk],
        ["Moulding", "mold_void_count", mold_void_count, mold_void_zone, mold_void_risk],

        ["Post-Mould Cure", "pmc_temp", pmc_temp, pmc_temp_zone, pmc_temp_risk],
        ["Post-Mould Cure", "pmc_time", pmc_time, pmc_time_zone, pmc_time_risk],
        ["Post-Mould Cure", "cooling_rate", cooling_rate, cooling_zone, cooling_risk],
        ["Post-Mould Cure", "warpage_mm", warpage_mm, warpage_zone, warpage_risk],

        ["Solder Reflow", "floor_life_hours", floor_life_hours, floor_life_zone, floor_life_risk],
        ["Solder Reflow", "moisture_content", moisture_content, moisture_zone, moisture_risk],
        ["Solder Reflow", "reflow_peak_temp", reflow_peak_temp, peak_temp_zone, peak_temp_risk],
        ["Solder Reflow", "reflow_ramp_rate", reflow_ramp_rate, reflow_ramp_zone, reflow_ramp_risk],
        ["Solder Reflow", "time_above_liquidus", time_above_liquidus, tal_zone, tal_risk],
    ], columns=["Stage", "Parameter", "Value", "Zone", "Normalized Risk"])

    def highlight_zone(val):
        if val == "Danger":
            return "background-color: #f8d7da; color: #721c24; font-weight: bold;"
        elif val == "Warning":
            return "background-color: #fff3cd; color: #856404; font-weight: bold;"
        elif val == "Normal":
            return "background-color: #d4edda; color: #155724; font-weight: bold;"
        return ""

    styled_sensor_df = sensor_df.style.map(highlight_zone, subset=["Zone"])

    st.write(styled_sensor_df)

    st.divider()

    # -------------------------------------------------
    # Abnormal parameters only
    # -------------------------------------------------
    st.subheader("Warning / Danger Parameters")

    abnormal_df = sensor_df[sensor_df["Zone"] != "Normal"]

    if abnormal_df.empty:
        st.success("All parameters are currently in the Normal Zone.")
    else:
        styled_abnormal_df = abnormal_df.style.map(highlight_zone, subset=["Zone"])
        st.write(styled_abnormal_df)

    st.divider()

    # -------------------------------------------------
    # Top weighted contributors
    # -------------------------------------------------
    st.subheader("Top Current Risk Contributors")

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

    contribution_df = sensor_df.copy()
    contribution_df["Weight"] = contribution_df["Parameter"].map(weight_lookup)
    contribution_df["Weighted Contribution"] = contribution_df["Normalized Risk"] * contribution_df["Weight"]
    contribution_df = contribution_df.sort_values(by="Weighted Contribution", ascending=False)

    fig_contrib = px.bar(
        contribution_df.head(10),
        x="Parameter",
        y="Weighted Contribution",
        color="Stage",
        title="Top Weighted Contributors Under Current Settings"
    )
    st.plotly_chart(fig_contrib, use_container_width=True)

    st.info(
        "This page also acts as the what-if simulator. Change any sidebar value and the zones, "
        "stage scores, overall risk, and decision will update immediately."
    )

    st.divider()

    # -------------------------------------------------
    # Historical Trend
    # -------------------------------------------------
    st.subheader("Historical Trend")

    trend_df = pd.DataFrame({
        "Stage": ["Die Attach", "Die Attach Cure", "Moulding", "Post-Mould Cure", "Solder Reflow"],
        "Stage Risk": [
            die_attach_score,
            die_attach_cure_score,
            moulding_score,
            pmc_score,
            reflow_score
        ],
        "Cumulative Weighted Risk": [
            stage_weights["die_attach"] * die_attach_score,
            stage_weights["die_attach"] * die_attach_score + stage_weights["die_attach_cure"] * die_attach_cure_score,
            stage_weights["die_attach"] * die_attach_score + stage_weights["die_attach_cure"] * die_attach_cure_score + stage_weights["moulding"] * moulding_score,
            stage_weights["die_attach"] * die_attach_score + stage_weights["die_attach_cure"] * die_attach_cure_score + stage_weights["moulding"] * moulding_score + stage_weights["pmc"] * pmc_score,
            overall_risk
        ]
    })

    fig_trend = px.line(
        trend_df,
        x="Stage",
        y="Cumulative Weighted Risk",
        markers=True,
        title="Cumulative Delamination Risk Across 5 Stages"
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    st.dataframe(trend_df, use_container_width=True)


elif page == "Live Lot Simulation":
    st.header("Live Lot Simulation")
    st.write("This page simulates preset lots stage by stage.")

    demo_lot = st.selectbox(
        "Choose Demo Lot",
        [
            "Lot A - Safe Lot",
            "Lot B - Caution Lot",
            "Lot C - High Stage Risk",
            "Lot D - Danger Zone Lot"
        ]
    )

    demo_lots = {
        "Lot A - Safe Lot": [
            {
                "stage_name": "Die Attach",
                "score": 0.10,
                "score_class": "Low",
                "weight": stage_weights["die_attach"],
                "danger_params": {
                    "die_attach_temp": "Normal",
                    "bond_force": "Normal",
                    "epoxy_volume": "Normal",
                    "die_attach_void_percent": "Normal"
                }
            },
            {
                "stage_name": "Die Attach Cure",
                "score": 0.15,
                "score_class": "Low",
                "weight": stage_weights["die_attach_cure"],
                "danger_params": {
                    "cure_temp": "Normal",
                    "cure_time": "Normal",
                    "cure_ramp_rate": "Normal"
                }
            },
            {
                "stage_name": "Moulding",
                "score": 0.20,
                "score_class": "Low",
                "weight": stage_weights["moulding"],
                "danger_params": {
                    "mold_temp": "Normal",
                    "mold_pressure": "Normal",
                    "transfer_speed": "Normal",
                    "vacuum_level": "Normal",
                    "mold_void_count": "Normal"
                }
            },
            {
                "stage_name": "Post-Mould Cure",
                "score": 0.25,
                "score_class": "Low",
                "weight": stage_weights["pmc"],
                "danger_params": {
                    "pmc_temp": "Normal",
                    "pmc_time": "Normal",
                    "cooling_rate": "Normal",
                    "warpage_mm": "Normal"
                }
            },
            {
                "stage_name": "Solder Reflow",
                "score": 0.20,
                "score_class": "Low",
                "weight": stage_weights["reflow"],
                "danger_params": {
                    "floor_life_hours": "Normal",
                    "moisture_content": "Normal",
                    "reflow_peak_temp": "Normal",
                    "reflow_ramp_rate": "Normal",
                    "time_above_liquidus": "Normal"
                }
            }
        ],

        "Lot B - Caution Lot": [
            {
                "stage_name": "Die Attach",
                "score": 0.30,
                "score_class": "Low",
                "weight": stage_weights["die_attach"],
                "danger_params": {
                    "die_attach_temp": "Warning",
                    "bond_force": "Normal",
                    "epoxy_volume": "Warning",
                    "die_attach_void_percent": "Normal"
                }
            },
            {
                "stage_name": "Die Attach Cure",
                "score": 0.45,
                "score_class": "Medium",
                "weight": stage_weights["die_attach_cure"],
                "danger_params": {
                    "cure_temp": "Warning",
                    "cure_time": "Normal",
                    "cure_ramp_rate": "Warning"
                }
            },
            {
                "stage_name": "Moulding",
                "score": 0.40,
                "score_class": "Medium",
                "weight": stage_weights["moulding"],
                "danger_params": {
                    "mold_temp": "Normal",
                    "mold_pressure": "Warning",
                    "transfer_speed": "Warning",
                    "vacuum_level": "Normal",
                    "mold_void_count": "Normal"
                }
            },
            {
                "stage_name": "Post-Mould Cure",
                "score": 0.35,
                "score_class": "Medium",
                "weight": stage_weights["pmc"],
                "danger_params": {
                    "pmc_temp": "Normal",
                    "pmc_time": "Warning",
                    "cooling_rate": "Normal",
                    "warpage_mm": "Warning"
                }
            },
            {
                "stage_name": "Solder Reflow",
                "score": 0.40,
                "score_class": "Medium",
                "weight": stage_weights["reflow"],
                "danger_params": {
                    "floor_life_hours": "Warning",
                    "moisture_content": "Normal",
                    "reflow_peak_temp": "Warning",
                    "reflow_ramp_rate": "Normal",
                    "time_above_liquidus": "Normal"
                }
            }
        ],

        "Lot C - High Stage Risk": [
            {
                "stage_name": "Die Attach",
                "score": 0.25,
                "score_class": "Low",
                "weight": stage_weights["die_attach"],
                "danger_params": {
                    "die_attach_temp": "Normal",
                    "bond_force": "Warning",
                    "epoxy_volume": "Normal",
                    "die_attach_void_percent": "Warning"
                }
            },
            {
                "stage_name": "Die Attach Cure",
                "score": 0.30,
                "score_class": "Low",
                "weight": stage_weights["die_attach_cure"],
                "danger_params": {
                    "cure_temp": "Normal",
                    "cure_time": "Normal",
                    "cure_ramp_rate": "Warning"
                }
            },
            {
                "stage_name": "Moulding",
                "score": 0.72,
                "score_class": "High",
                "weight": stage_weights["moulding"],
                "danger_params": {
                    "mold_temp": "Warning",
                    "mold_pressure": "Warning",
                    "transfer_speed": "Warning",
                    "vacuum_level": "Normal",
                    "mold_void_count": "Warning"
                }
            },
            {
                "stage_name": "Post-Mould Cure",
                "score": 0.45,
                "score_class": "Medium",
                "weight": stage_weights["pmc"],
                "danger_params": {
                    "pmc_temp": "Normal",
                    "pmc_time": "Warning",
                    "cooling_rate": "Normal",
                    "warpage_mm": "Warning"
                }
            },
            {
                "stage_name": "Solder Reflow",
                "score": 0.50,
                "score_class": "Medium",
                "weight": stage_weights["reflow"],
                "danger_params": {
                    "floor_life_hours": "Warning",
                    "moisture_content": "Warning",
                    "reflow_peak_temp": "Normal",
                    "reflow_ramp_rate": "Warning",
                    "time_above_liquidus": "Normal"
                }
            }
        ],

        "Lot D - Danger Zone Lot": [
            {
                "stage_name": "Die Attach",
                "score": 0.35,
                "score_class": "Medium",
                "weight": stage_weights["die_attach"],
                "danger_params": {
                    "die_attach_temp": "Normal",
                    "bond_force": "Warning",
                    "epoxy_volume": "Normal",
                    "die_attach_void_percent": "Normal"
                }
            },
            {
                "stage_name": "Die Attach Cure",
                "score": 0.40,
                "score_class": "Medium",
                "weight": stage_weights["die_attach_cure"],
                "danger_params": {
                    "cure_temp": "Warning",
                    "cure_time": "Normal",
                    "cure_ramp_rate": "Normal"
                }
            },
            {
                "stage_name": "Moulding",
                "score": 0.50,
                "score_class": "Medium",
                "weight": stage_weights["moulding"],
                "danger_params": {
                    "mold_temp": "Normal",
                    "mold_pressure": "Warning",
                    "transfer_speed": "Normal",
                    "vacuum_level": "Normal",
                    "mold_void_count": "Normal"
                }
            },
            {
                "stage_name": "Post-Mould Cure",
                "score": 0.55,
                "score_class": "Medium",
                "weight": stage_weights["pmc"],
                "danger_params": {
                    "pmc_temp": "Normal",
                    "pmc_time": "Warning",
                    "cooling_rate": "Normal",
                    "warpage_mm": "Warning"
                }
            },
            {
                "stage_name": "Solder Reflow",
                "score": 0.60,
                "score_class": "Medium",
                "weight": stage_weights["reflow"],
                "danger_params": {
                    "floor_life_hours": "Normal",
                    "moisture_content": "Danger",
                    "reflow_peak_temp": "Warning",
                    "reflow_ramp_rate": "Danger",
                    "time_above_liquidus": "Warning"
                }
            }
        ]
    }

    def highlight_zone(val):
        if val == "Danger":
            return "background-color: #f8d7da; color: #721c24; font-weight: bold;"
        elif val == "Warning":
            return "background-color: #fff3cd; color: #856404; font-weight: bold;"
        elif val == "Normal":
            return "background-color: #d4edda; color: #155724; font-weight: bold;"
        return ""

    def status_badge_html(status):
        if status == "PASSED":
            return '<span style="color:#155724; background-color:#d4edda; padding:3px 8px; border-radius:8px; font-weight:bold;">PASSED</span>'
        elif status == "STOPPED":
            return '<span style="color:#721c24; background-color:#f8d7da; padding:3px 8px; border-radius:8px; font-weight:bold;">STOPPED</span>'
        return ""

    placeholder = st.empty()
    run_simulation = st.button("Run Demo Simulation")

    if run_simulation:
        stages = demo_lots[demo_lot]
        completed = []
        cumulative = 0.0

        for stage in stages:
            stage_name = stage["stage_name"]
            score = stage["score"]
            score_class = stage["score_class"]
            weight = stage["weight"]
            danger_params = stage["danger_params"]

            cumulative += score * weight
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

            with placeholder.container():
                # 1. Overall Risk
                st.subheader("Overall Risk")
                o1, o2 = st.columns(2)
                o1.metric("Live Lot Overall Risk", f"{live_overall_risk:.2f}")
                o2.metric("Overall Risk Class", live_overall_class)

                st.divider()

                # 2. Current Stage
                st.subheader("Current Stage")
                st.markdown(
                    f"### {current_stage['stage_name']} {status_badge_html(current_stage['badge'])}",
                    unsafe_allow_html=True
                )

                c1, c2, c3 = st.columns(3)
                c1.metric("Stage Risk", f"{current_stage['score']:.2f}")
                c2.metric("Stage Class", current_stage["score_class"])
                c3.metric("Cumulative Risk", f"{current_stage['cumulative']:.2f}")

                current_df = pd.DataFrame({
                    "Parameter": list(current_stage["danger_params"].keys()),
                    "Zone": list(current_stage["danger_params"].values())
                })
                st.write(current_df.style.map(highlight_zone, subset=["Zone"]))

                if current_stage["status_type"] == "error":
                    st.error(current_stage["status_message"])
                else:
                    st.success(current_stage["status_message"])

                st.divider()

                # 3. Previous stages
                for prev in completed:
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

                    st.divider()

                # 4. Live Dashboard
                st.subheader("Live Dashboard")
                live_dashboard_df = pd.DataFrame({
                    "Stage": [rec["stage_name"] for rec in live_stage_list],
                    "Score": [rec["score"] for rec in live_stage_list],
                    "Class": [rec["score_class"] for rec in live_stage_list],
                    "Status": [rec["badge"] for rec in live_stage_list]
                })
                st.dataframe(live_dashboard_df, use_container_width=True)

                st.divider()

                # 5. Live Parameter Status
                st.subheader("Live Parameter Status")
                st.write(live_sensor_df.style.map(highlight_zone, subset=["Zone"]))

                st.divider()

                # 6. Warning Parameters
                st.subheader("Warning Parameters")
                if live_warning_df.empty:
                    st.success("No warning or danger parameters currently active.")
                else:
                    st.write(live_warning_df.style.map(highlight_zone, subset=["Zone"]))

                st.divider()

                # 7. Stage-by-Stage Risk
                st.subheader("Stage-by-Stage Risk")
                fig_stage = px.bar(
                    live_stage_df,
                    x="Stage",
                    y="Score",
                    color="Class",
                    text="Score",
                    title="Current Live Stage Risk View"
                )
                st.plotly_chart(fig_stage, use_container_width=True)

                # 8. Top Current Risk Contributors
                st.subheader("Top Current Risk Contributors")
                fig_contrib = px.bar(
                    live_contrib_df.head(10),
                    x="Parameter",
                    y="Weighted Contribution",
                    color="Stage",
                    title="Top Weighted Contributors in Current Live View"
                )
                st.plotly_chart(fig_contrib, use_container_width=True)

            time.sleep(1)

            if badge == "STOPPED":
                st.info(f"Simulation stopped early. Current cumulative risk = {cumulative:.2f}")
                break

            completed.insert(0, current_stage)
        else:
            st.success(f"Simulation complete. Final cumulative risk = {cumulative:.2f}")                

            st.divider()

            # 9. Historical Trend
            st.subheader("Historical Trend")

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

            fig_trend = px.line(
                trend_df,
                x="Stage",
                y="Cumulative Risk",
                markers=True,
                title="Cumulative Delamination Risk Across Reached Stages"
            )
            st.plotly_chart(fig_trend, use_container_width=True)

            st.dataframe(trend_df, use_container_width=True)            