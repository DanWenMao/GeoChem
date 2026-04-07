import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="GeoChem 1:1 Plot", layout="wide")
st.title("1:1 图绘制工具（CSV）")
st.caption("支持多维筛选、颜色/形状双分类，并对第 2/3/4 象限点自动标灰。")

uploaded_file = st.file_uploader("上传 CSV 文件", type=["csv"])
if uploaded_file is None:
    st.info("请先上传 CSV 文件。")
    st.stop()

try:
    df = pd.read_csv(uploaded_file)
except Exception as exc:
    st.error(f"CSV 读取失败：{exc}")
    st.stop()

if df.empty:
    st.warning("CSV 为空，无法绘图。")
    st.stop()

numeric_cols = df.select_dtypes(include="number").columns.tolist()
all_cols = df.columns.tolist()

if len(numeric_cols) < 2:
    st.error("至少需要两列数值列作为 X/Y 坐标。")
    st.stop()


def build_group_label(data: pd.DataFrame, cols: list[str], fallback: str) -> pd.Series:
    if not cols:
        return pd.Series([fallback] * len(data), index=data.index)
    return data[cols].astype(str).fillna("NA").agg(" | ".join, axis=1)


with st.sidebar:
    st.header("参数设置")

    x_col = st.selectbox("X 轴列", numeric_cols, index=0)
    y_col = st.selectbox("Y 轴列", numeric_cols, index=min(1, len(numeric_cols) - 1))

    st.subheader("数据筛选")
    filter_count = st.number_input(
        "筛选维度数量",
        min_value=0,
        max_value=min(8, len(all_cols)),
        value=0,
        step=1,
    )

    chosen_filter_cols: list[str] = []
    filter_configs: list[tuple[str, list[str]]] = []

    for i in range(int(filter_count)):
        candidate_cols = [c for c in all_cols if c not in chosen_filter_cols]
        filter_col = st.selectbox(f"筛选列 {i + 1}", candidate_cols, key=f"filter_col_{i}")
        chosen_filter_cols.append(filter_col)

        options = sorted(df[filter_col].dropna().astype(str).unique().tolist())
        selected = st.multiselect(
            f"{filter_col} 保留值",
            options=options,
            default=options,
            key=f"filter_value_{i}",
        )
        filter_configs.append((filter_col, selected))

    st.subheader("多维分类")
    color_dims = st.multiselect("颜色分类维度（可多选）", options=all_cols, default=[])
    shape_candidates = [c for c in all_cols if c not in color_dims]
    shape_dims = st.multiselect("形状分类维度（可多选）", options=shape_candidates, default=[])

plot_df = df.copy()
for filter_col, selected_values in filter_configs:
    if not selected_values:
        plot_df = plot_df.iloc[0:0]
        break
    plot_df = plot_df[plot_df[filter_col].astype(str).isin(selected_values)]

plot_df = plot_df.dropna(subset=[x_col, y_col]).copy()

if plot_df.empty:
    st.warning("当前筛选下无可绘制数据。")
    st.stop()

plot_df["__color_group__"] = build_group_label(plot_df, color_dims, "默认颜色")
plot_df["__shape_group__"] = build_group_label(plot_df, shape_dims, "默认形状")

# 第 2/3/4 象限（x<0 或 y<0）标灰
plot_df["__is_gray__"] = (plot_df[x_col] < 0) | (plot_df[y_col] < 0)

shape_order = sorted(plot_df["__shape_group__"].unique().tolist())
symbol_pool = [
    "circle",
    "square",
    "diamond",
    "cross",
    "x",
    "triangle-up",
    "triangle-down",
    "triangle-left",
    "triangle-right",
    "pentagon",
    "hexagon",
    "star",
]
symbol_map = {name: symbol_pool[i % len(symbol_pool)] for i, name in enumerate(shape_order)}

color_order = sorted(plot_df["__color_group__"].unique().tolist())
palette = [
    "#1f77b4",
    "#ff7f0e",
    "#2ca02c",
    "#d62728",
    "#9467bd",
    "#8c564b",
    "#e377c2",
    "#7f7f7f",
    "#bcbd22",
    "#17becf",
]
color_map = {name: palette[i % len(palette)] for i, name in enumerate(color_order)}

fig = go.Figure()

for color_group in color_order:
    for shape_group in shape_order:
        subset = plot_df[
            (plot_df["__color_group__"] == color_group)
            & (plot_df["__shape_group__"] == shape_group)
        ]
        if subset.empty:
            continue

        normal_data = subset[~subset["__is_gray__"]]
        gray_data = subset[subset["__is_gray__"]]

        if not normal_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=normal_data[x_col],
                    y=normal_data[y_col],
                    mode="markers",
                    marker={
                        "size": 9,
                        "color": color_map[color_group],
                        "symbol": symbol_map[shape_group],
                        "line": {"width": 0.5, "color": "#222"},
                    },
                    name=f"颜色: {color_group} | 形状: {shape_group}",
                    legendgroup=f"{color_group}|{shape_group}",
                    showlegend=True,
                    customdata=normal_data[["__color_group__", "__shape_group__"]],
                    hovertemplate=(
                        f"{x_col}: %{{x}}<br>{y_col}: %{{y}}<br>"
                        "颜色类: %{customdata[0]}<br>"
                        "形状类: %{customdata[1]}<extra></extra>"
                    ),
                )
            )

        if not gray_data.empty:
            fig.add_trace(
                go.Scatter(
                    x=gray_data[x_col],
                    y=gray_data[y_col],
                    mode="markers",
                    marker={
                        "size": 9,
                        "color": "#b3b3b3",
                        "symbol": symbol_map[shape_group],
                        "line": {"width": 0.5, "color": "#666"},
                    },
                    name=f"灰点(2/3/4象限) | 形状: {shape_group}",
                    legendgroup=f"gray|{shape_group}",
                    showlegend=True,
                    customdata=gray_data[["__color_group__", "__shape_group__"]],
                    hovertemplate=(
                        f"{x_col}: %{{x}}<br>{y_col}: %{{y}}<br>"
                        "颜色类: %{customdata[0]}<br>"
                        "形状类: %{customdata[1]}<br>"
                        "状态: 灰点（x<0 或 y<0）<extra></extra>"
                    ),
                )
            )

x_min, x_max = plot_df[x_col].min(), plot_df[x_col].max()
y_min, y_max = plot_df[y_col].min(), plot_df[y_col].max()
overall_min = min(x_min, y_min)
overall_max = max(x_max, y_max)

if math.isclose(overall_min, overall_max):
    overall_min -= 1
    overall_max += 1

span = overall_max - overall_min
padding = span * 0.05
axis_min = overall_min - padding
axis_max = overall_max + padding

fig.add_trace(
    go.Scatter(
        x=[axis_min, axis_max],
        y=[axis_min, axis_max],
        mode="lines",
        line={"color": "#111", "dash": "dash"},
        name="1:1 参考线",
        hoverinfo="skip",
    )
)

fig.update_layout(
    title=f"1:1 Plot: {y_col} vs {x_col}",
    xaxis={"title": x_col, "range": [axis_min, axis_max]},
    yaxis={
        "title": y_col,
        "range": [axis_min, axis_max],
        "scaleanchor": "x",
        "scaleratio": 1,
    },
    width=850,
    height=850,
    legend={"orientation": "v", "x": 1.02, "y": 1, "xanchor": "left"},
)

st.success(f"当前绘制点数：{len(plot_df)}")
st.plotly_chart(fig, use_container_width=False)

st.dataframe(plot_df.head(200), use_container_width=True)
