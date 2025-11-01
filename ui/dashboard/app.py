import streamlit as st
import requests

st.set_page_config(page_title="Mitch AI Marketing Suite", layout="wide")
st.title("📈 Mitch — Trends → Content → Publish")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Weekly Instagram Insights")
    if st.button("Refresh insights"):
        data = requests.get("http://api-gateway:8000/trends/instagram").json()
        st.json(data)

with col2:
    st.subheader("Generate Post")
    topic = st.text_input("Topic (e.g., 'mici on charcoal')")
    if st.button("Generate"):
        g = requests.post(
            "http://api-gateway:8000/posts/generate",
            params={"topic": topic},
        ).json()
        st.session_state["variants"] = g.get("variants", [])
    for i, variant in enumerate(st.session_state.get("variants", []), start=1):
        st.markdown(f"**Variant {i}:** {variant}")
        img = st.text_input(f"Image URL for Variant {i}", key=f"img{i}")
        if st.button(f"Publish Variant {i}"):
            response = requests.post(
                "http://api-gateway:8000/posts/publish",
                params={"caption": variant, "image_url": img},
            ).json()
            st.success(response)
