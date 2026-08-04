import streamlit as st

from app import DigitalTwinApplication
from devices.fault_injection import FaultMode
from core.data_collector_manager import DataCollectorManager
from ui.charts import (
    show_measurements,
    show_prediction,
    show_residuals,
)

st.set_page_config(
    page_title="Digital Twin Platform",
    page_icon="⚡",
    layout="wide"
)

st.title("Digital Twin Platform")

# ==========================================================
# Data source
# ==========================================================

st.sidebar.header("Data Source")

mode = st.sidebar.radio(
    "Mode",
    ["Offline", "Live"],
    index=0,
)

# При смяна на режима прекратяваме стария collector.
if st.session_state.get("current_mode") != mode:

    DataCollectorManager.reset()

    st.session_state.pop("app", None)
    st.session_state.pop("experiment_reader", None)
    st.session_state.pop("loaded_experiment", None)
    st.session_state.pop("last_data", None)

    st.session_state.current_mode = mode

if "app" not in st.session_state:

    st.session_state.app = DigitalTwinApplication()

app = st.session_state.app

# ==========================================================
# Offline mode
# ==========================================================

if mode == "Offline":

    experiments = app.list_experiments()

    experiment_names = {
        f"{e['id']} - {e['experiment_name']}": e["id"]
        for e in experiments
    }

    selected = st.sidebar.selectbox(
        "Experiment",
        list(experiment_names.keys())
    )

    if st.sidebar.button("Load Experiment"):

        count = app.load_experiment(
            experiment_names[selected]
        )

        st.sidebar.success(
            f"Loaded {count} samples."
        )

        st.session_state.last_data = None

        st.rerun()

# ==========================================================
# Live mode
# ==========================================================


# ==========================================================
# Fault injection
# ==========================================================

st.sidebar.divider()

if mode == "Offline":

    col1, col2 = st.sidebar.columns(2)

    with col1:

        if st.button("▶ Play"):

            app.play()

            st.rerun()

    with col2:

        if st.button("■ Stop"):

            app.stop()

            st.rerun()

@st.fragment(run_every=0.5)
def show_playback_progress():

    if mode != "Offline":
        return

    progress = app.progress()
    current, total = app.sample_info()

    st.sidebar.progress(
        min(max(progress, 0.0), 1.0)
    )

    st.sidebar.write(
        f"{current} / {total}"
    )

    st.sidebar.caption(
        f"{progress * 100:.1f}% completed"
    )


if mode == "Offline":
    show_playback_progress()

if mode == "Live":

    st.sidebar.header("Fault Injection")

    fault_name = st.sidebar.selectbox(
        "Active Fault",
        [
            "None",
            "Mechanical Overload",
            "Cooling Failure",
            "Voltage Drop",
            "Current Sensor Offset",
            "RPM Sensor Offset",
            "Efficiency Loss",
        ],
    )

    fault_map = {
        "None": None,
        "Mechanical Overload": FaultMode.MECHANICAL_OVERLOAD,
        "Cooling Failure": FaultMode.COOLING_FAILURE,
        "Voltage Drop": FaultMode.VOLTAGE_DROP,
        "Current Sensor Offset": FaultMode.CURRENT_SENSOR_OFFSET,
        "RPM Sensor Offset": FaultMode.RPM_SENSOR_OFFSET,
        "Efficiency Loss": FaultMode.EFFICIENCY_LOSS,
    }

    app.set_fault(fault_map[fault_name])

toggle_label = (
    "Playback"
    if mode == "Offline"
    else "Live update"
)

automatic_update = st.toggle(
    toggle_label,
    value=True
)

@st.fragment(
    run_every=0.5 if automatic_update else None
)

def show_dashboard():
    if automatic_update:

        st.caption(
            f"{mode} mode — automatic refresh "
            "every 0.5 seconds"
        )

        st.session_state.last_data = (
            app.get_snapshot()
        )

    else:

        st.caption(
            f"{mode} mode — automatic refresh stopped"
        )

        if "last_data" not in st.session_state:
            st.session_state.last_data = (
                app.get_snapshot()
            )

    data = st.session_state.last_data

    if data is None:
        st.info("Waiting for first measurements...")
        return

    real = data["real"]
    twin = data["twin"]
    diag = data["diagnostics"]
    res = data["residuals"]

    history = app.get_history()

    metric_col1, metric_col2, metric_col3 = st.columns(3)

    with metric_col1:

        st.metric(
            "RPM",
            f"{real['rpm']:.1f}"
        )

        st.metric(
            "Current",
            f"{real['current']:.2f} A"
        )

        st.metric(
            "Torque",
            f"{real['torque']:.1f} Nm"
        )

    with metric_col2:

        st.metric(
            "Temperature",
            f"{real['temperature']:.1f} °C"
        )

        st.metric(
            "Power",
            f"{real['power']:.2f} kW"
        )

        st.metric(
            "Efficiency",
            f"{real['efficiency'] * 100:.1f} %"
        )

        st.metric(
            "Voltage",
            f"{real['voltage']:.1f} V"
        )

        st.metric(
            "Frequency",
            f"{real['frequency']:.2f} Hz"
        )

    with metric_col3:

        st.metric(
            "Health",
            f"{diag['health']:.1f} %"
        )
        st.metric(
            "Status",
            diag["status"]
        )
    st.divider()

    st.subheader("Digital Twin Prediction")

    twin_col1, twin_col2 = st.columns(2)

    with twin_col1:

        st.metric(
            "Expected RPM",
            f"{twin['rpm']:.1f}"
        )

        st.metric(
            "Expected Current",
            f"{twin['current']:.2f} A"
        )

        st.metric(
            "Expected Temperature",
            f"{twin['temperature']:.1f} °C"
        )

    with twin_col2:

        st.metric(
            "Expected Voltage",
            f"{twin['voltage']:.1f} V"
        )

        st.metric(
            "Expected Power",
            f"{twin['power']:.2f} kW"
        )

        st.metric(
            "Expected Efficiency",
            f"{twin['efficiency'] * 100:.1f} %"
        )

    st.divider()

    st.subheader("Residuals")

    res_col1, res_col2 = st.columns(2)

    with res_col1:

        st.metric(
            "RPM Error",
            f"{res['rpm_error']:.2f}"
        )

        st.metric(
            "Current Error",
            f"{res['current_error']:.2f}"
        )

        st.metric(
            "Temperature Error",
            f"{res['temperature_error']:.2f}"
        )

        st.metric(
            "Voltage Error",
            f"{res['voltage_error']:.2f}"
        )

    with res_col2:

        st.metric(
            "Torque Error",
            f"{res['torque_error']:.2f}"
        )

        st.metric(
            "Power Error",
            f"{res['power_error']:.2f}"
        )

        st.metric(
            "Efficiency Error",
            f"{res['efficiency_error'] * 100:.2f} %"
        )

        st.metric(
            "Frequency Error",
            f"{res['frequency_error']:.2f} Hz"
        )
    st.subheader("Active alarms")

    if diag["faults"]:

        for fault in diag["faults"]:
            st.warning(fault)

    else:

        st.success("No active faults")

    st.divider()

    if mode == "Live":
        button_col1, button_col2 = st.columns(2)



        with button_col1:

            if st.button(
                "Increase Load",
                key="increase_load"
            ):
                app.increase_load()

        with button_col2:

            if st.button(
                "Decrease Load",
                key="decrease_load"
            ):
                app.decrease_load()

    st.divider()

    history = app.get_history()

    duration = (
        app.experiment_duration()
        if mode == "Offline"
        else None
    )

    show_measurements(
        history=history,
        mode=mode,
        duration=duration,
    )

    st.divider()

    show_prediction(
        history=history,
        mode=mode,
        duration=duration,
    )

    st.divider()

    show_residuals(
        history=history,
        mode=mode,
        duration=duration,
    )


show_dashboard()