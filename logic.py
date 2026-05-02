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

stage_thresholds = {
    "Die Attach": 0.50,
    "Die Attach Cure": 0.55,
    "Moulding": 0.50,
    "Post-Mould Cure": 0.35,
    "Solder Reflow": 0.50
}

cumulative_risk_threshold = 0.20

def evaluate_demo_stage(stage_name, param_values, parameter_weights):
    if stage_name == "Die Attach":
        z1, r1 = classify_three_zone(param_values["die_attach_temp"], 145, 155, 140, 160, "both")
        z2, r2 = classify_three_zone(param_values["bond_force"], 18, 22, 15, 25, "both")
        z3, r3 = classify_three_zone(param_values["epoxy_volume"], 95, 105, 90, 110, "both")
        z4, r4 = classify_three_zone(param_values["die_attach_void_percent"], 0, 5, 5, 10, "high")

        danger_params = {
            "die_attach_temp": z1,
            "bond_force": z2,
            "epoxy_volume": z3,
            "die_attach_void_percent": z4
        }

        risk_dict = {
            "die_attach_temp": r1,
            "bond_force": r2,
            "epoxy_volume": r3,
            "die_attach_void_percent": r4
        }

        score = weighted_stage_score(risk_dict, parameter_weights["die_attach"])
        return danger_params, score, classify_score(score)

    elif stage_name == "Die Attach Cure":
        z1, r1 = classify_three_zone(param_values["cure_temp"], 160, 170, 150, 180, "both")
        z2, r2 = classify_three_zone(param_values["cure_time"], 50, 70, 40, 90, "both")
        z3, r3 = classify_three_zone(param_values["cure_ramp_rate"], 3, 6, 2, 8, "both")

        danger_params = {
            "cure_temp": z1,
            "cure_time": z2,
            "cure_ramp_rate": z3
        }

        risk_dict = {
            "cure_temp": r1,
            "cure_time": r2,
            "cure_ramp_rate": r3
        }

        score = weighted_stage_score(risk_dict, parameter_weights["die_attach_cure"])
        return danger_params, score, classify_score(score)

    elif stage_name == "Moulding":
        z1, r1 = classify_three_zone(param_values["mold_temp"], 170, 180, 165, 185, "both")
        z2, r2 = classify_three_zone(param_values["mold_pressure"], 75, 85, 65, 90, "both")
        z3, r3 = classify_three_zone(param_values["transfer_speed"], 0.9, 1.1, 0.7, 1.3, "both")
        z4, r4 = classify_three_zone(param_values["vacuum_level"], 0.4, 0.7, 0.2, 0.8, "both")
        z5, r5 = classify_three_zone(param_values["mold_void_count"], 0, 2, 3, 5, "high")

        danger_params = {
            "mold_temp": z1,
            "mold_pressure": z2,
            "transfer_speed": z3,
            "vacuum_level": z4,
            "mold_void_count": z5
        }

        risk_dict = {
            "mold_temp": r1,
            "mold_pressure": r2,
            "transfer_speed": r3,
            "vacuum_level": r4,
            "mold_void_count": r5
        }

        score = weighted_stage_score(risk_dict, parameter_weights["moulding"])
        return danger_params, score, classify_score(score)

    elif stage_name == "Post-Mould Cure":
        z1, r1 = classify_three_zone(param_values["pmc_temp"], 165, 175, 155, 185, "both")
        z2, r2 = classify_three_zone(param_values["pmc_time"], 80, 100, 60, 120, "both")
        z3, r3 = classify_three_zone(param_values["cooling_rate"], 3, 5, 2, 7, "both")
        z4, r4 = classify_three_zone(param_values["warpage_mm"], 0, 0.10, 0.10, 0.20, "high")

        danger_params = {
            "pmc_temp": z1,
            "pmc_time": z2,
            "cooling_rate": z3,
            "warpage_mm": z4
        }

        risk_dict = {
            "pmc_temp": r1,
            "pmc_time": r2,
            "cooling_rate": r3,
            "warpage_mm": r4
        }

        score = weighted_stage_score(risk_dict, parameter_weights["pmc"])
        return danger_params, score, classify_score(score)

    elif stage_name == "Solder Reflow":
        z1, r1 = classify_three_zone(param_values["floor_life_hours"], 0, 48, 49, 72, "high")
        z2, r2 = classify_three_zone(param_values["moisture_content"], 0, 0.30, 0.31, 0.50, "high")
        z3, r3 = classify_three_zone(param_values["reflow_peak_temp"], 235, 250, 251, 260, "high")
        z4, r4 = classify_three_zone(param_values["reflow_ramp_rate"], 0, 3.0, 3.0, 3.5, "high")
        z5, r5 = classify_three_zone(param_values["time_above_liquidus"], 60, 120, 121, 150, "high")

        danger_params = {
            "floor_life_hours": z1,
            "moisture_content": z2,
            "reflow_peak_temp": z3,
            "reflow_ramp_rate": z4,
            "time_above_liquidus": z5
        }

        risk_dict = {
            "floor_life_hours": r1,
            "moisture_content": r2,
            "reflow_peak_temp": r3,
            "reflow_ramp_rate": r4,
            "time_above_liquidus": r5
        }

        score = weighted_stage_score(risk_dict, parameter_weights["reflow"])
        return danger_params, score, classify_score(score)

    return {}, 0.0, "Low"