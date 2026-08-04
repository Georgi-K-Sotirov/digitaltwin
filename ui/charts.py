import pandas as pd
import plotly.graph_objects as go
import streamlit as st


# ==========================================================
# Universal chart
# ==========================================================

def plot_chart(
    df,
    x_column,
    y_column,
    title,
    unit,
    mode,
    duration=None,
    twin_column=None,
    padding=0,
    fixed_range=None,
):

    fig = go.Figure()

    # ------------------------------------------------------
    # Real measurements
    # ------------------------------------------------------

    fig.add_trace(

        go.Scatter(

            x=df[x_column],

            y=df[y_column],

            mode="lines",

            name="Real",

            line=dict(width=2)

        )

    )

    # ------------------------------------------------------
    # Digital Twin
    # ------------------------------------------------------

    if twin_column is not None:

        fig.add_trace(

            go.Scatter(

                x=df[x_column],

                y=df[twin_column],

                mode="lines",

                name="Digital Twin",

                line=dict(
                    dash="dash",
                    width=2
                )

            )

        )

    # ------------------------------------------------------
    # Y Axis
    # ------------------------------------------------------

    values = df[y_column]

    if twin_column is not None:

        values = pd.concat(
            [
                values,
                df[twin_column]
            ]
        )

    if fixed_range is None:

        ymin = values.min() - padding
        ymax = values.max() + padding

    else:

        ymin = fixed_range[0]
        ymax = fixed_range[1]

    fig.update_yaxes(

        range=[ymin, ymax]

    )

    # ------------------------------------------------------
    # X Axis
    # ------------------------------------------------------

    if mode == "Offline":

        fig.update_xaxes(

            range=[
                0,
                duration
            ],

            title="Simulation Time [s]"

        )

    else:

        fig.update_xaxes(

            title="Time"

        )

    # ------------------------------------------------------
    # Layout
    # ------------------------------------------------------

    fig.update_layout(

        title=title,

        height=300,

        margin=dict(

            l=20,
            r=20,
            t=50,
            b=20

        ),

        showlegend=True,

        legend=dict(

            orientation="h",

            y=1.05,

            x=0

        ),

        yaxis_title=unit,

        uirevision=title

    )

    st.plotly_chart(

        fig,

        width="stretch",

        config={

            "displaylogo": False,

            "scrollZoom": True

        }

    )


# ==========================================================
# Measurements
# ==========================================================

def show_measurements(
    history,
    mode,
    duration=None
):

    st.header("Measurements")

    if not history:
        return

    df = pd.DataFrame(history)

    if mode == "Offline":

        df["x"] = df["simulation_time"]

    else:

        df["x"] = pd.to_datetime(
            df["timestamp"]
        )

    col1, col2 = st.columns(2)

    with col1:

        plot_chart(

            df=df,

            x_column="x",

            y_column="rpm",

            title="Speed",

            unit="rpm",

            mode=mode,

            duration=duration,

            padding=10

        )

        plot_chart(

            df=df,

            x_column="x",

            y_column="torque",

            title="Torque",

            unit="Nm",

            mode=mode,

            duration=duration,

            padding=1

        )

    with col2:

        plot_chart(

            df=df,

            x_column="x",

            y_column="current",

            title="Current",

            unit="A",

            mode=mode,

            duration=duration,

            padding=0.5

        )

        plot_chart(

            df=df,

            x_column="x",

            y_column="power",

            title="Power",

            unit="kW",

            mode=mode,

            duration=duration,

            padding=0.2

        )


# ==========================================================
# Digital Twin Prediction
# ==========================================================

def show_prediction(
    history,
    mode,
    duration=None
):

    st.header("Digital Twin Prediction")

    if not history:
        return

    df = pd.DataFrame(history)

    if mode == "Offline":

        df["x"] = df["simulation_time"]

    else:

        df["x"] = pd.to_datetime(
            df["timestamp"]
        )

    col1, col2 = st.columns(2)

    with col1:

        plot_chart(

            df=df,

            x_column="x",

            y_column="rpm",

            twin_column="twin_rpm",

            title="Speed Prediction",

            unit="rpm",

            mode=mode,

            duration=duration,

            padding=10

        )

        plot_chart(

            df=df,

            x_column="x",

            y_column="torque",

            twin_column="twin_torque",

            title="Torque Prediction",

            unit="Nm",

            mode=mode,

            duration=duration,

            padding=1

        )

    with col2:

        plot_chart(

            df=df,

            x_column="x",

            y_column="current",

            twin_column="twin_current",

            title="Current Prediction",

            unit="A",

            mode=mode,

            duration=duration,

            padding=0.5

        )

        plot_chart(

            df=df,

            x_column="x",

            y_column="power",

            twin_column="twin_power",

            title="Power Prediction",

            unit="kW",

            mode=mode,

            duration=duration,

            padding=0.2

        )


# ==========================================================
# Residual Analysis
# ==========================================================

def show_residuals(
    history,
    mode,
    duration=None
):

    st.header("Residual Analysis")

    if not history:
        return

    df = pd.DataFrame(history)

    if mode == "Offline":

        df["x"] = df["simulation_time"]

    else:

        df["x"] = pd.to_datetime(
            df["timestamp"]
        )

    col1, col2 = st.columns(2)

    with col1:

        plot_chart(

            df=df,

            x_column="x",

            y_column="rpm_error",

            title="Speed Residual",

            unit="rpm",

            mode=mode,

            duration=duration,

            padding=0.5

        )

        plot_chart(

            df=df,

            x_column="x",

            y_column="torque_error",

            title="Torque Residual",

            unit="Nm",

            mode=mode,

            duration=duration,

            padding=0.2

        )

    with col2:

        plot_chart(

            df=df,

            x_column="x",

            y_column="current_error",

            title="Current Residual",

            unit="A",

            mode=mode,

            duration=duration,

            padding=0.1

        )

        plot_chart(

            df=df,

            x_column="x",

            y_column="power_error",

            title="Power Residual",

            unit="kW",

            mode=mode,

            duration=duration,

            padding=0.05

        )