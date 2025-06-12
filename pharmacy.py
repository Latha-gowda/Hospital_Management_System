import streamlit as st
from db_config import get_connection
import mysql.connector
from datetime import date

st.set_page_config(page_title="💊 Pharmacy Management", layout="centered")
st.title("💊 Issue Medicines to Patient")

def add_medicines():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch patients
        cursor.execute("SELECT id, name FROM patients")
        patients = cursor.fetchall()

        if not patients:
            st.warning("No patients found.")
            return

        # Select patient
        patient_selection = st.selectbox("Select Patient", [f"{p['name']} (ID: {p['id']})" for p in patients])
        selected_patient = next(p for p in patients if f"{p['name']} (ID: {p['id']})" == patient_selection)

        st.subheader("📝 Add Medicines")

        num_meds = st.number_input("Number of medicines to add", min_value=1, max_value=10, value=1, step=1)
        medicine_entries = []

        with st.form("pharmacy_form"):
            for i in range(num_meds):
                st.markdown(f"### Medicine #{i+1}")
                medicine_name = st.text_input(f"Medicine Name #{i+1}", key=f"name_{i}")
                quantity = st.number_input(f"Quantity #{i+1}", min_value=1, key=f"qty_{i}")
                dosage = st.text_input(f"Dosage #{i+1} (e.g. 1-0-1)", key=f"dosage_{i}")
                price_per_unit = st.number_input(f"Price per Unit ₹ #{i+1}", min_value=0.0, key=f"price_{i}")
                issue_date = st.date_input(f"Issue Date #{i+1}", value=date.today(), key=f"date_{i}")
                medicine_entries.append({
                    "medicine_name": medicine_name,
                    "quantity": quantity,
                    "dosage": dosage,
                    "price_per_unit": price_per_unit,
                    "issue_date": issue_date
                })

            submit = st.form_submit_button("➕ Add Medicines")

        if submit:
            for med in medicine_entries:
                if med["medicine_name"] and med["quantity"] > 0:
                    cursor.execute("""
                        INSERT INTO pharmacy (patient_id, medicine_name, quantity, dosage, issue_date, price_per_unit)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        selected_patient["id"], med["medicine_name"], med["quantity"], 
                        med["dosage"], med["issue_date"], med["price_per_unit"]
                    ))
            conn.commit()
            st.success(f"✅ {len(medicine_entries)} medicines added for {selected_patient['name']}.")

        # Display all medicines for this patient
        st.subheader("📋 Issued Medicines for Patient")
        cursor.execute("SELECT * FROM pharmacy WHERE patient_id = %s", (selected_patient["id"],))
        data = cursor.fetchall()
        if data:
            st.dataframe(data)
        else:
            st.info("No medicines issued to this patient yet.")

    except mysql.connector.Error as e:
        st.error(f"❌ Database error: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

add_medicines()
