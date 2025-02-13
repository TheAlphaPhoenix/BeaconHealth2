import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

def init_db():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect('beacon_health.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            first_name TEXT,
            last_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Apps table
    c.execute('''
        CREATE TABLE IF NOT EXISTS apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            developer TEXT,
            clinical_score FLOAT,
            fda_status TEXT,
            price_model TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert demo apps if none exist
    c.execute('SELECT COUNT(*) FROM apps')
    if c.fetchone()[0] == 0:
        demo_apps = [
            ('MindfulPath', 'Mental Health', 'AI-powered CBT therapy platform', 'NeuroTech', 4.8, 'FDA Cleared', 'Subscription'),
            ('DiabetesGuard', 'Chronic Disease', 'Diabetes management with CGM integration', 'HealthTech', 4.9, 'FDA Cleared', 'Insurance'),
            ('SleepHarmony', 'Sleep', 'Advanced sleep therapy using CBT', 'DreamTech', 4.7, 'FDA Registered', 'Freemium')
        ]
        c.executemany('''
            INSERT INTO apps (name, category, description, developer, clinical_score, fda_status, price_model)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', demo_apps)
    
    conn.commit()
    conn.close()

def main():
    st.set_page_config(page_title="Beacon Health", layout="wide")
    init_db()
    
    # Session state initialization
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    
    # Sidebar
    with st.sidebar:
        if st.session_state.logged_in:
            st.write(f"Role: {st.session_state.user_role}")
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.user_role = None
                st.rerun()
    
    # Main content
    if not st.session_state.logged_in:
        show_login()
    else:
        if st.session_state.user_role == 'admin':
            show_admin_dashboard()
        elif st.session_state.user_role == 'provider':
            show_provider_dashboard()
        else:
            show_patient_dashboard()

def show_login():
    st.title("Beacon Health")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                # Demo login - in production, verify against database
                st.session_state.logged_in = True
                st.session_state.user_role = 'provider'  # Demo role
                st.rerun()
    
    with tab2:
        with st.form("register_form"):
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_pass")
            role = st.selectbox("Role", ["provider", "payer", "patient"])
            submitted = st.form_submit_button("Register")
            
            if submitted:
                st.success("Registration successful! Please login.")

def show_admin_dashboard():
    st.title("Admin Dashboard")
    
    tabs = st.tabs(["Apps Management", "User Management", "Analytics"])
    
    with tabs[0]:
        show_apps_management()
    
    with tabs[1]:
        show_user_management()
    
    with tabs[2]:
        show_analytics()

def show_apps_management():
    st.header("Digital Therapeutics Management")
    
    # Add new app form
    with st.form("add_app"):
        st.subheader("Add New App")
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("App Name")
            category = st.selectbox("Category", [
                "Mental Health",
                "Chronic Disease",
                "Sleep",
                "Pain Management"
            ])
            developer = st.text_input("Developer")
        
        with col2:
            clinical_score = st.slider("Clinical Evidence Score", 0.0, 5.0, 4.0)
            fda_status = st.selectbox("FDA Status", [
                "FDA Cleared",
                "FDA Registered",
                "FDA Pending",
                "Not Applicable"
            ])
            price_model = st.selectbox("Price Model", [
                "Free",
                "Subscription",
                "Insurance",
                "One-time Purchase"
            ])
        
        description = st.text_area("Description")
        submitted = st.form_submit_button("Add App")
        
        if submitted:
            conn = sqlite3.connect('beacon_health.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO apps (name, category, description, developer, 
                                clinical_score, fda_status, price_model)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, category, description, developer, 
                  clinical_score, fda_status, price_model))
            conn.commit()
            conn.close()
            st.success("App added successfully!")
    
    # Display existing apps
    st.subheader("Existing Apps")
    conn = sqlite3.connect('beacon_health.db')
    apps = pd.read_sql('SELECT * FROM apps', conn)
    conn.close()
    
    for _, app in apps.iterrows():
        with st.expander(f"{app['name']} - {app['category']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Developer:** {app['developer']}")
                st.write(f"**FDA Status:** {app['fda_status']}")
            with col2:
                st.write(f"**Clinical Score:** {app['clinical_score']}/5.0")
                st.write(f"**Price Model:** {app['price_model']}")
            st.write(f"**Description:** {app['description']}")

def show_user_management():
    st.header("User Management")
    
    # Demo user data
    users = pd.DataFrame({
        'Name': ['John Smith', 'Sarah Johnson', 'Michael Chen'],
        'Role': ['Provider', 'Patient', 'Provider'],
        'Status': ['Active', 'Active', 'Pending'],
        'Join Date': ['2024-01-15', '2024-02-01', '2024-02-10']
    })
    
    st.dataframe(users)

def show_analytics():
    st.header("Platform Analytics")
    
    # Demo metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Apps", "6")
        st.metric("Active Users", "124")
    with col2:
        st.metric("Providers", "45")
        st.metric("Patients", "79")
    with col3:
        st.metric("Avg Clinical Score", "4.7")
        st.metric("FDA Cleared Apps", "4")

def show_provider_dashboard():
    st.title("Provider Dashboard")
    
    tabs = st.tabs(["My Patients", "Prescribe Apps", "Monitor Progress"])
    
    with tabs[0]:
        st.header("My Patients")
        patients = pd.DataFrame({
            'Name': ['John Smith', 'Sarah Johnson'],
            'Age': [45, 32],
            'Condition': ['Diabetes', 'Anxiety'],
            'Active Apps': [2, 1]
        })
        st.dataframe(patients)
    
    with tabs[1]:
        st.header("Prescribe Digital Therapeutics")
        conn = sqlite3.connect('beacon_health.db')
        apps = pd.read_sql('SELECT * FROM apps', conn)
        conn.close()
        
        patient = st.selectbox("Select Patient", ["John Smith", "Sarah Johnson"])
        condition = st.selectbox("Condition", ["Anxiety", "Depression", "Diabetes", "Insomnia"])
        
        st.subheader("Recommended Apps")
        for _, app in apps.iterrows():
            with st.expander(f"{app['name']} - {app['category']}"):
                st.write(f"**Clinical Score:** {app['clinical_score']}/5.0")
                st.write(f"**Description:** {app['description']}")
                if st.button("Prescribe", key=f"prescribe_{app['id']}"):
                    st.success(f"Prescribed {app['name']} to {patient}")

def show_patient_dashboard():
    st.title("Patient Dashboard")
    
    tabs = st.tabs(["My Apps", "Progress", "Find Apps"])
    
    with tabs[0]:
        st.header("My Digital Therapeutics")
        with st.container():
            st.subheader("DiabetesGuard")
            st.write("Prescribed by: Dr. Smith")
            st.write("Status: Active")
            st.button("Launch App", key="launch_diabetes")
    
    with tabs[1]:
        st.header("My Progress")
        st.line_chart(pd.DataFrame({
            'Glucose Levels': [120, 118, 115, 112, 110],
            'Target': [110, 110, 110, 110, 110]
        }))
    
    with tabs[2]:
        st.header("Explore Apps")
        conn = sqlite3.connect('beacon_health.db')
        apps = pd.read_sql('SELECT * FROM apps', conn)
        conn.close()
        
        for _, app in apps.iterrows():
            with st.expander(f"{app['name']} - {app['category']}"):
                st.write(f"**Clinical Score:** {app['clinical_score']}/5.0")
                st.write(f"**Description:** {app['description']}")
                st.write(f"**FDA Status:** {app['fda_status']}")

if __name__ == "__main__":
    main()
