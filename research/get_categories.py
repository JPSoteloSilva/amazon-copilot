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
# can we dump the data into a json file like {main_category: [sub_category1, sub_category2, ...], sub_category: [sub_category1, sub_category2, ...]}
json_categories = {
    "main_category": list(df["main_category"].unique()),
    "sub_category": list(df["sub_category"].unique()),
}
# %%
import json
# dump the json file
with open("data/categories.json", "w") as f:
    json.dump(json_categories, f)
# %%
