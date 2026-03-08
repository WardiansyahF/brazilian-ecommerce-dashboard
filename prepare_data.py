"""
Script untuk menyiapkan data gabungan (main_data.csv) dari raw dataset E-Commerce Public Dataset.
Jalankan script ini terlebih dahulu sebelum menjalankan dashboard.
"""
import pandas as pd
import os

# Path ke folder dataset
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
DASHBOARD_DIR = os.path.join(os.path.dirname(__file__), 'dashboard')

# Load raw datasets
print("Loading datasets...")
orders_df = pd.read_csv(os.path.join(DATA_DIR, 'orders_dataset.csv'))
order_items_df = pd.read_csv(os.path.join(DATA_DIR, 'order_items_dataset.csv'))
customers_df = pd.read_csv(os.path.join(DATA_DIR, 'customers_dataset.csv'))
products_df = pd.read_csv(os.path.join(DATA_DIR, 'products_dataset.csv'))
translation_df = pd.read_csv(os.path.join(DATA_DIR, 'product_category_name_translation.csv'))
order_payments_df = pd.read_csv(os.path.join(DATA_DIR, 'order_payments_dataset.csv'))

# Convert datetime columns
print("Processing dates...")
datetime_cols = ['order_purchase_timestamp', 'order_approved_at',
                 'order_delivered_carrier_date', 'order_delivered_customer_date',
                 'order_estimated_delivery_date']
for col in datetime_cols:
    orders_df[col] = pd.to_datetime(orders_df[col], errors='coerce')

# Merge products with translation
products_df = products_df.merge(translation_df, on='product_category_name', how='left')

# Aggregate payments per order
payment_agg = order_payments_df.groupby('order_id').agg(
    payment_value=('payment_value', 'sum')
).reset_index()

# Build the main merged dataframe
print("Merging datasets...")
# order_items + orders
main_df = order_items_df.merge(orders_df, on='order_id', how='inner')

# + customers
main_df = main_df.merge(customers_df, on='customer_id', how='inner')

# + products (for category info)
main_df = main_df.merge(
    products_df[['product_id', 'product_category_name', 'product_category_name_english']],
    on='product_id',
    how='left'
)

# + payment aggregate
main_df = main_df.merge(payment_agg, on='order_id', how='left')

# Fill missing category names
main_df['product_category_name_english'] = main_df['product_category_name_english'].fillna('other')

# Data Quality: Filter date range to complete months only
# Sept-Dec 2016 very sparse (total ~312 orders), Sept 2018 only 1 order (incomplete)
# Keep only Jan 2017 - Aug 2018 for clean analysis
print("Filtering date range to Jan 2017 - Aug 2018 (complete months only)...")
main_df = main_df[
    (main_df['order_purchase_timestamp'] >= '2017-01-01') &
    (main_df['order_purchase_timestamp'] < '2018-09-01')
]

# Fill missing payment values with price + freight_value
main_df['payment_value'] = main_df['payment_value'].fillna(
    main_df['price'] + main_df['freight_value']
)

# Select columns that the dashboard needs
columns_to_keep = [
    'order_id',
    'order_item_id',
    'product_id',
    'customer_id',
    'customer_unique_id',
    'customer_city',
    'customer_state',
    'order_status',
    'order_purchase_timestamp',
    'order_delivered_customer_date',
    'product_category_name_english',
    'price',
    'freight_value',
    'payment_value',
]
main_df = main_df[columns_to_keep]

# Save to dashboard folder
os.makedirs(DASHBOARD_DIR, exist_ok=True)
output_path = os.path.join(DASHBOARD_DIR, 'main_data.csv')
main_df.to_csv(output_path, index=False)
print(f"Done! Saved {len(main_df)} rows to {output_path}")
print(f"Columns: {list(main_df.columns)}")
print(f"Date range: {main_df['order_purchase_timestamp'].min()} to {main_df['order_purchase_timestamp'].max()}")
print(f"Unique orders: {main_df['order_id'].nunique()}")
print(f"Unique customers: {main_df['customer_unique_id'].nunique()}")
