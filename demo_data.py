def get_demo_lots(stage_weights):
    return {
        "Lot A - Safe Lot": [
            {
                "stage_name": "Die Attach",
                "weight": stage_weights["die_attach"],
                "param_values": {
                    "die_attach_temp": 150.0,
                    "bond_force": 20.0,
                    "epoxy_volume": 100.0,
                    "die_attach_void_percent": 3.0
                }
            },
            {
                "stage_name": "Die Attach Cure",
                "weight": stage_weights["die_attach_cure"],
                "param_values": {
                    "cure_temp": 165.0,
                    "cure_time": 60.0,
                    "cure_ramp_rate": 5.0
                }
            },
            {
                "stage_name": "Moulding",
                "weight": stage_weights["moulding"],
                "param_values": {
                    "mold_temp": 175.0,
                    "mold_pressure": 80.0,
                    "transfer_speed": 1.0,
                    "vacuum_level": 0.50,
                    "mold_void_count": 2
                }
            },
            {
                "stage_name": "Post-Mould Cure",
                "weight": stage_weights["pmc"],
                "param_values": {
                    "pmc_temp": 170.0,
                    "pmc_time": 90.0,
                    "cooling_rate": 4.0,
                    "warpage_mm": 0.08
                }
            },
            {
                "stage_name": "Solder Reflow",
                "weight": stage_weights["reflow"],
                "param_values": {
                    "floor_life_hours": 24.0,
                    "moisture_content": 0.25,
                    "reflow_peak_temp": 245.0,
                    "reflow_ramp_rate": 2.5,
                    "time_above_liquidus": 90.0
                }
            }
        ],

        "Lot B - Caution Lot": [
            {
                "stage_name": "Die Attach",
                "weight": stage_weights["die_attach"],
                "param_values": {
                    "die_attach_temp": 158.0,
                    "bond_force": 20.0,
                    "epoxy_volume": 108.0,
                    "die_attach_void_percent": 4.0
                }
            },
            {
                "stage_name": "Die Attach Cure",
                "weight": stage_weights["die_attach_cure"],
                "param_values": {
                    "cure_temp": 176.0,
                    "cure_time": 60.0,
                    "cure_ramp_rate": 7.0
                }
            },
            {
                "stage_name": "Moulding",
                "weight": stage_weights["moulding"],
                "param_values": {
                    "mold_temp": 175.0,
                    "mold_pressure": 88.0,
                    "transfer_speed": 1.25,
                    "vacuum_level": 0.50,
                    "mold_void_count": 2
                }
            },
            {
                "stage_name": "Post-Mould Cure",
                "weight": stage_weights["pmc"],
                "param_values": {
                    "pmc_temp": 170.0,
                    "pmc_time": 110.0,
                    "cooling_rate": 4.0,
                    "warpage_mm": 0.16
                }
            },
            {
                "stage_name": "Solder Reflow",
                "weight": stage_weights["reflow"],
                "param_values": {
                    "floor_life_hours": 60.0,
                    "moisture_content": 0.25,
                    "reflow_peak_temp": 255.0,
                    "reflow_ramp_rate": 2.8,
                    "time_above_liquidus": 100.0
                }
            }
        ],

    "Lot C - High Stage Risk": [
    {
        "stage_name": "Die Attach",
        "weight": stage_weights["die_attach"],
        "param_values": {
            "die_attach_temp": 157.0,          # Warning, slight high temp
            "bond_force": 20.0,               # Normal
            "epoxy_volume": 100.0,            # Normal
            "die_attach_void_percent": 3.0    # Normal
        }
    },
    {
        "stage_name": "Die Attach Cure",
        "weight": stage_weights["die_attach_cure"],
        "param_values": {
            "cure_temp": 165.0,               # Normal
            "cure_time": 75.0,                # Warning, slightly longer cure time
            "cure_ramp_rate": 5.0             # Normal
        }
    },
    {
        "stage_name": "Moulding",
        "weight": stage_weights["moulding"],
        "param_values": {
            "mold_temp": 175.0,
            "mold_pressure": 80.0,
            "transfer_speed": 1.0,
            "vacuum_level": 0.50,
            "mold_void_count": 2
        }
    },
    {
        "stage_name": "Post-Mould Cure",
        "weight": stage_weights["pmc"],
        "param_values": {
            "pmc_temp": 190.0,
            "pmc_time": 180.0,
            "cooling_rate": 10.0,
            "warpage_mm": 0.50
        }
    },
    {
        "stage_name": "Solder Reflow",
        "weight": stage_weights["reflow"],
        "param_values": {
            "floor_life_hours": 24.0,
            "moisture_content": 0.25,
            "reflow_peak_temp": 245.0,
            "reflow_ramp_rate": 2.5,
            "time_above_liquidus": 90.0
        }
    }
],


"Lot D - Danger Zone Lot": [
    {
        "stage_name": "Die Attach",
        "weight": stage_weights["die_attach"],
        "param_values": {
            "die_attach_temp": 150.0,          # Normal
            "bond_force": 23.0,               # Warning, slightly high force
            "epoxy_volume": 100.0,            # Normal
            "die_attach_void_percent": 3.0    # Normal
        }
    },
    {
        "stage_name": "Die Attach Cure",
        "weight": stage_weights["die_attach_cure"],
        "param_values": {
            "cure_temp": 165.0,               # Normal
            "cure_time": 60.0,                # Normal
            "cure_ramp_rate": 7.0             # Warning, slightly high ramp rate
        }
    },
    {
        "stage_name": "Moulding",
        "weight": stage_weights["moulding"],
        "param_values": {
            "mold_temp": 175.0,               # Normal
            "mold_pressure": 88.0,            # Warning, slightly high pressure
            "transfer_speed": 1.0,            # Normal
            "vacuum_level": 0.50,             # Normal
            "mold_void_count": 2              # Normal
        }
    },
    {
        "stage_name": "Post-Mould Cure",
        "weight": stage_weights["pmc"],
        "param_values": {
            "pmc_temp": 170.0,                # Normal
            "pmc_time": 90.0,                 # Normal
            "cooling_rate": 4.0,              # Normal
            "warpage_mm": 0.30                # Danger, triggers stop
        }
    },
    {
        "stage_name": "Solder Reflow",
        "weight": stage_weights["reflow"],
        "param_values": {
            "floor_life_hours": 24.0,
            "moisture_content": 0.25,
            "reflow_peak_temp": 245.0,
            "reflow_ramp_rate": 2.5,
            "time_above_liquidus": 90.0
        }
    }
]

    }


def get_historical_lot_quality_data():
    return [
        {"Lot ID": "LOT-001", "Overall Risk": 0.12, "Risk Class": "Low", "Final Status": "Completed"},
        {"Lot ID": "LOT-002", "Overall Risk": 0.18, "Risk Class": "Low", "Final Status": "Completed"},
        {"Lot ID": "LOT-003", "Overall Risk": 0.29, "Risk Class": "Low", "Final Status": "Completed"},
        {"Lot ID": "LOT-004", "Overall Risk": 0.41, "Risk Class": "Medium", "Final Status": "Completed"},
        {"Lot ID": "LOT-005", "Overall Risk": 0.36, "Risk Class": "Medium", "Final Status": "Completed"},
        {"Lot ID": "LOT-006", "Overall Risk": 0.22, "Risk Class": "Low", "Final Status": "Completed"},
        {"Lot ID": "LOT-007", "Overall Risk": 0.55, "Risk Class": "Medium", "Final Status": "Completed"},
        {"Lot ID": "LOT-008", "Overall Risk": 0.68, "Risk Class": "High", "Final Status": "Stopped"},
        {"Lot ID": "LOT-009", "Overall Risk": 0.47, "Risk Class": "Medium", "Final Status": "Completed"},
        {"Lot ID": "LOT-010", "Overall Risk": 0.74, "Risk Class": "High", "Final Status": "Stopped"},
        {"Lot ID": "LOT-011", "Overall Risk": 0.31, "Risk Class": "Low", "Final Status": "Completed"},
        {"Lot ID": "LOT-012", "Overall Risk": 0.39, "Risk Class": "Medium", "Final Status": "Completed"},
    ]