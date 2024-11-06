import streamlit as st
import pandas as pd
from io import StringIO
import base64
import plotly.express as px
from helper.scrap import scraper  # Ensure your scraper function returns the DataFrame as described

# Streamlit app code
# Function to convert image to base64 string
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Streamlit app code
logo_base64 = image_to_base64("data/logo.png")

# Add the title and logo using HTML
st.markdown(f"""
    <div style="display: flex; align-items: center;">
        <img src="data:image/png;base64,{logo_base64}" style="width: 100px; height: 100px;">
        <h1 style="margin-left: 10px;"> Social Media Lead Generation</h1>
    </div>
""", unsafe_allow_html=True)

st.divider()


# Sidebar for settings with radio buttons
st.sidebar.title("Platforms")
lead_filter = st.sidebar.radio("Choose a Platform", ["LinkedIn", "Instagram", "X"])

x_logo_base64 = image_to_base64("data/x logo.png")
insta_logo_base64 = image_to_base64("data/insta logo.png")
linkedin_logo_base64 = image_to_base64("data/linkedin logo.png")
logos={'LinkedIn':linkedin_logo_base64,
       "Instagram":insta_logo_base64,
       "X":x_logo_base64}

# Input fields for LinkedIn credentials
st.markdown(f""" <div style="display: flex; align-items: center;">
        <img src="data:image/png;base64,{logos[lead_filter]}" style="width: 30px; height: 30px;">
        <h2 style="margin-left: 20px;"> {lead_filter} log in</h2>
        </div>""", unsafe_allow_html=True)

email = st.text_input("Email")
password = st.text_input("Password", type="password")

# Input URL from user
url = st.text_input("Enter a LinkedIn Post URL:")

# Generate button
generate_button = st.button("Generate")

# LinkedIn lead generation logic
if lead_filter == "LinkedIn":
    if url and email and password and generate_button:
        with st.spinner('Processing...'):
            try:
                # Pass the user credentials and URL to scraper function
                dataframe_result = scraper(url, email, password)
                print(dataframe_result,"***********************")
                # Display the DataFrame as a table
                st.markdown("### Potential Leads:")
                st.dataframe(dataframe_result)
                
                st.markdown("### Analysis")
                tab1, tab2, tab3 = st.tabs(["Pie Chart", "Histogram", "Bar Chart"])

                with tab1:
                    fig = px.pie(dataframe_result, names="Is Lead")
                    st.plotly_chart(fig, use_container_width=True)

                with tab2:
                    st.info("Histogram is coming soon!")
                
                with tab3:
                    st.info("Bar Chart is coming soon!")
                        

                # Download button for CSV file
                def convert_df_to_csv(df):
                    output = StringIO()
                    df.to_csv(output, index=False)
                    return output.getvalue()

                csv_data = convert_df_to_csv(dataframe_result)

                # Show download button for CSV
                st.download_button(
                    label="Download as CSV",
                    data=csv_data,
                    file_name="dataframe_result.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"Error processing URL: {e}")
    else:
        st.warning("Please enter LinkedIn credentials and a URL.")
else:
    # Show "Coming Soon" message for Instagram and X
    st.info(f"{lead_filter} functionality is coming soon!")

# Help section
st.divider()


st.markdown(f"""
### How to Use
1. Enter {lead_filter} credentials and a {lead_filter} post URL in the text box.
2. Click on **Generate** to extract potential leads.
3. Download the data as a CSV file if needed.
""")
st.divider()

