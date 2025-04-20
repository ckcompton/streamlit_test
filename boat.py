import streamlit as st
import pandas as pd
import json
import os
import csv
from io import StringIO

# Set page configuration
st.set_page_config(page_title="2008 Supra 22SSV First Startup Diagnostic Checklist", layout="wide")

# File to store persistent data
DATA_FILE = "checklist_data.json"
REPORT_FILE = "checklist_report.csv"

# Define DataFrames for parameters
params = [
    {"Parameter": "Battery Voltage", "Expected Value": "12.2–12.8V", "Notes": "If <12.2V, charge or replace battery."},
    {"Parameter": "Manifold Absolute Pressure (MAP)", "Expected Value": "~90–100 kPa (at sea level)", "Notes": "Varies with altitude; should be steady."},
    {"Parameter": "Throttle Position Sensor (TPS)", "Expected Value": "0–1% at idle", "Notes": "Ensure throttle is closed; erratic values indicate a faulty TPS."},
    {"Parameter": "Engine Coolant Temperature (ECT)", "Expected Value": "Ambient temp (~20–30°C)", "Notes": "Should match air temp after sitting."},
    {"Parameter": "Intake Air Temperature (IAT)", "Expected Value": "Ambient temp (~20–30°C)", "Notes": "Should match air temp."},
    {"Parameter": "Ignition Status", "Expected Value": "OFF", "Notes": "Confirm no unexpected activity."}
]
df = pd.DataFrame(params)

idle_params = [
    {"Parameter": "Engine RPM", "Target Value": "600–800 RPM", "Notes": "Should be steady; surging indicates fuel or air issues."},
    {"Parameter": "Battery Voltage", "Target Value": "13.5–14.5V", "Notes": "Indicates alternator is charging."},
    {"Parameter": "Engine Coolant Temperature (ECT)", "Target Value": "70–85°C (after warmup)", "Notes": "Should rise steadily; overheating (>95°C) requires immediate shutdown."},
    {"Parameter": "Intake Air Temperature (IAT)", "Target Value": "Ambient + 5–10°C", "Notes": "Higher values may indicate heat soak."},
    {"Parameter": "Manifold Absolute Pressure (MAP)", "Target Value": "30–50 kPa", "Notes": "Should stabilize; erratic values suggest vacuum leaks."},
    {"Parameter": "Throttle Position Sensor (TPS)", "Target Value": "0–1%", "Notes": "Should remain steady at idle."},
    {"Parameter": "Fuel Injector Pulse Width", "Target Value": "2–4 ms", "Notes": "Varies with load; erratic values indicate fuel delivery issues."},
    {"Parameter": "Ignition Timing", "Target Value": "8–12° BTDC", "Notes": "Should be stable; check for misfires."},
    {"Parameter": "Oxygen Sensor (O2)", "Target Value": "0.1–0.9V (oscillating)", "Notes": "If equipped; steady values indicate a lean/rich condition."}
]
idle_df = pd.DataFrame(idle_params)

# Function to load data from JSON file
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {"checkboxes": {}, "inputs": {}}
    return {"checkboxes": {}, "inputs": {}}

# Function to save data to JSON file
def save_data():
    data = {
        "checkboxes": st.session_state.checkboxes,
        "inputs": st.session_state.inputs
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Function to generate a human-readable report
def generate_report():
    report_data = []
    report_data.append(["Section", "Field", "Value"])
    report_data.append(["Metadata", "Date", st.session_state.inputs.get("date", "")])
    report_data.append(["Metadata", "Technician", st.session_state.inputs.get("technician", "")])
    report_data.append(["Metadata", "Boat Hours", st.session_state.inputs.get("boat_hours", "")])

    for key, value in st.session_state.checkboxes.items():
        report_data.append(["Checklist", key, "Checked" if value else "Unchecked"])

    for i, row in df.iterrows():
        param_key = f"param_{i}"
        report_data.append(["Pre-Start Parameters", row["Parameter"], st.session_state.inputs.get(param_key, "")])

    for i, row in idle_df.iterrows():
        param_key = f"idle_param_{i}"
        report_data.append(["Idle Parameters", row["Parameter"], st.session_state.inputs.get(param_key, "")])

    report_data.append(["Post-Run", "Codes Found", st.session_state.inputs.get("codes_found", "")])
    report_data.append(["Post-Run", "Actions Needed", st.session_state.inputs.get("actions_needed", "")])
    report_data.append(["Post-Run", "Observations", st.session_state.inputs.get("observations", "")])
    report_data.append(["Finalization", "Signature", st.session_state.inputs.get("signature", "")])
    report_data.append(["Finalization", "Date Completed", st.session_state.inputs.get("date_completed", "")])

    output = StringIO()
    writer = csv.writer(output)
    writer.writerows(report_data)
    return output.getvalue()

# Initialize session state
if 'checkboxes' not in st.session_state or 'inputs' not in st.session_state:
    saved_data = load_data()
    st.session_state.checkboxes = saved_data.get("checkboxes", {})
    st.session_state.inputs = saved_data.get("inputs", {})

# Function to create a checkbox with session state persistence
def create_checkbox(label, key):
    if key not in st.session_state.checkboxes:
        st.session_state.checkboxes[key] = False
    st.session_state.checkboxes[key] = st.checkbox(label, value=st.session_state.checkboxes[key], key=key)

# Function to create a text input with session state persistence
def create_text_input(label, key, placeholder=""):
    if key not in st.session_state.inputs:
        st.session_state.inputs[key] = ""
    value = st.text_input(label, value=st.session_state.inputs[key], placeholder=placeholder, key=key)
    st.session_state.inputs[key] = value
    return value

# Main title and header
st.title("2008 Supra 22SSV First Startup Diagnostic Checklist")
st.markdown("**For 350 Indmar V8 with MEFI-5 ECM Using EFI 5/6 Scan Tool**", unsafe_allow_html=True)

# Input fields for metadata
col1, col2, col3 = st.columns(3)
with col1:
    create_text_input("Date", "date", "YYYY-MM-DD")
with col2:
    create_text_input("Technician", "technician")
with col3:
    create_text_input("Boat Hours (if known)", "boat_hours")

# Save and Download buttons
col_save, col_download, col_report = st.columns(3)
with col_save:
    if st.button("Save Data"):
        save_data()
        st.success("Data saved successfully!")
with col_download:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            st.download_button(
                label="Download JSON Data",
                data=f,
                file_name="checklist_data.json",
                mime="application/json"
            )
with col_report:
    st.download_button(
        label="Download Report (CSV)",
        data=generate_report(),
        file_name="checklist_report.csv",
        mime="text/csv"
    )

# Section 1: Pre-Start Checks
st.header("1. Pre-Start Checks")
st.write("Ensure the boat is in a safe, well-ventilated area, either in the water or on a trailer with a flush kit. Complete these checks before connecting the scan tool or attempting to start the engine.")

# 1.1 Battery
st.subheader("1.1 Battery")
create_checkbox("Inspect battery terminals: Check for corrosion or loose connections. Clean and tighten as needed.", "battery_terminals")
create_checkbox("Measure battery voltage: Use a multimeter to confirm voltage is ≥12.6V (fully charged). Charge or replace if below 12.2V.", "battery_voltage")
create_checkbox("Check battery age: If over 4 years old or showing signs of weakness, consider replacement.", "battery_age")
create_checkbox("Ensure battery is secure: Verify straps or mounts are tight to prevent movement.", "battery_secure")

# 1.2 Engine Oil
st.subheader("1.2 Engine Oil")
create_checkbox("Check oil level: Pull dipstick, wipe, reinsert, and confirm level is within the safe range. Top off with manufacturer-recommended oil (e.g., 15W-40 marine-grade) if low.", "oil_level")
create_checkbox("Inspect oil condition: Look for milky or contaminated oil, indicating water intrusion. If present, change oil and filter before proceeding.", "oil_condition")
create_checkbox("Check for leaks: Inspect around oil pan, filter, and lines for signs of leaks.", "oil_leaks")

# 1.3 Cooling System
st.subheader("1.3 Cooling System")
create_checkbox("Verify coolant level: For closed-loop systems, check reservoir level and top off with 50/50 antifreeze mix if needed.", "coolant_level")
create_checkbox("Inspect raw water system: Check impeller (replace if over 2 years old or brittle), strainer, and hoses for cracks or blockages.", "raw_water")
create_checkbox("Confirm water supply: If on a trailer, connect a flush kit with adequate water flow. If in water, ensure seacock is open.", "water_supply")

# 1.4 Fuel System
st.subheader("1.4 Fuel System")
create_checkbox("Check fuel condition: After 2 years, fuel may be stale. If possible, drain tank and replace with fresh marine-grade fuel (non-ethanol preferred).", "fuel_condition")
create_checkbox("Inspect fuel lines: Look for cracks, leaks, or degradation. Replace any suspect lines.", "fuel_lines")
create_checkbox("Check fuel filter: Replace if not changed in the last year or if contaminated.", "fuel_filter")
create_checkbox("Prime fuel system: Cycle ignition key (without starting) 2–3 times to prime fuel pump and check for leaks.", "fuel_prime")

# 1.5 General Engine Inspection
st.subheader("1.5 General Engine Inspection")
create_checkbox("Inspect belts and pulleys: Check for wear, cracking, or improper tension. Adjust or replace as needed.", "belts_pulleys")
create_checkbox("Check spark plugs: Remove and inspect for fouling or corrosion. Replace if worn (use marine-grade plugs).", "spark_plugs")
create_checkbox("Verify throttle linkage: Ensure smooth operation with no binding.", "throttle_linkage")
create_checkbox("Check exhaust system: Inspect manifolds and risers for corrosion or leaks.", "exhaust_system")

# 1.6 Diagnostic Setup
st.subheader("1.6 Diagnostic Setup")
create_checkbox("Connect EFI 5/6 Scan Tool: Locate the 6-pin marine diagnostic port (typically near the ECM). Securely connect the scan tool using the provided adapter (#94027 for MEFI-5).", "connect_scan_tool")
create_checkbox("Power on scan tool: Connect to a laptop with the EFI 5/6 software installed (e.g., ScannerPro or MEFI Scan & Tune). Verify communication with the ECM.", "power_scan_tool")
create_checkbox("Clear existing codes: If the scan tool shows stored codes, note them for reference and clear them to start fresh.", "clear_codes")
create_checkbox("Start data logging: Begin a new log file in the scan tool software to record all parameters during the session.", "start_logging")

# Section 2: Pre-Start Parameter Monitoring
st.header("2. Pre-Start Parameter Monitoring")
st.write("With the ignition in the “ON” position (engine not running), use the EFI 5/6 Scan Tool to verify the following parameters. Record values for reference.")

# Update df with actual values
for i, row in df.iterrows():
    param_key = f"param_{i}"
    df.at[i, "Actual Value"] = create_text_input(f"Actual Value for {row['Parameter']}", param_key)
st.table(df[["Parameter", "Expected Value", "Actual Value", "Notes"]])
st.markdown("*Notes:* If any parameter is out of range, investigate before starting (e.g., faulty sensor, wiring issue). Verify scan tool is displaying real-time data with no communication errors.", unsafe_allow_html=True)

# Section 3: Engine Start and Idle Monitoring
st.header("3. Engine Start and Idle Monitoring")
st.write("Start the engine and let it idle in neutral. Monitor live data using the EFI 5/6 Scan Tool for at least 5 minutes to ensure stable operation. Record values and compare to targets.")

# 3.1 Starting Procedure
st.subheader("3.1 Starting Procedure")
create_checkbox("Confirm water flow: Ensure flush kit or raw water system is supplying water.", "water_flow")
create_checkbox("Turn ignition to START: Crank engine for no more than 10 seconds at a time. Allow 30 seconds between attempts if it doesn’t start.", "ignition_start")
create_checkbox("Check for unusual noises: Listen for knocking, rattling, or grinding during startup.", "unusual_noises")

# 3.2 Live Data Targets at Idle
st.subheader("3.2 Live Data Targets at Idle")
for i, row in idle_df.iterrows():
    param_key = f"idle_param_{i}"
    idle_df.at[i, "Actual Value"] = create_text_input(f"Actual Value for {row['Parameter']}", param_key)
st.table(idle_df[["Parameter", "Target Value", "Actual Value", "Notes"]])
st.markdown("*Notes:* Allow engine to reach operating temperature (70–85°C) before proceeding. If engine fails to start, check for fault codes immediately and troubleshoot (e.g., fuel pump, ignition, or ECM issues). Watch for warning lights or alarms on the dash and correlate with scan tool data.", unsafe_allow_html=True)

# Section 4: Post-Run Review
st.header("4. Post-Run Review")
st.write("After running the engine for 5–10 minutes, shut it down and perform the following checks to evaluate performance and prepare for future use.")

# 4.1 Diagnostic Checks
st.subheader("4.1 Diagnostic Checks")
create_checkbox("Check for fault codes: Use the scan tool to read any new Diagnostic Trouble Codes (DTCs). Record codes and their descriptions (e.g., “P0107 – MAP Sensor Low Voltage”).", "fault_codes")
create_text_input("Codes Found", "codes_found")
create_text_input("Actions Needed", "actions_needed")
create_checkbox("Review live data log: Analyze the recorded data for anomalies (e.g., erratic RPM, high temps, or sensor failures).", "review_log")
create_checkbox("Save log file: Export the log to your laptop with a clear filename (e.g., “Supra22SSV_2025-04-19.log”) for future reference.", "save_log")

# 4.2 Physical Inspection
st.subheader("4.2 Physical Inspection")
create_checkbox("Check for leaks: Inspect engine compartment for oil, fuel, or coolant leaks.", "post_leaks")
create_checkbox("Inspect exhaust: Confirm exhaust is clear and no excessive smoke or unusual odors.", "post_exhaust")
create_checkbox("Recheck fluid levels: Verify oil and coolant levels after cooldown; top off if needed.", "post_fluids")

# 4.3 Maintenance Planning
st.subheader("4.3 Maintenance Planning")
create_checkbox("Address fault codes: Research and resolve any DTCs before next use (refer to Indmar MEFI-5 service manual or contact a technician).", "address_codes")
create_checkbox("Schedule maintenance: Based on findings, plan for oil change, impeller replacement, or other overdue services.", "schedule_maintenance")
create_checkbox("Document findings: Note any issues, repairs, or observations for future reference.", "document_findings")
create_text_input("Observations", "observations")

# 4.4 Scan Tool Shutdown
st.subheader("4.4 Scan Tool Shutdown")
create_checkbox("Disconnect scan tool: Power off the tool and disconnect from the diagnostic port.", "disconnect_tool")
create_checkbox("Store equipment: Keep the scan tool and cables in a dry, protected location.", "store_equipment")

# Section 5: Additional Notes
st.header("5. Additional Notes")
st.markdown("""
- **Safety First:** Always work in a well-ventilated area, keep a fire extinguisher nearby, and avoid loose clothing near moving parts.
- **Reference Manual:** Consult the Indmar MEFI-5 Service and Diagnostic Manual for detailed troubleshooting if codes or issues arise.
- **Professional Help:** If you encounter persistent issues (e.g., no-start, overheating, or complex DTCs), contact a certified marine technician.
- **Tool Support:** For scan tool issues, refer to OBD Diagnostics’ support at support@obd2allinone.com or 310-793-2410.
""", unsafe_allow_html=True)

# Final signature and date
st.subheader("Finalization")
create_text_input("Signature", "signature")
create_text_input("Date Completed", "date_completed", "YYYY-MM-DD")

# Add some basic styling
st.markdown("""
<style>
    .stTextInput > div > div > input {
        border: 1px solid #000;
        padding: 8px;
    }
    .stCheckbox > label {
        margin-bottom: 5px;
    }
    .stTable {
        border-collapse: collapse;
        width: 100%;
    }
    .stTable th, .stTable td {
        border: 1px solid #000;
        padding: 8px;
        text-align: left;
    }
    .stTable th {
        background-color: #f2f2f2;
    }
</style>
""", unsafe_allow_html=True)