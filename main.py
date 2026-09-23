import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="영화 데이터 그래프 도감 2 - 분포와 관계", layout="wide")

st.title("영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption(
    "최근 1년간 박스오피스 10위권에 든 영화 중, 그 기간에 개봉한 216편의 데이터를 바탕으로 만든 그래프 모음입니다."
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # genre 열에 세로막대 기호(|)로 여러 장르가 적혀 있으면 첫 번째 장르만 사용
    df["genre"] = df["genre"].astype(str).str.split("|").str[0].str.strip()

    # openDt(개봉일)는 여덟 자리 숫자 -> 날짜 형식으로 변환
    df["openDt"] = pd.to_datetime(df["openDt"].astype(str), format="%Y%m%d", errors="coerce")

    return df


df = load_data()

with st.expander("원본 데이터 미리 보기"):
    st.dataframe(df, use_container_width=True)

st.divider()

# ------------------------------------------------------------------
# 그래프 1. 장르별 영화 편수 - 도넛 그래프
# ------------------------------------------------------------------
st.header("1. 장르별 영화 편수")

genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

fig_donut = px.pie(
    genre_counts,
    names="genre",
    values="count",
    hole=0.5,
)
fig_donut.update_traces(
    textinfo="label+percent",
    hovertemplate="장르: %{label}<br>편수: %{value}편<br>비율: %{percent}<extra></extra>",
)

st.plotly_chart(fig_donut, use_container_width=True)

st.text_input("이 그래프로 알 수 있는 것", key="insight_1", placeholder="여기에 한 문장으로 적어 보세요.")

st.divider()

# ------------------------------------------------------------------
# 그래프 2. 총 관객 수 분포 - 히스토그램
# ------------------------------------------------------------------
st.header("2. 총 관객 수의 분포")

fig_hist = px.histogram(
    df,
    x="total_audi",
    nbins=30,
    labels={"total_audi": "총 관객 수"},
)
fig_hist.update_traces(
    hovertemplate="총 관객 구간: %{x}<br>영화 수: %{y}편<extra></extra>"
)
fig_hist.update_layout(yaxis_title="영화 수")

st.plotly_chart(fig_hist, use_container_width=True)

st.text_input("이 그래프로 알 수 있는 것", key="insight_2", placeholder="여기에 한 문장으로 적어 보세요.")

st.divider()

# ------------------------------------------------------------------
# 그래프 3. 장르별 10위권 유지 일수 분포 - 박스플롯
# ------------------------------------------------------------------
st.header("3. 장르별 박스오피스 10위권 유지 일수")

fig_box = px.box(
    df,
    x="genre",
    y="days_in_top10",
    labels={"genre": "장르", "days_in_top10": "10위권 유지 일수"},
)

st.plotly_chart(fig_box, use_container_width=True)

st.text_input("이 그래프로 알 수 있는 것", key="insight_3", placeholder="여기에 한 문장으로 적어 보세요.")

st.divider()

# ------------------------------------------------------------------
# 그래프 4. 개봉일 스크린수와 총 관객 수의 관계 - 산점도
# ------------------------------------------------------------------
st.header("4. 개봉일 스크린수와 총 관객 수의 관계")

fig_scatter = px.scatter(
    df,
    x="first_scrn",
    y="total_audi",
    color="genre",
    hover_name="movieNm",
    labels={"first_scrn": "개봉일 스크린수", "total_audi": "총 관객 수"},
)

st.plotly_chart(fig_scatter, use_container_width=True)

st.text_input("이 그래프로 알 수 있는 것", key="insight_4", placeholder="여기에 한 문장으로 적어 보세요.")

st.divider()

# ------------------------------------------------------------------
# 그래프 5. 주요 수치 변수 간 상관관계 - 히트맵
# ------------------------------------------------------------------
st.header("5. 주요 수치 변수 간 상관관계")

numeric_cols = ["first_scrn", "first_show", "first_week_audi", "total_audi", "days_in_top10"]
corr = df[numeric_cols].corr()

fig_heatmap = px.imshow(
    corr,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1,
    labels=dict(color="상관계수"),
)

st.plotly_chart(fig_heatmap, use_container_width=True)

st.text_input("이 그래프로 알 수 있는 것", key="insight_5", placeholder="여기에 한 문장으로 적어 보세요.")
