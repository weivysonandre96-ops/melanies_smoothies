# Import python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# App title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie!")

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Name input
name_on_order = st.text_input("Name on Smoothie:")
st.write("The name on your Smoothie will be:", name_on_order)

# Load Snowflake dataframe with SEARCH_ON column
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))

# Convert to pandas so we can use loc/iloc
pd_df = my_dataframe.to_pandas()

# Show dataframe (optional for debugging)
# st.dataframe(pd_df)
# st.stop()

# Fruit list for the multiselect
fruit_names = pd_df["FRUIT_NAME"].tolist()

# Multiselect
ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_names,
    max_selections=5
)

# API fruit info section
st.subheader("🍉 Fruit Nutrition Info")

if ingredients_list:
    for fruit_chosen in ingredients_list:

        # Get SEARCH_ON value from pandas df
        search_on = pd_df.loc[
            pd_df["FRUIT_NAME"] == fruit_chosen, "SEARCH_ON"
        ].iloc[0]

        st.write(f"🔎 **API search value for {fruit_chosen}:** `{search_on}`")

        # API request
        api_url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        response = requests.get(api_url)

        # Show API results
        if response.status_code == 200:
            st.dataframe(response.json(), use_container_width=True)
        else:
            st.error(f"API did not return data for {search_on}")

# Submit order
if ingredients_list and name_on_order:

    ingredients_string = ", ".join(ingredients_list)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    if st.button("Submit Order"):
        session.sql(my_insert_stmt).collect()
        st.success("Your Smoothie is ordered! ✅")
