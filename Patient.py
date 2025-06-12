import streamlit as st
from db_config import get_connection

st.title("📝 Register New Patient")

conn = get_connection()
cursor = conn.cursor(dictionary=True)

# Fetch options for selects outside the form
cursor.execute("SELECT id, name FROM guardians")
guardians = cursor.fetchall()
guardian_options = {f"{g['id']} - {g['name']}": g['id'] for g in guardians}

cursor.execute("SELECT id, name FROM doctors")
doctors = cursor.fetchall()
doctor_options = {f"{d['id']} - {d['name']}": d['id'] for d in doctors}

cursor.execute("SELECT id, name FROM nurses")
nurses = cursor.fetchall()
nurse_options = {f"{n['id']} - {n['name']}": n['id'] for n in nurses}

with st.form("register_patient_form"):
    id = st.number_input("Patient Id", min_value=1)
    name = st.text_input("Patient Name")
    age = st.number_input("Age", 0, 120)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    phone = st.text_input("Phone Number")
    address = st.text_area("Address")
    disease = st.text_input("Disease (if any)")
    #guardian_label = st.selectbox("Guardian", list(guardian_options.keys()))
    #guardian_id = guardian_options[guardian_label]
    doctor_label = st.selectbox("Doctor", list(doctor_options.keys()))
    doctor_id = doctor_options[doctor_label]
    nurse_label = st.selectbox("Nurse", list(nurse_options.keys()))
    nurse_id = nurse_options[nurse_label]
    room_number = st.text_input("Room Number (if assigned)")
    submit = st.form_submit_button("Register Patient")

    if submit:
        try:
            cursor.execute("""
                INSERT INTO patients (id, name, age, gender, disease, doctor_id, phone, address,  nurse_id, room_number)
                VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (id, name, age, gender, disease, doctor_id, phone, address,  nurse_id, room_number))
            conn.commit()
            st.success(f"✅ Patient '{name}' registered successfully.")
        except Exception as e:
            st.error(f"❌ Error: {e}")

# Display registered patients
st.subheader("Registered Patients")
cursor.execute("""
    SELECT p.id, p.name, p.age, p.gender, p.disease, p.phone, p.address, p.room_number,
           g.name AS guardian_name, d.name AS doctor_name, n.name AS nurse_name
    FROM patients p
    LEFT JOIN guardians g ON p.guardian_id = g.id
    LEFT JOIN doctors d ON p.doctor_id = d.id
    LEFT JOIN nurses n ON p.nurse_id = n.id
""")
patients = cursor.fetchall()
st.dataframe(patients)

cursor.close()
conn.close()
