
import streamlit as st
import json

# --- Password Gate ---
st.title("🔒 PCT National Phase Estimator")
password = st.text_input("Enter Password to Continue", type="password")
if password != "Maxval@2025":
    st.warning("Access Denied ❌")
    st.stop()

st.success("Access Granted ✅")
st.header("📄 Enter PCT Details")

# Load fee table
with open("pct_country_fees.json") as f:
    fee_table = json.load(f)

# Simulated fetcher
def fetch_pct_data(pct_number):
    return {
        "filing_date": "2023-04-20",
        "priority_date": "2022-04-19",
        "claim_count": 20,
        "word_count": {
            "abstract": 150,
            "description": 3000,
            "claims": 1200
        }
    }

# Calculate logic
def calculate_costs(pct_data, selected_countries, user_claim_count, user_page_count):
    results = []
    total_word_count = sum(pct_data["word_count"].values())
    for row in fee_table:
        if row["code"] not in selected_countries:
            continue
        filing_fee = row["filing_fee_usd"]
        claim_limit = row["claim_limit"]
        page_limit = row["page_limit"]
        excess_claim_fee = row["excess_claims_fee_usd"]
        excess_page_fee = row["excess_pages_fee_usd"]
        translation_required = row["translation_required"].strip().lower() == "yes"
        translation_rate = row["translation_fees"]
        service_fee = row["service_fee_usd"]

        excess_claims = max(0, user_claim_count - claim_limit)
        excess_pages = max(0, user_page_count - page_limit)
        excess_claim_cost = excess_claims * excess_claim_fee
        excess_page_cost = excess_pages * excess_page_fee
        translation_cost = round((total_word_count / 100) * translation_rate, 2) if translation_required else 0
        total_cost = filing_fee + excess_claim_cost + excess_page_cost + translation_cost + service_fee

        results.append({
            "country": row["country"],
            "filing_fee": filing_fee,
            "excess_claim_cost": excess_claim_cost,
            "excess_page_cost": excess_page_cost,
            "translation_cost": translation_cost,
            "service_fee": service_fee,
            "total_cost": round(total_cost, 2)
        })
    return results

# Input form
pct_number = st.text_input("PCT Application Number", "PCT/US2023/123456")
claim_count = st.number_input("Number of Claims", value=22)
page_count = st.number_input("Number of Pages", value=45)

country_codes = [row["code"] + " - " + row["country"] for row in fee_table]
selected = st.multiselect("Select Countries", options=country_codes)

# Process
if st.button("Estimate Cost") and selected:
    selected_codes = [c.split(" - ")[0] for c in selected]
    data = fetch_pct_data(pct_number)
    results = calculate_costs(data, selected_codes, claim_count, page_count)

    for res in results:
        st.subheader(f"📌 {res['country']}")
        st.markdown(f"""
- Filing Fee: **${res['filing_fee']}**
- Excess Claim Fee: **${res['excess_claim_cost']}**
- Excess Page Fee: **${res['excess_page_cost']}**
- Translation Cost: **${res['translation_cost']}**
- Service Fee: **${res['service_fee']}**
- ✅ Total: **${res['total_cost']}**
        """)
