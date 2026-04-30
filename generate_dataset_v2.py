import pandas as pd
import numpy as np

np.random.seed(42)

NUM_LOTS = 1000


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


def generate_one_lot(lot_id):
    die_attach_temp = np.random.normal(150, 6)
    bond_force = np.random.normal(20, 3)
    epoxy_volume = np.random.normal(100, 8)
    die_attach_void_percent = max(0, np.random.normal(4, 4))

    cure_temp = np.random.normal(165, 8)
    cure_time = np.random.normal(60, 15)
    cure_ramp_rate = np.random.normal(5, 1.5)

    mold_temp = np.random.normal(175, 6)
    mold_pressure = np.random.normal(80, 8)
    transfer_speed = np.random.normal(1.0, 0.2)
    vacuum_level = np.clip(np.random.normal(0.5, 0.2), 0, 1)
    mold_void_count = max(0, int(round(np.random.normal(2, 3))))

    pmc_temp = np.random.normal(170, 7)
    pmc_time = np.random.normal(90, 18)
    cooling_rate = np.random.normal(4, 1.5)
    warpage_mm = max(0, np.random.normal(0.08, 0.08))

    floor_life_hours = max(0, np.random.normal(24, 24))
    moisture_content = np.clip(np.random.normal(0.25, 0.15), 0, 1)
    reflow_peak_temp = np.random.normal(245, 8)
    reflow_ramp_rate = np.random.normal(2.5, 0.8)
    time_above_liquidus = max(0, np.random.normal(90, 30))

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

    danger_trigger_stage = "None"
    for stage_name, flag in danger_flags.items():
        if flag:
            danger_trigger_stage = stage_name
            break

    if any(danger_flags.values()):
        final_action = "Immediate Hold / Halt"
    elif any(high_stage_flags.values()):
        final_action = "Hold for Engineering Review"
    else:
        if overall_class == "Low":
            final_action = "Continue"
        elif overall_class == "Medium":
            final_action = "Continue with Caution / Review"
        else:
            final_action = "Hold / Review"

    return {
        "lot_id": f"LOT_{lot_id:04d}",
        "die_attach_temp": round(die_attach_temp, 2),
        "bond_force": round(bond_force, 2),
        "epoxy_volume": round(epoxy_volume, 2),
        "die_attach_void_percent": round(die_attach_void_percent, 2),
        "cure_temp": round(cure_temp, 2),
        "cure_time": round(cure_time, 2),
        "cure_ramp_rate": round(cure_ramp_rate, 2),
        "mold_temp": round(mold_temp, 2),
        "mold_pressure": round(mold_pressure, 2),
        "transfer_speed": round(transfer_speed, 2),
        "vacuum_level": round(vacuum_level, 2),
        "mold_void_count": mold_void_count,
        "pmc_temp": round(pmc_temp, 2),
        "pmc_time": round(pmc_time, 2),
        "cooling_rate": round(cooling_rate, 2),
        "warpage_mm": round(warpage_mm, 3),
        "floor_life_hours": round(floor_life_hours, 2),
        "moisture_content": round(moisture_content, 3),
        "reflow_peak_temp": round(reflow_peak_temp, 2),
        "reflow_ramp_rate": round(reflow_ramp_rate, 2),
        "time_above_liquidus": round(time_above_liquidus, 2),
        "die_attach_score": round(die_attach_score, 3),
        "die_attach_cure_score": round(die_attach_cure_score, 3),
        "moulding_score": round(moulding_score, 3),
        "pmc_score": round(pmc_score, 3),
        "reflow_score": round(reflow_score, 3),
        "overall_risk": round(overall_risk, 3),
        "overall_class": overall_class,
        "danger_trigger_stage": danger_trigger_stage,
        "final_action": final_action
    }


rows = [generate_one_lot(i + 1) for i in range(NUM_LOTS)]
df = pd.DataFrame(rows)

df.to_csv("delamguard_lot_dataset.csv", index=False)

print("Dataset generated successfully!")
print("File saved as: delamguard_lot_dataset.csv")
print(df.head())
print(df["final_action"].value_counts())