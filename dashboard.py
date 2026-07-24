import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app import DigitalTwinApplication


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
        use_container_width=True,
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

if "application" not in st.session_state:
    st.session_state.application = DigitalTwinApplication()

app = st.session_state.application

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

        st.session_state.last_data = app.update()

    else:

        st.caption(
            "Analysis mode — automatic refresh stopped"
        )

        if "last_data" not in st.session_state:
            st.session_state.last_data = app.update()

    data = st.session_state.last_data

    real = data["real"]
    twin = data["twin"]
    diag = data["diagnostics"]

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

    with metric_col3:

        st.metric(
            "Health",
            f"{twin['health']:.1f} %"
        )

        st.metric(
            "Status",
            diag["status"]
        )

    st.subheader("Active alarms")

    if diag["alarms"]:

        for alarm in diag["alarms"]:
            st.warning(alarm)

    else:

        st.success("No active alarms")

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