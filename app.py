import streamlit as st

st.set_page_config(page_title="🏥 Hospital Management System", layout="wide")




# CSS styling
st.markdown("""
    <style>
    .big-title {
        font-size: 40px;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 30px;
    }
    .card {
        background-color: #f0f9ff;
        border: 2px solid #91caff;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        transition: all 0.3s ease;
        height: 200px;
    }
    .card:hover {
        background-color: #cce6ff;
        transform: scale(1.05);
    }
    </style>
""", unsafe_allow_html=True)

# Title
st.markdown('<div class="big-title">🏥 Welcome to Hospital Management System</div>', unsafe_allow_html=True)
st.image("hospital.jpg", use_container_width=True)

# Layout: 3 columns x 3 rows = 9 pages
cols = st.columns(3)

# Row 1
with cols[0]:
    st.markdown('<div class="card">🧑‍⚕️ <br><b>Patient</b><br>Manage patient records, admission, and vitals.</div>', unsafe_allow_html=True)
    st.page_link("pages/Patient.py", label="Go to Patient", icon="🧑‍⚕️")

with cols[1]:
    st.markdown('<div class="card">📋 <br><b>Receptionist</b><br>Handle registrations and appointments.</div>', unsafe_allow_html=True)
    st.page_link("pages/Receptionist.py", label="Go to Receptionist", icon="📋")

with cols[2]:
    st.markdown('<div class="card">💊 <br><b>Pharmacy</b><br>Issue prescriptions and manage inventory.</div>', unsafe_allow_html=True)
    st.page_link("pages/Pharmacy.py", label="Go to Pharmacy", icon="💊")

# Row 2
cols = st.columns(3)

with cols[0]:
    st.markdown('<div class="card">🩺 <br><b>Doctor</b><br>Access patient charts and treatment plans.</div>', unsafe_allow_html=True)
    st.page_link("pages/doctor.py", label="Go to Doctor", icon="🩺")

with cols[1]:
    st.markdown('<div class="card">🧑‍⚕️ <br><b>Nurse</b><br>Monitor patient status and assist doctors.</div>', unsafe_allow_html=True)
    st.page_link("pages/nurse.py", label="Go to Nurse", icon="🧑‍⚕️")

with cols[2]:
    st.markdown('<div class="card">👨‍👩‍👧 <br><b>Guardian</b><br>Track patient info and visitation details.</div>', unsafe_allow_html=True)
    st.page_link("pages/guardian.py", label="Go to Guardian", icon="👨‍👩‍👧")

# Row 3
cols = st.columns(3)

with cols[0]:
    st.markdown('<div class="card">📅 <br><b>Appointments</b><br>View and schedule upcoming visits.</div>', unsafe_allow_html=True)
    st.page_link("pages/appointments.py", label="Go to Appointments", icon="📅")

with cols[1]:
    st.markdown('<div class="card">🧾 <br><b>Billing</b><br>Generate invoices and payment records.</div>', unsafe_allow_html=True)
    st.page_link("pages/Billing.py", label="Go to Billing", icon="🧾")

with cols[2]:
    st.markdown('<div class="card">🩹 <br><b>Treatment</b><br>Manage diagnosis, treatment & reports.</div>', unsafe_allow_html=True)
    st.page_link("pages/Treatment.py", label="Go to Treatment", icon="🩹")


    