# Copyright © 2026 Danwen Mao & Codex. All rights reserved.
import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st

st.set_page_config(page_title="GeoChem 投图工具", layout="wide")
st.title("地球化学投图（CSV）")
st.caption("上传 CSV 后，自定义横纵坐标、多列筛选与多维分类，再导出图片。")

uploaded_file = st.file_uploader("上传 CSV 文件", type=["csv"])

if uploaded_file is None:
    st.info("请先上传 CSV 文件。上传后会显示交互式设置面板。")
    st.stop()

try:
    df = pd.read_csv(uploaded_file)
except Exception as exc:
    st.error(f"CSV 读取失败：{exc}")
    st.stop()

if df.empty:
    st.warning("CSV 文件为空，无法绘图。")
    st.stop()

columns = df.columns.tolist()
numeric_columns = df.select_dtypes(include="number").columns.tolist()

if len(numeric_columns) < 2:
    st.error("至少需要两列数值列用于横纵坐标绘图。")
    st.stop()

filter_configs = []
with st.sidebar:
    st.header("绘图设置")

    x_col = st.selectbox("横坐标（X）", options=numeric_columns, index=0)
    y_col = st.selectbox("纵坐标（Y）", options=numeric_columns, index=1 if len(numeric_columns) > 1 else 0)

    st.subheader("多列筛选")
    filter_count = st.number_input("筛选列数量", min_value=0, max_value=min(8, len(columns)), value=0, step=1)

    chosen_filter_cols = []
    for i in range(int(filter_count)):
        available_cols = [c for c in columns if c not in chosen_filter_cols]
        filter_col = st.selectbox(f"筛选列 {i + 1}", options=available_cols, key=f"filter_col_{i}")
        chosen_filter_cols.append(filter_col)

        raw_values = sorted(df[filter_col].dropna().astype(str).unique().tolist())
        selected_values = st.multiselect(
            f"{filter_col} 保留取值",
            options=raw_values,
            default=raw_values,
            key=f"filter_vals_{i}",
        )
        filter_configs.append((filter_col, selected_values))

    st.subheader("多维分类")
    class_count = st.number_input("分类列数量", min_value=0, max_value=min(3, len(columns)), value=0, step=1)

    chosen_class_cols = []
    for i in range(int(class_count)):
        available_cols = [c for c in columns if c not in chosen_class_cols]
        class_col = st.selectbox(f"分类列 {i + 1}", options=available_cols, key=f"class_col_{i}")
        chosen_class_cols.append(class_col)

plot_df = df.copy()
for filter_col, selected_values in filter_configs:
    if len(selected_values) == 0:
        plot_df = plot_df.iloc[0:0]
        break
    plot_df = plot_df[plot_df[filter_col].astype(str).isin(selected_values)]

if plot_df.empty:
    st.warning("当前筛选条件下没有数据。请调整筛选条件。")
    st.stop()

st.success(f"当前满足条件并绘制的点数：{len(plot_df)}")

hover_columns = [
    c
    for c in ["Sample", "country", "Location1", "Location2", "Group", "Type", "Sub type"]
    if c in plot_df.columns
]

plot_kwargs = {
    "data_frame": plot_df,
    "x": x_col,
    "y": y_col,
    "hover_data": hover_columns,
    "title": f"{y_col} vs {x_col}",
}

legend_parts = []
if len(chosen_class_cols) >= 1:
    plot_kwargs["color"] = chosen_class_cols[0]
    legend_parts.append(f"颜色: {chosen_class_cols[0]}")
if len(chosen_class_cols) >= 2:
    plot_kwargs["symbol"] = chosen_class_cols[1]
    legend_parts.append(f"形状: {chosen_class_cols[1]}")
if len(chosen_class_cols) >= 3:
    size_col = chosen_class_cols[2]
    size_series = pd.to_numeric(plot_df[size_col], errors="coerce")
    if size_series.notna().sum() == 0:
        coded = plot_df[size_col].astype(str)
        code_map = {value: idx + 1 for idx, value in enumerate(sorted(coded.unique()))}
        size_series = coded.map(code_map)
    plot_df = plot_df.copy()
    plot_df["__size_mapped__"] = size_series.fillna(size_series.median() if size_series.notna().sum() else 1)
    plot_kwargs["data_frame"] = plot_df
    plot_kwargs["size"] = "__size_mapped__"
    plot_kwargs["size_max"] = 18
    legend_parts.append(f"大小: {size_col}")

fig = px.scatter(**plot_kwargs)
fig.update_layout(legend_title_text="; ".join(legend_parts) if legend_parts else "")

st.plotly_chart(fig, use_container_width=True)

st.subheader("导出图片")
image_format = st.selectbox("图片格式", ["png", "svg", "pdf"], index=0)

try:
    image_bytes = pio.to_image(fig, format=image_format, scale=2)
    st.download_button(
        label=f"保存当前投图为 .{image_format}",
        data=image_bytes,
        file_name=f"geochem_plot.{image_format}",
        mime=f"image/{image_format}" if image_format in ["png", "svg"] else "application/pdf",
    )
except Exception as exc:
    st.error(
        "图片导出失败，请确认已安装 Kaleido（`pip install kaleido`）。"
        f"\n\n错误信息：{exc}"
    )
