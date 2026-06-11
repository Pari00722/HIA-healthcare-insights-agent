import streamlit as st


def show_footer(in_sidebar=False):
    base_styles = """
        text-align: center;
        padding: 0.75rem;
        background: linear-gradient(to right,
            rgba(25, 118, 210, 0.03),
            rgba(100, 181, 246, 0.05),
            rgba(25, 118, 210, 0.03)
        );
        border-top: 1px solid rgba(100, 181, 246, 0.15);
        box-shadow: 0 -2px 10px rgba(100, 181, 246, 0.05);
    """

    if in_sidebar:
        base_styles += "margin-top: 0;"
    else:
        base_styles += "margin-top: 2rem; width: 100%;"

    st.markdown(
        f"""
        <div style='{base_styles}'></div>
        """,
        unsafe_allow_html=True,
    )
