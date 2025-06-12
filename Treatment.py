import streamlit as st
import mysql.connector
from datetime import date
from db_config import get_connection

st.set_page_config(page_title="Add Treatment", layout="centered")
st.title("💊 Add Patient Treatment Record")

# Get patient list
def fetch_patients():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name FROM patients")
        return cursor.fetchall()
    except mysql.connector.Error as e:
        st.error(f"Database error: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# Insert treatment
def add_treatment(patient_id, details, medicine, treat_date):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO treatments (patient_id, treatment_details, medicine, date)
            VALUES (%s, %s, %s, %s)
        """, (patient_id, details, medicine, treat_date))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        st.error(f"Failed to add treatment: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# UI
patients = fetch_patients()
if not patients:
    st.warning("No patients found.")
else:
    patient_names = {f"{p['name']} (ID: {p['id']})": p['id'] for p in patients}
    selected_patient = st.selectbox("Select Patient", list(patient_names.keys()))
    patient_id = patient_names[selected_patient]

    treatment_details = st.text_area("Treatment Details", height=100)
    medicine = st.text_input("Medicine Prescribed")
    treatment_date = st.date_input("Date", value=date.today())

    if st.button("Submit Treatment"):
        if not treatment_details or not medicine:
            st.error("All fields are required.")
        else:
            if add_treatment(patient_id, treatment_details, medicine, treatment_date):
                st.success("✅ Treatment record added successfully.")
