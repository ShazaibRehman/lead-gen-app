import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Lead Generation Tool", layout="wide")

st.markdown('<h1 style="color: #1F4E78;">🎯 Lead Generation Tool</h1>', unsafe_allow_html=True)

try:
    google_key = st.secrets["google_places_api_key"]
except KeyError:
    st.error("Missing google_places_api_key in Streamlit Secrets")
    st.stop()

def search_google_places(query, max_results=20):
    """Search for businesses using Google Places API"""
    businesses = []

    try:
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": google_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.websiteUri,places.internationalPhoneNumber,places.editorialSummary"
        }

        payload = {"textQuery": query}

        response = requests.post(
            "https://places.googleapis.com/v1/places:searchText",
            json=payload,
            headers=headers,
            timeout=20
        )

        if response.status_code == 200:
            data = response.json()
            for place in data.get("places", [])[:max_results]:
                display_name = place.get("displayName", {})
                name = display_name.get("text", "N/A") if isinstance(display_name, dict) else str(display_name)

                about = "N/A"
                summary = place.get("editorialSummary", {})
                if isinstance(summary, dict):
                    about = summary.get("text", "N/A")

                business = {
                    "Business Name": name,
                    "Website": place.get("websiteUri", "N/A"),
                    "Phone": place.get("internationalPhoneNumber", "N/A"),
                    "Address": place.get("formattedAddress", "N/A"),
                    "About": about[:300] if about != "N/A" else "N/A"
                }
                businesses.append(business)
            
            return businesses
        else:
            st.error(f"API error: {response.status_code}")
            return []

    except Exception as e:
        st.error(f"Error: {str(e)}")
        return []

def create_excel(businesses_df):
    """Create Excel file"""
    wb = Workbook()
    if 'Sheet' in wb.sheetnames:
        wb.remove(wb['Sheet'])

    ws = wb.create_sheet("Business Leads")
    headers = ["Business Name", "Website", "Phone", "Address", "About"]
    ws.append(headers)

    for _, row in businesses_df.iterrows():
        ws.append([row.get(h, "") for h in headers])

    # Format
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)

    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    light_gray_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
    thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                       top=Side(style='thin'), bottom=Side(style='thin'))

    for row_idx, row in enumerate(ws.iter_rows(min_row=2, max_row=ws.max_row), 2):
        for cell in row:
            cell.border = thin_border
            cell.alignment = Alignment(horizontal="left", vertical="top", wrap_text=True)
            if row_idx % 2 == 0:
                cell.fill = light_gray_fill

    for col, width in [("A", 25), ("B", 30), ("C", 20), ("D", 35), ("E", 30)]:
        ws.column_dimensions[col].width = width

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output

if "businesses" not in st.session_state:
    st.session_state.businesses = None

col1, col2, col3 = st.columns(3)

with col1:
    business_type = st.text_input("Business Type", placeholder="hospitals, recovery centers")

with col2:
    location = st.text_input("Location", placeholder="Florida, Texas")

with col3:
    num_results = st.number_input("Results", min_value=5, max_value=50, value=10)

if st.button("🔍 Search", use_container_width=True):
    if business_type and location:
        query = f"{business_type} in {location}"
        st.info(f"Searching for {query}...")
        businesses = search_google_places(query, num_results)

        if businesses:
            st.session_state.businesses = businesses
            st.success(f"✅ Found {len(businesses)} businesses!")

            st.dataframe(pd.DataFrame(businesses), use_container_width=True, hide_index=True)

            excel_file = create_excel(pd.DataFrame(businesses))
            filename = f"{business_type} {location} leads.xlsx".replace(" ", "_").lower()

            st.download_button(
                label="📊 Download Excel",
                data=excel_file,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        else:
            st.error("No businesses found")
    else:
        st.error("Enter business type and location")
