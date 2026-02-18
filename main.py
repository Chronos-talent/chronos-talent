import streamlit as st

st.set_page_config(page_title="Chronos Talent", page_icon="🤖")

st.title("🤖 Chronos Talent")
st.write("Hello! This is a test with NO database.")

# Simple counter to test interactivity
if "count" not in st.session_state:
    st.session_state.count = 0

if st.button("Click me"):
    st.session_state.count += 1

st.write(f"Button clicked: {st.session_state.count} times")
