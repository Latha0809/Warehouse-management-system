# dashboard.py
import streamlit as st
import pandas as pd
import mysql.connector

st.markdown("""
<style>

/*Dark Blue Background */
[data-testid="stAppViewContainer"] {
    background-color: #0b1d51;
    color: white;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #1a2a70;
}

/* Fade-in + Slide-up Animation */
@keyframes fadeSlideUp {
    0% {
        opacity: 0;
        transform: translateY(50px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Main Title Styling */
h1 {
    color: #00ffff;
    text-align: center;
    animation: fadeSlideUp 1.5s ease-out;
}

/* Subheadings */
h2, h3 {
    color: #87ceeb;
}

/* Buttons */
.stButton>button {
    background-color: #00ffff;
    color: #0b1d51;
    border-radius: 10px;
    font-weight: bold;
}

/* Table text */
.stDataFrame {
    color: white;
}

</style>
""", unsafe_allow_html=True)

# 1️ Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root123",
    database="WarehouseDB"
)
cursor = conn.cursor(dictionary=True)

# 2️ Dashboard Title (animation applies here)
st.title("📦 Inventory & Warehouse Management Dashboard")
st.write("Manage products, warehouses, stock, transactions, and purchase orders interactively.")

# -----------------------
# 3️⃣ Display Tables
# -----------------------

def load_table(query):
    return pd.read_sql(query, conn)

st.subheader("Products Table")
products_df = load_table("SELECT * FROM Products")
st.dataframe(products_df)

st.subheader("Warehouses Table")
warehouse_df = load_table("SELECT * FROM Warehouse")
st.dataframe(warehouse_df)

st.subheader("Suppliers Table")
suppliers_df = load_table("SELECT * FROM Suppliers")
st.dataframe(suppliers_df)

st.subheader("Inventory Table")
inventory_df = load_table("""
    SELECT i.inventory_id, w.warehouse_name, p.product_name, i.quantity
    FROM Inventory i
    JOIN Products p ON i.product_id = p.product_id
    JOIN Warehouse w ON i.warehouse_id = w.warehouse_id
""")
st.dataframe(inventory_df)

st.subheader("Transactions Table")
transactions_df = load_table("""
    SELECT t.transaction_id, p.product_name, t.type, t.quantity, t.date, w.warehouse_name
    FROM Transactions t
    JOIN Products p ON t.product_id = p.product_id
    LEFT JOIN Inventory i ON t.inventory_id = i.inventory_id
    LEFT JOIN Warehouse w ON i.warehouse_id = w.warehouse_id
""")
st.dataframe(transactions_df)

st.subheader("Pending Purchase Orders")
purchase_orders_df = load_table("""
    SELECT po.order_id, s.supplier_name, p.product_name, po.quantity, po.order_date, po.status
    FROM PurchaseOrders po
    JOIN Suppliers s ON po.supplier_id = s.supplier_id
    JOIN Products p ON po.product_id = p.product_id
    WHERE po.status='Pending'
""")
st.dataframe(purchase_orders_df)

# 4️ Charts

st.subheader("📊 Total Stock per Product")
total_stock_df = load_table("""
    SELECT p.product_name, SUM(i.quantity) AS total_quantity
    FROM Inventory i
    JOIN Products p ON i.product_id = p.product_id
    GROUP BY p.product_name
""")
st.bar_chart(total_stock_df.set_index('product_name'))

st.subheader("📊 Stock per Warehouse")
stock_warehouse_df = load_table("""
    SELECT w.warehouse_name, p.product_name, i.quantity
    FROM Inventory i
    JOIN Products p ON i.product_id = p.product_id
    JOIN Warehouse w ON i.warehouse_id = w.warehouse_id
""")
st.dataframe(stock_warehouse_df)

st.subheader("⚠️ Low Stock Alerts")
low_stock_df = load_table("""
    SELECT p.product_name, i.quantity
    FROM Inventory i
    JOIN Products p ON i.product_id = p.product_id
    WHERE i.quantity < 20
""")
st.dataframe(low_stock_df)

# 5️ Insert New Data Forms

st.subheader("➕ Add New Product")
with st.form("add_product_form"):
    product_name = st.text_input("Product Name")
    price = st.number_input("Price", min_value=0)
    category = st.text_input("Category")
    submitted = st.form_submit_button("Add Product")
    if submitted:
        cursor.execute("INSERT INTO Products (product_name, price, category) VALUES (%s, %s, %s)",
                       (product_name, price, category))
        conn.commit()
        st.success(f"Product '{product_name}' added successfully!")

st.subheader("➕ Add New Warehouse")
with st.form("add_warehouse_form"):
    warehouse_name = st.text_input("Warehouse Name")
    location = st.text_input("Location")
    submitted = st.form_submit_button("Add Warehouse")
    if submitted:
        cursor.execute("INSERT INTO Warehouse (warehouse_name, location) VALUES (%s, %s)",
                       (warehouse_name, location))
        conn.commit()
        st.success(f"Warehouse '{warehouse_name}' added successfully!")

st.subheader("➕ Add New Inventory")
with st.form("add_inventory_form"):
    product_id = st.selectbox("Select Product", products_df['product_id'])
    warehouse_id = st.selectbox("Select Warehouse", warehouse_df['warehouse_id'])
    quantity = st.number_input("Quantity", min_value=0)
    submitted = st.form_submit_button("Add Inventory")
    if submitted:
        cursor.execute("INSERT INTO Inventory (product_id, warehouse_id, quantity) VALUES (%s, %s, %s)",
                       (product_id, warehouse_id, quantity))
        conn.commit()
        st.success("Inventory added successfully!")

st.subheader("➕ Add New Transaction")
with st.form("add_transaction_form"):
    product_id_t = st.selectbox("Select Product", products_df['product_id'], key="trans_prod")
    inventory_id_t = st.selectbox("Select Inventory", inventory_df['inventory_id'], key="trans_inv")
    type_t = st.selectbox("Type", ["IN", "OUT"])
    quantity_t = st.number_input("Quantity", min_value=0, key="trans_qty")
    date_t = st.date_input("Date")
    submitted = st.form_submit_button("Add Transaction")
    if submitted:
        cursor.execute("""
            INSERT INTO Transactions (product_id, type, quantity, date, inventory_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (product_id_t, type_t, quantity_t, date_t, inventory_id_t))
        conn.commit()
        st.success("Transaction added successfully!")

st.subheader("➕ Add New Purchase Order")
with st.form("add_order_form"):
    supplier_id = st.selectbox("Select Supplier", suppliers_df['supplier_id'])
    product_id_po = st.selectbox("Select Product", products_df['product_id'], key="po_prod")
    quantity_po = st.number_input("Quantity", min_value=0, key="po_qty")
    order_date = st.date_input("Order Date", key="po_date")
    status = st.selectbox("Status", ["Pending", "Completed"])
    submitted = st.form_submit_button("Add Purchase Order")
    if submitted:
        cursor.execute("""
            INSERT INTO PurchaseOrders (supplier_id, product_id, quantity, order_date, status)
            VALUES (%s, %s, %s, %s, %s)
        """, (supplier_id, product_id_po, quantity_po, order_date, status))
        conn.commit()
        st.success("Purchase order added successfully!")

st.write("✅ Dashboard Loaded Successfully!")
