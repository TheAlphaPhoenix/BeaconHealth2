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
    
    # Insert demo data if tables are empty
    if c.execute('SELECT COUNT(*) FROM apps').fetchone()[0] == 0:
        # Insert demo apps
        demo_apps = [
            ('MindfulPath', 'Mental Health', 'AI-powered CBT therapy platform', 
             'NeuroTech', 4.8, 'FDA Cleared', 'Subscription'),
            ('DiabetesGuard', 'Chronic Disease', 'Diabetes management with CGM integration', 
             'HealthTech', 4.9, 'FDA Cleared', 'Insurance'),
            ('SleepHarmony', 'Sleep', 'Advanced sleep therapy platform', 
             'DreamTech', 4.7, 'FDA Registered', 'Freemium'),
            ('PainPal', 'Pain Management', 'VR-based pain management', 
             'ChronicCare', 4.6, 'FDA Cleared', 'Insurance'),
            ('CardioCoach', 'Heart Health', 'Cardiac rehabilitation platform', 
             'HeartTech', 4.9, 'FDA Cleared', 'Prescription')
        ]
        
        c.executemany('''
            INSERT INTO apps (name, category, description, developer, 
                            clinical_score, fda_status, price_model)
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
            ('provider', 'patient', 'DiabetesGuard Progress', 
             'How are you finding the glucose tracking features?', 'DiabetesGuard'),
            ('patient', 'provider', 'Question about MindfulPath', 
             'When is the best time to use the meditation exercises?', 'MindfulPath'),
            ('provider', 'patient', 'SleepHarmony Update', 
             'Here is your sleep therapy prescription', 'SleepHarmony')
        ]
        
        c.executemany('''
            INSERT INTO messages (sender_role, recipient_role, subject, message, app_name)
            VALUES (?, ?, ?, ?, ?)
        ''', demo_messages)
    
    conn.commit()
    conn.close()

def show_patient_experience():
    st.title("Patient Portal")
    
    # Create tabs
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
    
    # Create tabs
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
    
    # Get and display apps
    conn = sqlite3.connect('beacon_health.db')
    apps = pd.read_sql('SELECT * FROM apps', conn)
    conn.close()
    
    # Apply filters if not "All"
    if category != "All":
        apps = apps[apps['category'] == category]
    if fda_status != "All":
        apps = apps[apps['fda_status'] == fda_status]
    if price_model != "All":
        apps = apps[apps['price_model'] == price_model]
    
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
            
            conn = sqlite3.connect('beacon_health.db')
            apps = pd.read_sql('SELECT name FROM apps', conn)
            conn.close()
            
            app = st.selectbox("Related App", ["None"] + list(apps['name']))
            
            if st.form_submit_button("Send Message"):
                conn = sqlite3.connect('beacon_health.db')
                c = conn.cursor()
                c.execute('''
                    INSERT INTO messages (sender_role, recipient_role, subject, message, app_name)
                    VALUES (?, ?, ?, ?, ?)
                ''', (role, 'provider' if role == 'patient' else 'patient', 
                      subject, message, app))
                conn.commit()
                conn.close()
                st.success("Message sent!")
    
    # Message History
    st.subheader("Message History")
    conn = sqlite3.connect('beacon_health.db')
    messages = pd.read_sql('''
        SELECT * FROM messages 
        WHERE sender_role = ? OR recipient_role = ? 
        ORDER BY created_at DESC
    ''', conn, params=(role, role))
    conn.close()
    
    for _, msg in messages.iterrows():
        with st.expander(f"{msg['subject']} - {msg['created_at']}"):
            st.write(f"**From:** {msg['sender_role'].capitalize()}")
            st.write(f"**To:** {msg['recipient_role'].capitalize()}")
            if msg['app_name'] != 'None':
                st.write(f"**Related App:** {msg['app_name']}")
            st.write(f"**Message:** {msg['message']}")
            
            if st.button("Reply", key=f"reply_{msg['id']}"):
                st.session_state.replying_to = msg['id']

def show_patient_progress():
    st.header("My Health Progress")
    
    # Demo progress data
    progress_data = pd.DataFrame({
        'Week': ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
        'Engagement': [85, 92, 88, 95],
        'Wellness': [75, 80, 85, 88]
    })
    
    # Display metrics
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Current Engagement", "95%", "+7%")
    with col2:
        st.metric("Wellness Score", "88", "+3")
    
    # Progress charts
    st.subheader("Progress Over Time")
    st.line_chart(progress_data.set_index('Week'))
    
    # Progress notes
    st.subheader("Recent Updates")
    with st.expander("Latest Progress Note"):
        st.write("""
        - Completed all recommended sessions
        - Sleep quality improved
        - Stress levels decreased
        - High medication adherence
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
    
    # Overview metrics
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
    
    # Charts
    st.subheader("Patient Engagement")
    engagement_data = pd.DataFrame({
        'Day': range(1, 8),
        'Engagement': [85, 87, 82, 88, 85, 90, 87]
    })
    st.line_chart(engagement_data.set_index('Day'))

def main():
    st.set_page_config(
        page_title="Beacon Health",
        page_icon="🏥",
        layout="wide"
    )
    
    init_db()
    
    # Role selection in sidebar
    with st.sidebar:
        st.title("Beacon Health")
        st.write("Digital Therapeutics Platform")
        role = st.selectbox("Select Role", ["Patient", "Provider"])
        st.info("Demo Mode: Roles can be switched freely")
    
    # Display appropriate dashboard based on role
    if role == "Patient":
        show_patient_experience()
    else:
        show_provider_experience()

if __name__ == "__main__":
    main()
