import streamlit as st
import json
import logging
from utils.ai_summarizer import get_summary_from_ai

# Configure logging
logging.basicConfig(level=logging.INFO)

# Streamlit UI
def main():
    st.title('JSON Summarization with OpenAI')

    st.write('Upload up to 10 JSON files, and we will send each to OpenAI to get a summarized version.')

    # Initialize session state for files and summaries if not already initialized
    if 'summaries' not in st.session_state:
        st.session_state.summaries = []
        st.session_state.uploaded_files = []

    # Initialize session state for file uploader key if not set
    if 'file_uploader_key' not in st.session_state:
        st.session_state['file_uploader_key'] = 0

    

    # File upload (allow multiple files)
    uploaded_files = st.file_uploader("Choose JSON files", type="json", accept_multiple_files=True, key=st.session_state["file_uploader_key"])

    # Limit the number of files to 10
    if uploaded_files:
        if len(uploaded_files) > 10:
            st.error("You can upload a maximum of 10 files.")
            return

        # Process each uploaded file, but only if it's a new one
        for uploaded_file in uploaded_files:
            if uploaded_file.name not in st.session_state.uploaded_files:
                try:
                    # Load JSON data
                    data = json.load(uploaded_file)

                    # Get summary from OpenAI API
                    summary = get_summary_from_ai(data)

                    # Store file name and corresponding summary in session state
                    st.session_state.summaries.append((uploaded_file.name, summary))
                    st.session_state.uploaded_files.append(uploaded_file.name)

                    # Display success message
                    st.success(f"Summary for {uploaded_file.name} generated successfully.")

                except json.JSONDecodeError as e:
                    logging.error(f"Error decoding JSON in {uploaded_file.name}: {e}")
                    st.error(f"There was an error decoding the JSON file: {uploaded_file.name}. Please upload a valid JSON file.")
                except Exception as e:
                    logging.error(f"An unexpected error occurred for {uploaded_file.name}: {e}")
                    st.error(f"An unexpected error occurred while processing the file: {uploaded_file.name}. Please try again.")
            else:
                st.info(f"{uploaded_file.name} has already been processed.")

        # Show all summaries
        if st.session_state.summaries:
            st.subheader("Generated Summaries")
            for file_name, summary in st.session_state.summaries:
                st.write(f"**{file_name}:** {summary}")

    # Clear button logic
    if st.button('Clear'):
        # Reset the session state variables
        st.session_state.summaries = []
        st.session_state.uploaded_files = []

        # Change the key of the file uploader to reset it and trigger a rerun
        st.session_state['file_uploader_key'] += 1  # Change key to force reinitialization
        st.rerun()  # Trigger a rerun to reset the file uploader

if __name__ == "__main__":
    main()
