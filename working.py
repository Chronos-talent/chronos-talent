import streamlit as st

st.set_page_config(page_title="Chronos Talent - Working", page_icon="✅")

st.title("✅ Chronos Talent - Working Version")
st.write("This is our fresh start!")

# Simple test
if st.button("Click to Test"):
    st.success("It works! 🎉")
else:
    st.info("Click the button above to test")
