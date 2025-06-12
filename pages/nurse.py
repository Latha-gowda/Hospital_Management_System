import streamlit as st
import mysql.connector
import bcrypt
from db_config import get_connection

# Hashing & checking
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode() if isinstance(hashed, str) else hashed)

# Streamlit UI
st.set_page_config(page_title="Nurse Portal", layout="centered")
st.title("👩‍⚕️ Nurse Portal")

if "nurse_logged_in" not in st.session_state:
    st.session_state.nurse_logged_in = False

if st.session_state.nurse_logged_in:
    st.success(f"✅ Welcome Nurse {st.session_state.nurse_name} ({st.session_state.nurse_department})")
    st.info(f"Experience: {st.session_state.nurse_experience} years")

    # Show assigned patients
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.id, p.name, p.age, p.gender, p.disease, t.treatment_details, t.medicine, t.date
            FROM patients p
            LEFT JOIN treatments t ON p.id = t.patient_id
            WHERE p.nurse_id = %s
            ORDER BY t.date DESC
        """, (st.session_state.nurse_id,))
        patients = cursor.fetchall()

        if patients:
            st.subheader("🧑‍⚕️ Assigned Patients & Treatment Info")
            for pat in patients:
                st.markdown(f"**Patient ID:** {pat['id']}")
                st.markdown(f"**Name:** {pat['name']}, **Age:** {pat['age']}, **Gender:** {pat['gender']}")
                st.markdown(f"**Disease:** {pat['disease']}")
                st.markdown(f"**Treatment:** {pat['treatment_details'] or 'No treatment info yet'}")
                st.markdown(f"**Medicine:** {pat['medicine'] or 'N/A'}")
                st.markdown(f"**Date:** {pat['date'] or 'N/A'}")
                st.markdown("---")
        else:
            st.info("No patients assigned yet.")
    except mysql.connector.Error as e:
        st.error(f"❌ Error fetching patients: {e}")
    finally:
        cursor.close()
        conn.close()

    if st.button("Logout"):
        st.session_state.nurse_logged_in = False
        st.rerun()

else:
    menu = st.selectbox("Choose Action", ["Login", "Register"])

    if menu == "Register":
        st.subheader("📋 Register New Nurse")
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        department = st.text_input("Department")
        experience = st.number_input("Years of Experience", min_value=0, step=1)
        register = st.button("Register")

        if register:
            if not (name and email and password and department):
                st.error("Please fill all required fields.")
            else:
                try:
                    conn = get_connection()
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("SELECT * FROM nurses WHERE email = %s", (email,))
                    if cursor.fetchone():
                        st.error("❌ Email already registered.")
                    else:
                        hashed_pw = hash_password(password)
                        cursor.execute("""
                            INSERT INTO nurses (name, email, password, department, experience)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (name, email, hashed_pw.decode(), department, experience))
                        conn.commit()
                        st.success("✅ Nurse registered successfully. Please login.")
                except mysql.connector.Error as e:
                    st.error(f"❌ Registration failed: {e}")
                finally:
                    cursor.close()
                    conn.close()

    elif menu == "Login":
        st.subheader("🔐 Nurse Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login = st.button("Login")

        if login:
            if not (email and password):
                st.error("Please enter email and password.")
            else:
                try:
                    conn = get_connection()
                    cursor = conn.cursor(dictionary=True)
                    cursor.execute("SELECT * FROM nurses WHERE email = %s", (email,))
                    nurse = cursor.fetchone()

                    if nurse and check_password(password, nurse["password"]):
                        st.session_state.nurse_logged_in = True
                        st.session_state.nurse_id = nurse["id"]
                        st.session_state.nurse_name = nurse["name"]
                        st.session_state.nurse_department = nurse["department"]
                        st.session_state.nurse_experience = nurse["experience"]
                        st.success(f"✅ Welcome Nurse {nurse['name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password.")
                except mysql.connector.Error as e:
                    st.error(f"❌ Login failed: {e}")
                finally:
                    cursor.close()
                    conn.close()
