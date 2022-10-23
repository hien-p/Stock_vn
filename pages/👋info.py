import streamlit as st
from app import * 


def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def remote_css(url):
    st.markdown(f'<link href="{url}" rel="stylesheet">', unsafe_allow_html=True)    

def icon(icon_name):
    st.markdown(f'<i class="material-icons">{icon_name}</i>', unsafe_allow_html=True)

local_css("pages/style.css")
remote_css('https://fonts.googleapis.com/icon?family=Material+Icons')

#icon("search")
selected = st.text_input("", "Search...")
st.write(selected)
button_clicked = st.button("OK")
about()