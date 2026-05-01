import streamlit as st
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict
import time
import json

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
    background: linear-gradient(90deg,#00ffcc,#00cc99);
    color: black;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🔥 PROXY TOOL PRO MAX 🔥</div>', unsafe_allow_html=True)

# ================= INPUT =================
apis = st.text_area("📌 Dán API (mỗi dòng 1 link)", height=180)

# ================= RESET =================
if st.button("♻️ Reset IP đã dùng"):
    st.session_state.used_ips = set()
    st.success("Đã reset IP")

# ================= FIND VALUE =================
def deep_find(obj, keys):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() in keys:
                return v
            found = deep_find(v, keys)
            if found is not None:
                return found

    elif isinstance(obj, list):
        for item in obj:
            found = deep_find(item, keys)
            if found is not None:
                return found

    return None

# ================= EXTRACT PROXY =================
def extract_proxy(data):

    # ưu tiên field chuẩn
    keys = {
        "proxyhttp", "proxysocks5", "proxy", "http",
        "https", "socks5", "sock5", "ipport"
    }

    proxy = deep_find(data, keys)

    if proxy:
        return str(proxy)

    # dò string có ip:port:user:pass
    text = json.dumps(data)

    import re
    m = re.search(r'(\d+\.\d+\.\d+\.\d+:\d+(?::[^"\s]+){0,2})', text)

    if m:
        return m.group(1)

    return None

# ================= FETCH =================
def get_proxy(url):
    for _ in range(3):
        try:
            r = requests.get(url, timeout=12)
            data = r.json()

            proxy = extract_proxy(data)

            if proxy:
                live = deep_find(data, {"time", "live", "ping"}) or 0
                die = deep_find(data, {"time_die", "expire", "die"}) or "?"
                nxt = deep_find(data, {"next_allowed_in_seconds", "next", "cooldown"}) or "?"

                return {
                    "proxy": proxy,
                    "live": int(float(live)) if str(live).isdigit() else 0,
                    "die": die,
                    "next": nxt
                }

        except:
            time.sleep(1)

    return {"error": url}

# ================= RUN =================
if st.button("🚀 LẤY PROXY"):

    lines = [x.strip() for x in apis.split("\n") if x.strip()]
    results = []

    if not lines:
        st.warning("Nhập API trước")
        st.stop()

    progress = st.progress(0)

    with ThreadPoolExecutor(max_workers=60) as executor:
        futures = [executor.submit(get_proxy, url) for url in lines]

        for i, future in enumerate(as_completed(futures)):
            res = future.result()

            if res:
                if "error" in res:
                    st.warning(f"Lỗi: {res['error']}")
                else:
                    results.append(res)

            progress.progress((i + 1) / len(lines))

    # ================= GROUP =================
    ip_map = defaultdict(list)

    for r in results:
        ip = r["proxy"].split(":")[0]

        if ip in st.session_state.used_ips:
            continue

        ip_map[ip].append(r)

    st.success(
        f"Tổng API: {len(lines)} | Proxy mới: {len(ip_map)} | Đã dùng: {len(st.session_state.used_ips)}"
    )

    # ================= SHOW =================
    st.markdown("## 📦 DANH SÁCH PROXY")

    final_output = []

    for ip, items in ip_map.items():

        if len(items) == 1:
            best = items[0]
            color = "good"
        else:
            best = max(items, key=lambda x: x["live"])
            color = "bad"

        final_output.append(best["proxy"])
        st.session_state.used_ips.add(ip)

        st.markdown(f"""
        <div class="box {color}">
            {best["proxy"]} {"(x"+str(len(items))+")" if len(items)>1 else ""}
            <div class="meta">
                ⏳ {best["live"]}s | 💀 {best["die"]} | 🔄 {best["next"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ================= COPY =================
    st.markdown("## 📋 COPY ALL")
    st.text_area("", "\n".join(final_output), height=250)