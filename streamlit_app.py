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

# ===============================
#        API FRUIT INFO
# ===============================
st.subheader("🍉 Fruit Nutrition Information")

# Selecionar **uma** fruta para ver informações nutricionais
fruit_choice = st.selectbox("Select a fruit to see details:", fruit_names)

if fruit_choice:
    st.write(f"### {fruit_choice} Nutrition Information")

    # Request da fruta selecionada
    response = requests.
