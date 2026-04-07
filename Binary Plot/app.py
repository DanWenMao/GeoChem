import pandas as pd
import plotly.express as px
import plotly.io as pio
import streamlit as st

st.set_page_config(page_title="GeoChem 投图工具", layout="wide")
st.title("地球化学投图（CSV）")
st.caption("上传 CSV 后，可对原始列做四则运算，再进行多列筛选/分类并导出图片。")

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


def build_axis_series(axis_name: str, data: pd.DataFrame, number_cols: list[str]) -> tuple[pd.Series, str]:
    mode = st.radio(
        f"{axis_name} 数据来源",
        options=["原始列", "四则运算"],
        horizontal=True,
        key=f"{axis_name}_mode",
    )

    if mode == "原始列":
        col = st.selectbox(f"{axis_name} 列", options=number_cols, key=f"{axis_name}_raw_col")
        return pd.to_numeric(data[col], errors="coerce"), col
    
    left_mode = st.radio(
        f"{axis_name} 左操作数类型",
        options=["列", "常数"],
        horizontal=True,
        key=f"{axis_name}_left_mode",
    )

    if left_mode == "列":
        left_col = st.selectbox(f"{axis_name} 左操作数列", options=number_cols, key=f"{axis_name}_left_col")
        left_series = pd.to_numeric(data[left_col], errors="coerce")
        left_label = left_col
    else:
        left_const = st.number_input(f"{axis_name} 左操作数常数", value=1.0, key=f"{axis_name}_left_const")
        left_series = pd.Series([left_const] * len(data), index=data.index, dtype="float64")
        left_label = str(left_const)

    # left_col = st.selectbox(f"{axis_name} 左操作数列", options=number_cols, key=f"{axis_name}_left")
    operator = st.selectbox(f"{axis_name} 运算符", options=["+", "-", "*", "/"], key=f"{axis_name}_op")

    right_mode = st.radio(
        f"{axis_name} 右操作数类型",
        options=["列", "常数"],
        horizontal=True,
        key=f"{axis_name}_right_mode",
    )

    # left_series = pd.to_numeric(data[left_col], errors="coerce")

    if right_mode == "列":
        right_col = st.selectbox(f"{axis_name} 右操作数列", options=number_cols, key=f"{axis_name}_right_col")
        right_series = pd.to_numeric(data[right_col], errors="coerce")
        right_label = right_col
    else:
        right_const = st.number_input(f"{axis_name} 右操作数常数", value=1.0, key=f"{axis_name}_right_const")
        right_series = pd.Series([right_const] * len(data), index=data.index, dtype="float64")
        right_label = str(right_const)

    if operator == "+":
        result = left_series + right_series
    elif operator == "-":
        result = left_series - right_series
    elif operator == "*":
        result = left_series * right_series
    else:
        safe_denominator = right_series.mask(right_series == 0)
        result = left_series / safe_denominator

    label = f"({left_label} {operator} {right_label})"
    return result, label


filter_configs = []
with st.sidebar:
    st.header("绘图设置")

    st.subheader("横纵坐标")
    x_series, x_label = build_axis_series("X", df, numeric_columns)
    y_series, y_label = build_axis_series("Y", df, numeric_columns)

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
plot_df["__x__"] = x_series
plot_df["__y__"] = y_series

for filter_col, selected_values in filter_configs:
    if len(selected_values) == 0:
        plot_df = plot_df.iloc[0:0]
        break
    plot_df = plot_df[plot_df[filter_col].astype(str).isin(selected_values)]

plot_df = plot_df.dropna(subset=["__x__", "__y__"])

if plot_df.empty:
    st.warning("当前筛选或运算结果下没有可绘图数据。请调整条件。")
    st.stop()

st.success(f"当前满足条件并绘制的点数：{len(plot_df)}")

hover_columns = [
    c
    for c in ["Sample", "country", "Location1", "Location2", "Group", "Type", "Sub type"]
    if c in plot_df.columns
]

plot_kwargs = {
    "data_frame": plot_df,
    "x": "__x__",
    "y": "__y__",
    "labels": {"__x__": x_label, "__y__": y_label},
    "hover_data": hover_columns,
    "title": f"{y_label} vs {x_label}",
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

fig = px.scatter(**plot_kwargs,color_discrete_sequence=px.colors.qualitative.Plotly)
legend_title = "; ".join(legend_parts) if legend_parts else ""
fig.update_layout(
    legend=dict(
        title_text=legend_title,
        orientation="v",
        x=0.95,
        y=0.95,
        xanchor="left",
        yanchor="top",
        font_size=10,
    ),
    margin=dict(r=150)
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("导出图片")
image_format = st.selectbox("图片格式", ["png", "svg", "pdf"], index=0)

try:
    image_bytes = pio.to_image(fig, format=image_format, scale=2)
    st.download_button(
        label=f"保存当前投图为 .{image_format}",
        data=image_bytes,
        file_name=f"{x_label}_{y_label}.{image_format}",
        mime=f"image/{image_format}" if image_format in ["png", "svg"] else "application/pdf",
    )
except Exception as exc:
    st.error(
        "图片导出失败，请确认已安装 Kaleido（`pip install kaleido`）。"
        f"\n\n错误信息：{exc}"
    )
