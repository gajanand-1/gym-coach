"""
Chart Service
-------------
All Plotly chart builders used across UI pages.
Returns plotly Figure objects — Streamlit renders them with st.plotly_chart().
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
from typing import Optional

# ---- Brand colours ----
COLOR_PRIMARY   = "#00D4FF"   # cyan accent
COLOR_SUCCESS   = "#00E676"   # green
COLOR_WARNING   = "#FFB300"   # amber
COLOR_DANGER    = "#FF5252"   # red
COLOR_BG        = "#0E1117"   # streamlit dark bg
COLOR_CARD      = "#1E2130"   # card background
COLOR_TEXT      = "#FAFAFA"


class ChartService:

    # ------------------------------------------------------------------ #
    # Weight Progress
    # ------------------------------------------------------------------ #

    @staticmethod
    def weight_progress_chart(trend_data: list, target_kg: float) -> go.Figure:
        if not trend_data:
            fig = go.Figure()
            fig.add_annotation(text="No weight data yet", showarrow=False,
                               font=dict(color=COLOR_TEXT, size=16))
            fig.update_layout(template="plotly_dark", height=300)
            return fig

        df = pd.DataFrame(trend_data)
        df["date"] = pd.to_datetime(df["date"])

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["date"], y=df["weight_kg"],
            mode="lines+markers",
            name="Weight",
            line=dict(color=COLOR_PRIMARY, width=2.5),
            marker=dict(size=7, color=COLOR_PRIMARY),
        ))

        # Target line
        fig.add_hline(
            y=target_kg, line_dash="dash",
            line_color=COLOR_SUCCESS,
            annotation_text=f"Target: {target_kg}kg",
            annotation_font_color=COLOR_SUCCESS,
        )

        # 7-day rolling average if enough data
        if len(df) >= 7:
            df["rolling"] = df["weight_kg"].rolling(7).mean()
            fig.add_trace(go.Scatter(
                x=df["date"], y=df["rolling"],
                mode="lines", name="7-day Avg",
                line=dict(color=COLOR_WARNING, width=1.5, dash="dot"),
            ))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=COLOR_CARD,
            plot_bgcolor=COLOR_CARD,
            height=350,
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis_title="Date",
            yaxis_title="Weight (kg)",
            legend=dict(orientation="h", y=1.1),
        )
        return fig

    # ------------------------------------------------------------------ #
    # Calorie / Macro Donut
    # ------------------------------------------------------------------ #

    @staticmethod
    def macro_donut(protein_g: float, carbs_g: float, fat_g: float) -> go.Figure:
        labels = ["Protein", "Carbs", "Fat"]
        values = [protein_g * 4, carbs_g * 4, fat_g * 9]  # convert to kcal
        colors = [COLOR_PRIMARY, COLOR_SUCCESS, COLOR_WARNING]

        fig = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=0.6,
            marker_colors=colors,
            textinfo="percent",
            hovertemplate="%{label}: %{value:.0f} kcal<extra></extra>",
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=COLOR_CARD,
            showlegend=True,
            height=280,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", x=0.1, y=-0.1),
        )
        return fig

    # ------------------------------------------------------------------ #
    # Weekly Calorie Bar Chart
    # ------------------------------------------------------------------ #

    @staticmethod
    def weekly_calories_chart(weekly_data: list, target_cal: float) -> go.Figure:
        if not weekly_data:
            fig = go.Figure()
            fig.update_layout(template="plotly_dark", height=300)
            return fig

        df = pd.DataFrame(weekly_data)
        df["date"] = pd.to_datetime(df["date"])
        df["day"] = df["date"].dt.strftime("%a")

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df["day"], y=df["calories"],
            name="Calories",
            marker_color=[
                COLOR_SUCCESS if c <= target_cal else COLOR_DANGER
                for c in df["calories"]
            ],
        ))
        fig.add_hline(
            y=target_cal, line_dash="dash",
            line_color=COLOR_WARNING,
            annotation_text=f"Target {target_cal:.0f}",
            annotation_font_color=COLOR_WARNING,
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=COLOR_CARD,
            plot_bgcolor=COLOR_CARD,
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis_title="Day",
            yaxis_title="kcal",
        )
        return fig

    # ------------------------------------------------------------------ #
    # Weekly Protein Bar Chart
    # ------------------------------------------------------------------ #

    @staticmethod
    def weekly_protein_chart(weekly_data: list, target_protein: float) -> go.Figure:
        if not weekly_data:
            fig = go.Figure()
            fig.update_layout(template="plotly_dark", height=300)
            return fig

        df = pd.DataFrame(weekly_data)
        df["date"] = pd.to_datetime(df["date"])
        df["day"] = df["date"].dt.strftime("%a")

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df["day"], y=df["protein"],
            name="Protein (g)",
            marker_color=COLOR_PRIMARY,
        ))
        fig.add_hline(
            y=target_protein, line_dash="dash",
            line_color=COLOR_SUCCESS,
            annotation_text=f"Target {target_protein:.0f}g",
            annotation_font_color=COLOR_SUCCESS,
        )
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=COLOR_CARD,
            plot_bgcolor=COLOR_CARD,
            height=300,
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis_title="Day",
            yaxis_title="Protein (g)",
        )
        return fig

    # ------------------------------------------------------------------ #
    # Workout Volume Chart
    # ------------------------------------------------------------------ #

    @staticmethod
    def workout_volume_chart(sessions: list) -> go.Figure:
        if not sessions:
            fig = go.Figure()
            fig.add_annotation(text="No workout data yet", showarrow=False,
                               font=dict(color=COLOR_TEXT, size=16))
            fig.update_layout(template="plotly_dark", height=300)
            return fig

        df = pd.DataFrame([
            {"date": s["date"], "volume": s["volume_kg"], "session": s["session_name"]}
            for s in sessions
        ])
        df["date"] = pd.to_datetime(df["date"])

        fig = go.Figure(go.Bar(
            x=df["date"], y=df["volume"],
            text=df["session"],
            textposition="outside",
            marker_color=COLOR_PRIMARY,
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=COLOR_CARD,
            plot_bgcolor=COLOR_CARD,
            height=320,
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis_title="Date",
            yaxis_title="Total Volume (kg)",
        )
        return fig

    # ------------------------------------------------------------------ #
    # Water intake gauge
    # ------------------------------------------------------------------ #

    @staticmethod
    def water_gauge(consumed: float, target: float) -> go.Figure:
        pct = min(consumed / target * 100, 100) if target else 0
        color = COLOR_SUCCESS if pct >= 80 else (COLOR_WARNING if pct >= 50 else COLOR_DANGER)

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=consumed,
            delta={"reference": target, "valueformat": ".1f"},
            gauge={
                "axis": {"range": [0, target], "tickformat": ".1f"},
                "bar": {"color": color},
                "bgcolor": COLOR_CARD,
                "steps": [
                    {"range": [0, target * 0.5], "color": "#1a1f2e"},
                    {"range": [target * 0.5, target * 0.8], "color": "#1f2a3a"},
                    {"range": [target * 0.8, target], "color": "#1a2e2a"},
                ],
                "threshold": {
                    "line": {"color": COLOR_SUCCESS, "width": 3},
                    "thickness": 0.75,
                    "value": target,
                },
            },
            title={"text": "Water (L)", "font": {"color": COLOR_TEXT}},
            number={"suffix": "L", "font": {"color": COLOR_TEXT}},
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=COLOR_CARD,
            height=260,
            margin=dict(l=20, r=20, t=30, b=10),
        )
        return fig

    # ------------------------------------------------------------------ #
    # Exercise history (progressive overload view)
    # ------------------------------------------------------------------ #

    @staticmethod
    def exercise_history_chart(history: list, exercise_name: str) -> go.Figure:
        if not history:
            fig = go.Figure()
            fig.add_annotation(text="No history yet", showarrow=False,
                               font=dict(color=COLOR_TEXT, size=16))
            fig.update_layout(template="plotly_dark", height=280)
            return fig

        df = pd.DataFrame(history)
        df["date"] = pd.to_datetime(df["date"])

        # Max weight per session date
        max_per_date = df.groupby("date")["weight_kg"].max().reset_index()

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=max_per_date["date"], y=max_per_date["weight_kg"],
            mode="lines+markers",
            name="Max Weight",
            line=dict(color=COLOR_PRIMARY, width=2.5),
            marker=dict(size=8),
        ))
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=COLOR_CARD,
            plot_bgcolor=COLOR_CARD,
            height=280,
            title=dict(text=exercise_name, font=dict(color=COLOR_TEXT)),
            margin=dict(l=10, r=10, t=40, b=10),
            xaxis_title="Date",
            yaxis_title="Weight (kg)",
        )
        return fig

    # ------------------------------------------------------------------ #
    # Sleep trend
    # ------------------------------------------------------------------ #

    @staticmethod
    def sleep_trend_chart(sleep_data: list) -> go.Figure:
        if not sleep_data:
            fig = go.Figure()
            fig.update_layout(template="plotly_dark", height=260)
            return fig

        df = pd.DataFrame(sleep_data)
        df["date"] = pd.to_datetime(df["date"])
        colors = [COLOR_SUCCESS if h >= 7 else (COLOR_WARNING if h >= 6 else COLOR_DANGER)
                  for h in df["hours"]]

        fig = go.Figure(go.Bar(
            x=df["date"], y=df["hours"],
            marker_color=colors,
            name="Sleep Hours",
        ))
        fig.add_hline(y=7, line_dash="dash", line_color=COLOR_SUCCESS,
                      annotation_text="7h target", annotation_font_color=COLOR_SUCCESS)
        fig.add_hline(y=8, line_dash="dot", line_color=COLOR_WARNING,
                      annotation_text="8h ideal", annotation_font_color=COLOR_WARNING)
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor=COLOR_CARD,
            plot_bgcolor=COLOR_CARD,
            height=260,
            margin=dict(l=10, r=10, t=30, b=10),
            xaxis_title="Date",
            yaxis_title="Hours",
        )
        return fig
