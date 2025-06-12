import streamlit as st
import mysql.connector
from db_config import get_connection

st.set_page_config(page_title="Receptionist Dashboard", layout="centered")
st.title("💁‍♀️ Receptionist Dashboard")

# Get list of all patients (id + name)
def get_all_patients():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM patients")
        return cursor.fetchall()
    except mysql.connector.Error as e:
        st.error(f"Database error: {e}")
        return []
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Get total bill for patient (pharmacy + appointments + other bills)
def get_total_bill(patient_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT 
            COALESCE(SUM(p.quantity * p.price_per_unit), 0) +
            COALESCE((SELECT SUM(charge) FROM appointments WHERE patient_id = %s), 0) +
            COALESCE((SELECT SUM(amount) FROM bills WHERE patient_id = %s), 0) AS total_bill
        FROM pharmacy p
        WHERE p.patient_id = %s
        """
        cursor.execute(query, (patient_id, patient_id, patient_id))
        result = cursor.fetchone()
        return float(result[0]) if result else 0.0

    except mysql.connector.Error as e:
        st.error(f"Database error: {e}")
        return 0.0
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Get total paid amount
def get_total_paid(patient_id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COALESCE(SUM(amount_paid), 0) FROM payments WHERE patient_id = %s", (patient_id,))
        result = cursor.fetchone()
        return float(result[0]) if result else 0.0
    except mysql.connector.Error as e:
        st.error(f"Database error: {e}")
        return 0.0
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Load patient options
patients = get_all_patients()

if not patients:
    st.warning("No patients available.")
else:
    name_to_id = {f"{name} (ID: {pid})": pid for pid, name in patients}
    selected_patient = st.selectbox("🔎 Select Patient Name", list(name_to_id.keys()))

    if "selected_patient" in locals():
        patient_id = name_to_id[selected_patient]

        # Display details
        total_bill = get_total_bill(patient_id)
        total_paid = get_total_paid(patient_id)
        remaining_amount = total_bill - total_paid
        payment_status = "Paid" if total_paid >= total_bill else "Unpaid"

        st.markdown(f"""
        ### 👤 Patient Info  
        **ID:** {patient_id}  
        **Name:** {selected_patient.split(" (ID")[0]}  

        ### 💳 Billing Summary  
        - **Total Bill:** ₹{total_bill:.2f}  
        - **Total Paid:** ₹{total_paid:.2f}  
        - **Remaining Amount:** ₹{remaining_amount:.2f}  
        - **Payment Status:** `{payment_status}`  
        """)

        # ➕ Payment Form
        st.markdown("### ➕ Add Payment")
        payment_amount = st.number_input("Enter Amount Paid (₹)", min_value=0.0, step=0.5, format="%.2f")

        if st.button("Submit Payment"):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO payments (patient_id, amount_paid) VALUES (%s, %s)",
                    (patient_id, payment_amount)
                )
                conn.commit()
                st.success(f"✅ ₹{payment_amount:.2f} recorded successfully for patient ID {patient_id}.")

                # Refresh the values
                total_paid = get_total_paid(patient_id)
                remaining_amount = total_bill - total_paid
                payment_status = "Paid" if total_paid >= total_bill else "Unpaid"

                st.info(f"""
                ### 🔁 Updated Billing Summary  
                - **Total Paid:** ₹{total_paid:.2f}  
                - **Remaining Amount:** ₹{remaining_amount:.2f}  
                - **Payment Status:** `{payment_status}`  
                """)
            except mysql.connector.Error as e:
                st.error(f"❌ Error saving payment: {e}")
            finally:
                if conn.is_connected():
                    cursor.close()
                    conn.close()
