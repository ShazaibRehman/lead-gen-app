import streamlit as st
import pandas as pd
import requests
import time
from io import BytesIO
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(page_title="Lead Generation Tool", layout="wide")

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1F4E78;
        margin-bottom: 1rem;
    }
    .subheader {
        font-size: 1.2rem;
        color: #444;
        margin-bottom: 1.5rem;
    }
    .success-box {
        background-color: #D4EDDA;
        border: 1px solid #C3E6CB;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #F8D7DA;
        border: 1px solid #F5C6CB;
        color: #721C24;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🎯 Lead Generation Tool</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Find businesses and their executives</div>', unsafe_allow_html=True)

class LeadGeneratorAPI:
    def __init__(self, google_key, serpapi_key):
        self.google_key = google_key
        self.serpapi_key = serpapi_key

    def search_google_places(self, query, max_results=20):
        """Search for businesses using Google Places API"""
        businesses = []

        try:
            headers = {
                "Content-Type": "application/json",
                "X-Goog-Api-Key": self.google_key,
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
                    if isinstance(display_name, dict):
                        name = display_name.get("text", "N/A")
                    else:
                        name = str(display_name)

                    about = "N/A"
                    summary = place.get("editorialSummary", {})
                    if isinstance(summary, dict):
                        about = summary.get("text", "N/A")

                    business = {
                        "Business Name": name,
                        "Address": place.get("formattedAddress", "N/A"),
                        "Phone": place.get("internationalPhoneNumber", "N/A"),
                        "Website": place.get("websiteUri", "N/A"),
                        "About": about[:300] if about != "N/A" else "N/A"
                    }
                    businesses.append(business)
                
                return businesses
            else:
                st.error(f"Google Places API error: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Google Places error: {str(e)}")
            st.error(f"⚠️ Error searching businesses: {str(e)}")
            return []

    def search_linkedin_executive(self, company_name):
        """Search for executives on LinkedIn"""
        search_strategies = [
            f'"{company_name}" CEO site:linkedin.com/in',
            f'"{company_name}" founder site:linkedin.com/in',
            f'"{company_name}" director site:linkedin.com/in',
            f'"{company_name}" CEO linkedin',
            f'"{company_name}" founder linkedin',
            f"{company_name} CEO",
            f"{company_name} founder",
        ]

        for query in search_strategies:
            try:
                params = {
                    "q": query,
                    "engine": "google",
                    "api_key": self.serpapi_key,
                    "num": 10,
                    "google_domain": "google.com"
                }

                response = requests.get(
                    "https://api.serpapi.com/search",
                    params=params,
                    timeout=20
                )

                if response.status_code == 200:
                    data = response.json()

                    # Try organic results first
                    for result in data.get("organic_results", []):
                        link = result.get("link", "").lower()
                        title = result.get("title", "")

                        if "linkedin.com/in" in link:
                            name = title.split("|")[0].strip() if "|" in title else title
                            if name and len(name) > 2:
                                return {
                                    "Executive Name": name[:80],
                                    "Role": "Professional",
                                    "LinkedIn Profile": result.get("link", ""),
                                    "About": result.get("snippet", "")[:300]
                                }

                    # Try people results
                    for person in data.get("people_results", []):
                        name = person.get("name", "")
                        link = person.get("link", "")
                        if name and link and "linkedin" in link.lower():
                            return {
                                "Executive Name": name[:80],
                                "Role": person.get("title", "Professional"),
                                "LinkedIn Profile": link,
                                "About": person.get("snippet", "")[:300]
                            }

                time.sleep(2)

            except Exception as e:
                logger.error(f"SerpAPI error: {str(e)}")
                time.sleep(1)

        return {
            "Executive Name": "Not Found",
            "Role": "Not Found",
            "LinkedIn Profile": "Not Found",
            "About": ""
        }

    def generate_leads(self, business_type, location, num_results=20):
        """Generate complete lead list"""
        query = f"{business_type} in {location}"

        st.info(f"🔍 Searching for {num_results} businesses...")
        businesses = self.search_google_places(query, num_results)

        if not businesses:
            st.error(f"❌ No businesses found")
            return None, None

        st.success(f"✅ Found {len(businesses)} businesses!")

        st.info("🔎 Searching for executives...")
        progress_bar = st.progress(0)

        executives = []
        for idx, business in enumerate(businesses):
            company_name = business.get("Business Name", "")
            executive = self.search_linkedin_executive(company_name)
            executive["Target_Company_Name"] = company_name
            executives.append(executive)
            progress_bar.progress((idx + 1) / len(businesses))
            time.sleep(1)

        st.success(f"✅ Complete!")
        return businesses, executives


def create_professional_excel(businesses_df, executives_df):
    """Create Excel with two sheets"""
    wb = Workbook()

    if 'Sheet' in wb.sheetnames:
        wb.remove(wb['Sheet'])

    # Business sheet
    ws_business = wb.create_sheet("Business Leads")
    headers_business = ["Business Name", "Website", "Phone", "Address", "About"]
    ws_business.append(headers_business)

    for _, row in businesses_df.iterrows():
        ws_business.append([
            row.get("Business Name", ""),
            row.get("Website", ""),
            row.get("Phone", ""),
            row.get("Address", ""),
            row.get("About", "")
        ])

    # Executive sheet
    ws_exec = wb.create_sheet("Executive Leads")
    headers_exec = ["Person Name", "Company Name", "Role", "LinkedIn Profile", "About"]
    ws_exec.append(headers_exec)

    for _, row in executives_df.iterrows():
        ws_exec.append([
            row.get("Executive Name", ""),
            row.get("Target_Company_Name", ""),
            row.get("Role", ""),
            row.get("LinkedIn Profile", ""),
            row.get("About", "")
        ])

    # Format
    for ws in [ws_business, ws_exec]:
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

        ws.row_dimensions[1].height = 25

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output


# Initialize session
if "businesses" not in st.session_state:
    st.session_state.businesses = None
    st.session_state.executives = None

# Check credentials
try:
    google_key = st.secrets["google_places_api_key"]
    serpapi_key = st.secrets["serpapi_api_key"]
    api = LeadGeneratorAPI(google_key, serpapi_key)
except KeyError as e:
    st.error(f"❌ Missing API key: {str(e)}")
    st.stop()

# UI
col1, col2, col3 = st.columns(3)

with col1:
    business_type = st.text_input("Business Type", placeholder="e.g., hospitals, recovery centers")

with col2:
    location = st.text_input("Location", placeholder="e.g., Florida, Texas")

with col3:
    num_results = st.number_input("Results", min_value=5, max_value=50, value=10)

if st.button("🔍 Generate Leads", use_container_width=True):
    if business_type and location:
        businesses, executives = api.generate_leads(business_type, location, num_results)

        if businesses and executives:
            st.session_state.businesses = businesses
            st.session_state.executives = executives

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Businesses", len(businesses))
            with col2:
                found = sum(1 for e in executives if e["Executive Name"] != "Not Found")
                st.metric("Executives Found", found)

            st.subheader("📍 Businesses")
            st.dataframe(pd.DataFrame(businesses), use_container_width=True, hide_index=True)

            st.subheader("👤 Executives")
            st.dataframe(pd.DataFrame(executives), use_container_width=True, hide_index=True)
    else:
        st.error("Enter business type and location")

# Download
if st.session_state.businesses and st.session_state.executives:
    st.markdown("---")
    businesses_df = pd.DataFrame(st.session_state.businesses)
    executives_df = pd.DataFrame(st.session_state.executives)

    excel_file = create_professional_excel(businesses_df, executives_df)
    filename = f"{business_type} {location} leads.xlsx".replace(" ", "_").lower()

    st.download_button(
        label="📊 Download Excel",
        data=excel_file,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
