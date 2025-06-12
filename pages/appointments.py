import streamlit as st
from db_config import get_connection

st.title("📅 Schedule/View Appointments")

conn = get_connection()
cursor = conn.cursor(dictionary=True)

# Schedule Appointment
with st.form("schedule_appointment"):
    
    cursor.execute("SELECT id, name FROM patients")
    patients = cursor.fetchall()
    patient_option = st.selectbox("Select Patient", patients, format_func=lambda x: x["name"])

    cursor.execute("SELECT id, name FROM doctors")
    doctors = cursor.fetchall()
    doctor_option = st.selectbox("Select Doctor", doctors, format_func=lambda x: x["name"])

    date = st.date_input("Date")
    time = st.time_input("Time")
    reason = st.text_area("Reason for Visit")
    charge = st.number_input("Consultation Charge", min_value=0, step=1000)
    submit = st.form_submit_button("Submit")

    if submit:
        cursor.execute("""
            INSERT INTO appointments (patient_id, doctor_id, date, time, reason,charge)
            VALUES (%s, %s, %s, %s, %s,%s)
        """, (patient_option["id"], doctor_option["id"], date, time, reason,charge))
        conn.commit()
        st.success("✅ Appointment booked successfully.")
        

# View Appointments
st.subheader("Scheduled Appointments")
cursor.execute("""
    SELECT  p.name AS patient, d.name AS doctor, a.date, a.time, a.reason,a.charge
    FROM appointments a
    JOIN patients p ON a.patient_id = p.id
    JOIN doctors d ON a.doctor_id = d.id
    ORDER BY a.date, a.time
""")
st.dataframe(cursor.fetchall())
