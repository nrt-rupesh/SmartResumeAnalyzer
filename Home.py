import streamlit as st
import pandas as pd
import base64,random
import time,datetime
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager,PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io,random
from streamlit_tags import st_tags
from PIL import Image
import psycopg2
import pafy
import plotly.express as px
from streamlit_option_menu import option_menu
import tkinter as tk
from tkinter import filedialog
import os
#from resume_parser import resumeparse

# Page Configuration
st.set_page_config(
    page_title="Home :: Smart Resume Analyser",
    page_icon="./images/generic-company-logo-png-2.png",
)

# Page Side Menu and Icon
with st.sidebar:
    image = Image.open("./images/generic-company-logo-png-2.png")
    st.image(image)
    choose = option_menu("Main Menu", ["Home", "Admin Login","Report","Logout"],
                         icons=['house','person', 'pie-chart',"box-arrow-right"],
                         menu_icon="app-indicator", default_index=0,
                         styles={
        "container": {"padding": "5!important", "background-color": "#fafafa"},
        "icon": {"color": "dark-blue", "font-size": "25px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin":"0px", "--hover-color": "#eee"},
        "nav-link-selected": {"background-color": "primaryColor"},
    }
    )

# horizontal menu
#selected2 = option_menu(None, ["Home", "Upload", "Tasks", 'Settings'], 
#    icons=['house', 'cloud-upload', "list-task", 'gear'], 
#    menu_icon="cast", default_index=0, orientation="horizontal")
#    selected2


connection = psycopg2.connect(database="nlp", user = "postgres", password = "postgres", host = "localhost", port = "5432")
cursor = connection.cursor()

def get_table_download_link(df,filename,text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    # href = f'<a href="data:file/csv;base64,{b64}">Download Report</a>'
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text

# excution starts from here
def run():
    #st.sidebar.markdown("# Choose user")
    #choice = st.sidebar.selectbox("Choose among the given options :",users)
    st.title("Smart Resume Analyser :fire:")
    
    # Create the DB
    # db_sql = """CREATE DATABASE IF NOT EXISTS nlp;"""
    # cursor.execute(db_sql)

    # Create table
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    ("ID" int4 NOT NULL,
                     "Name" varchar NOT NULL,
                     "Email_ID" varchar NOT NULL,
                     "resume_score" varchar NOT NULL,
                     "Timestamp" varchar NOT NULL,
                     "Page_no" varchar NOT NULL,
                     "Predicted_Field" varchar NOT NULL,
                     "User_level" varchar NOT NULL,
                     "Actual_skills" varchar NOT NULL,
                     "Recommended_skills" varchar NOT NULL,
                     "Recommended_courses" varchar NOT NULL,
                     "total_experience" float4 NOT NULL
                );
                    """
    cursor.execute(table_sql)
run()

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="700" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def home():
    file_options = ["For single file","For multiple files"]
    selected_option =  st.radio("Choose an Option First 👇",file_options,horizontal=True)
    if selected_option == 'For single file':
        single_pdf_file = st.file_uploader("Choose a single Resume", type=['txt','docx','pdf'])
        if single_pdf_file is not None:
            save_file_path = './Uploaded_Resumes/'+single_pdf_file.name
            with open(save_file_path,"wb") as f:
                f.write(single_pdf_file.getbuffer())
            if st.button("View"):
                show_pdf(save_file_path)
            resume_data = ResumeParser(save_file_path).get_extracted_data()
            #resume_data2 = resumeparse.read_file(save_file_path)
            if resume_data:
                resume_text = pdf_reader(save_file_path)
                st.markdown("<h1 style='text-align: center; color: red;'>Resume Analysis</h1>", unsafe_allow_html=True)
                st.subheader("Basic Details")
                col1,col2 = st.columns([1,3])
                try:
                    with col1:
                        st.text("Name :")
                        st.text('Email :')
                        st.text('Mobile No. :')
                        st.text('Total Experience :')
                        st.text('University :')
                        st.text('Designition :')
                        st.text('Degree :')
                        st.text('Skills :')
                        st.text('Companies worked at :')
                        st.text('Experience :')
                        st.text('No. of Pages :')
                    with col2:
                        st.text(resume_data['name'])
                        st.text(resume_data['email'])
                        st.text(resume_data['mobile_number'])
                        st.text(resume_data['total_experience'])
                        st.text(resume_data['college_name'])
                        st.text(resume_data['designation'])
                        st.text(resume_data['degree'])
                        st.text(resume_data['skills'])
                        st.text(resume_data['company_names'])
                        st.text(resume_data['experience'])
                        st.text(resume_data['no_of_pages'])
                except:
                    pass
                # try:
                #     with col1:
                #         st.text("Name2 :")
                #         st.text('Email2 :')
                #         st.text('Mobile No.2 :')
                #         st.text('Total Experience :')
                #         st.text('University :')
                #         st.text('Designition :')
                #         st.text('Degree :')
                #         st.text('Skills :')
                #         st.text('Companies worked at :')
                #     with col2:
                #         st.text(resume_data2['name'])
                #         st.text(resume_data2['email'])
                #         st.text(resume_data2['phone'])
                #         st.text(resume_data2['total_exp'])
                #         st.text(resume_data2['university'])
                #         st.text(resume_data2['designition'])
                #         st.text(resume_data2['degree'])
                #         st.text(resume_data2['skills'])
                #         st.text(resume_data2['Companies worked at'])
                # except:
                #     pass





    elif selected_option == 'For multiple files':
        # Set up tkinter
        root = tk.Tk()
        root.withdraw()
        # Make folder picker dialog appear on top of other windows
        root.wm_attributes('-topmost', 1)
        # Folder picker button
        clicked = st.button('Select Folder')
        if clicked:
            dirname = st.text_input('Selected folder:', filedialog.askdirectory(master=root))
            dir_list = os.listdir(dirname)
            pdf_files = []
            for l in dir_list:
                if l.endswith(".pdf"):
                    pdf_files.append(l)
            st.write("Total ",str(len(pdf_files))," files selected.")
        #folder_pdf = st.file_uploader("Choose a Folder where all PDFs stored", accept_multiple_files=True)

def admin_login():
    st.subheader("Admin Login")
    # st.markdown(""" <style> .font {
    # font-size:35px ; font-family: 'Cooper Black'; color: #FF9633;} 
    # </style> """, unsafe_allow_html=True)
    #st.markdown('<p class="font">Contact Form</p>', unsafe_allow_html=True)
    with st.form(key='login_form',clear_on_submit=True): #set clear_on_submit=True so that the form will be reset/cleared once it's submitted
        #st.write('Please help us improve!')
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        login_btn = st.form_submit_button('Login')
    if login_btn:
        if ad_user == 'nrt' and ad_password == '123':
            login_success = st.success("Welcome Admin")
            time.sleep(3)
            login_success.empty()
            # Display Data
            cursor.execute('''SELECT*FROM user_data''')
            data = cursor.fetchall()
            st.header("**User's👨‍💻 Data**")
            df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                                                'Predicted Field', 'User Level', 'Actual Skills', 'Recommended Skills',
                                                'Recommended Course','Year Of Experience'])
            st.dataframe(df)
            st.markdown(get_table_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)
        else:
            login_error = st.error("Incorrect Username or Password.")
            time.sleep(2)
            login_error.empty()


if choose == "Home":
    home()
elif choose == "Admin Login":
    admin_login()

