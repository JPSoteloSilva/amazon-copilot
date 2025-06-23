# %%
import start_research
import pandas as pd

from amazon_copilot.utils import clean_data

df = pd.read_csv("data/Amazon-Products.csv")
df = clean_data(df)

# %%
df.head()
# %%
# list the unique values of the main_category column
df["main_category"].unique()
# %%
# list the unique values of the sub_category column
df["sub_category"].unique()
# %%
# create a mapping of main_category to sub_categories
category_mapping = {}
for main_cat in df["main_category"].unique():
    sub_cats = df[df["main_category"] == main_cat]["sub_category"].unique().tolist()
    category_mapping[main_cat] = sub_cats

# %%
import json
# dump the json file with proper mapping
with open("data/categories.json", "w") as f:
    json.dump(category_mapping, f, indent=2)
# %%
