import streamlit as st
import mysql.connector
import bcrypt
from db_config import get_connection

# Hash password using bcrypt
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

# Check password against hashed bcrypt password
def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode() if isinstance(hashed, str) else hashed)

# Streamlit page setup
st.set_page_config(page_title="Doctor Portal", layout="centered")
st.title("👨‍⚕️ Doctor Portal")

# Session state for login persistence
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# If logged in, show welcome and patient info
if st.session_state.logged_in:
    st.success(f"✅ Welcome Dr. {st.session_state.doctor_name} ({st.session_state.doctor_specialization})")
    st.info(f"Experience: {st.session_state.doctor_experience} years")

    # Show assigned patients
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Fetch patients assigned to this doctor
        cursor.execute("SELECT * FROM patients WHERE doctor_id = %s", (st.session_state.doctor_id,))
        patients = cursor.fetchall()

        st.subheader("🧑‍🤝‍🧑 Assigned Patients")
        if patients:
            for patient in patients:
                st.markdown(f" **Name:** {patient['name']}")
                st.markdown(f"**Age:** {patient['age']}")
                st.markdown(f"**Gender:** {patient['gender']}")
                st.markdown(f"**Disease:** {patient['disease']}")
                st.markdown(f"**Phone:** {patient['phone']}")
                st.markdown(f"**Address:** {patient['address']}") 
                st.markdown("---")
       
        else:
            st.info("No patients assigned yet.")

    except mysql.connector.Error as e:
        st.error(f"❌ Error loading patients: {e}")
    finally:
        cursor.close()
        conn.close()

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun() if hasattr(st, "experimental_rerun") else st.warning("🔄 Please refresh the page.")

else:
    menu = st.selectbox("Choose Action", ["Login", "Register"])

    if menu == "Register":
        st.subheader("📋 Register New Doctor")

        name = st.text_input("Full Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        specialization = st.text_input("Specialization")
        experience = st.number_input("Years of Experience", min_value=0, step=1)
        register = st.button("Register")

        if register:
            if not (name and email and password and specialization):
                st.error("Please fill all required fields.")
            else:
                try:
                    conn = get_connection()
                    cursor = conn.cursor(dictionary=True)

                    # Check if email already exists
                    cursor.execute("SELECT * FROM doctors WHERE email = %s", (email,))
                    if cursor.fetchone():
                        st.error("❌ Email already registered.")
                    else:
                        hashed_pw = hash_password(password)
                        cursor.execute("""
                            INSERT INTO doctors (name, email, password, specialization, experience)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (name, email, hashed_pw.decode(), specialization, experience))
                        conn.commit()
                        st.success("✅ Registration successful. Please login.")
                except mysql.connector.Error as e:
                    st.error(f"❌ Registration failed: {e}")
                finally:
                    cursor.close()
                    conn.close()

    elif menu == "Login":
        st.subheader("🔐 Doctor Login")

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

                    cursor.execute("SELECT * FROM doctors WHERE email = %s", (email,))
                    doctor = cursor.fetchone()

                    if doctor and check_password(password, doctor['password']):
                        st.session_state.logged_in = True
                        st.session_state.doctor_name = doctor['name']
                        st.session_state.doctor_specialization = doctor['specialization']
                        st.session_state.doctor_experience = doctor['experience']
                        st.session_state.doctor_id = doctor['id']  # Needed to fetch assigned patients
                        st.success(f"✅ Welcome Dr. {doctor['name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid email or password.")
                except mysql.connector.Error as e:
                    st.error(f"❌ Login failed: {e}")
                finally:
                    cursor.close()
                    conn.close()
