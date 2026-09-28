import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA_URL = "https://raw.githubusercontent.com/happykth/data/main/kobis_movies.csv"

st.set_page_config(page_title="영화 데이터 그래프 도감 2", layout="wide")
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption("1년간 박스오피스 10위권에 든 영화 가운데 이 기간에 개봉한 216편의 요약표")


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_URL, dtype={"movieCd": str, "openDt": str})
    # 개봉일: 여덟 자리 숫자 -> 날짜
    df["openDt"] = pd.to_datetime(df["openDt"], format="%Y%m%d", errors="coerce")
    # 장르: '|'로 여러 개 적힌 경우 첫 번째 장르만 사용
    df["genre"] = (
        df["genre"].fillna("미상").astype(str).str.split("|").str[0].str.strip()
    )
    df.loc[df["genre"] == "", "genre"] = "미상"
    return df


def chart_section(title: str) -> None:
    """그래프 구역의 머리말. 그래프는 이 아래에서 그린다."""
    st.divider()
    st.subheader(title)


def takeaway(text: str = "") -> None:
    """그래프 아래 '이 그래프로 알 수 있는 것' 한 문장 자리."""
    if text:
        st.info(f"**이 그래프로 알 수 있는 것:** {text}")
    else:
        st.info("**이 그래프로 알 수 있는 것:** (여기에 한 문장을 적어 주세요)")


try:
    df = load_data()
except Exception as e:
    st.error(f"데이터를 불러오지 못했어요: {e}")
    st.stop()

st.write(f"불러온 영화: **{len(df)}편**")

# ---------------------------------------------------------------
# 구역 1. 장르별 영화 편수 (도넛 그래프)
# ---------------------------------------------------------------
chart_section("1. 장르별 영화 편수")

genre_counts = df["genre"].value_counts().reset_index()
genre_counts.columns = ["genre", "count"]

fig = go.Figure(
    go.Pie(
        labels=genre_counts["genre"],
        values=genre_counts["count"],
        hole=0.5,
        sort=False,  # 이미 편수 순으로 정렬됨
        textinfo="label+percent",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "편수: %{value}편<br>"
            "비율: %{percent}"
            "<extra></extra>"
        ),
    )
)
fig.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
    height=480,
    annotations=[
        dict(text=f"총 {len(df)}편", x=0.5, y=0.5, font_size=20, showarrow=False)
    ],
)
st.plotly_chart(fig, use_container_width=True)

takeaway()

# ---------------------------------------------------------------
# 구역 2. 장르 안의 영화별 총 관객 (트리맵)
# ---------------------------------------------------------------
chart_section("2. 장르 안의 영화별 총 관객")

movies = df.assign(total_audi=df["total_audi"].fillna(0))
genre_totals = movies.groupby("genre")["total_audi"].sum()

tree_ids = [f"g:{g}" for g in genre_totals.index] + movies["movieCd"].tolist()
tree_labels = genre_totals.index.tolist() + movies["movieNm"].tolist()
tree_parents = [""] * len(genre_totals) + [f"g:{g}" for g in movies["genre"]]
tree_values = genre_totals.tolist() + movies["total_audi"].tolist()

fig2 = go.Figure(
    go.Treemap(
        ids=tree_ids,
        labels=tree_labels,
        parents=tree_parents,
        values=tree_values,
        branchvalues="total",  # 장르 칸 = 안에 든 영화 관객의 합
        textinfo="label",
        hovertemplate=(
            "<b>%{label}</b><br>"
            "총 관객: %{value:,}명"
            "<extra></extra>"
        ),
    )
)
fig2.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=600)
st.plotly_chart(fig2, use_container_width=True)

takeaway()
