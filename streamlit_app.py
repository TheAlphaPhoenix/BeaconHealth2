import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

def init_db():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect('beacon_health.db')
    c = conn.cursor()
    
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
    
    # Messages table
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_role TEXT NOT NULL,
            recipient_role TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            app_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Prescriptions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT NOT NULL,
            prescribed_by TEXT NOT NULL,
            prescribed_to TEXT NOT NULL,
            status TEXT NOT NULL,
            prescribed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert demo apps if none exist
    c.execute('SELECT COUNT(*) FROM apps')
    if c.fetchone()[0] == 0:
        demo_apps = [
            ('MindfulPath', 'Mental Health', 'AI-powered CBT therapy platform with personalized interventions', 
             'NeuroTech', 4.8, 'FDA Cleared', 'Subscription'),
            ('DiabetesGuard', 'Chronic Disease', 'Comprehensive diabetes management with CGM integration', 
             'HealthTech', 4.9, 'FDA Cleared', 'Insurance'),
            ('SleepHarmony', 'Sleep', 'Advanced sleep therapy using cognitive behavioral techniques', 
             'DreamTech', 4.7, 'FDA Registered', 'Freemium'),
            ('PainPal', 'Pain Management', 'VR-based chronic pain management with biofeedback', 
             'ChronicCare', 4.6, 'FDA Cleared', 'Insurance'),
            ('CardioCoach', 'Heart Health', 'AI-driven cardiac rehabilitation platform', 
             'HeartTech', 4.9, 'FDA Cleared', 'Prescription'),
            ('AnxietyEase', 'Mental Health', 'Personalized anxiety management with real-time monitoring', 
             'MindTech', 4.7, 'FDA Registered', 'Subscription')
        ]
        c.executemany('''
            INSERT INTO apps (name, category, description, developer, clinical_score, fda_status, price_model)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', demo_apps)
        
        # Insert demo prescriptions
        demo_prescriptions = [
            ('DiabetesGuard', 'Dr. Smith', 'Demo Patient', 'Active'),
            ('MindfulPath', 'Dr. Johnson', 'Demo Patient', 'Active'),
            ('SleepHarmony', 'Dr. Smith', 'Demo Patient', 'Pending')
        ]
        c.executemany('''
            INSERT INTO prescriptions (app_name, prescribed_by, prescribed_to, status)
            VALUES (?, ?, ?, ?)
        ''', demo_prescriptions)
        
        # Insert demo messages
        demo_messages = [
            ('provider', 'patient', 'DiabetesGuard Progress', 'How are you finding the glucose tracking features?', 'DiabetesGuard'),
            ('patient', 'provider', 'Question about MindfulPath', 'When is the best time to use the meditation exercises?', 'MindfulPath'),
            ('provider', 'patient', 'SleepHarmony Prescription', 'I've prescribed SleepHarmony to help with your sleep patterns.', 'SleepHarmony')
        ]
        c.executemany('''
            INSERT INTO messages (sender_role, recipient_role, subject, message, app_name)
            VALUES (?, ?, ?, ?, ?)
        ''', demo_messages)
    
    conn.commit()
    conn.close()

def main():
    st.set_page_config(page_title="Beacon Health", layout="wide")
    init_db()
    
    # Role selection in sidebar
    with st.sidebar:
        st.title("Beacon Health")
        role = st.selectbox("Select Role", ["Patient", "Provider", "Admin"])
        st.info("Demo Mode: Roles can be switched freely")
    
    # Display appropriate dashboard based on role
    if role == "Patient":
        show_patient_experience()
    elif role == "Provider":
        show_provider_experience()
    else:
        show_admin_experience()

def show_patient_experience():
    st.title("Patient Portal")
    tabs = st.tabs(["My Apps", "Browse Apps", "Messages", "Progress"])
    
    with tabs[0]:
        show_patient_apps()
    
    with tabs[1]:
        show_app_directory(for_patient=True)
    
    with tabs[2]:
        show_messages("patient")
    
    with tabs[3]:
        show_patient_progress()

def show_provider_experience():
    st.title("Provider Portal")
    tabs = st.tabs(["Patient Management", "Prescribe Apps", "Messages", "Analytics"])
    
    with tabs[0]:
        show_provider_patients()
    
    with tabs[1]:
        show_app_directory(for_patient=False)
    
    with tabs[2]:
        show_messages("provider")
    
    with tabs[3]:
        show_provider_analytics()

def show_patient_apps():
    st.header("My Digital Therapeutics")
    
    # Prescribed Apps
    st.subheader("Prescribed Apps")
    conn = sqlite3.connect('beacon_health.db')
    prescriptions = pd.read_sql('''
        SELECT p.*, a.description, a.clinical_score, a.fda_status 
        FROM prescriptions p 
        JOIN apps a ON p.app_name = a.name 
        WHERE prescribed_to = 'Demo Patient'
    ''', conn)
    conn.close()
    
    for _, app in prescriptions.iterrows():
        with st.expander(f"{app['app_name']} - Prescribed by {app['prescribed_by']}"):
            col1, col2 = st.columns([2,1])
            with col1:
                st.write(f"**Description:** {app['description']}")
                st.write(f"**Status:** {app['status']}")
                st.write(f"**Clinical Score:** {app['clinical_score']}/5.0")
                st.write(f"**FDA Status:** {app['fda_status']}")
            with col2:
                st.button("Launch App", key=f"launch_{app['id']}")
                st.button("Message Provider", key=f"msg_{app['id']}")

def show_app_directory(for_patient=True):
    st.header("Digital Therapeutics Directory")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        category = st.selectbox("Category", [
            "All",
            "Mental Health",
            "Chronic Disease",
            "Sleep",
            "Pain Management",
            "Heart Health"
        ])
    with col2:
        fda_status = st.selectbox("FDA Status", [
            "All",
            "FDA Cleared",
            "FDA Registered"
        ])
    with col3:
        price_model = st.selectbox("Price Model", [
            "All",
            "Free",
            "Subscription",
            "Insurance",
            "Prescription"
        ])
    
    # Display apps
    conn = sqlite3.connect('beacon_health.db')
    apps = pd.read_sql('SELECT * FROM apps', conn)
    conn.close()
    
    for _, app in apps.iterrows():
        with st.expander(f"{app['name']} - {app['category']}"):
            col1, col2 = st.columns([2,1])
            with col1:
                st.write(f"**Developer:** {app['developer']}")
                st.write(f"**Description:** {app['description']}")
                st.write(f"**Clinical Score:** {app['clinical_score']}/5.0")
                st.write(f"**FDA Status:** {app['fda_status']}")
                st.write(f"**Price Model:** {app['price_model']}")
            with col2:
                if for_patient:
                    if st.button("Request Access", key=f"request_{app['id']}"):
                        st.success("Request sent to your healthcare provider")
                else:
                    if st.button("Prescribe", key=f"prescribe_{app['id']}"):
                        st.success(f"Prescribed {app['name']}")

def show_messages(role):
    st.header("Message Center")
    
    # New Message Form
    with st.expander("New Message"):
        with st.form("new_message"):
            subject = st.text_input("Subject")
            message = st.text_area("Message")
            app = st.selectbox("Related App", ["None"] + list(pd.read_sql(
                'SELECT name FROM apps', sqlite3.connect('beacon_health.db')
            )['name']))
            
            if st.form_submit_button("Send Message"):
                conn = sqlite3.connect('beacon_health.db')
                c = conn.cursor()
                c.execute('''
                    INSERT INTO messages (sender_role, recipient_role, subject, message, app_name)
                    VALUES (?, ?, ?, ?, ?)
                ''', (role, 'provider' if role == 'patient' else 'patient', subject, message, app))
                conn.commit()
                conn.close()
                st.success("Message sent!")
    
    # Message History
    st.subheader("Message History")
    conn = sqlite3.connect('beacon_health.db')
    messages = pd.read_sql(
        f"SELECT * FROM messages WHERE sender_role = ? OR recipient_role = ? ORDER BY created_at DESC",
        conn,
        params=(role, role)
    )
    conn.close()
    
    for _, msg in messages.iterrows():
        with st.expander(f"{msg['subject']} - {msg['created_at']}"):
            st.write(f"**From:** {msg['sender_role'].capitalize()}")
            st.write(f"**To:** {msg['recipient_role'].capitalize()}")
            if msg['app_name'] != 'None':
                st.write(f"**Related App:** {msg['app_name']}")
            st.write(f"**Message:** {msg['message']}")
            
            # Reply button
            if st.button("Reply", key=f"reply_{msg['id']}"):
                st.session_state.replying_to = msg['id']

def show_patient_progress():
    st.header("My Progress")
    
    # Demo progress data
    progress_data = pd.DataFrame({
        'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        'Engagement': [85, 92, 88, 95],
        'Wellness Score': [75, 80, 85, 88]
    })
    
    st.line_chart(progress_data.set_index('Week'))
    
    # Progress notes
    st.subheader("Progress Notes")
    with st.expander("Week 4 Summary"):
        st.write("""
        - Completed all recommended meditation sessions
        - Sleep quality improved by 25%
        - Stress levels decreased
        - Medication adherence at 95%
        """)

def show_provider_patients():
    st.header("Patient Management")
    
    # Demo patient list
    patients = pd.DataFrame({
        'Name': ['John Smith', 'Sarah Johnson', 'Michael Chen'],
        'Active Apps': [2, 1, 3],
        'Engagement': ['High', 'Medium', 'High'],
        'Last Check-in': ['2 days ago', '1 week ago', '3 days ago']
    })
    
    for _, patient in patients.iterrows():
        with st.expander(f"{patient['Name']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Active Apps:** {patient['Active Apps']}")
                st.write(f"**Engagement:** {patient['Engagement']}")
                st.write(f"**Last Check-in:** {patient['Last Check-in']}")
            with col2:
                st.button("View Details", key=f"details_{patient['Name']}")
                st.button("Send Message", key=f"message_{patient['Name']}")
                st.button("Prescribe App", key=f"prescribe_to_{patient['Name']}")

def show_provider_analytics():
    st.header("Provider Analytics")
    
    # Demo metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Active Patients", "15")
        st.metric("Total Prescriptions", "28")
    with col2:
        st.metric("Avg. Engagement", "87%")
        st.metric("Patient Messages", "12")
    with col3:
        st.metric("Positive Outcomes", "92%")
        st.metric("Pending Reviews", "3")

def show_admin_experience():
    st.title("Admin Portal")
    tabs = st.tabs(["App Management", "User Management", "System Analytics"])
    
    with tabs[0]:
        show_app_management()
    
    with tabs[1]:
        show_user_management()
    
    with tabs[2]:
        show_system_analytics()

def show_app_management():
    st.header("Digital Therapeutics Management")
    
    # Add new app form
    with st.form("add_app"):
        st.subheader("Add New App")
        name = st.text_input("App Name")
        category = st.selectbox("Category", [
            "Mental Health",
            "Chronic Disease",
            "Sleep",
            "Pain Management",
            "Heart Health"
        ])
        description = st.text_area("Description")
        
        col1, col2 = st.columns(2)
        with col1:
            clinical_score = st.slider("Clinical Score", 0.0, 5.0, 4.0)
            fda_status = st.selectbox("FDA Status", ["FDA Cleared", "FDA Registered"])
        with col2:
            developer = st.text_input("Developer")
            price_model = st.selectbox("Price Model", ["Free", "Subscription", "Insurance", "Prescription"])
        
        if st.form_submit_button("Add App"):
            conn = sqlite3.connect('beacon_health.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO apps (name, category, description, developer, clinical_score, fda_status, price_model)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, category,
        import streamlit as st
import pandas as pd
from datetime import datetime
import sqlite3

def init_db():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect('beacon_health.db')
    c = conn.cursor()
    
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
    
    # Messages table
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_role TEXT NOT NULL,
            recipient_role TEXT NOT NULL,
            subject TEXT NOT NULL,
            message TEXT NOT NULL,
            app_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Prescriptions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT NOT NULL,
            prescribed_by TEXT NOT NULL,
            prescribed_to TEXT NOT NULL,
            status TEXT NOT NULL,
            prescribed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert demo apps if none exist
    c.execute('SELECT COUNT(*) FROM apps')
    if c.fetchone()[0] == 0:
        demo_apps = [
            ('MindfulPath', 'Mental Health', 'AI-powered CBT therapy platform with personalized interventions', 
             'NeuroTech', 4.8, 'FDA Cleared', 'Subscription'),
            ('DiabetesGuard', 'Chronic Disease', 'Comprehensive diabetes management with CGM integration', 
             'HealthTech', 4.9, 'FDA Cleared', 'Insurance'),
            ('SleepHarmony', 'Sleep', 'Advanced sleep therapy using cognitive behavioral techniques', 
             'DreamTech', 4.7, 'FDA Registered', 'Freemium'),
            ('PainPal', 'Pain Management', 'VR-based chronic pain management with biofeedback', 
             'ChronicCare', 4.6, 'FDA Cleared', 'Insurance'),
            ('CardioCoach', 'Heart Health', 'AI-driven cardiac rehabilitation platform', 
             'HeartTech', 4.9, 'FDA Cleared', 'Prescription'),
            ('AnxietyEase', 'Mental Health', 'Personalized anxiety management with real-time monitoring', 
             'MindTech', 4.7, 'FDA Registered', 'Subscription')
        ]
        c.executemany('''
            INSERT INTO apps (name, category, description, developer, clinical_score, fda_status, price_model)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', demo_apps)
        
        # Insert demo prescriptions
        demo_prescriptions = [
            ('DiabetesGuard', 'Dr. Smith', 'Demo Patient', 'Active'),
            ('MindfulPath', 'Dr. Johnson', 'Demo Patient', 'Active'),
            ('SleepHarmony', 'Dr. Smith', 'Demo Patient', 'Pending')
        ]
        c.executemany('''
            INSERT INTO prescriptions (app_name, prescribed_by, prescribed_to, status)
            VALUES (?, ?, ?, ?)
        ''', demo_prescriptions)
        
        # Insert demo messages
        demo_messages = [
            ('provider', 'patient', 'DiabetesGuard Progress', 'How are you finding the glucose tracking features?', 'DiabetesGuard'),
            ('patient', 'provider', 'Question about MindfulPath', 'When is the best time to use the meditation exercises?', 'MindfulPath'),
            ('provider', 'patient', 'SleepHarmony Prescription', 'I've prescribed SleepHarmony to help with your sleep patterns.', 'SleepHarmony')
        ]
        c.executemany('''
            INSERT INTO messages (sender_role, recipient_role, subject, message, app_name)
            VALUES (?, ?, ?, ?, ?)
        ''', demo_messages)
    
    conn.commit()
    conn.close()

def main():
    st.set_page_config(page_title="Beacon Health", layout="wide")
    init_db()
    
    # Role selection in sidebar
    with st.sidebar:
        st.title("Beacon Health")
        role = st.selectbox("Select Role", ["Patient", "Provider", "Admin"])
        st.info("Demo Mode: Roles can be switched freely")
    
    # Display appropriate dashboard based on role
    if role == "Patient":
        show_patient_experience()
    elif role == "Provider":
        show_provider_experience()
    else:
        show_admin_experience()

def show_patient_experience():
    st.title("Patient Portal")
    tabs = st.tabs(["My Apps", "Browse Apps", "Messages", "Progress"])
    
    with tabs[0]:
        show_patient_apps()
    
    with tabs[1]:
        show_app_directory(for_patient=True)
    
    with tabs[2]:
        show_messages("patient")
    
    with tabs[3]:
        show_patient_progress()

def show_provider_experience():
    st.title("Provider Portal")
    tabs = st.tabs(["Patient Management", "Prescribe Apps", "Messages", "Analytics"])
    
    with tabs[0]:
        show_provider_patients()
    
    with tabs[1]:
        show_app_directory(for_patient=False)
    
    with tabs[2]:
        show_messages("provider")
    
    with tabs[3]:
        show_provider_analytics()

def show_patient_apps():
    st.header("My Digital Therapeutics")
    
    # Prescribed Apps
    st.subheader("Prescribed Apps")
    conn = sqlite3.connect('beacon_health.db')
    prescriptions = pd.read_sql('''
        SELECT p.*, a.description, a.clinical_score, a.fda_status 
        FROM prescriptions p 
        JOIN apps a ON p.app_name = a.name 
        WHERE prescribed_to = 'Demo Patient'
    ''', conn)
    conn.close()
    
    for _, app in prescriptions.iterrows():
        with st.expander(f"{app['app_name']} - Prescribed by {app['prescribed_by']}"):
            col1, col2 = st.columns([2,1])
            with col1:
                st.write(f"**Description:** {app['description']}")
                st.write(f"**Status:** {app['status']}")
                st.write(f"**Clinical Score:** {app['clinical_score']}/5.0")
                st.write(f"**FDA Status:** {app['fda_status']}")
            with col2:
                st.button("Launch App", key=f"launch_{app['id']}")
                st.button("Message Provider", key=f"msg_{app['id']}")

def show_app_directory(for_patient=True):
    st.header("Digital Therapeutics Directory")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        category = st.selectbox("Category", [
            "All",
            "Mental Health",
            "Chronic Disease",
            "Sleep",
            "Pain Management",
            "Heart Health"
        ])
    with col2:
        fda_status = st.selectbox("FDA Status", [
            "All",
            "FDA Cleared",
            "FDA Registered"
        ])
    with col3:
        price_model = st.selectbox("Price Model", [
            "All",
            "Free",
            "Subscription",
            "Insurance",
            "Prescription"
        ])
    
    # Display apps
    conn = sqlite3.connect('beacon_health.db')
    apps = pd.read_sql('SELECT * FROM apps', conn)
    conn.close()
    
    for _, app in apps.iterrows():
        with st.expander(f"{app['name']} - {app['category']}"):
            col1, col2 = st.columns([2,1])
            with col1:
                st.write(f"**Developer:** {app['developer']}")
                st.write(f"**Description:** {app['description']}")
                st.write(f"**Clinical Score:** {app['clinical_score']}/5.0")
                st.write(f"**FDA Status:** {app['fda_status']}")
                st.write(f"**Price Model:** {app['price_model']}")
            with col2:
                if for_patient:
                    if st.button("Request Access", key=f"request_{app['id']}"):
                        st.success("Request sent to your healthcare provider")
                else:
                    if st.button("Prescribe", key=f"prescribe_{app['id']}"):
                        st.success(f"Prescribed {app['name']}")

def show_messages(role):
    st.header("Message Center")
    
    # New Message Form
    with st.expander("New Message"):
        with st.form("new_message"):
            subject = st.text_input("Subject")
            message = st.text_area("Message")
            app = st.selectbox("Related App", ["None"] + list(pd.read_sql(
                'SELECT name FROM apps', sqlite3.connect('beacon_health.db')
            )['name']))
            
            if st.form_submit_button("Send Message"):
                conn = sqlite3.connect('beacon_health.db')
                c = conn.cursor()
                c.execute('''
                    INSERT INTO messages (sender_role, recipient_role, subject, message, app_name)
                    VALUES (?, ?, ?, ?, ?)
                ''', (role, 'provider' if role == 'patient' else 'patient', subject, message, app))
                conn.commit()
                conn.close()
                st.success("Message sent!")
    
    # Message History
    st.subheader("Message History")
    conn = sqlite3.connect('beacon_health.db')
    messages = pd.read_sql(
        f"SELECT * FROM messages WHERE sender_role = ? OR recipient_role = ? ORDER BY created_at DESC",
        conn,
        params=(role, role)
    )
    conn.close()
    
    for _, msg in messages.iterrows():
        with st.expander(f"{msg['subject']} - {msg['created_at']}"):
            st.write(f"**From:** {msg['sender_role'].capitalize()}")
            st.write(f"**To:** {msg['recipient_role'].capitalize()}")
            if msg['app_name'] != 'None':
                st.write(f"**Related App:** {msg['app_name']}")
            st.write(f"**Message:** {msg['message']}")
            
            # Reply button
            if st.button("Reply", key=f"reply_{msg['id']}"):
                st.session_state.replying_to = msg['id']

def show_patient_progress():
    st.header("My Progress")
    
    # Demo progress data
    progress_data = pd.DataFrame({
        'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        'Engagement': [85, 92, 88, 95],
        'Wellness Score': [75, 80, 85, 88]
    })
    
    st.line_chart(progress_data.set_index('Week'))
    
    # Progress notes
    st.subheader("Progress Notes")
    with st.expander("Week 4 Summary"):
        st.write("""
        - Completed all recommended meditation sessions
        - Sleep quality improved by 25%
        - Stress levels decreased
        - Medication adherence at 95%
        """)

def show_provider_patients():
    st.header("Patient Management")
    
    # Demo patient list
    patients = pd.DataFrame({
        'Name': ['John Smith', 'Sarah Johnson', 'Michael Chen'],
        'Active Apps': [2, 1, 3],
        'Engagement': ['High', 'Medium', 'High'],
        'Last Check-in': ['2 days ago', '1 week ago', '3 days ago']
    })
    
    for _, patient in patients.iterrows():
        with st.expander(f"{patient['Name']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Active Apps:** {patient['Active Apps']}")
                st.write(f"**Engagement:** {patient['Engagement']}")
                st.write(f"**Last Check-in:** {patient['Last Check-in']}")
            with col2:
                st.button("View Details", key=f"details_{patient['Name']}")
                st.button("Send Message", key=f"message_{patient['Name']}")
                st.button("Prescribe App", key=f"prescribe_to_{patient['Name']}")

def show_provider_analytics():
    st.header("Provider Analytics")
    
    # Demo metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Active Patients", "15")
        st.metric("Total Prescriptions", "28")
    with col2:
        st.metric("Avg. Engagement", "87%")
        st.metric("Patient Messages", "12")
    with col3:
        st.metric("Positive Outcomes", "92%")
        st.metric("Pending Reviews", "3")

def show_admin_experience():
    st.title("Admin Portal")
    tabs = st.tabs(["App Management", "User Management", "System Analytics"])
    
    with tabs[0]:
        show_app_management()
    
    with tabs[1]:
        show_user_management()
    
    with tabs[2]:
        show_system_analytics()

def show_app_management():
    st.header("Digital Therapeutics Management")
    
    # Add new app form
    with st.form("add_app"):
        st.subheader("Add New App")
        name = st.text_input("App Name")
        category = st.selectbox("Category", [
            "Mental Health",
            "Chronic Disease",
            "Sleep",
            "Pain Management",
            "Heart Health"
        ])
        description = st.text_area("Description")
        
        col1, col2 = st.columns(2)
        with col1:
            clinical_score = st.slider("Clinical Score", 0.0, 5.0, 4.0)
            fda_status = st.selectbox("FDA Status", ["FDA Cleared", "FDA Registered"])
        with col2:
            developer = st.text_input("Developer")
            price_model = st.selectbox("Price Model", ["Free", "Subscription", "Insurance", "Prescription"])
        
        if st.form_submit_button("Add App"):
            conn = sqlite3.connect('beacon_health.db')
            c = conn.cursor()
            c.execute('''
                INSERT INTO apps (name, category, description, developer, clinical_score, fda_status, price_model)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, category, description, developer, clinical_score, fda_status, price_model))
            conn.commit()
            conn.close()
            st.success("App added successfully!")

def show_user_management():
    st.header("User Management")
    
    # Demo user data
    users = pd.DataFrame({
        'Name': ['Dr. Smith', 'Dr. Johnson', 'John Doe', 'Sarah Smith'],
        'Role': ['Provider', 'Provider', 'Patient', 'Patient'],
        'Status': ['Active', 'Active', 'Active', 'Active'],
        'Apps Used': ['-', '-', '2', '3'],
        'Last Login': ['2 days ago', '1 day ago', '12 hours ago', '3 days ago']
    })
    
    # Display users in expandable sections
    for _, user in users.iterrows():
        with st.expander(f"{user['Name']} - {user['Role']}"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Status:** {user['Status']}")
                st.write(f"**Last Login:** {user['Last Login']}")
                if user['Role'] == 'Patient':
                    st.write(f"**Active Apps:** {user['Apps Used']}")
            with col2:
                st.button("Edit Access", key=f"edit_{user['Name']}")
                st.button("View Activity", key=f"activity_{user['Name']}")

def show_system_analytics():
    st.header("System Analytics")
    
    # Overview metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Users", "156")
        st.metric("Active Providers", "45")
    with col2:
        st.metric("Active Patients", "111")
        st.metric("Total Apps", "24")
    with col3:
        st.metric("Messages Today", "34")
        st.metric("New Prescriptions", "12")
    
    # Usage statistics
    st.subheader("Platform Usage")
    usage_data = pd.DataFrame({
        'Date': pd.date_range(start='2024-01-01', periods=7),
        'Active Users': [120, 125, 130, 128, 135, 140, 156],
        'Messages': [25, 28, 30, 27, 32, 35, 34],
        'Prescriptions': [8, 10, 9, 11, 10, 13, 12]
    })
    
    tab1, tab2 = st.tabs(["User Activity", "App Usage"])
    
    with tab1:
        st.line_chart(usage_data.set_index('Date')[['Active Users']])
    
    with tab2:
        st.line_chart(usage_data.set_index('Date')[['Messages', 'Prescriptions']])
    
    # App performance
    st.subheader("App Performance")
    conn = sqlite3.connect('beacon_health.db')
    apps = pd.read_sql('SELECT name, clinical_score, category FROM apps', conn)
    conn.close()
    
    st.bar_chart(apps.set_index('name')['clinical_score'])

if __name__ == "__main__":
    main()
