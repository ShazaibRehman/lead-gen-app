import streamlit as st
import pandas as pd
import requests
import time
import json
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

st.set_page_config(
    page_title="Lead Generation Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    h1 { color: #1F4E78; border-bottom: 3px solid #1F4E78; padding-bottom: 1rem; }
    .success-msg { background-color: #d4edda; padding: 1rem; border-radius: 0.5rem; }
    .info-msg { background-color: #d1ecf1; padding: 1rem; border-radius: 0.5rem; }
</style>
""", unsafe_allow_html=True)

class LeadAPI:
    def __init__(self, google_key, serpapi_key):
        self.google_key = google_key
        self.serpapi_key = serpapi_key

    def search_businesses(self, query, limit=20):
        businesses = []
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.google_key,
            "X-Goog-FieldMask": "places.displayName,places.websiteUri,places.nationalPhoneNumber,places.formattedAddress"
        }
        payload = {"textQuery": query, "pageSize": min(20, limit)}

        for attempt in range(3):
            try:
                r = requests.post("https://places.googleapis.com/v1/places:searchText", 
                    json=payload, headers=headers, timeout=15)
                if r.status_code == 200:
                    for p in r.json().get("places", []):
                        if len(businesses) >= limit: break
                        nm = p.get("displayName", {})
                        name = nm.get("text", "") if isinstance(nm, dict) else ""
                        if name:
                            businesses.append({
                                "Company Name": name.strip(),
                                "Address": p.get("formattedAddress", ""),
                                "Web Link": p.get("websiteUri", ""),
                                "Phone": p.get("nationalPhoneNumber", ""),
                                "Email": "N/A",
                                "About": "N/A"
                            })
                    return businesses
                if attempt < 2: time.sleep(2)
            except:
                if attempt < 2: time.sleep(2)
        return businesses

    def search_executive(self, company):
        for query in [f"{company} CEO", f"{company} director"]:
            for att in range(2):
                try:
                    params = {"q": query, "engine": "google", "api_key": self.serpapi_key, "num": 5}
                    r = requests.get("https://api.serpapi.com/search", params=params, timeout=15)
                    if r.status_code == 200:
                        for res in r.json().get("organic_results", []):
                            if "linkedin" in res.get("link", "").lower():
                                return {
                                    "Executive Name": res.get("snippet", "")[:50],
                                    "Role": "Executive",
                                    "LinkedIn Profile": res.get("link", ""),
                                    "About": res.get("snippet", "")[:300]
                                }
                    if att == 0: time.sleep(1)
                except:
                    if att == 0: time.sleep(1)
        return {"Executive Name": "Not Found", "Role": "Not Found", "LinkedIn Profile": "Not Found", "About": ""}

    def generate(self, btype, loc, cnt):
        biz = self.search_businesses(f"{btype} {loc}", cnt)
        execs = []
        for b in biz:
            e = self.search_executive(b["Company Name"])
            e["Company Name"] = b["Company Name"]
            execs.append(e)
            time.sleep(0.3)
        return biz, execs

def make_excel(df_b, df_e):
    wb = Workbook()
    wb.remove(wb.active)
    
    h_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    h_font = Font(bold=True, color="FFFFFF", size=12, name="Calibri")
    d_font = Font(name="Calibri", size=11)
    alt_fill = PatternFill(start_color="F2F2F2", fill_type="solid")
    b = Border(left=Side(style="thin", color="D3D3D3"), right=Side(style="thin", color="D3D3D3"),
        top=Side(style="thin", color="D3D3D3"), bottom=Side(style="thin", color="D3D3D3"))

    ws1 = wb.create_sheet("Business Leads")
    cols1 = ["Company Name", "Address", "Web Link", "Email", "Phone", "About"]
    for i, h in enumerate(cols1, 1):
        c = ws1.cell(1, i)
        c.value, c.fill, c.font, c.border = h, h_fill, h_font, b
        c.alignment = Alignment(horizontal="center", wrap_text=True)
    
    for ri, row in df_b.iterrows():
        for ci, col in enumerate(cols1, 1):
            c = ws1.cell(ri+2, ci)
            c.value, c.font, c.border = row.get(col, ""), d_font, b
            if (ri+2) % 2 == 0: c.fill = alt_fill
    
    for col in "ABCDEF": ws1.column_dimensions[col].width = [32,42,35,30,18,40]["ABCDEF".find(col)]
    ws1.row_dimensions[1].height = 25

    ws2 = wb.create_sheet("Executive Leads")
    cols2 = ["Executive Name", "Company Name", "Role", "LinkedIn Profile", "About"]
    for i, h in enumerate(cols2, 1):
        c = ws2.cell(1, i)
        c.value, c.fill, c.font, c.border = h, h_fill, h_font, b
        c.alignment = Alignment(horizontal="center", wrap_text=True)
    
    for ri, row in df_e.iterrows():
        for ci, col in enumerate(cols2, 1):
            c = ws2.cell(ri+2, ci)
            c.value, c.font, c.border = row.get(col, ""), d_font, b
            if (ri+2) % 2 == 0: c.fill = alt_fill
    
    for col in "ABCDE": ws2.column_dimensions[col].width = [30,32,30,40,42]["ABCDE".find(col)]
    ws2.row_dimensions[1].height = 25

    out = BytesIO()
    wb.save(out)
    out.seek(0)
    return out

try:
    with open("/sessions/loving-focused-ride/mnt/lead-gen-plugin/config/credentials.json") as f:
        c = json.load(f)
        KEY_G = c["google_places_api_key"]
        KEY_S = c["serpapi_api_key"]
except:
    st.error("❌ API credentials not configured")
    st.stop()

col1, col2 = st.columns([3,1])
with col1: st.title("🎯 Lead Generation Platform")
st.markdown("**Discover and reach decision-makers at your target companies**")
st.divider()

with st.sidebar:
    st.header("⚙️ Search")
    btype = st.text_input("Business Type", "law firms")
    loc = st.text_input("Location", "Florida")
    cnt = st.slider("Results", 5, 50, 20)

col1, col2, col3 = st.columns(3)
with col1: st.metric("Type", btype)
with col2: st.metric("Location", loc)
with col3: st.metric("Count", cnt)

if st.button("🔍 Generate Leads", use_container_width=True, type="primary"):
    st.info("⏳ Searching for businesses and executives...")
    pb = st.progress(0)
    txt = st.empty()
    
    api = LeadAPI(KEY_G, KEY_S)
    txt.text("Searching businesses...")
    pb.progress(25)
    
    biz, execs = api.generate(btype, loc, cnt)
    pb.progress(100)
    txt.empty()
    
    if biz:
        st.markdown(f"<div class='success-msg'>✅ Found {len(biz)} businesses and {len([e for e in execs if e['Executive Name'] != 'Not Found'])} executives!</div>", unsafe_allow_html=True)
        st.divider()
        st.subheader("📋 Business Leads")
        st.dataframe(pd.DataFrame(biz), use_container_width=True, hide_index=True)
        st.subheader("👔 Executive Leads")
        st.dataframe(pd.DataFrame(execs), use_container_width=True, hide_index=True)
        
        st.divider()
        st.subheader("💾 Download")
        df_b = pd.DataFrame(biz)
        df_e = pd.DataFrame(execs)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            fn = f"{btype} {loc} business leads.xlsx"
            st.download_button("📊 Excel", make_excel(df_b, df_e), fn,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col2:
            st.download_button("📄 Business CSV", df_b.to_csv(index=False),
                f"{btype}_{loc}_business.csv", "text/csv", use_container_width=True)
        with col3:
            st.download_button("📄 Executive CSV", df_e.to_csv(index=False),
                f"{btype}_{loc}_executive.csv", "text/csv", use_container_width=True)
    else:
        st.error("❌ No results found. Try different search terms.")

st.divider()
st.markdown("<center><small>Lead Generation Platform © 2026 | Powered by Google Places & SerpAPI</small></center>", unsafe_allow_html=True)
