# DelamGuard AI UI Spec

Goal:
Build a React UI only. Do not change the current logic.

Brand:
- Micron-inspired theme
- dark background
- purple accent
- premium, modern control-room style
- Micron logo in header

Logic must stay the same:
- Normal = 0.0
- Warning = 0.5
- Danger = 1.0

Stage weights:
- Die Attach = 0.20
- Die Attach Cure = 0.15
- Moulding = 0.25
- Post-Mould Cure = 0.15
- Solder Reflow = 0.25

Stop rules:
- Any Danger parameter => STOPPED
- Any High stage risk => STOPPED
- Otherwise PASSED

Preset lots:
- Lot A - Safe Lot
- Lot B - Caution Lot
- Lot C - High Stage Risk
- Lot D - Danger Zone Lot

Main page:
Live Lot Simulation

Main page order:
1. Overall Risk
2. Current Stage
3. Previous Stage(s)
4. Live Dashboard
5. Live Parameter Status
6. Warning Parameters
7. Stage-by-Stage Risk
8. Top Current Risk Contributors
9. Historical Trend

Other pages:
- Overview & Live Dashboard
- Model Calibration (Future AI/ML)

Important:
UI/UX only. Do not invent new thresholds, formulas, or stop logic.