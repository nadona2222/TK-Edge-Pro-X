import streamlit as st

st.set_page_config(
    page_title="TK AI Market Center V5000",
    page_icon="📈",
    layout="wide"
)

st.title("📈 TK AI Market Center")
st.caption("V5000")

menu = st.radio(
    "",
    ["🏠 HOME", "🇰🇷 국장", "🇺🇸 미장", "🤖 AI"],
    horizontal=True,
    label_visibility="collapsed"
)

st.divider()

# ===========================
# HOME
# ===========================

if menu == "🏠 HOME":

    st.header("📈 AI 시장 브리핑")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("시장점수", "82")
    c2.metric("Risk", "ON")
    c3.metric("국장", "🟢")
    c4.metric("미장", "🟢")

    st.subheader("오늘 강한 섹터")

    cols = st.columns(4)

    cols[0].success("반도체")
    cols[1].success("전력")
    cols[2].success("소부장")
    cols[3].info("방산")

# ===========================
# 국장
# ===========================

elif menu == "🇰🇷 국장":

    st.header("🇰🇷 대한민국 시장")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 시장",
        "💰 수급",
        "📦 ETF",
        "🏢 종목"
    ])

    with tab1:

        st.metric("KOSPI","-")
        st.metric("KOSDAQ","-")
        st.metric("KOSPI200","-")

    with tab2:

        st.metric("외국인","-")
        st.metric("기관","-")

    with tab3:

        st.write("반도체")
        st.write("소부장")
        st.write("전력")
        st.write("우주")
        st.write("방산")

    with tab4:

        st.write("삼성전자")
        st.write("SK하이닉스")

# ===========================
# 미장
# ===========================

elif menu == "🇺🇸 미장":

    st.header("🇺🇸 미국 시장")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 시장",
        "🌏 선물",
        "📦 ETF",
        "🏢 빅테크"
    ])

    with tab1:

        st.metric("S&P500","-")
        st.metric("NASDAQ100","-")
        st.metric("SOX","-")
        st.metric("VIX","-")

    with tab2:

        st.metric("나스닥선물","-")
        st.metric("S&P선물","-")
        st.metric("다우선물","-")

    with tab3:

        st.write("QQQ")
        st.write("SOXX")
        st.write("SMH")
        st.write("GRID")

    with tab4:

        st.write("NVIDIA")
        st.write("Microsoft")
        st.write("Amazon")
        st.write("Meta")

# ===========================
# AI
# ===========================

elif menu == "🤖 AI":

    st.header("🤖 AI 투자센터")

    st.success("오늘 추천")

    st.write("🥇 반도체")

    st.write("🥈 전력")

    st.write("🥉 소부장")

    st.warning("관망")

    st.write("2차전지")
