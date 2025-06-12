# Top of billing.py
import streamlit as st
from db_config import get_connection
import mysql.connector
from decimal import Decimal
from datetime import date

st.set_page_config(page_title="💰 Billing", layout="centered")
st.title("💰 Patient Billing Summary")


def billing_dashboard():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch patients
        cursor.execute("SELECT id, name FROM patients")
        patients = cursor.fetchall()

        if not patients:
            st.warning("No patients found.")
            return

        selected = st.selectbox("Select Patient", [f"{p['name']} (ID: {p['id']})" for p in patients])
        selected_patient = next(p for p in patients if f"{p['name']} (ID: {p['id']})" == selected)
        patient_id = selected_patient["id"]

        st.markdown("---")

        # 💊 Pharmacy Charges
        st.subheader("💊 Pharmacy Bill")
        cursor.execute("""
            SELECT medicine_name, quantity, price_per_unit, 
                   (quantity * price_per_unit) AS total_cost, issue_date 
            FROM pharmacy WHERE patient_id = %s
        """, (patient_id,))
        pharmacy_data = cursor.fetchall()
        total_pharmacy = sum(Decimal(str(item["total_cost"])) for item in pharmacy_data) if pharmacy_data else Decimal('0.00')

        if pharmacy_data:
            st.dataframe(pharmacy_data)
        else:
            st.info("No pharmacy data found.")
        st.success(f"Total Pharmacy Bill: ₹{total_pharmacy:.2f}")

        # 📅 Consultation Charges
        st.subheader("📅 Consultation Charges")
        cursor.execute("""
            SELECT date, charge 
            FROM appointments WHERE patient_id = %s
        """, (patient_id,))
        appointment_data = cursor.fetchall()
        total_consultation = sum(Decimal(str(item["charge"])) for item in appointment_data) if appointment_data else Decimal('0.00')

        if appointment_data:
            st.dataframe(appointment_data)
        else:
            st.info("No appointments found.")
        st.success(f"Total Consultation Charges: ₹{total_consultation:.2f}")

        # ➕ Add Custom Other Bills
        st.subheader("➕ Add Other Bills (e.g. Room, Food, Lab)")
        with st.form("add_bill_form"):
            description = st.text_input("Description (e.g., Room Bill, Food Charges)")
            amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
            billing_date = st.date_input("Billing Date", value=date.today())
            submit = st.form_submit_button("Add Bill")

            if submit:
                if description and amount > 0:
                    cursor.execute(
                        "INSERT INTO bills (patient_id, description, amount, billing_date) VALUES (%s, %s, %s, %s)",
                        (patient_id, description, Decimal(str(amount)), billing_date)
                    )
                    conn.commit()
                    st.success("✅ Bill added successfully!")
                else:
                    st.error("❌ Please provide a valid description and amount.")

        # 🧾 Show Existing Other Bills
        st.subheader("🧾 Other Bills")
        cursor.execute("SELECT billing_date, amount, description FROM bills WHERE patient_id = %s", (patient_id,))
        bills = cursor.fetchall()
        if bills:
            st.dataframe(bills)
            total_other_bills = sum(Decimal(str(b["amount"])) for b in bills)
        else:
            st.info("No other bills found.")
            total_other_bills = Decimal('0.00')
        st.success(f"Total Other Charges: ₹{total_other_bills:.2f}")

        # 📊 Final Total
        st.subheader("📊 Final Bill")
        grand_total = total_pharmacy + total_consultation + total_other_bills
        st.success(f"🧾 Total Payable Amount: ₹{grand_total:.2f}")

    except mysql.connector.Error as e:
        st.error(f"❌ Database error: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


billing_dashboard()
