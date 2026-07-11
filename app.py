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
    page_title="TK EDGE Pro X V1310",
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
div.stButton>button[kind="primary"]{
  background:#ffd166!important;
  border-color:#ffd166!important;
  color:#111827!important;
}
div.stButton>button[kind="secondary"]{
  background:#17202b!important;
  border-color:#415066!important;
  color:#ffffff!important;
}
div.stButton>button[kind="secondary"] *{color:#ffffff!important}
@media(max-width:760px){
 .title{font-size:23px}.grid{grid-template-columns:repeat(3,minmax(0,1fr));gap:6px}
 .card{min-height:72px;padding:8px 5px}.name{font-size:12px}.price{font-size:16px}.change{font-size:15px}
 .hero{grid-template-columns:84px 1fr}.score{width:76px;height:76px;border-width:6px}.score b{font-size:25px}.strategy{font-size:18px}
}

.tomorrow-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin-top:9px}
.tomorrow-card{border:1px solid #415066;border-radius:11px;background:#111923;padding:10px;text-align:center}
.tomorrow-label{font-size:12px;color:#cbd5e1!important}
.tomorrow-value{font-size:19px;font-weight:1000;margin-top:5px}
.signal-up{color:#4ade80!important}.signal-down{color:#fb7185!important}.signal-flat{color:#ffd166!important}
.reason-list{font-size:12px;color:#d4dbe6!important;line-height:1.55;margin-top:8px}
@media(max-width:760px){.tomorrow-grid{grid-template-columns:repeat(3,minmax(0,1fr));gap:6px}.tomorrow-value{font-size:16px}}
</style>

""", unsafe_allow_html=True)

REFRESH_MS = {"1분": 60_000, "5분": 300_000, "10분": 600_000, "30분": 1_800_000}

INDEXES = {
    "S&P500": "SPY",
    "NASDAQ100": "QQQ",
    "DOW": "DIA",
    "Russell2000": "IWM",
    "SOX": "SOXX",
    "VIX": "^VIX",
    "달러지수": "DX-Y.NYB",
    "USD/KRW": "KRW=X",
    "KOSPI": "^KS11",
    "KOSDAQ": "^KQ11",
}

CORE_US = {
    "S&P500": "SPY",
    "NASDAQ100": "QQQ",
    "AI반도체": "SMH",
    "반도체": "SOXX",
    "소형반도체": "XSD",
    "AI전력": "GRID",
    "원전": "URA",
    "방산": "ITA",
    "우주": "ARKX",
    "로봇": "BOTZ",
    "클라우드": "CLOU",
    "사이버보안": "HACK",
    "바이오": "IBB",
    "금융": "XLF",
    "에너지": "XLE",
    "자동차": "CARZ",
    "2차전지": "LIT",
}

CORE_KR = {
    "KODEX 200": "069500.KS",
    "KODEX 코스닥150": "229200.KS",
    "TIGER 미국필반": "381180.KS",
    "KODEX AI반도체장비": "471990.KS",
    "KODEX 미국AI전력": "487230.KS",
    "KODEX AI전력설비": "487240.KS",
    "PLUS K방산": "436180.KS",
    "PLUS 우주항공": "421320.KS",
    "KODEX 은행": "091170.KS",
    "KODEX 바이오": "244580.KS",
}

SECTORS = {
    "AI반도체": {
        "미국 SMH": "SMH",
        "미국 SOXX": "SOXX",
        "한국 TIGER 미국필반": "381180.KS",
    },
    "반도체 소부장": {
        "미국 XSD": "XSD",
        "미국 SOXX": "SOXX",
        "한국 KODEX AI반도체장비": "471990.KS",
    },
    "AI전력·전력인프라": {
        "미국 GRID": "GRID",
        "미국 PAVE": "PAVE",
        "한국 KODEX 미국AI전력": "487230.KS",
        "한국 KODEX AI전력설비": "487240.KS",
    },
    "원전": {
        "미국 URA": "URA",
        "미국 NLR": "NLR",
        "한국 KODEX 미국원자력SMR": "0091H0.KS",
    },
    "방산": {
        "미국 ITA": "ITA",
        "미국 XAR": "XAR",
        "한국 PLUS K방산": "436180.KS",
    },
    "우주항공": {
        "미국 ARKX": "ARKX",
        "미국 UFO": "UFO",
        "한국 PLUS 우주항공": "421320.KS",
    },
    "로봇": {
        "미국 BOTZ": "BOTZ",
        "미국 ROBO": "ROBO",
        "한국 KODEX 로봇액티브": "445290.KS",
    },
    "클라우드": {
        "미국 CLOU": "CLOU",
        "미국 SKYY": "SKYY",
        "한국 TIGER 글로벌AI클라우드": "371450.KS",
    },
    "사이버보안": {
        "미국 HACK": "HACK",
        "미국 CIBR": "CIBR",
        "한국 TIGER 글로벌사이버보안": "418670.KS",
    },
    "바이오": {
        "미국 IBB": "IBB",
        "미국 XBI": "XBI",
        "한국 KODEX 바이오": "244580.KS",
    },
    "금융": {
        "미국 XLF": "XLF",
        "미국 KRE": "KRE",
        "한국 KODEX 은행": "091170.KS",
    },
    "에너지": {
        "미국 XLE": "XLE",
        "미국 XOP": "XOP",
        "한국 TIGER 200에너지화학": "139250.KS",
    },
    "자동차": {
        "미국 CARZ": "CARZ",
        "미국 DRIV": "DRIV",
        "한국 TIGER 현대차그룹": "138540.KS",
    },
    "2차전지": {
        "미국 LIT": "LIT",
        "미국 BATT": "BATT",
        "한국 TIGER 2차전지테마": "305540.KS",
    },
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


def etf_rotation_score(data):
    """당일, 60분, 상승확산을 합친 ETF 섹터 로테이션 점수."""
    day_vals, m60_vals = [], []
    for item in data.values():
        d = finite(item.get("chg"))
        m = finite(item.get("chg60"))
        if d is not None:
            day_vals.append(d)
        if m is not None:
            m60_vals.append(m)
    if not day_vals:
        return 50, 0.0, 0.0, 0.0
    day_avg = sum(day_vals) / len(day_vals)
    m60_avg = sum(m60_vals) / len(m60_vals) if m60_vals else 0.0
    breadth = sum(1 for v in day_vals if v > 0) / len(day_vals)
    score = 50 + day_avg * 8 + m60_avg * 6 + (breadth - 0.5) * 35
    score = int(max(0, min(100, round(score))))
    return score, day_avg, m60_avg, breadth

def trade_zone(score, m60_avg):
    """미래 예측이 아닌 현재 신호 강도에 따른 분할매매 참고구간."""
    if score >= 90 and m60_avg < 0:
        return "🔴 분할매도 검토"
    if score >= 82:
        return "🟢 보유·추세추종"
    if score >= 68:
        return "🟡 1차 분할매수 검토"
    if score >= 55:
        return "🟠 2차 관찰구간"
    return "⚪ 대기·추세확인"

def leader_probability(score, day_avg, m60_avg):
    """다음 주도주 '확률'이 아니라 신호 일치도를 0~99로 표시."""
    value = 40 + (score - 50) * 0.7 + max(-10, min(10, day_avg * 5)) + max(-10, min(10, m60_avg * 8))
    return int(max(1, min(99, round(value))))


def tomorrow_direction_signal(data):
    """다음 거래일 방향성 참고 신호.

    미래를 예측하는 확률이 아니라, 현재 ETF·지수 신호의 일치도를 계산합니다.
    """
    weights = {
        "SPY": 1.2,
        "QQQ": 1.5,
        "SOXX": 1.6,
        "^VIX": -1.2,
        "DX-Y.NYB": -0.8,
        "KRW=X": -0.9,
        "^KS11": 1.0,
        "^KQ11": 0.9,
    }

    score = 50.0
    reasons_up, reasons_down = [], []

    for ticker, weight in weights.items():
        item = data.get(ticker, {})
        chg = finite(item.get("chg"))
        m60 = finite(item.get("chg60"))
        if chg is None:
            continue

        contribution = max(-8, min(8, chg * 3.0)) * weight
        if m60 is not None:
            contribution += max(-4, min(4, m60 * 4.0)) * (0.5 if weight > 0 else -0.5)
        score += contribution

        name_map = {
            "SPY":"S&P500", "QQQ":"NASDAQ100", "SOXX":"반도체",
            "^VIX":"VIX", "DX-Y.NYB":"달러지수", "KRW=X":"원달러",
            "^KS11":"KOSPI", "^KQ11":"KOSDAQ",
        }
        name = name_map.get(ticker, ticker)

        positive = (chg > 0 and weight > 0) or (chg < 0 and weight < 0)
        reason = f"{name} {chg:+.2f}%"
        if positive:
            reasons_up.append(reason)
        else:
            reasons_down.append(reason)

    score = int(max(1, min(99, round(score))))
    if score >= 62:
        direction = "상승 우세"
        css = "signal-up"
    elif score <= 38:
        direction = "하락 우세"
        css = "signal-down"
    else:
        direction = "혼조·중립"
        css = "signal-flat"

    confidence = abs(score - 50) * 2
    confidence = int(max(0, min(98, confidence)))

    return {
        "score": score,
        "direction": direction,
        "css": css,
        "confidence": confidence,
        "up_reasons": reasons_up[:4],
        "down_reasons": reasons_down[:4],
    }

# Header / navigation
now_kst, kr_open, us_pre, us_reg, us_after = market_times()
c1,c2,c3 = st.columns([1.2,1.45,.7])
with c1:
    st.markdown("<div class='title'>TK EDGE Pro X <span class='badge'>V1310</span></div>",unsafe_allow_html=True)
with c2:
    us_state = "🌅 미국 프리장" if us_pre else ("🟢 미국 정규장" if us_reg else ("🌙 미국 애프터장" if us_after else "⚪ 미국 장마감"))
    kr_state = "🟢 한국 정규장" if kr_open else "⚪ 한국 장마감"
    st.markdown(f"<div class='panel' style='margin:0;padding:9px'><b>{kr_state}</b> | <b>{us_state}</b> · {now_kst:%H:%M:%S}</div>",unsafe_allow_html=True)
with c3:
    refresh = st.selectbox("갱신", list(REFRESH_MS), index=2, label_visibility="collapsed")
if st_autorefresh:
    st_autorefresh(interval=REFRESH_MS[refresh], key="v1310_refresh")

# 화면 이동은 셀렉트박스 대신 큰 버튼으로 처리합니다.
if "page" not in st.session_state:
    st.session_state.page = "🏠 홈"

nav1, nav2, nav3 = st.columns(3)
with nav1:
    if st.button(
        "🏠 홈",
        use_container_width=True,
        type="primary" if st.session_state.page == "🏠 홈" else "secondary",
        key="nav_home",
    ):
        st.session_state.page = "🏠 홈"
        st.rerun()
with nav2:
    if st.button(
        "🧩 섹터",
        use_container_width=True,
        type="primary" if st.session_state.page == "🧩 섹터" else "secondary",
        key="nav_sector",
    ):
        st.session_state.page = "🧩 섹터"
        st.rerun()
with nav3:
    if st.button(
        "📈 피크/순환",
        use_container_width=True,
        type="primary" if st.session_state.page == "📈 피크/순환" else "secondary",
        key="nav_peak",
    ):
        st.session_state.page = "📈 피크/순환"
        st.rerun()

page = st.session_state.page

if page == "🏠 홈":
    tickers = list(dict.fromkeys(
        list(INDEXES.values())
        + list(CORE_US.values())
        + list(CORE_KR.values())
        + ["SPY", "QQQ", "SOXX", "^VIX", "DX-Y.NYB", "KRW=X", "^KS11", "^KQ11"]
    ))
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

    tomorrow = tomorrow_direction_signal(data)
    up_reason_text = "<br>".join(f"＋ {reason}" for reason in tomorrow["up_reasons"]) or "＋ 뚜렷한 상승 신호 없음"
    down_reason_text = "<br>".join(f"－ {reason}" for reason in tomorrow["down_reasons"]) or "－ 뚜렷한 하락 신호 없음"

    st.markdown(
        f"""
        <div class='panel'>
          <div class='panel-title'>🌙 다음 거래일 방향성 참고</div>
          <div class='tomorrow-grid'>
            <div class='tomorrow-card'>
              <div class='tomorrow-label'>방향</div>
              <div class='tomorrow-value {tomorrow["css"]}'>{tomorrow["direction"]}</div>
            </div>
            <div class='tomorrow-card'>
              <div class='tomorrow-label'>신호 점수</div>
              <div class='tomorrow-value'>{tomorrow["score"]}점</div>
            </div>
            <div class='tomorrow-card'>
              <div class='tomorrow-label'>신호 일치도</div>
              <div class='tomorrow-value'>{tomorrow["confidence"]}%</div>
            </div>
          </div>
          <div class='reason-list'>
            <b class='green'>상승 쪽 근거</b><br>{up_reason_text}<br><br>
            <b class='red'>하락 쪽 근거</b><br>{down_reason_text}
          </div>
          <div class='small'>※ 실제 상승확률이 아니라 S&P500·NASDAQ·SOXX·VIX·달러·환율·한국지수 신호의 방향 일치도입니다.</div>
        </div>
        """,
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
    sector_names = list(SECTORS.keys())
    if "selected_sector" not in st.session_state:
        st.session_state.selected_sector = sector_names[0]

    st.markdown("<div class='panel-title'>🧩 ETF 분야를 누르세요</div>", unsafe_allow_html=True)
    for start in range(0, len(sector_names), 3):
        cols = st.columns(3)
        for offset, col in enumerate(cols):
            idx = start + offset
            if idx >= len(sector_names):
                continue
            sector_name = sector_names[idx]
            with col:
                if st.button(
                    sector_name,
                    use_container_width=True,
                    type="primary" if st.session_state.selected_sector == sector_name else "secondary",
                    key=f"sector_btn_{idx}",
                ):
                    st.session_state.selected_sector = sector_name
                    st.rerun()

    selected = st.session_state.selected_sector
    items = SECTORS[selected]
    tickers = list(items.values())
    with st.spinner(f"{selected} ETF 데이터 불러오는 중..."):
        data = yahoo_prices(tuple(tickers))
        kr_tickers = [t for t in tickers if t.endswith((".KS", ".KQ"))]
        if kis_ready() and kr_tickers:
            try:
                km = kis_prices(tuple(kr_tickers[:6]), st.secrets["KIS_APP_KEY"], st.secrets["KIS_APP_SECRET"])
                for t, d in km.items():
                    d["chg60"] = data.get(t, {}).get("chg60")
                    data[t] = d
            except Exception:
                pass

    score, day_avg, m60_avg, breadth = etf_rotation_score(data)
    status = "🔥 주도" if score >= 82 else ("🟢 강화" if score >= 68 else ("🟡 중립" if score >= 55 else "🔴 약화"))
    zone = trade_zone(score, m60_avg)
    confidence = leader_probability(score, day_avg, m60_avg)

    st.markdown(
        f"<div class='panel hero'><div class='score'><b>{score}</b><span>ROTATION SCORE</span></div>"
        f"<div><div class='strategy'>{selected} · {status}</div>"
        f"<div class='small'>당일 평균 {day_avg:+.2f}% · 60분 {m60_avg:+.2f}% · 상승 ETF {breadth*100:.0f}%</div>"
        f"<div class='small'>매매 참고: {zone} · 다음 주도 신호 일치도 {confidence}%</div>"
        f"<div class='small'>내일 섹터 방향 참고: {'상승 우세' if score >= 68 and m60_avg >= 0 else ('하락 주의' if score < 50 or m60_avg < -0.3 else '혼조')}</div></div></div>",
        unsafe_allow_html=True,
    )
    st.markdown(f"<div class='panel'><div class='panel-title'>🇺🇸 미국 ETF + 🇰🇷 한국 ETF</div>", unsafe_allow_html=True)
    render_cards(items, data)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='notice'>점수와 신호 일치도는 현재 가격·60분 흐름·상승 확산을 계산한 참고지표이며 미래 수익을 보장하지 않습니다.</div>",
        unsafe_allow_html=True,
    )

else:
    # 각 분야의 미국 대표 ETF 1개 + 한국 대표 ETF 1개만 사용해 빠르게 순환 계산
    proxies = {}
    for sec, items in SECTORS.items():
        pairs = list(items.items())
        selected_pairs = []
        us_added = kr_added = False
        for name, ticker in pairs:
            is_kr = ticker.endswith((".KS", ".KQ"))
            if is_kr and not kr_added:
                selected_pairs.append((name, ticker))
                kr_added = True
            elif not is_kr and not us_added:
                selected_pairs.append((name, ticker))
                us_added = True
            if us_added and kr_added:
                break
        proxies[sec] = dict(selected_pairs)

    all_ticks = list(dict.fromkeys(t for items in proxies.values() for t in items.values()))
    with st.spinner("ETF 자금순환 계산 중..."):
        data = yahoo_prices(tuple(all_ticks))
        kr_ticks = [t for t in all_ticks if t.endswith((".KS", ".KQ"))]
        if kis_ready() and kr_ticks:
            try:
                km = kis_prices(tuple(kr_ticks[:14]), st.secrets["KIS_APP_KEY"], st.secrets["KIS_APP_SECRET"])
                for t, d in km.items():
                    d["chg60"] = data.get(t, {}).get("chg60")
                    data[t] = d
            except Exception:
                pass

    rows = []
    for sec, items in proxies.items():
        subset = {t: data.get(t, {}) for t in items.values()}
        score, day_avg, m60_avg, breadth = etf_rotation_score(subset)
        confidence = leader_probability(score, day_avg, m60_avg)
        rows.append((sec, score, day_avg, m60_avg, breadth, confidence))
    rows.sort(key=lambda x: (x[1], x[5]), reverse=True)

    st.markdown("<div class='panel'><div class='panel-title'>💰 ETF 자금순환 · 다음 주도 섹터</div>", unsafe_allow_html=True)
    for rank, (sec, score, day_avg, m60_avg, breadth, confidence) in enumerate(rows, 1):
        tag = "🟢 주도 유지" if score >= 82 else ("🟡 강화 중" if score >= 68 else ("⚪ 중립" if score >= 55 else "🔴 약화"))
        zone = trade_zone(score, m60_avg)
        st.markdown(f"**{rank}. {sec} — {score}점 · {tag}**")
        st.progress(score)
        st.caption(
            f"당일 {day_avg:+.2f}% · 60분 {m60_avg:+.2f}% · 신호 일치도 {confidence}% · {zone}"
        )
    st.markdown("</div>", unsafe_allow_html=True)


st.caption(f"Last Update: {now_kst:%Y-%m-%d %H:%M:%S} · V1310 ETF Rotation · 미국+한국 ETF 기반")
