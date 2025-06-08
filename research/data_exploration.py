# %%
import start_research
import pandas as pd
import re

from amazon_copilot.schemas import Product

# %%
df = pd.read_csv("data/Amazon-Products.csv")
df.head()
# %%
df.info()
# %%
df.describe()
# %%
df.isnull().sum()

# %%
def convert_rupee_to_dollar(price_str: str) -> int:
    """
    Convert price from Indian Rupee (₹) format to USD as integer
    
    Args:
        price_str: String price in format "₹XX,XXX"
        
    Returns:
        Integer price in USD
    """
    if not isinstance(price_str, str) or not price_str:
        return 0
        
    # Extract numeric value using regex (removing ₹ and comma)
    match = re.search(r'₹([\d,]+)', price_str)
    if not match:
        return 0
        
    # Remove commas and convert to float
    rupee_amount = float(match.group(1).replace(',', ''))
    
    # Convert to USD (approximate exchange rate: 1 USD = 83 INR)
    exchange_rate = 85.50
    dollar_amount = rupee_amount / exchange_rate
    
    # Return as integer
    return int(dollar_amount)

# %%
# Example usage
if not df.empty and 'discount_price' in df.columns and 'actual_price' in df.columns:
    # Create new columns with prices in USD
    df['discount_price_usd'] = df['discount_price'].apply(convert_rupee_to_dollar)
    df['actual_price_usd'] = df['actual_price'].apply(convert_rupee_to_dollar)
    
    # Display sample results
    sample_df = df[['name', 'discount_price', 'discount_price_usd', 'actual_price', 'actual_price_usd']].head()
    print("Sample prices converted to USD:")
    print(sample_df)
# %%
df.head()
# %%
df.info()
# %%
df.describe()
# %%
# distinct values in main_category
len(df['main_category'].unique())
# %%
# distinct values in sub_category
df['sub_category'].value_counts()

# %%

from typing import Any
import csv
import pandas as pd


from amazon_copilot.database import QdrantService
from amazon_copilot.models import AmazonProduct

from amazon_copilot.schemas import DenseEmbedding, SparseEmbedding, LateInteractionEmbedding, Product



def convert_rupee_to_dollar(price_str: str) -> int:
    """
    Convert price from Indian Rupee (₹) format to USD as integer
    
    Args:
        price_str: String price in format "₹XX,XXX"
        
    Returns:
        Integer price in USD
    """
    if not isinstance(price_str, str) or not price_str:
        return 0
        
    # Extract numeric value using regex (removing ₹ and comma)
    match = re.search(r'₹([\d,]+)', price_str)
    if not match:
        return 0
        
    # Remove commas and convert to float
    rupee_amount = float(match.group(1).replace(',', ''))
    
    # Convert to USD (approximate exchange rate: 1 USD = 83 INR)
    exchange_rate = 85.50
    dollar_amount = rupee_amount / exchange_rate
    
    # Return as integer
    return int(dollar_amount)

def load_csv(
    csv_path: str = "data/Amazon-Products.csv", nrows: int | None = None
) -> list[Product]:
    with open(csv_path, "r") as file:
        reader = csv.DictReader(file)
        products = [Product(**row) for row in reader]
    return products

df = load_csv(nrows=10)
df.head()
# %%
df.info()
# %%
amazon_products = turn_to_amazon_product(df)
# %%
