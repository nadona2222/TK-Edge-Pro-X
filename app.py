import math
from datetime import datetime, time
from zoneinfo import ZoneInfo

import pandas as pd
import requests
import streamlit as st
import yfinance as yf

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None

st.set_page_config(
    page_title="TK EDGE Pro X V1200",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

KST = ZoneInfo("Asia/Seoul")
ET = ZoneInfo("America/New_York")
KIS_BASE_URL = "https://openapi.koreainvestment.com:9443"

st.markdown("""
<style>
:root{
 --bg:#0b1017;--panel:#17202b;--card:#111923;--line:#3d4b5f;
 --txt:#fff;--muted:#cbd5e1;--green:#4ade80;--red:#fb7185;--yellow:#ffd166;
}
.stApp{background:radial-gradient(circle at top left,#1d2938 0,#0b1017 43%,#070a0f 100%);color:var(--txt)}
[data-testid="stHeader"]{background:rgba(8,12,18,.88)}
.block-container{max-width:1450px;padding:.7rem .7rem 3rem}
h1,h2,h3,p,span,label{color:inherit}
.title{font-size:27px;font-weight:1000;color:#fff;margin:0 0 8px}
.badge{display:inline-block;background:#ffd166;color:#111!important;border-radius:999px;padding:4px 8px;font-size:11px;margin-left:5px}
.panel{border:1px solid var(--line);background:rgba(23,32,43,.97);border-radius:15px;padding:12px;margin:9px 0;box-shadow:0 5px 16px rgba(0,0,0,.28)}
.panel-title{font-size:20px;font-weight:1000;color:#fff;margin-bottom:9px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(105px,1fr));gap:7px}
.card{border:1px solid #415066;border-radius:11px;background:#111923;padding:9px;min-height:78px;text-align:center;overflow:hidden}
.name{font-size:14px;font-weight:1000;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.price{font-size:19px;font-weight:1000;color:#fff;margin-top:6px}
.change{font-size:17px;font-weight:1000;margin-top:6px}
.small{font-size:11px;color:var(--muted)!important;margin-top:4px}
.green{color:var(--green)!important}.red{color:var(--red)!important}.yellow{color:var(--yellow)!important}.muted{color:var(--muted)!important}
.heat-p3{background:#14783a!important}.heat-p2{background:#18512e!important}.heat-p1{background:#153623!important}
.heat-n3{background:#7c1f2f!important}.heat-n2{background:#5a202b!important}.heat-n1{background:#3a1d25!important}
.heat-flat{background:#202938!important}
.hero{display:grid;grid-template-columns:100px 1fr;gap:13px;align-items:center}
.score{width:92px;height:92px;border-radius:50%;border:7px solid #22c55e;background:#0c141d;display:flex;flex-direction:column;align-items:center;justify-content:center}
.score b{font-size:29px;color:#fff}.score span{font-size:10px;color:var(--muted)}
.strategy{font-size:21px;font-weight:1000;color:#fff}
.notice{border:1px solid #5a4c22;background:#211b0e;border-radius:10px;padding:8px 10px;color:#ffd166!important;font-size:12px}
.nav label{font-weight:1000}
div.stButton>button{background:#f8fafc!important;color:#111827!important;font-weight:1000!important;border:1px solid #94a3b8!important}
div.stButton>button *{color:#111827!important}
@media(max-width:760px){
 .title{font-size:23px}.grid{grid-template-columns:repeat(3,minmax(0,1fr));gap:6px}
 .card{min-height:72px;padding:8px 5px}.name{font-size:12px}.price{font-size:16px}.change{font-size:15px}
 .hero{grid-template-columns:84px 1fr}.score{width:76px;height:76px;border-width:6px}.score b{font-size:25px}.strategy{font-size:18px}
}
</style>
""", unsafe_allow_html=True)

REFRESH_MS = {"1분": 60_000, "5분": 300_000, "10분": 600_000, "30분": 1_800_000}

INDEXES = {
    "S&P500": "^GSPC", "NASDAQ100": "^NDX", "SOX": "^SOX", "VIX": "^VIX",
    "미국10년물": "^TNX", "달러지수": "DX-Y.NYB", "USD/KRW": "KRW=X",
    "KOSPI": "^KS11", "KOSDAQ": "^KQ11", "KOSPI200": "^KS200",
}

CORE_US = {
    "NVIDIA":"NVDA","Microsoft":"MSFT","Apple":"AAPL","Amazon":"AMZN","Alphabet":"GOOGL",
    "Meta":"META","Broadcom":"AVGO","Tesla":"TSLA","AMD":"AMD","Micron":"MU",
    "Vertiv":"VRT","GE Vernova":"GEV","Bloom Energy":"BE","RTX":"RTX","Rocket Lab":"RKLB",
}
CORE_KR = {
    "삼성전자":"005930.KS","SK하이닉스":"000660.KS","HD현대일렉트릭":"267260.KS",
    "두산에너빌리티":"034020.KS","한화에어로":"012450.KS","현대로템":"064350.KS",
    "현대차":"005380.KS","기아":"000270.KS","삼성바이오":"207940.KS","KB금융":"105560.KS",
}

SECTORS = {
    "AI반도체": {"NVIDIA":"NVDA","AMD":"AMD","Broadcom":"AVGO","TSMC":"TSM","ASML":"ASML","ARM":"ARM","Micron":"MU","SK하이닉스":"000660.KS","삼성전자":"005930.KS"},
    "메모리": {"Micron":"MU","Sandisk":"SNDK","Western Digital":"WDC","Seagate":"STX","SK하이닉스":"000660.KS","삼성전자":"005930.KS","한미반도체":"042700.KQ","리노공업":"058470.KQ"},
    "반도체장비": {"ASML":"ASML","Applied Materials":"AMAT","Lam Research":"LRCX","KLA":"KLAC","한미반도체":"042700.KQ","원익IPS":"240810.KQ","주성엔지니어링":"036930.KQ"},
    "AI전력": {"Vertiv":"VRT","Eaton":"ETN","GE Vernova":"GEV","Constellation":"CEG","Vistra":"VST","Bloom Energy":"BE","HD현대일렉트릭":"267260.KS","LS ELECTRIC":"010120.KS","효성중공업":"298040.KS"},
    "원전": {"NuScale":"SMR","Oklo":"OKLO","Cameco":"CCJ","Constellation":"CEG","두산에너빌리티":"034020.KS","한전기술":"052690.KS","한전KPS":"051600.KS"},
    "우주항공": {"Rocket Lab":"RKLB","AST SpaceMobile":"ASTS","Intuitive Machines":"LUNR","Redwire":"RDW","한국항공우주":"047810.KS","한화에어로":"012450.KS"},
    "방산": {"RTX":"RTX","Lockheed":"LMT","Northrop":"NOC","General Dynamics":"GD","한화에어로":"012450.KS","현대로템":"064350.KS","LIG넥스원":"079550.KS"},
    "로봇": {"ABB":"ABBNY","Rockwell":"ROK","Symbotic":"SYM","Teradyne":"TER","레인보우로보틱스":"277810.KQ","두산로보틱스":"454910.KS"},
    "자동차": {"Tesla":"TSLA","Toyota":"TM","Rivian":"RIVN","현대차":"005380.KS","기아":"000270.KS","현대모비스":"012330.KS"},
    "2차전지": {"Albemarle":"ALB","LG에너지솔루션":"373220.KS","삼성SDI":"006400.KS","포스코퓨처엠":"003670.KS","에코프로비엠":"247540.KQ"},
    "클라우드": {"Microsoft":"MSFT","Amazon":"AMZN","Alphabet":"GOOGL","Oracle":"ORCL","Snowflake":"SNOW","Cloudflare":"NET","Datadog":"DDOG"},
    "사이버보안": {"CrowdStrike":"CRWD","Palo Alto":"PANW","Fortinet":"FTNT","Zscaler":"ZS","SentinelOne":"S","Okta":"OKTA"},
    "바이오": {"Eli Lilly":"LLY","AbbVie":"ABBV","Merck":"MRK","Vertex":"VRTX","삼성바이오":"207940.KS","셀트리온":"068270.KS","알테오젠":"196170.KQ"},
    "조선": {"HD현대중공업":"329180.KS","HD한국조선해양":"009540.KS","한화오션":"042660.KS","삼성중공업":"010140.KS","HMM":"011200.KS"},
    "금융": {"JPMorgan":"JPM","Bank of America":"BAC","Goldman Sachs":"GS","Visa":"V","KB금융":"105560.KS","신한지주":"055550.KS","하나금융지주":"086790.KS"},
}

def finite(value):
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except Exception:
        return None

def fmt(value, percent=False):
    number = finite(value)
    if number is None:
        return "-"
    if percent:
        return f"{number:+.2f}%"
    if abs(number) >= 10_000:
        return f"{number:,.0f}"
    if abs(number) >= 1_000:
        return f"{number:,.1f}"
    return f"{number:,.2f}"

def heat(change):
    c = finite(change)
    if c is None: return "heat-flat"
    if c >= 3: return "heat-p3"
    if c >= 1: return "heat-p2"
    if c > .05: return "heat-p1"
    if c <= -3: return "heat-n3"
    if c <= -1: return "heat-n2"
    if c < -.05: return "heat-n1"
    return "heat-flat"

def market_times():
    now_kst = datetime.now(KST)
    now_et = now_kst.astimezone(ET)
    kr = now_kst.weekday() < 5 and time(9,0) <= now_kst.time() <= time(15,30)
    pre = now_et.weekday() < 5 and time(4,0) <= now_et.time() < time(9,30)
    reg = now_et.weekday() < 5 and time(9,30) <= now_et.time() <= time(16,0)
    aft = now_et.weekday() < 5 and time(16,0) < now_et.time() <= time(20,0)
    return now_kst, kr, pre, reg, aft

def _extract(data, ticker):
    if data is None or getattr(data, "empty", True):
        return pd.DataFrame()
    if isinstance(data.columns, pd.MultiIndex):
        if ticker not in data.columns.get_level_values(0):
            return pd.DataFrame()
        return data[ticker].dropna(how="all")
    return data.dropna(how="all")

@st.cache_data(ttl=300, show_spinner=False)
def yahoo_prices(tickers_tuple):
    tickers = list(dict.fromkeys(tickers_tuple))
    result = {t: {"price":None,"chg":None,"chg60":None,"source":"Yahoo"} for t in tickers}
    if not tickers:
        return result

    for start in range(0, len(tickers), 25):
        batch = tickers[start:start+25]
        try:
            intraday = yf.download(batch, period="5d", interval="5m", group_by="ticker",
                                   prepost=True, auto_adjust=False, progress=False, threads=True)
        except Exception:
            intraday = pd.DataFrame()
        try:
            daily = yf.download(batch, period="10d", interval="1d", group_by="ticker",
                                prepost=False, auto_adjust=False, progress=False, threads=True)
        except Exception:
            daily = pd.DataFrame()

        for ticker in batch:
            try:
                i = _extract(intraday, ticker)
                d = _extract(daily, ticker)
                ic = pd.to_numeric(i["Close"], errors="coerce").dropna() if not i.empty and "Close" in i else pd.Series(dtype=float)
                dc = pd.to_numeric(d["Close"], errors="coerce").dropna() if not d.empty and "Close" in d else pd.Series(dtype=float)
                price = finite(ic.iloc[-1]) if len(ic) else (finite(dc.iloc[-1]) if len(dc) else None)
                if price is None:
                    continue
                prev = finite(dc.iloc[-2]) if len(dc) >= 2 else (finite(dc.iloc[-1]) if len(dc) else price)
                base60 = finite(ic.iloc[-13]) if len(ic) >= 13 else (finite(ic.iloc[0]) if len(ic) else price)
                result[ticker] = {
                    "price":price,
                    "chg":((price/prev)-1)*100 if prev else None,
                    "chg60":((price/base60)-1)*100 if base60 else None,
                    "source":"Yahoo",
                }
            except Exception:
                continue
    return result

def kis_ready():
    try:
        return bool(st.secrets.get("KIS_APP_KEY")) and bool(st.secrets.get("KIS_APP_SECRET"))
    except Exception:
        return False

@st.cache_data(ttl=21600, show_spinner=False)
def kis_token(app_key, app_secret):
    response = requests.post(
        f"{KIS_BASE_URL}/oauth2/tokenP",
        json={"grant_type":"client_credentials","appkey":app_key,"appsecret":app_secret},
        timeout=12,
    )
    response.raise_for_status()
    body = response.json()
    token = body.get("access_token")
    if not token:
        raise RuntimeError(body.get("error_description") or "토큰 발급 실패")
    return token

@st.cache_data(ttl=60, show_spinner=False)
def kis_prices(tickers_tuple, app_key, app_secret):
    result = {}
    token = kis_token(app_key, app_secret)
    url = f"{KIS_BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {
        "content-type":"application/json; charset=utf-8","authorization":f"Bearer {token}",
        "appkey":app_key,"appsecret":app_secret,"tr_id":"FHKST01010100","custtype":"P",
    }
    session = requests.Session()

    def query(code, market):
        r = session.get(url, headers=headers, params={"FID_COND_MRKT_DIV_CODE":market,"FID_INPUT_ISCD":code}, timeout=7)
        r.raise_for_status()
        body = r.json()
        if str(body.get("rt_cd")) != "0":
            return None
        out = body.get("output") or {}
        price = finite(out.get("stck_prpr"))
        pct = finite(out.get("prdy_ctrt"))
        return {"price":price,"pct":pct} if price and price > 0 else None

    for ticker in dict.fromkeys(tickers_tuple):
        code = ticker.replace(".KS","").replace(".KQ","")
        try:
            krx = query(code, "J")
            nxt = query(code, "NX")
            unified = query(code, "UN")
            chosen = unified or nxt or krx
            if not chosen:
                continue
            prev = krx["price"]/(1+(krx.get("pct") or 0)/100) if krx and (1+(krx.get("pct") or 0)/100) else None
            price = chosen["price"]
            result[ticker] = {
                "price":price,
                "chg":((price/prev)-1)*100 if prev else chosen.get("pct"),
                "chg60":None,"source":"KIS",
                "session":"통합" if unified else ("NXT" if nxt else "KRX"),
                "krx_price":krx["price"] if krx else None,
                "nxt_price":nxt["price"] if nxt else None,
            }
        except Exception:
            continue
    return result

def render_cards(items, data):
    html = "<div class='grid'>"
    for name, ticker in items.items():
        d = data.get(ticker,{})
        chg = finite(d.get("chg"))
        cls = "green" if chg is not None and chg >= 0 else "red"
        footer = ""
        if d.get("source") == "KIS":
            footer = f"KIS {d.get('session','')} · KRX {fmt(d.get('krx_price'))}"
            if d.get("nxt_price") is not None:
                footer += f" · NXT {fmt(d.get('nxt_price'))}"
        else:
            footer = f"60분 {fmt(d.get('chg60'), True)}"
        html += (
            f"<div class='card {heat(chg)}'><div class='name'>{name}</div>"
            f"<div class='price'>{fmt(d.get('price'))}</div>"
            f"<div class='change {cls}'>{fmt(chg,True)}</div><div class='small'>{footer}</div></div>"
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

def sector_score(data):
    vals = [finite(v.get("chg")) for v in data.values()]
    vals = [v for v in vals if v is not None]
    if not vals:
        return 50, 0, 0
    avg = sum(vals)/len(vals)
    up = sum(1 for v in vals if v > 0)/len(vals)
    score = max(0,min(100,round(50+avg*8+(up-.5)*40)))
    return int(score), avg, up

# Header / navigation
now_kst, kr_open, us_pre, us_reg, us_after = market_times()
c1,c2,c3 = st.columns([1.2,1.45,.7])
with c1:
    st.markdown("<div class='title'>TK EDGE Pro X <span class='badge'>V1200</span></div>",unsafe_allow_html=True)
with c2:
    us_state = "🌅 미국 프리장" if us_pre else ("🟢 미국 정규장" if us_reg else ("🌙 미국 애프터장" if us_after else "⚪ 미국 장마감"))
    kr_state = "🟢 한국 정규장" if kr_open else "⚪ 한국 장마감"
    st.markdown(f"<div class='panel' style='margin:0;padding:9px'><b>{kr_state}</b> | <b>{us_state}</b> · {now_kst:%H:%M:%S}</div>",unsafe_allow_html=True)
with c3:
    refresh = st.selectbox("갱신", list(REFRESH_MS), index=2, label_visibility="collapsed")
if st_autorefresh:
    st_autorefresh(interval=REFRESH_MS[refresh], key="v1200_refresh")

page = st.radio("화면", ["🏠 홈","🧩 섹터","📈 피크/순환"], horizontal=True, label_visibility="collapsed")

if page == "🏠 홈":
    tickers = list(INDEXES.values()) + list(CORE_US.values()) + list(CORE_KR.values())
    with st.spinner("핵심 시장 데이터 불러오는 중..."):
        data = yahoo_prices(tuple(tickers))
        if kis_ready():
            try:
                km = kis_prices(tuple(CORE_KR.values()), st.secrets["KIS_APP_KEY"], st.secrets["KIS_APP_SECRET"])
                for t,d in km.items():
                    d["chg60"] = data.get(t,{}).get("chg60")
                    data[t] = d
                st.success("✅ KIS 연결됨 · 국내 KRX/NXT 조회")
            except Exception as exc:
                st.warning(f"⚠️ KIS 연결 실패, Yahoo 대체: {type(exc).__name__}")

    idx_scores = [finite(data.get(t,{}).get("chg")) for t in INDEXES.values()]
    idx_scores = [v for v in idx_scores if v is not None]
    market_score = round(50 + (sum(idx_scores)/len(idx_scores))*8) if idx_scores else 50
    market_score = max(0,min(100,market_score))
    strategy = "선택적 매수" if market_score >= 68 else ("보유·관망" if market_score >= 50 else "방어 우선")
    ring = "#22c55e" if market_score >= 68 else ("#ffd166" if market_score >= 50 else "#fb7185")

    st.markdown(
        f"<div class='panel hero'><div class='score' style='border-color:{ring}'><b>{market_score}</b><span>MARKET SCORE</span></div>"
        f"<div><div class='strategy'>오늘 전략: {strategy}</div><div class='small'>핵심 지수의 전일 대비 흐름을 종합한 참고 점수입니다.</div></div></div>",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='panel'><div class='panel-title'>🌐 글로벌 지수</div>",unsafe_allow_html=True)
    render_cards(INDEXES,data)
    st.markdown("</div>",unsafe_allow_html=True)

    a,b = st.columns(2)
    with a:
        st.markdown("<div class='panel'><div class='panel-title'>🇺🇸 미국 핵심 대표주</div>",unsafe_allow_html=True)
        render_cards(CORE_US,data)
        st.markdown("</div>",unsafe_allow_html=True)
    with b:
        st.markdown("<div class='panel'><div class='panel-title'>🇰🇷 한국 핵심 대표주</div>",unsafe_allow_html=True)
        render_cards(CORE_KR,data)
        st.markdown("</div>",unsafe_allow_html=True)

elif page == "🧩 섹터":
    selected = st.selectbox("섹터 선택", list(SECTORS.keys()))
    items = SECTORS[selected]
    tickers = list(items.values())
    with st.spinner(f"{selected} 데이터 불러오는 중..."):
        data = yahoo_prices(tuple(tickers))
        kr_tickers = [t for t in tickers if t.endswith((".KS",".KQ"))]
        if kis_ready() and kr_tickers:
            try:
                km = kis_prices(tuple(kr_tickers[:10]), st.secrets["KIS_APP_KEY"], st.secrets["KIS_APP_SECRET"])
                for t,d in km.items():
                    d["chg60"] = data.get(t,{}).get("chg60")
                    data[t] = d
            except Exception:
                pass

    score, avg, up = sector_score(data)
    status = "🔥 강세" if score >= 80 else ("🟢 상승" if score >= 65 else ("🟡 중립" if score >= 50 else "🔴 약세"))
    st.markdown(
        f"<div class='panel hero'><div class='score'><b>{score}</b><span>SECTOR SCORE</span></div>"
        f"<div><div class='strategy'>{selected} · {status}</div><div class='small'>평균 {avg:+.2f}% · 상승 종목 비율 {up*100:.0f}%</div></div></div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"<div class='panel'><div class='panel-title'>🧩 {selected} 대표주</div>",unsafe_allow_html=True)
    render_cards(items,data)
    st.markdown("</div>",unsafe_allow_html=True)
    st.markdown("<div class='notice'>섹터 페이지는 선택한 종목만 조회하므로 전체 종목을 한꺼번에 받을 때보다 빠르고 안정적입니다.</div>",unsafe_allow_html=True)

else:
    # 섹터 순환은 각 섹터 대표 3종목만 조회해 속도 유지
    proxies = {}
    for sec, items in SECTORS.items():
        proxies[sec] = dict(list(items.items())[:3])
    all_ticks = [t for items in proxies.values() for t in items.values()]
    with st.spinner("섹터 순환 계산 중..."):
        data = yahoo_prices(tuple(all_ticks))
    rows = []
    for sec, items in proxies.items():
        subset = {t:data.get(t,{}) for t in items.values()}
        score, avg, up = sector_score(subset)
        rows.append((sec,score,avg,up))
    rows.sort(key=lambda x:x[1],reverse=True)

    st.markdown("<div class='panel'><div class='panel-title'>📈 섹터 순환 · 피크/피크아웃</div>",unsafe_allow_html=True)
    for rank,(sec,score,avg,up) in enumerate(rows,1):
        tag = "🟢 피크 유지" if score >= 80 else ("🟡 피크 근처" if score >= 65 else "🔴 피크아웃 주의")
        st.markdown(f"**{rank}. {sec} — {score}점 · {tag}**")
        st.progress(score)
        st.caption(f"대표 3종목 평균 {avg:+.2f}% · 상승비율 {up*100:.0f}%")
    st.markdown("</div>",unsafe_allow_html=True)

st.caption(f"Last Update: {now_kst:%Y-%m-%d %H:%M:%S} · V1200 Ultimate Single · 화면별 필요한 데이터만 조회")
