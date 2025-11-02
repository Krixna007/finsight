"""
💼 FinSight — Smart Portfolio Manager & Investment Predictor
A stunning AI-powered financial portfolio management dashboard
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import numpy as np
import sqlite3
import hashlib
import random
from datetime import datetime

# ============================================
# 🎨 CUSTOM CSS STYLING - FUTURISTIC DARK THEME
# ============================================

def inject_custom_css():
    """Inject modern, futuristic CSS styling"""
    st.markdown("""
    <style>
    /* Import Modern Font */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* Global Styling */
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    /* Main Background */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1a2e 50%, #16213e 100%);
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1419 0%, #1a1f35 100%);
        border-right: 2px solid #00d4ff;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #00d4ff;
        font-weight: 700;
        text-shadow: 0 0 20px rgba(0, 212, 255, 0.5);
    }
    
    /* Metric Cards */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1e2a3a 0%, #2d3748 100%);
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #00d4ff;
        box-shadow: 0 8px 32px rgba(0, 212, 255, 0.2);
        transition: transform 0.3s ease;
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 212, 255, 0.4);
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > select {
        background: rgba(30, 42, 58, 0.8);
        color: #ffffff;
        border: 2px solid #00d4ff;
        border-radius: 10px;
        padding: 10px;
        font-size: 14px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #ff006e;
        box-shadow: 0 0 15px rgba(255, 0, 110, 0.5);
    }
    
    /* Data Tables */
    .dataframe {
        background: rgba(30, 42, 58, 0.6);
        border-radius: 10px;
        border: 1px solid #00d4ff;
    }
    
    /* Info Cards */
    .info-card {
        background: linear-gradient(135deg, #1e2a3a 0%, #2d3748 100%);
        padding: 25px;
        border-radius: 15px;
        border-left: 5px solid #00d4ff;
        margin: 20px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    
    /* Animated Title */
    .animated-title {
        background: linear-gradient(90deg, #00d4ff, #ff006e, #00d4ff);
        background-size: 200% auto;
        color: white;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient 3s ease infinite;
        font-size: 3em;
        font-weight: 700;
        text-align: center;
        margin-bottom: 30px;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Profile Section */
    .profile-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    </style>
    """, unsafe_allow_html=True)

# ============================================
# 🗄️ DATABASE SETUP
# ============================================

def init_database():
    """Initialize SQLite database for users and portfolios"""
    conn = sqlite3.connect('finsight.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Portfolio table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS portfolio (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            asset_name TEXT NOT NULL,
            asset_type TEXT NOT NULL,
            current_value REAL NOT NULL,
            added_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')
    
    conn.commit()
    return conn

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(conn, username, email, password):
    """Register a new user"""
    try:
        cursor = conn.cursor()
        hashed_pw = hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            (username, email, hashed_pw)
        )
        conn.commit()
        return True, "✅ Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "❌ Username or email already exists!"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def authenticate_user(conn, username, password):
    """Authenticate user login"""
    cursor = conn.cursor()
    hashed_pw = hash_password(password)
    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, hashed_pw)
    )
    return cursor.fetchone() is not None

# ============================================
# 💼 PORTFOLIO MANAGEMENT FUNCTIONS
# ============================================

def add_asset(conn, username, asset_name, asset_type, current_value):
    """Add new asset to user's portfolio"""
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO portfolio (username, asset_name, asset_type, current_value) VALUES (?, ?, ?, ?)",
            (username, asset_name, asset_type, current_value)
        )
        conn.commit()
        return True
    except Exception as e:
        st.error(f"Error adding asset: {e}")
        return False

def get_portfolio(conn, username):
    """Retrieve user's portfolio"""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, asset_name, asset_type, current_value, added_date FROM portfolio WHERE username=?",
        (username,)
    )
    data = cursor.fetchall()
    if data:
        df = pd.DataFrame(data, columns=['ID', 'Asset Name', 'Type', 'Value (₹)', 'Date Added'])
        return df
    return pd.DataFrame()

def delete_asset(conn, asset_id):
    """Delete asset from portfolio"""
    cursor = conn.cursor()
    cursor.execute("DELETE FROM portfolio WHERE id=?", (asset_id,))
    conn.commit()

# ============================================
# 📊 ANALYTICS & VISUALIZATION
# ============================================

def create_pie_chart(df):
    """Create interactive pie chart for asset distribution"""
    type_sum = df.groupby('Type')['Value (₹)'].sum().reset_index()
    
    fig = px.pie(
        type_sum,
        values='Value (₹)',
        names='Type',
        title='📊 Portfolio Distribution by Asset Type',
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.Plasma
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Value: ₹%{value:,.0f}<br>Percentage: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=14),
        title_font=dict(size=20, color='#00d4ff'),
        showlegend=True,
        height=500
    )
    
    return fig

def create_growth_chart(total_value):
    """Create simulated growth trend chart"""
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Simulate historical growth data
    np.random.seed(42)
    growth_rate = np.random.uniform(0.95, 1.05, 11)
    values = [max(total_value * 0.7, 0.0)]  # Start from 70% of current value
    
    for rate in growth_rate:
        values.append(values[-1] * rate)
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=months,
        y=values,
        mode='lines+markers',
        name='Portfolio Value',
        line=dict(color='#00d4ff', width=3),
        marker=dict(size=10, color='#ff006e', line=dict(width=2, color='white')),
        fill='tozeroy',
        fillcolor='rgba(0, 212, 255, 0.1)'
    ))
    
    fig.update_layout(
        title='📈 Portfolio Growth Trend (Last 12 Months)',
        xaxis_title='Month',
        yaxis_title='Portfolio Value (₹)',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(30, 42, 58, 0.5)',
        font=dict(color='white', size=14),
        title_font=dict(size=20, color='#00d4ff'),
        hovermode='x unified',
        height=400
    )
    
    return fig

# ============================================
# 🤖 ML PREDICTION MODEL
# ============================================

def predict_portfolio_value(current_value, years):
    """Predict future portfolio value using Linear Regression"""
    # Historical data simulation (months, value)
    X = np.array([[0], [6], [12], [18], [24], [30], [36]])  # months
    y = np.array([
        current_value * 0.7,
        current_value * 0.8,
        current_value * 0.9,
        current_value * 0.95,
        current_value,
        current_value * 1.05,
        current_value * 1.1
    ])
    
    # Train model
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict future value
    future_months = years * 12
    prediction = model.predict([[future_months]])[0]
    
    # Add realistic variance
    prediction = prediction * random.uniform(0.98, 1.08)
    
    return max(prediction, current_value * 0.8)  # Ensure minimum reasonable value

def generate_investment_advice(df, total_value):
    """Generate smart AI-driven investment advice"""
    advice = []
    
    if df.empty:
        return ["💡 Start building your portfolio by adding your first asset!"]
    
    # Calculate asset type percentages
    type_distribution = df.groupby('Type')['Value (₹)'].sum() / total_value * 100
    
    # Check for high crypto exposure
    if 'Crypto' in type_distribution and type_distribution['Crypto'] > 30:
        advice.append("⚠️ High crypto exposure detected (>30%). Consider diversifying into stable assets like mutual funds or gold.")
    
    # Check for lack of diversification
    if len(type_distribution) < 3:
        advice.append("📊 Low diversification! Try adding different asset types to balance risk and returns.")
    
    # Check for heavy concentration in one asset
    if type_distribution.max() > 50:
        advice.append("🎯 One asset type dominates your portfolio (>50%). Spread investments to reduce risk.")
    
    # Positive feedback for balanced portfolio
    if len(type_distribution) >= 4 and type_distribution.max() < 40:
        advice.append("✅ Excellent diversification! Your portfolio is well-balanced across multiple asset types.")
    
    # Check for gold allocation
    if 'Gold' not in type_distribution or type_distribution.get('Gold', 0) < 5:
        advice.append("💰 Consider adding 5-10% gold to your portfolio as a hedge against inflation.")
    
    # Growth potential advice
    if total_value < 100000:
        advice.append("🚀 Great start! Consider systematic investing (SIP) to grow your portfolio steadily.")
    elif total_value > 1000000:
        advice.append("🎉 Impressive portfolio! Consider consulting a financial advisor for tax-efficient strategies.")
    
    if not advice:
        advice.append("✅ Your portfolio looks healthy. Keep monitoring and rebalancing regularly!")
    
    return advice

# ============================================
# 💡 FINANCIAL TIPS
# ============================================

FINANCIAL_TIPS = [
    "💡 Invest regularly through SIP to benefit from rupee cost averaging.",
    "📚 Diversification is the only free lunch in investing.",
    "⏰ Time in the market beats timing the market.",
    "🎯 Set clear financial goals before making investment decisions.",
    "📊 Review and rebalance your portfolio every 6 months.",
    "💰 Emergency fund first, investments second.",
    "🔍 Research thoroughly before investing in any asset.",
    "📈 Long-term investing reduces risk and increases returns.",
    "🎓 Invest in your financial education continuously.",
    "⚖️ Balance risk and return based on your age and goals."
]

# ============================================
# 🎭 AUTHENTICATION UI
# ============================================

def show_auth_page(conn):
    """Display login/signup page"""
    st.markdown('<h1 class="animated-title">💼 FinSight</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #00d4ff; font-size: 1.2em;">Smart Portfolio Manager & Investment Predictor</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        st.subheader("Welcome Back!")
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            login_btn = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if login_btn:
                if username and password:
                    if authenticate_user(conn, username, password):
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.success("✅ Login successful!")
                        st.experimental_rerun()
                    else:
                        st.error("❌ Invalid credentials!")
                else:
                    st.warning("⚠️ Please fill all fields!")
    
    with tab2:
        st.subheader("Create Your Account")
        with st.form("signup_form"):
            new_username = st.text_input("Username", placeholder="Choose a username", key="su_user")
            new_email = st.text_input("Email", placeholder="your.email@example.com", key="su_email")
            new_password = st.text_input("Password", type="password", placeholder="Create a strong password", key="su_pw")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password", key="su_pw2")
            signup_btn = st.form_submit_button("✨ Create Account", use_container_width=True)
            
            if signup_btn:
                if new_username and new_email and new_password and confirm_password:
                    if new_password == confirm_password:
                        success, message = register_user(conn, new_username, new_email, new_password)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
                    else:
                        st.error("❌ Passwords don't match!")
                else:
                    st.warning("⚠️ Please fill all fields!")

# ============================================
# 🏠 MAIN DASHBOARD
# ============================================

def show_dashboard(conn, username):
    """Display main portfolio dashboard"""
    
    # Sidebar Profile Section
    with st.sidebar:
        st.markdown(f"""
        <div class="profile-section">
            <h2 style="margin: 0; color: white;">👤 {username}</h2>
            <p style="margin: 5px 0; color: rgba(255,255,255,0.8);">Portfolio Manager</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation
        page = st.radio("📍 Navigate", ["🏠 Dashboard", "📊 Analytics", "🔮 Predictions", "ℹ️ About"], label_visibility="collapsed")
        
        st.markdown("---")
        
        # Add Asset Form
        st.subheader("➕ Add New Asset")
        with st.form("add_asset_form"):
            asset_name = st.text_input("Asset Name", placeholder="e.g., Apple Stock", key="asset_name")
            asset_type = st.selectbox("Asset Type", ["Stock", "Crypto", "Mutual Fund", "Real Estate", "Gold", "Others"], key="asset_type")
            current_value = st.number_input("Current Value (₹)", min_value=0.0, step=1000.0, format="%.2f", key="asset_value")
            add_btn = st.form_submit_button("💾 Add Asset", use_container_width=True)
            
            if add_btn:
                if asset_name and current_value > 0:
                    if add_asset(conn, username, asset_name, asset_type, current_value):
                        st.success(f"✅ {asset_name} added successfully!")
                        st.experimental_rerun()
                else:
                    st.warning("⚠️ Please fill all fields!")
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.experimental_rerun()
    
    # Main Content
    st.markdown('<h1 class="animated-title">💼 FinSight Dashboard</h1>', unsafe_allow_html=True)
    
    # Get portfolio data
    df = get_portfolio(conn, username)
    total_value = df['Value (₹)'].sum() if not df.empty else 0
    
    if page == "🏠 Dashboard":
        # Key Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💰 Total Portfolio Worth", f"₹{total_value:,.2f}")
        with col2:
            st.metric("📦 Total Assets", len(df))
        with col3:
            avg_value = total_value / len(df) if len(df) > 0 else 0
            st.metric("📊 Average Asset Value", f"₹{avg_value:,.2f}")
        
        st.markdown("---")
        
        # Portfolio Table
        if not df.empty:
            st.subheader("📋 Your Portfolio")
            
            # Add delete buttons
            for idx, row in df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([3, 2, 2, 2, 1])
                with col1:
                    st.write(f"**{row['Asset Name']}**")
                with col2:
                    st.write(f"🏷️ {row['Type']}")
                with col3:
                    st.write(f"💵 ₹{row['Value (₹)']:,.2f}")
                with col4:
                    st.write(f"📅 {row['Date Added'][:10]}")
                with col5:
                    if st.button("🗑️", key=f"del_{row['ID']}"):
                        delete_asset(conn, row['ID'])
                        st.experimental_rerun()
            
            st.markdown("---")
            
            # Export to CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Export Portfolio to CSV",
                data=csv,
                file_name=f"portfolio_{username}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("📭 Your portfolio is empty. Add your first asset to get started!")
        
        # Random Financial Tip
        st.markdown("---")
        st.markdown(f"""
        <div class="info-card">
            <h3>💡 Financial Tip of the Day</h3>
            <p style="font-size: 1.1em; line-height: 1.8; margin: 10px 0;">{random.choice(FINANCIAL_TIPS)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Disclaimer
        st.warning("""
        ⚠️ **Disclaimer:** FinSight is an educational tool for portfolio tracking and analysis. 
        Predictions are based on historical-like simulated data and should not be considered as financial advice. 
        Always consult with a certified financial advisor before making investment decisions.
        """)
    
    elif page == "📊 Analytics":
        if not df.empty:
            st.subheader("📊 Portfolio Analytics")
            
            # Pie Chart
            fig_pie = create_pie_chart(df)
            st.plotly_chart(fig_pie, use_container_width=True)
            
            st.markdown("---")
            
            # Growth Chart
            fig_growth = create_growth_chart(total_value)
            st.plotly_chart(fig_growth, use_container_width=True)
            
            st.markdown("---")
            
            # Asset Type Breakdown Table
            st.subheader("📈 Asset Type Breakdown")
            breakdown = df.groupby('Type').agg({
                'Value (₹)': ['sum', 'count', 'mean']
            }).round(2)
            breakdown.columns = ['Total Value (₹)', 'Count', 'Avg Value (₹)']
            breakdown['Percentage'] = (breakdown['Total Value (₹)'] / total_value * 100).round(2)
            st.dataframe(breakdown.reset_index(), use_container_width=True)
        else:
            st.info("📭 No data available for analytics. Add assets to your portfolio first!")
    
    elif page == "🔮 Predictions":
        st.subheader("🔮 AI-Powered Portfolio Predictions")
        
        if total_value > 0:
            # Prediction Input
            years = st.slider("📅 Predict portfolio value after how many years?", 1, 20, 5)
            
            if st.button("🚀 Generate Prediction", use_container_width=True):
                with st.spinner("🤖 AI is analyzing your portfolio..."):
                    predicted_value = predict_portfolio_value(total_value, years)
                    growth_percentage = ((predicted_value - total_value) / total_value) * 100
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("📊 Current Portfolio Value", f"₹{total_value:,.2f}")
                    with col2:
                        st.metric(
                            f"🎯 Predicted Value ({years} years)",
                            f"₹{predicted_value:,.2f}",
                            f"{growth_percentage:,.2f}%"
                        )
                    
                    st.markdown("---")
                    
                    # Prediction Visualization
                    years_range = list(range(0, years + 1))
                    values_range = [total_value + (predicted_value - total_value) * (y / years) for y in years_range]
                    
                    fig_pred = go.Figure()
                    fig_pred.add_trace(go.Scatter(
                        x=years_range,
                        y=values_range,
                        mode='lines+markers',
                        name='Predicted Growth',
                        line=dict(color='#00ff88', width=3),
                        marker=dict(size=10),
                        fill='tozeroy',
                        fillcolor='rgba(0, 255, 136, 0.1)'
                    ))
                    
                    fig_pred.update_layout(
                        title=f'📈 {years}-Year Portfolio Growth Projection',
                        xaxis_title='Years',
                        yaxis_title='Portfolio Value (₹)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(30, 42, 58, 0.5)',
                        font=dict(color='white', size=14),
                        title_font=dict(size=20, color='#00d4ff'),
                        height=400
                    )
                    
                    st.plotly_chart(fig_pred, use_container_width=True)
            
            st.markdown("---")
            
            # Investment Advice
            st.subheader("🧠 Smart Investment Advice")
            advice_list = generate_investment_advice(df, total_value)
            
            for advice in advice_list:
                st.markdown(f"""
                <div class="info-card">
                    <p style="font-size: 1.1em; margin: 0;">{advice}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("📭 Add assets to your portfolio to see predictions and advice!")
    
    elif page == "ℹ️ About":
        st.subheader("ℹ️ About FinSight")
        
        st.markdown("""
        <div class="info-card">
            <h3>🎯 What is FinSight?</h3>
            <p style="font-size: 1.1em; line-height: 1.8;">
                FinSight is an AI-powered portfolio management platform that helps you track, analyze, and predict 
                the performance of your investment portfolio. Built with cutting-edge machine learning algorithms 
                and modern data visualization techniques, FinSight provides actionable insights to help you make 
                smarter investment decisions.
            </p>
        </div>
        
        <div class="info-card">
            <h3>✨ Key Features</h3>
            <ul style="font-size: 1.1em; line-height: 1.8;">
                <li>🔐 Secure user authentication system</li>
                <li>💼 Multi-asset portfolio management (Stocks, Crypto, Mutual Funds, Real Estate, Gold)</li>
                <li>📊 Interactive charts and analytics</li>
                <li>🤖 AI-powered portfolio value predictions</li>
                <li>🧠 Smart investment advice and diversification tips</li>
                <li>📥 Export portfolio data to CSV</li>
                <li>🎨 Beautiful, modern, futuristic UI</li>
            </ul>
        </div>
        
        <div class="info-card">
            <h3>🛠️ Technology Stack</h3>
            <ul style="font-size: 1.1em; line-height: 1.8;">
                <li><strong>Frontend:</strong> Streamlit with custom CSS</li>
                <li><strong>Database:</strong> SQLite</li>
                <li><strong>ML Model:</strong> Scikit-learn (Linear Regression)</li>
                <li><strong>Visualization:</strong> Plotly</li>
                <li><strong>Data Processing:</strong> Pandas, NumPy</li>
            </ul>
        </div>
        
        <div class="info-card">
            <h3>👨‍💻 Developer Info</h3>
            <p style="font-size: 1.1em; line-height: 1.8;">
                Created as a comprehensive financial management solution that combines modern web technologies 
                with artificial intelligence to deliver a professional-grade portfolio management experience.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# 🚀 MAIN APPLICATION
# ============================================

def main():
    """Main application entry point"""
    
    # Page Configuration
    st.set_page_config(
        page_title="💼 FinSight - Portfolio Manager",
        page_icon="💼",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inject Custom CSS
    inject_custom_css()
    
    # Initialize Database
    conn = init_database()
    
    # Session State Management
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
    
    # Route to appropriate page
    if not st.session_state.logged_in:
        show_auth_page(conn)
    else:
        show_dashboard(conn, st.session_state.username)

# ============================================
# 🎬 RUN APPLICATION
# ============================================

if __name__ == "__main__":
    main()
