import numpy as np
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

# ---------------------------------------------------------------
# 구역 3. 총 관객 분포 (히스토그램)
# ---------------------------------------------------------------
chart_section("3. 총 관객 분포")

audi = df.dropna(subset=["total_audi"])
counts, edges = np.histogram(audi["total_audi"], bins=30)
bin_size = edges[1] - edges[0]

fig3 = go.Figure(
    go.Histogram(
        x=audi["total_audi"],
        xbins=dict(start=edges[0], end=edges[-1], size=bin_size),
        hovertemplate="관객 구간: %{x}명<br>영화: %{y}편<extra></extra>",
    )
)
fig3.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
    height=450,
    xaxis_title="총 관객(명)",
    yaxis_title="영화 편수",
    bargap=0.05,
)
st.plotly_chart(fig3, use_container_width=True)

# 가장 많은 영화가 몰린 구간과 관객이 가장 많은 영화
peak = int(np.argmax(counts))
lo, hi = edges[peak], edges[peak + 1]
peak_share = counts[peak] / len(audi) * 100
top = audi.loc[audi["total_audi"].idxmax()]

takeaway(
    f"영화 대부분은 총 관객 {lo:,.0f}명~{hi:,.0f}명 구간에 몰려 있고"
    f"(이 구간 {counts[peak]}편, 전체의 {peak_share:.1f}%), "
    f"관객이 가장 많은 영화는 '{top['movieNm']}'({top['total_audi']:,.0f}명)입니다."
)

# ---------------------------------------------------------------
# 구역 4. 개봉일 스크린수와 총 관객 (산점도)
# ---------------------------------------------------------------
chart_section("4. 개봉일 스크린수와 총 관객")

scatter_df = df.dropna(subset=["first_scrn", "total_audi"])

fig4 = go.Figure()
for genre_name in scatter_df["genre"].value_counts().index:  # 편수 많은 장르부터
    sub = scatter_df[scatter_df["genre"] == genre_name]
    fig4.add_trace(
        go.Scatter(
            x=sub["first_scrn"],
            y=sub["total_audi"],
            mode="markers",
            name=genre_name,  # 장르별 색과 범례
            marker=dict(size=9, opacity=0.8),
            text=sub["movieNm"],
            customdata=sub[["genre"]],
            hovertemplate=(
                "<b>%{text}</b><br>"
                "장르: %{customdata[0]}<br>"
                "개봉일 스크린수: %{x:,}개<br>"
                "총 관객: %{y:,}명"
                "<extra></extra>"
            ),
        )
    )
fig4.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
    height=520,
    xaxis_title="개봉일 스크린수(개)",
    yaxis_title="총 관객(명)",
    legend_title_text="장르",
)
st.plotly_chart(fig4, use_container_width=True)

takeaway()

# ---------------------------------------------------------------
# 구역 5. 장르별 총 관객 분포 (상자 그림)
# ---------------------------------------------------------------
chart_section("5. 장르별 총 관객 분포 (영화 10편 이상인 장르)")

MIN_MOVIES = 10
box_df = df.dropna(subset=["total_audi"])
genre_n = box_df["genre"].value_counts()
big_genres = genre_n[genre_n >= MIN_MOVIES].index.tolist()  # 편수 많은 순

if not big_genres:
    st.info(f"영화가 {MIN_MOVIES}편 이상인 장르가 없어요.")
else:
    fig5 = go.Figure()
    for genre_name in big_genres:
        sub = box_df[box_df["genre"] == genre_name]
        fig5.add_trace(
            go.Box(
                y=sub["total_audi"],
                name=f"{genre_name} ({len(sub)}편)",
                boxpoints="outliers",  # 상자 밖으로 튀는 점만 표시
                hoveron="points",      # 튀는 점에 올렸을 때만 정보 표시
                text=sub["movieNm"],
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    "총 관객: %{y:,}명"
                    "<extra></extra>"
                ),
                showlegend=False,
            )
        )
    fig5.update_layout(
        margin=dict(t=20, b=20, l=20, r=20),
        height=520,
        xaxis_title="장르",
        yaxis_title="총 관객(명)",
    )
    st.plotly_chart(fig5, use_container_width=True)

takeaway()

# ---------------------------------------------------------------
# 구역 6. 스크린수·총 관객·첫 주 관객 (버블 그래프)
# ---------------------------------------------------------------
chart_section("6. 개봉일 스크린수와 총 관객 - 점 크기는 첫 주 관객")

bubble_df = df.dropna(subset=["first_scrn", "total_audi", "first_week_audi"])
bubble_df = bubble_df[bubble_df["first_week_audi"] > 0]  # 0 이하는 점이 그려지지 않음

# 모든 장르에서 같은 기준으로 크기가 정해지도록 sizeref를 한 번만 계산
max_size = bubble_df["first_week_audi"].max()
sizeref = 2.0 * max_size / (45**2)  # 가장 큰 버블의 지름이 약 45px

fig6 = go.Figure()
for genre_name in bubble_df["genre"].value_counts().index:
    sub = bubble_df[bubble_df["genre"] == genre_name]
    fig6.add_trace(
        go.Scatter(
            x=sub["first_scrn"],
            y=sub["total_audi"],
            mode="markers",
            name=genre_name,
            marker=dict(
                size=sub["first_week_audi"],
                sizemode="area",  # 면적이 첫 주 관객에 비례
                sizeref=sizeref,
                sizemin=3,
                opacity=0.6,
                line=dict(width=0.5, color="white"),
            ),
            text=sub["movieNm"],
            customdata=sub[["genre", "first_week_audi"]],
            hovertemplate=(
                "<b>%{text}</b><br>"
                "장르: %{customdata[0]}<br>"
                "개봉일 스크린수: %{x:,}개<br>"
                "첫 주 관객: %{customdata[1]:,}명<br>"
                "총 관객: %{y:,}명"
                "<extra></extra>"
            ),
        )
    )
fig6.update_layout(
    margin=dict(t=20, b=20, l=20, r=20),
    height=560,
    xaxis_title="개봉일 스크린수(개)",
    yaxis_title="총 관객(명)",
    legend_title_text="장르",
)
st.plotly_chart(fig6, use_container_width=True)

takeaway()

# ---------------------------------------------------------------
# 구역 7. 제작 국가 → 장르 (선버스트)
# ---------------------------------------------------------------
chart_section("7. 제작 국가에서 장르로 - 영화 편수")

sun_df = df.assign(nation=df["nation"].fillna("미상").astype(str).str.strip())
sun_df.loc[sun_df["nation"] == "", "nation"] = "미상"

nation_counts = sun_df["nation"].value_counts()
pair_counts = sun_df.groupby(["nation", "genre"]).size().reset_index(name="count")

sun_ids = [f"n:{n}" for n in nation_counts.index] + [
    f"n:{r.nation}|g:{r.genre}" for r in pair_counts.itertuples()
]
sun_labels = nation_counts.index.tolist() + pair_counts["genre"].tolist()
sun_parents = [""] * len(nation_counts) + [f"n:{n}" for n in pair_counts["nation"]]
sun_values = nation_counts.tolist() + pair_counts["count"].tolist()

fig7 = go.Figure(
    go.Sunburst(
        ids=sun_ids,
        labels=sun_labels,
        parents=sun_parents,
        values=sun_values,
        branchvalues="total",  # 국가 칸 = 안에 든 장르 편수의 합
        hovertemplate=(
            "<b>%{label}</b><br>"
            "편수: %{value}편"
            "<extra></extra>"
        ),
    )
)
fig7.update_layout(margin=dict(t=20, b=20, l=20, r=20), height=600)
st.plotly_chart(fig7, use_container_width=True)

takeaway()
