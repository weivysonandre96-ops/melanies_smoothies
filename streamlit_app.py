# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# App title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom smoothie!")

# Connect to Snowflake (apenas funciona dentro do Snowflake)
cnx = st.connection("snowflake")
session = cnx.session()

# Name input
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Get fruit list from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Convert Snowpark DF → Python list
fruit_options = my_dataframe.collect()
fruit_names = [row['FRUIT_NAME'] for row in fruit_options]

# Multiselect
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_names,
    max_selections=5
)

# API request (seu complemento)
st.subheader("🍉 Info about a fruit: Watermelon")
st.subheader(fruit_names + 'Nutrition Information')
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_names)

# Show API data
st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

# Submit order
if ingredients_list:

    ingredients_string = " ".join(ingredients_list)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
