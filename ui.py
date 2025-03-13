import base64
import streamlit as st
import tempfile
from main import TableOfContent
import os
st.title("PDF Indexer")

st.write("""
    This tool helps you merge multiple PDF files into a single document with an automatically 
    generated table of contents page. It creates bookmarks for easy navigation between sections 
    and preserves the original document names. Simply upload your PDF files, and download the 
    combined result with a professional index.
""")

uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files:
    output_file = "indexed_output.pdf"
    temp_files = []
    names = {}
    for uploaded_file in uploaded_files:
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp.write(uploaded_file.getbuffer())  # Write file contents
        temp.flush()  # Ensure contents are written before processing
        temp_files.append(temp.name)
        names[temp.name] = uploaded_file.name

    try:
        replace_name_func = lambda x: names.get(x, x)
        toc = TableOfContent(temp_files, output_file, replace_name_func=replace_name_func)

        with open(output_file, "rb") as f:
            st.download_button("Download Indexed PDF", f, file_name=output_file, mime="application/pdf")

    finally:
        # Cleanup temporary files
        for path in temp_files:
            try:
                os.remove(path)
            except OSError:
                pass

st.markdown("""
<div style="position: fixed; bottom: 10px; left: 0; width: 100%; padding: 10px; text-align: center;">
    Tzvi Greenfeld 🤖 <a href="https://github.com/TzviGreenfeld/pdf_indexer" target="_blank">View on GitHub</a>
</div>
""", unsafe_allow_html=True)