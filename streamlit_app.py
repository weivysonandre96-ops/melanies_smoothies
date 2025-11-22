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
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Get FRUIT_NAME + SEARCH_ON from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options") \
    .select(col("FRUIT_NAME"), col("SEARCH_ON"))

# Convert Snowpark DF → Pandas DF
pd_df = my_dataframe.to_pandas()

# Show for debugging
st.subheader("📋 Fruit Options Table")
st.dataframe(pd_df, use_container_width=True)

# STOP so you can inspect this step (remove later)
st.stop()

# Create list of fruit names for the multiselect
fruit_names = pd_df["FRUIT_NAME"].tolist()

# Multiselect
fruit_chosen = st.multiselect(
    "Choose up to 5 ingredients:",
    fruit_names,
    max_selections=5
)

# API Lookup Section
if fruit_chosen:
    st.subheader("🔍 Nutrition Search Results")

    for fruit in fruit_chosen:
        # Get SEARCH_ON value from dataframe
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit, 'SEARCH_ON'].iloc[0]

        st.write(f"Searching for **{fruit}** using API value **{search_on}**")

        # API call
        response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)

        if response.status_code == 200:
            st.dataframe(response.json(), use_container_width=True)
        else:
            st.error(f"No API data found for: {search_on}")

# SUBMIT ORDER
if fruit_chosen:
    ingredients_string = ", ".join(fruit_chosen)

    insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    if st.button("Submit Order"):
        session.sql(insert_stmt).collect()
        st.success("Your Smoothie is ordered! 🥤✨")
