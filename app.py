import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Sales Analytics Pro", layout="wide", page_icon="📊")

# --- DARK THEME + POWER BI FEEL ---
st.markdown("""
<style>
  .stApp { background-color: #0F0E2E; }
  .kpi-card {
        background: linear-gradient(135deg, #1e1e3f 0%, #2d2d5f 100%);
        padding: 18px; border-radius: 12px; text-align: center;
        border: 1px solid #4a4a8a; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
    }
  .kpi-value { font-size: 28px; font-weight: bold; color: #00d4ff; }
  .kpi-label { font-size: 12px; color: #b8b8d4; margin-top: 4px; }
    h1, h2, h3 { color: #ffffff!important; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>SALES DATA</h1>", unsafe_allow_html=True)

# --- FILE UPLOAD ---
file = st.file_uploader("CSV/Excel upload chey", type=['csv','xlsx','xls'])

@st.cache_data
def load_data(file):
    if file:
        if file.name.endswith('.csv'): df = pd.read_csv(file)
        else: df = pd.read_excel(file)
    else: # SAMPLE DATA - Power BI lanti data
        dates = pd.date_range(start='2022-01-01', end='2024-12-31', freq='D')
        cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune', 'Ahmedabad']
        city_lat_lon = {
            'Mumbai':[19.07,72.87], 'Delhi':[28.61,77.20], 'Bangalore':[12.97,77.59],
            'Hyderabad':[17.38,78.48], 'Chennai':[13.08,80.27], 'Kolkata':[22.57,88.36],
            'Pune':[18.52,73.85], 'Ahmedabad':[23.02,72.57]
        }
        df = pd.DataFrame({
            'Date': np.random.choice(dates, 800),
            'Sales_Amount': np.random.randint(5000, 60000, 800),
            'Profit': np.random.randint(500, 12000, 800),
            'Quantity': np.random.randint(1, 25, 800),
            'Order ID': ['ORD' + str(i) for i in range(1000, 1800)],
            'Customer_Segment': np.random.choice(['Consumer', 'Corporate', 'Home Office'], 800),
            'Product_Category': np.random.choice(['Furniture', 'Office Supplies', 'Technology'], 800),
            'Product_Sub_Category': np.random.choice(['Chairs','Tables','Storage','Phones','Laptops','Binders'], 800),
            'Region': np.random.choice(['East', 'West', 'North', 'South'], 800),
            'Payment_Mode': np.random.choice(['Cash', 'Credit Card', 'UPI', 'Debit Card'], 800),
            'City': np.random.choice(cities, 800)
        })
        df['Latitude'] = df['City'].map(lambda x: city_lat_lon[x][0])
        df['Longitude'] = df['City'].map(lambda x: city_lat_lon[x][1])

    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    if 'Month' not in df.columns: df['Month'] = df['Date'].dt.month_name()
    if 'Year' not in df.columns: df['Year'] = df['Date'].dt.year
    if 'Quarter' not in df.columns: df['Quarter'] = 'Q' + df['Date'].dt.quarter.astype(str)
    return df

df = load_data(file)

# --- SIDEBAR MAPPING ---
st.sidebar.header("⚙️ Column Mapping")
cols = df.columns.tolist()
def pick(col_name): return cols.index(col_name) if col_name in cols else 0
SALES = st.sidebar.selectbox("Sales Amount", cols, index=pick('Sales_Amount'))
PROFIT = st.sidebar.selectbox("Profit", cols, index=pick('Profit'))
QTY = st.sidebar.selectbox("Quantity", cols, index=pick('Quantity'))
SEGMENT = st.sidebar.selectbox("Customer Segment", cols, index=pick('Customer_Segment'))
CAT = st.sidebar.selectbox("Product Category", cols, index=pick('Product_Category'))
SUB_CAT = st.sidebar.selectbox("Product Sub Category", cols, index=pick('Product_Sub_Category'))
PAYMENT = st.sidebar.selectbox("Payment Mode", cols, index=pick('Payment_Mode'))
REGION = st.sidebar.selectbox("Region", cols, index=pick('Region'))
CITY = st.sidebar.selectbox("City", cols, index=pick('City'))

# --- CONVERT TO NUMERIC ---
for col in [SALES, PROFIT, QTY]:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

# --- KPI CARDS ---
total_sales = df[SALES].sum()
total_profit = df[PROFIT].sum()
total_qty = df[QTY].sum()

c1, c2, c3 = st.columns(3)
c1.markdown(f"<div class='kpi-card'><div class='kpi-value'>{total_sales:,.2f}</div><div class='kpi-label'>Sum of Sales_Amount</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='kpi-card'><div class='kpi-value'>{total_profit/1e6:.2f}M $</div><div class='kpi-label'>Sum of Profit</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='kpi-card'><div class='kpi-value'>{total_qty/1000:.0f}K</div><div class='kpi-label'>Sum of Quantity</div></div>", unsafe_allow_html=True)

st.divider()

# --- ROW 1: MONTH BAR + SEGMENT PIE ---
col1, col2 = st.columns([1,2])
with col1:
    month_order = ['January','February','March','April','May','June','July','August','September','October','November','December']
    monthly = df.groupby('Month')[SALES].sum().reindex(month_order).reset_index()
    fig = px.bar(monthly, y='Month', x=SALES, orientation='h', title='Sum of Sales_Amount by Month',
                 template='plotly_dark', color_discrete_sequence=['#4a90e2'], text_auto='.2s')
    fig.update_layout(paper_bgcolor='#0F0E2E', plot_bgcolor='#0F0E2E', height=450, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    seg = df.groupby(SEGMENT)[SALES].sum().reset_index()
    fig = px.pie(seg, names=SEGMENT, values=SALES, title='Sum of Sales_Amount by Customer_Segment',
                 template='plotly_dark', hole=0.3, color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(textposition='inside', textinfo='percent+value')
    fig.update_layout(paper_bgcolor='#0F0E2E', height=450)
    st.plotly_chart(fig, use_container_width=True)

# --- ROW 2: AVG BY SUB CATEGORY LINE ---
avg_sub = df.groupby(SUB_CAT)[SALES].mean().sort_values(ascending=False).reset_index()
fig = px.line(avg_sub, x=SUB_CAT, y=SALES, title='Average of Sales_Amount by Product_Sub_Category',
              template='plotly_dark', markers=True, color_discrete_sequence=['#00d4ff'])
fig.update_layout(paper_bgcolor='#0F0E2E', plot_bgcolor='#0F0E2E', height=350)
st.plotly_chart(fig, use_container_width=True)

# --- ROW 3: 7 CHARTS GRID ---
c1, c2, c3, c4 = st.columns(4)
with c1:
    pay = df.groupby(PAYMENT)[SALES].sum().reset_index()
    fig = px.pie(pay, names=PAYMENT, values=SALES, title='Sum of Sales_Amount by Payment_Mode',
                 template='plotly_dark', hole=0.6)
    fig.update_layout(paper_bgcolor='#0F0E2E', height=300, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    treemap = df.groupby([CAT, SUB_CAT])[SALES].sum().reset_index()
    fig = px.treemap(treemap, path=[CAT, SUB_CAT], values=SALES,
                     title='Sum of Sales_Amount by Product_Category and Product_Sub_Category',
                     template='plotly_dark')
    fig.update_layout(paper_bgcolor='#0F0E2E', height=300)
    st.plotly_chart(fig, use_container_width=True)

with c3:
    profit_year = df.groupby(['Year', REGION])[PROFIT].sum().reset_index()
    fig = px.line(profit_year, x='Year', y=PROFIT, color=REGION,
                  title='Average of Profit by Year and Region', template='plotly_dark', markers=True)
    fig.update_layout(paper_bgcolor='#0F0E2E', plot_bgcolor='#0F0E2E', height=300)
    st.plotly_chart(fig, use_container_width=True)

with c4:
    qtr_profit = df.groupby(['Quarter', REGION])[PROFIT].mean().reset_index()
    fig = px.bar(qtr_profit, x='Quarter', y=PROFIT, color=REGION,
                 title='Average of Profit by Quarter and Region', template='plotly_dark', barmode='group')
    fig.update_layout(paper_bgcolor='#0F0E2E', plot_bgcolor='#0F0E2E', height=300)
    st.plotly_chart(fig, use_container_width=True)

c5, c6, c7 = st.columns(3)
with c5:
    city_profit = df.groupby(CITY)[PROFIT].sum().sort_values().reset_index()
    fig = px.bar(city_profit, x=PROFIT, y=CITY, orientation='h',
                 title='Sum of Profit by City and Customer_Segment', template='plotly_dark')
    fig.update_layout(paper_bgcolor='#0F0E2E', plot_bgcolor='#0F0E2E', height=300, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with c6:
    # INDIA MAP - City wise Sales
    if 'Latitude' in df.columns and 'Longitude' in df.columns:
        map_df = df.groupby(['City', 'Latitude', 'Longitude'])[SALES].sum().reset_index()
        fig = px.scatter_geo(map_df, lat='Latitude', lon='Longitude', size=SALES, color=SALES,
                             hover_name='City', title='Sum of Sales_Amount by City',
                             template='plotly_dark', scope='asia', projection='natural earth')
        fig.update_geos(fitbounds="locations", visible=False, bgcolor='#0F0E2E')
        fig.update_layout(paper_bgcolor='#0F0E2E', height=300, geo=dict(bgcolor='#0F0E2E'))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Map kosam 'City', 'Latitude', 'Longitude' columns kavali")

with c7:
    region_profit = df.groupby(REGION)[PROFIT].sum().reset_index()
    fig = px.bar(region_profit, x=REGION, y=PROFIT, title='Sum of Profit by Region',
                 template='plotly_dark', color=REGION, text_auto='.2s')
    fig.update_layout(paper_bgcolor='#0F0E2E', plot_bgcolor='#0F0E2E', height=300, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)