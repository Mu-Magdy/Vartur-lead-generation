import streamlit as st
import pandas as pd
from io import BytesIO
from helper.scrap import scraper

# Streamlit app code
st.title("Social Media Lead Generation")

# Sidebar for settings with radio buttons
st.sidebar.title("Platforms")
lead_filter = st.sidebar.radio("Choose a Platform", ["LinkedIn", "Instagram", "X"])

url = st.text_input("Enter a Post URL:")
generate_button = st.button("Generate")


if lead_filter == "LinkedIn":
    if generate_button:
        if url:
            with st.spinner('Processing...'):
                try:
                    text_result, dataframe_result = scraper(url)

                    # Display the DataFrame as a table
                    st.markdown("### Potential Leads:")
                    st.dataframe(dataframe_result.style.highlight_max(axis=0))

                    # Download button for the DataFrame
                    def convert_df_to_xlsx(df):
                        output = BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df.to_excel(writer, index=False, sheet_name='Sheet1')
                        return output.getvalue()

                    xlsx_data = convert_df_to_xlsx(dataframe_result)

                    # Show download button
                    st.download_button(
                        label="Download as XLSX",
                        data=xlsx_data,
                        file_name="dataframe_result.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                except Exception as e:
                    st.error(f"Error processing URL: {e}")
        else:
            st.warning("Please enter a URL.")
else:
    # Show "Coming Soon" message for Instagram and X
    st.info(f"{lead_filter} functionality is coming soon!")

# Help section
st.markdown("""
### How to Use
1. Enter a LinkedIn post URL in the text box.
2. Click on **Generate** to extract potential leads.
3. Download the data as an XLSX file if needed.
""")

