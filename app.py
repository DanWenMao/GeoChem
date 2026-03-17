# Copyright © 2026 Danwen Mao & Codex. All rights reserved.
import io

import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st

st.set_page_config(page_title="GeoChem 投图工具", layout="wide")
st.title("地球化学投图（CSV）")
st.caption("上传 CSV 后，自定义横纵坐标、筛选条件和分类样式，再导出图片。")

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

with st.sidebar:
    st.header("绘图设置")
    x_col = st.selectbox("横坐标（X）", options=numeric_columns, index=0)
    y_default = 1 if len(numeric_columns) > 1 else 0
    y_col = st.selectbox("纵坐标（Y）", options=numeric_columns, index=y_default)

    filter_col = st.selectbox("筛选列（可选）", options=["不筛选"] + columns, index=0)

    selected_values = None
    if filter_col != "不筛选":
        raw_values = sorted(df[filter_col].dropna().astype(str).unique().tolist())
        selected_values = st.multiselect(
            "保留以下取值",
            options=raw_values,
            default=raw_values,
        )

    category_col = st.selectbox("分类列（颜色/符号，可选）", options=["不分类"] + columns, index=0)

plot_df = df.copy()

if filter_col != "不筛选":
    if selected_values is None or len(selected_values) == 0:
        plot_df = plot_df.iloc[0:0]
    else:
        plot_df = plot_df[plot_df[filter_col].astype(str).isin(selected_values)]

if plot_df.empty:
    st.warning("当前筛选条件下没有数据。请调整筛选条件。")
    st.stop()

hover_columns = [c for c in ["Sample", "country", "Location1", "Location2", "Type", "Sub type"] if c in plot_df.columns]

plot_kwargs = {
    "data_frame": plot_df,
    "x": x_col,
    "y": y_col,
    "hover_data": hover_columns,
    "title": f"{y_col} vs {x_col}",
}

if category_col != "不分类":
    plot_kwargs["color"] = category_col
    plot_kwargs["symbol"] = category_col

fig = px.scatter(**plot_kwargs)
fig.update_layout(legend_title_text=category_col if category_col != "不分类" else "")

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
