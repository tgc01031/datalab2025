import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import platform
import matplotlib.font_manager as fm
import matplotlib
import matplotlib.ticker as ticker
from matplotlib.ticker import MaxNLocator
import numpy as np
import os
import math
from PIL import Image


font_path = os.path.join("fonts", "NotoSansKR-Regular.ttf")
if os.path.exists(font_path):
    matplotlib.font_manager.fontManager.addfont(font_path)
    font_prop = fm.FontProperties(fname=font_path)
    matplotlib.rcParams["font.family"] = font_prop.get_name()
else:
    if platform.system() == "Darwin":
        matplotlib.rcParams["font.family"] = "AppleGothic"
    elif platform.system() == "Windows":
        matplotlib.rcParams["font.family"] = "Malgun Gothic"
    else:
        matplotlib.rcParams["font.family"] = "DejaVu Sans"
    font_prop = None

matplotlib.rcParams["axes.unicode_minus"] = False

st.set_page_config(
    page_title="데이터분석 (4) 예측 실행",
    page_icon="📊",
    layout="centered"
)

hide_default_sidebar = """
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
"""
st.markdown(hide_default_sidebar, unsafe_allow_html=True)


banner = Image.open("images/(11)title_run_prediction.png")  
st.image(banner, use_container_width=True)
with st.sidebar:
    st.page_link("app.py", label="HOME", icon="🏠")
    st.markdown("---")

    st.markdown("## 📖 개념 익히기")
    st.page_link("pages/1_경사하강법_(1)_최적화란.py", label="(1) 최적화란?")
    st.page_link("pages/2_경사하강법_(2)_학습률이란.py", label="(2) 학습률이란?")
    st.page_link("pages/3_경사하강법_(3)_반복횟수란.py", label="(3) 반복횟수란?")

    st.markdown("---")
    st.markdown("## 💻 시뮬레이션")
    st.page_link("pages/4_시뮬레이션_(1)_학습률_실험.py", label="(1) 학습률 실험")
    st.page_link("pages/5_시뮬레이션_(2)_반복횟수_실험.py", label="(2) 반복횟수 실험")

    st.markdown("---")
    st.markdown("## 🔎 예제")
    st.page_link("pages/6_example.py", label="Q. 나 혼자 산다! 다 혼자 산다?")

    st.markdown("---")
    st.markdown("## 📊 데이터분석")
    st.page_link("pages/7_데이터분석_(1)_기본정보입력.py", label="(1) 기본 정보 입력")
    st.page_link("pages/8_데이터분석_(2)_분석주제선택.py", label="(2) 분석 주제 선택")
    st.page_link("pages/9_데이터분석_(3)_데이터입력.py", label="(3) 데이터 입력")
    st.page_link("pages/10_데이터분석_(4)_예측실행.py", label="(4) 예측 실행")
    st.page_link("pages/11_데이터분석_(5)_요약결과.py", label="(5) 요약 결과")

if "x_values" not in st.session_state or "y_values" not in st.session_state:
    st.warning("이전 단계에서 데이터를 먼저 입력해 주세요.")
    st.stop()

x_raw = st.session_state.x_values
y_raw = st.session_state.y_values
x_label = st.session_state.get("x_label", "x")
y_label = st.session_state.get("y_label", "y")

if "lr_value" not in st.session_state:
    st.session_state.lr_value = 0.0001
if "epochs_value" not in st.session_state:
    st.session_state.epochs_value = 1000
if "predict_requested" not in st.session_state:
    st.session_state.predict_requested = False
if "attempt_count" not in st.session_state:  
    st.session_state.attempt_count = 0

learning_rate = st.session_state.lr_value
epoch = st.session_state.epochs_value

st.markdown("""
    <style>
    .custom-radio-label h4 {
        margin-bottom: 0.2rem;
    }
    div[data-testid="stRadio"] > div {
        margin-top: -10px;
    }
    </style>
""", unsafe_allow_html=True)

with st.container():
    st.markdown("### 📈 함수 형태를 선택하세요")
    func_type = st.radio(
        "", ["1차 함수", "2차 함수"],
        horizontal=True,
        label_visibility="collapsed"
    )

st.markdown("### 🔧 학습률 조절")
lr_col1, lr_col2, lr_col3, lr_col4 = st.columns([1, 5, 1, 4])
with lr_col1:
    if st.button("➖", key="lr_minus"):
        st.session_state.lr_value = max(0.0001, st.session_state.lr_value - 0.0001)
with lr_col2:
    new_lr = st.slider("학습률", 0.0001, 0.01, st.session_state.lr_value,
                       step=0.0002, format="%.4f", label_visibility="collapsed")
    st.session_state.lr_value = new_lr
with lr_col3:
    if st.button("➕", key="lr_plus"):
        st.session_state.lr_value = min(0.01, st.session_state.lr_value + 0.0001)
with lr_col4:
    st.markdown(f"<b>현재 학습률: {st.session_state.lr_value:.4f}</b>", unsafe_allow_html=True)

st.markdown("### 🔁 반복 횟수 조절")
ep_col1, ep_col2, ep_col3, ep_col4 = st.columns([1, 5, 1, 4])
with ep_col1:
    if st.button("➖", key="ep_minus"):
        st.session_state.epochs_value = max(100, st.session_state.epochs_value - 100)
with ep_col2:
    new_epochs = st.slider("반복 횟수", 100, 7000, st.session_state.epochs_value,
                           step=100, label_visibility="collapsed")
    st.session_state.epochs_value = new_epochs
with ep_col3:
    if st.button("➕", key="ep_plus"):
        st.session_state.epochs_value = min(7000, st.session_state.epochs_value + 100)
with ep_col4:
    st.markdown(f"<b>현재 반복 횟수: {st.session_state.epochs_value}회</b>", unsafe_allow_html=True)

if st.button("📈 예측 실행"):
    x_arr = np.array(x_raw)
    y_arr = np.array(y_raw)
    if len(x_arr) < 2 or np.std(x_arr) == 0 or np.any(np.isnan(x_arr)) or np.any(np.isnan(y_arr)):
        st.session_state.predict_requested = False
        st.error("⚠️ 예측할 수 없습니다. 입력 데이터가 너무 적거나, 모든 X값이 같거나, 결츠치가 포함되어 있습니다.")
        st.stop()

    st.session_state.predict_requested = True
    st.session_state.history = []
    st.session_state.attempt_count += 1  

if st.session_state.predict_requested:
    st.divider() 
    st.markdown("### 📊 예측 결과")
    x = np.array(x_raw)
    y = np.array(y_raw)
    x_plot = np.linspace(x.min(), x.max(), 100)

    if func_type == "1차 함수":
        x_mean = x.mean()
        x_std = x.std()
        x_scaled = (x - x_mean) / x_std
        x_plot_scaled = (x_plot - x_mean) / x_std

        m, b = 0.0, 0.0
        for _ in range(epoch):
            y_pred = m * x_scaled + b
            error = y_pred - y
            m -= learning_rate * (2 / len(x)) * (error @ x_scaled)
            b -= learning_rate * (2 / len(x)) * error.sum()

            y_pred = m * x_plot_scaled + b

            m_real = m / x_std
            b_real = -m * x_mean / x_std + b
            equation = f"y = {m_real:.4f}x {'+' if b_real >= 0 else '-'} {abs(b_real):.4f}"


    else:
        x_mean = x.mean()
        x_std = x.std()
        x_scaled = (x - x_mean) / x_std
        x_input_scaled = (x_plot - x_mean) / x_std
        a = b = c = 0.0
        for _ in range(epoch):
            y_pred = a * x_scaled**2 + b * x_scaled + c
            error = y_pred - y
            a -= learning_rate * (2 / len(x)) * (error @ (x_scaled**2))
            b -= learning_rate * (2 / len(x)) * (error @ x_scaled)
            c -= learning_rate * (2 / len(x)) * error.sum()
        y_pred = a * x_input_scaled**2 + b * x_input_scaled + c
        a_real = a / (x_std**2)
        b_real = (-2 * a * x_mean / (x_std**2)) + (b / x_std)
        c_real = (a * x_mean**2 / (x_std**2)) - (b * x_mean / x_std) + c
        equation = f"y = {a_real:.4f}x² {'+' if b_real >= 0 else '-'} {abs(b_real):.4f}x {'+' if c_real >= 0 else '-'} {abs(c_real):.4f}"

    ss_total = np.sum((y - y.mean()) ** 2)

    if func_type == "1차 함수":
        x_scaled = (x - x.mean()) / x.std()
        y_pred_for_accuracy = m * x_scaled + b
    else:
        y_pred_for_accuracy = a * ((x - x_mean) / x_std)**2 + b * ((x - x_mean) / x_std) + c

    ss_res = np.sum((y - y_pred_for_accuracy) ** 2)
    r2 = 1 - ss_res / ss_total

    if (
        np.any(np.isnan(y_pred)) or np.any(np.isinf(y_pred)) or
        np.isnan(ss_total) or np.isnan(ss_res) or np.isnan(r2) or
        np.isinf(ss_total) or np.isinf(ss_res) or np.isinf(r2)
    ):
        st.session_state.predict_requested = False
        st.error("❌ 예측 결과가 유효하지 않습니다.\n학습률이 너무 크거나 반복 횟수가 너무 많을 수 있습니다.\n적절한 값으로 조절해 주세요.")
        st.stop()

    accuracy = round(r2 * 100, 2)
    accuracy_color = "red" if accuracy >= 90 else "gray"
    accuracy_weight = "bold" if accuracy >= 90 else "normal"
    
    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots()
        ax.scatter(x, y, color="blue", label="입력 데이터")
        ax.plot(x_plot, y_pred, color="red", label="예측선")
        ax.set_title("예측 결과")
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.legend()
        ax.xaxis.set_major_locator(MaxNLocator(nbins='auto', prune='both'))
        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter('%d'))
        fig.tight_layout()
        st.pyplot(fig)

    with col2:
        st.markdown(f"🔍 예측 시도 횟수: {st.session_state.attempt_count}회")
        st.markdown(f"🖋️ **수식**: {equation}")
        st.markdown(f"📘 **학습률**: {learning_rate}")
        st.markdown(f"🔁 **반복 횟수**: {epoch}")
        st.markdown(
            f"<div style='text-align:center; font-size:32px; font-weight:{accuracy_weight}; color:{accuracy_color};'>🎯 모델 정확도: {accuracy:.2f}%</div>",
            unsafe_allow_html=True
        )
        input_x = st.number_input("예측하고 싶은 값을 입력하세요. (예: 연도, 나이, 기온 등)", value=int(x[-1]) + 1, step=1)

        try:
            if func_type == "1차 함수":
                y_input_pred = m_real * input_x + b_real
            else:
                y_input_pred = a_real * input_x**2 + b_real * input_x + c_real

            y_min, y_max = y.min(), y.max()
            y_range = y_max - y_min
            margin = 0.5
            lower_bound = y_min - y_range * margin
            upper_bound = y_max + y_range * margin

            if accuracy < 70 and (y_input_pred < lower_bound or y_input_pred > upper_bound):
                st.warning(f"⚠️ 예측값이 입력한 데이터의 범위를 벗어났습니다: {y_input_pred:.1f}\n\n학습률이나 반복 횟수를 조정해보세요.")
            else:
                st.success(f"📌 예측값: {y_input_pred:,.1f}")
            
            entry = {
                "x_plot": x_plot,
                "y_pred": y_pred,
                "label": equation,
                "lr": learning_rate,
                "epoch": epoch,
                "predicted_value": y_input_pred,
                "input_value": input_x,
                "accuracy": accuracy, 
                "attempt_count": st.session_state.attempt_count   

            }

            if func_type == "2차 함수":
                entry["x_mean"] = x_mean
                entry["x_std"] = x_std

            st.session_state.history.append(entry)
            st.session_state.selected_model_indices = [len(st.session_state.history) - 1]


        except Exception as e:
            st.warning("⚠️ 예측값 계산 중 문제가 발생했습니다. 입력값 또는 설정을 다시 확인해주세요.")
    st.markdown("### 📘 예측 결과 해석")
    if "predict_summary" not in st.session_state:
        st.session_state.predict_summary = ""

    predict_text = st.text_area(
    label="예측 결과와 수식을 바탕으로 어떤 의미 있는 결론을 도출할 수 있었나요?",
    placeholder="예: 예측 수식에 따르면 2025년에는 약 35% 수준까지 감소할 것으로 보입니다...",
    key="predict_summary_input",
    height=150
)
    colA, colB, colC = st.columns([3, 15, 3])
    with colA:
        if st.button("⬅️ 이전", key="go_back"):
            st.switch_page("pages/9_데이터분석_(3)_데이터입력.py")
    with colC:
        if st.button("➡️ 다음", key="go_summary"):
            st.session_state["predict_summary"] = predict_text 
            st.switch_page("pages/11_데이터분석_(5)_요약결과.py")
