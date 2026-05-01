import streamlit as st
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import time

# ================= CONFIG =================
st.set_page_config(page_title="PROXY PRO MAX", page_icon="🔥", layout="wide")

# ================= SESSION =================
if "used_ips" not in st.session_state:
    st.session_state.used_ips = set()

# ================= STYLE =================
st.markdown("""
<style>
body {background:#0e1117;}
.title {text-align:center;font-size:36px;font-weight:bold;color:#00ffcc;}
.box {background:#1c1f26;padding:10px;border-radius:10px;margin-bottom:8px;}
.good {color:#00ff99;}
.bad {color:#ff4d4d;}
.meta {font-size:12px;color:#aaa;}
.stButton {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    z-index: 9999;
}
.stButton > button {
    width: 300px;
    height: 50px;
    font-size: 18px;
    font-weight: bold;
    border-radius: 12px;
    background: linear-gradient(90deg, #00ffcc, #00cc99);
    color: black;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🔥 PROXY TOOL PRO MAX 🔥</div>', unsafe_allow_html=True)

# ================= INPUT =================
apis = st.text_area("📌 Dán API", height=180)

# ================= RESET =================
if st.button("♻️ Reset IP đã dùng"):
    st.session_state.used_ips = set()
    st.success("Đã reset IP")

# ================= FETCH =================
def get_proxy(url):
    for _ in range(3):
        try:
            r = requests.get(url, timeout=10)
            data = r.json()

            proxy = data.get("proxyhttp") or data.get("proxysocks5")

            if proxy:
                return {
                    "proxy": proxy,
                    "live": int(data.get("time", 0)),
                    "die": data.get("time_die", "?"),
                    "next": data.get("next_allowed_in_seconds", "?"),
                }

        except:
            time.sleep(1)

    return {"error": url}

# ================= RUN =================
if st.button("🚀 LẤY PROXY"):

    lines = [x.strip() for x in apis.split("\n") if x.strip()]
    results = []

    progress = st.progress(0)

    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(get_proxy, url) for url in lines]

        for i, future in enumerate(as_completed(futures)):
            res = future.result()

            if res:
                if "error" in res:
                    st.warning(f"Lỗi: {res['error']}")
                else:
                    results.append(res)

            progress.progress((i + 1) / len(lines))

    # ================= GROUP + FILTER IP CŨ =================
    ip_map = defaultdict(list)

    for r in results:
        ip = r["proxy"].split(":")[0]

        if ip in st.session_state.used_ips:
            continue

        ip_map[ip].append(r)

    st.success(f"Tổng API: {len(lines)} | Proxy mới: {len(ip_map)} | Đã dùng: {len(st.session_state.used_ips)}")

    # ================= HIỂN THỊ =================
    st.markdown("## 📦 DANH SÁCH PROXY")

    final_output = []

    for ip, items in ip_map.items():

        if len(items) == 1:
            r = items[0]
            final_output.append(r["proxy"])
            st.session_state.used_ips.add(ip)

            st.markdown(f"""
            <div class="box good">
                {r["proxy"]}
                <div class="meta">
                    ⏳ {r["live"]}s | 💀 {r["die"]}s | 🔄 {r["next"]}s
                </div>
            </div>
            """, unsafe_allow_html=True)

        else:
            best = max(items, key=lambda x: x["live"])
            final_output.append(best["proxy"])
            st.session_state.used_ips.add(ip)

            st.markdown(f"""
            <div class="box bad">
                {best["proxy"]} (x{len(items)})
                <div class="meta">
                    ⏳ {best["live"]}s | 💀 {best["die"]}s | 🔄 {best["next"]}s
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ================= COPY =================
    st.markdown("## 📋 COPY ALL")
    st.text_area("", "\n".join(final_output), height=250)