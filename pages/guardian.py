import streamlit as st
import mysql.connector
from db_config import get_connection

st.set_page_config(page_title="👨‍👩‍👧 Guardian Management", layout="centered")
st.title("👨‍👩‍👧 Add Guardian for a Patient")

def add_guardian_for_patient():
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch patient list
        cursor.execute("SELECT id, name FROM patients")
        patients = cursor.fetchall()

        if not patients:
            st.warning("No patients found.")
            return

        # Select patient
        patient_selection = st.selectbox("Select Patient", [f"{p['name']} (ID: {p['id']})" for p in patients])
        selected_patient = next(p for p in patients if f"{p['name']} (ID: {p['id']})" == patient_selection)

        st.subheader("Enter Guardian Details")
        guardian_name = st.text_input("Guardian Name")
        relation = st.text_input("Relation")
        contact = st.text_input("Contact Number")
        address = st.text_area("Address")

        if st.button("➕ Add Guardian"):
            if not all([guardian_name, relation, contact]):
                st.error("Please fill all required fields.")
            else:
                # Insert guardian
                cursor.execute("""
                    INSERT INTO guardians (name, relation, contact, address)
                    VALUES (%s, %s, %s, %s)
                """, (guardian_name, relation, contact, address))
                guardian_id = cursor.lastrowid

                # Update patient to link guardian
                cursor.execute("""
                    UPDATE patients SET guardian_id = %s WHERE id = %s
                """, (guardian_id, selected_patient["id"]))

                conn.commit()
                st.success(f"✅ Guardian added and linked to patient {selected_patient['name']} (ID: {selected_patient['id']})")

        # Display all guardians with linked patient names
        st.subheader("👨‍👩‍👧 Guardian Details")
        cursor.execute("""
            SELECT g.id, g.name AS guardian_name, g.relation, g.contact, g.address,
                   p.name AS patient_name, p.id AS patient_id
            FROM guardians g
            LEFT JOIN patients p ON g.id = p.guardian_id
            ORDER BY g.id DESC
        """)
        guardians = cursor.fetchall()
        st.dataframe(guardians)

    except mysql.connector.Error as e:
        st.error(f"❌ Failed to add guardian or fetch data: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

add_guardian_for_patient()
