import streamlit as st
import pandas as pd
import altair as alt

# 페이지 설정
st.set_page_config(page_title="동성혼 시나리오 감도 분석", layout="centered")

# ---- 헤더 ----
st.title("🏳️‍🌈 동성혼 법제화 시나리오 감도 분석")
st.markdown(
    """
    이 대시보드는 인구 가정(레즈비언/바이 비율, 이동률, 출산강도)에 따라 
    **동성혼 법제화가 출생률에 미치는 영향을 시각화합니다.** 
    슬라이더를 조정해 파라미터별 변화를 확인하세요.
    """
    #위쪽은 현재 b=1 기준의 시나리오 비교,아래는 b값 변화(0.5–2.0)에 따른 추세를 보여줍니다.

)

# ---- 기본 변수 ----
b = 1.0  # 커플당 평균 출생

# ---- 파라미터 입력 ----
st.markdown("---")
st.subheader("⚙️ 시나리오 가정 설정")

col1, col2 = st.columns(2)
with col1:
    L = st.slider("레즈비언 비율 (L)", 0.0, 0.10, 0.05, 0.005)
    B = st.slider("바이 여성 비율 (B)", 0.0, 0.10, 0.10, 0.005)
with col2:
    r = st.slider("여여 커플 출산 강도 (r, 남녀 대비)", 0.0, 2.0, 1.0, 0.05)
    sf = st.slider("바이 여성의 동성 결혼 이동률 (s_f)", 0.0, 1.0, 0.5, 0.05)

# ---- b 시뮬레이션 데이터 ----
b_values = [round(x, 2) for x in list(pd.Series(range(5, 21)) / 10)]  # 0.5~2.0
data = []
for b in b_values:
    A_abs = (1 - L) * b
    B_abs = ((1 - L - B * sf) * b) + (((L + B * sf) / 2) * (r * b))
    diff = B_abs - A_abs
    data.append({"b값": b, "시나리오": "A (불허)", "출생 총량": A_abs})
    data.append({"b값": b, "시나리오": "B (허용)", "출생 총량": B_abs})
df = pd.DataFrame(data)


# ---- 현재 b=1 기준 계산 ----
b = 1.0
A_abs = (1 - L) * b
B_abs = ((1 - L - B * sf) * b) + (((L + B * sf) / 2) * (r * b))
diff_abs = B_abs - A_abs
diff_rate = (diff_abs / A_abs) * 100

# ---- 그래프 1: 바 그래프 (b=1 기준) ----
chart_df = pd.DataFrame({
    "시나리오": ["A (불허)", "B (허용)"],
    "출생 총량": [A_abs, B_abs]
})

bar = (
    alt.Chart(chart_df)
    .mark_bar()
    .encode(
        x=alt.X("시나리오:N", title=None),
        y=alt.Y("출생 총량:Q", title="출생 총량",
                scale=alt.Scale(domain=[0, max(A_abs, B_abs) * 1.1])),
        color=alt.condition(
            alt.datum.시나리오 == "A (불허)",
            alt.value("#7CB9E8"),  # 파랑
            alt.value("#FF8B8B"),  # 빨강
        ),
    )
    .properties(width=500, height=350)
)

text = bar.mark_text(
    align="center", baseline="bottom", dy=-5, size=14
).encode(text=alt.Text("출생 총량:Q", format=".3f"))

# ---- 그래프 2: 선 그래프 (b 변화에 따른 추세) ----
line = (
    alt.Chart(df)
    .mark_line(point=True, strokeWidth=3)
    .encode(
        x=alt.X("b값:Q", title="커플당 평균 출산 (b)"),
        y=alt.Y("출생 총량:Q", title="절대 출생 총량"),
        color=alt.Color(
            "시나리오:N",
            scale=alt.Scale(domain=["A (불허)", "B (허용)"], range=["#7CB9E8", "#FF8B8B"])
        ),
        tooltip=["b값", "시나리오", alt.Tooltip("출생 총량:Q", format=".3f")],
    )
    .properties(width=500, height=300) # , title="b값 변화에 따른 절대 출생 총량 추세"
)

# ---- 그래프 1: 현재 b=1 기준 ----
st.markdown("### b=1 기준 절대 출생 총량 비교")
st.altair_chart(bar + text, use_container_width=True)

# ---- 요약 카드 ----
colA, colB, colD = st.columns(3)
with colA:
    st.metric(label="A 시나리오 (불허)", value=f"{A_abs:.3f}")
with colB:
    st.metric(label="B 시나리오 (허용)", value=f"{B_abs:.3f}")
with colD:
    st.metric(label="변화율", value=f"{diff_rate:+.2f} %", delta_color="inverse")

# ---- 설명 ----
# st.markdown("---")
st.caption(
    f"""
    **가정 요약:**  
    레즈비언 비율={L:.3%}, 바이 비율={B:.3%}, 
    이동률(s_f)={sf:.1%}, 출산강도(r)={r:.2f}.  
    커플당 평균 출생(b)=1.0 기준으로 계산.
    """
)

# ---- 그래프 2: b값 변화 추세 ----
st.markdown("---")
st.markdown("### b값 변화에 따른 절대 출생 총량")
st.altair_chart(line, use_container_width=True)
