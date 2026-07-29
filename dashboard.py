import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app import DigitalTwinApplication
from devices.fault_injection import FaultMode


def plot_trend(
    df,
    column,
    title,
    unit,
    padding,
    fixed_range=None
):
    values = df[column]

    if fixed_range is None:
        minimum = values.min()
        maximum = values.max()

        y_range = [
            minimum - padding,
            maximum + padding
        ]

    else:
        y_range = fixed_range

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=df["timestamp"],
            y=values,
            mode="lines",
            name=title,
            hovertemplate=(
                "Measurement: %{x}<br>"
                f"{title}: %{{y:.2f}} {unit}"
                "<extra></extra>"
            )
        )
    )

    fig.update_layout(
        title=title,
        height=300,
        margin=dict(
            l=20,
            r=20,
            t=50,
            b=20
        ),
        showlegend=False,
        xaxis_title="Date / Time",
        yaxis_title=unit,
        uirevision=column
    )

    fig.update_yaxes(
        range=y_range
    )

    st.plotly_chart(
        fig,
        width="stretch",
        key=f"chart_{column}",
        config={
            "displaylogo": False,
            "scrollZoom": True
        }
    )


st.set_page_config(
    page_title="Digital Twin Platform",
    page_icon="⚡",
    layout="wide"
)

st.title("Digital Twin Platform")

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

if "app" not in st.session_state:
    st.session_state.app = DigitalTwinApplication()

app = st.session_state.app

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

live_mode = st.toggle(
    "Live update",
    value=True
)


@st.fragment(
    run_every=0.5 if live_mode else None
)
def show_dashboard():

    if live_mode:

        st.caption(
            "Live mode — automatic refresh every 0.5 seconds"
        )

        st.session_state.last_data = app.get_snapshot()

    else:

        st.caption(
            "Analysis mode — automatic refresh stopped"
        )

        if "last_data" not in st.session_state:
            st.session_state.last_data = app.get_snapshot()

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

    st.subheader("Real-Time Trends")

    if not history:
        st.info("Waiting for measurements...")
        return

    df = pd.DataFrame(history)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:

        plot_trend(
            df=df,
            column="rpm",
            title="RPM",
            unit="rpm",
            padding=5
        )

        plot_trend(
            df=df,
            column="temperature",
            title="Temperature",
            unit="°C",
            padding=2
        )

    with chart_col2:

        plot_trend(
            df=df,
            column="current",
            title="Current",
            unit="A",
            padding=0.5
        )

        plot_trend(
            df=df,
            column="health",
            title="Health",
            unit="%",
            padding=1,
            fixed_range=[90, 101]
        )


show_dashboard()