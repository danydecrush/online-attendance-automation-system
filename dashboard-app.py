import streamlit as st
from streamlit_option_menu import option_menu
from st_aggrid import GridUpdateMode, DataReturnMode, AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
import pyrebase
import pandas as pd
import firebase_admin
from firebase_admin import auth, credentials
import time
from datetime import datetime

firebaseConfig = {
    "apiKey": "AIzaSyDmbYcKZHsK-OMn6aQJLpM4J_0N5ZMeM1I",
    "authDomain": "attendance-automation-bf5e4.firebaseapp.com",
    "databaseURL": "https://attendance-automation-bf5e4-default-rtdb.asia-southeast1.firebasedatabase.app",
    "projectId": "attendance-automation-bf5e4",
    "storageBucket": "attendance-automation-bf5e4.appspot.com",
    "messagingSenderId": "615078896726",
    "appId": "1:615078896726:web:dc3acc8691f006b0d847f7"
}


def create_student(email, password, reg):
#     uid = reg
#     user = auth.create_user(email=email, password=password, uid=uid)
#     return user.uid
#     cred = credentials.Certificate("private_key.json")
    a = firebase_admin.get_app().project_id
    return a


@st.cache(allow_output_mutation=True)
def init():
    fb = pyrebase.initialize_app(firebaseConfig)
    authvalue = fb.auth()
    database = fb.database()
    return fb, authvalue, database


@st.cache(allow_output_mutation=True)
def getDatabaseAsTable(db):
    data = db.get().val()
    dates = list(data.keys())
    dataframe = pd.DataFrame()
    for date in dates:
        df1 = pd.DataFrame(data[date]).transpose()
        df1.set_index('date', inplace=True)
        dataframe = dataframe.append(df1)
        dataframe = dataframe[['name', 'register-no', 'in-time', 'out-time', 'mobile']]
    return dataframe


def getMonthDataAsTable(db, sel_month):
    data = db.get().val()
    dates = list(data.keys())
    dataframe = pd.DataFrame()
    months_arr = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                  'November', 'December']
    month_number = months_arr.index(sel_month) + 1
    month_number = f'{month_number:02}'
    for date in dates:
        if date[3:5] == month_number:
            df2 = pd.DataFrame(data[date]).transpose()
            df2.set_index('date', inplace=True)
            dataframe = dataframe.append(df2)
            dataframe = dataframe[['name', 'register-no', 'in-time', 'out-time']]
    return dataframe


@st.cache
def convert_df(df3):
    return df3.to_csv().encode('utf-8')


def main():
    firebase, pbAuth, db = init()
    st.title("Attendance Dashboard")
    st.sidebar.title("Student / Staff Login")
    hide_watermark = """
        <style>
            #MainMenu{visibility:hidden;}
            footer {visibility:hidden;}
            .css-1rh8hwn.e16fv1kl2{font-size:18px;}
            .css-nlntq9.e16nr0p33 p{font-size:18px;}
            .element-container.css-1p1nwyz.e1tzin5v3{margin-top:20px;}

        </style>
        """
    st.markdown(hide_watermark, unsafe_allow_html=True)

    menu = ['Student Login', 'Staff Login', 'Reset Password']
    choice = st.sidebar.selectbox('Menu', menu)

    # To create a student user credential un it manually once at createUser.py

    if choice == 'Student Login':

        email = st.sidebar.text_input('Enter your email Address').strip()
        password = st.sidebar.text_input('Enter your password', type='password').strip()
        reg = st.sidebar.text_input('Enter your Register Number').strip()
        login = st.sidebar.checkbox('Login')
        if len(email) <= 0 or len(password) <= 0 or len(reg) <= 0:
            st.sidebar.warning("All Fields are necessary")
        if login:
            user = pbAuth.sign_in_with_email_and_password(email, password)
            table = getDatabaseAsTable()
            if user['registered'] and user['localId'] == reg:
                uname = table.loc[table['register-no'] == reg, 'name'].values[0]
                st.subheader(f'Welcome {uname}')
                # st.write(user)

                st.write("Select a month to generate report :")
                months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                          'October',
                          'November', 'December']
                selected_month = st.selectbox("Select a Month", months)
                selected_month = str(selected_month)
                total_w_days = 24
                st.write('\n')

                c1, c2 = st.columns(2)
                monthTable = getMonthDataAsTable(db, selected_month)
                if len(monthTable):
                    monthTable = monthTable[monthTable['register-no'] == reg]
                else:
                    monthTable = "No Records Found !!!"

                if type(monthTable) != str:
                    st.subheader("Monthly Report")
                    st.write(monthTable)
                    st.write('\n')

                    c1.metric(label=f'No of days present in {selected_month.upper()}',
                              value=f'{len(monthTable)}',
                              delta=f'{(len(monthTable) / total_w_days * 100):.2f}%'
                              )

                    c2.write("Get Monthly Report")
                    csv = convert_df(monthTable)

                    c2.download_button(
                        label="Download data as CSV",
                        data=csv,
                        file_name=f'{reg[8:]}_{selected_month}.csv',
                        mime='text/csv',
                    )
                else:
                    st.write(monthTable)

                c3, c4 = st.columns(2)
                c3.success("Show all months data   ------->")
                c4.write('\n')
                showAll = c4.checkbox("Show")
                st.write('\n')

                if showAll:
                    st.subheader("Whole Data report")
                    table = table[table["register-no"] == reg]
                    table = table[['in-time', 'out-time']]
                    s1, s2 = st.columns(2)

                    s1.write(table)
                    s2.write('\n')
                    s2.write('\n')
                    s2.subheader("Download All Data")
                    all_csv = convert_df(table)

                    s2.download_button(
                        label="Save All Data",
                        data=all_csv,
                        file_name=f'{reg[8:]}_database.csv',
                        mime='text/csv',
                    )

    elif choice == 'Staff Login':
        email = st.sidebar.text_input('Enter your email Address').strip()
        password = st.sidebar.text_input('Enter your password', type='password').strip()
        login = st.sidebar.checkbox('Login')

        if len(email) <= 0 or len(password) <= 0:
            st.sidebar.warning("All Fields are necessary")
        if login:
            user = pbAuth.sign_in_with_email_and_password(email, password)
            if user['registered'] and user['localId'] == "admin":
                st.subheader(f'Welcome staff')
                option = option_menu(
                    menu_title="Main Menu",
                    options=["Add Student", "Student Data", "Class Report"],
                    icons=["person-plus", "journal-text", "bookmark-check"],
                    menu_icon="cast",
                    default_index=0,
                    orientation="horizontal",
                    styles={
                        "nav-link": {"--hover-color": "#eee"},
                        "nav-link-selected": {"font-weight": "500"},
                    }
                )

                if option == "Add Student":
                    with st.form(key='my_form', clear_on_submit=True):
                        email = st.text_input('Enter Student email Address').strip()
                        password = st.text_input('Enter Student password', type='password').strip()
                        reg = st.text_input('Enter your Register Number').strip()
                        submit = st.form_submit_button(label='Submit')
                    if submit:
#                         if len(email) <= 0 or len(password) <= 0 or len(reg) <= 0:
#                             st.warning("All Fields are necessary")
#                         else:
                        status = create_student(email, password, reg)
                        st.write(status)
                        if status:
                            st.success(f"Student Login Id Created Successfully + {status}")
                        else:
                            st.error("There is a problem in inputs, Check your inputs.")
                elif option == "Student Data":
                    table = getDatabaseAsTable(db)
                    table['date'] = table.index
                    table = table[['date', 'name', 'register-no', 'in-time', 'out-time', 'mobile']]
                    st.subheader("Interactive Table")
                    st.info("Select starting date, Press & hold Shift and select Ending date to multi-select data.")

                    gb = GridOptionsBuilder.from_dataframe(table)
                    gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
                    gb.configure_selection(selection_mode="multiple", use_checkbox=True)
                    gb.configure_side_bar()
                    gridOptions = gb.build()

                    response = AgGrid(
                        table,
                        gridOptions=gridOptions,
                        enable_enterprise_modules=True,
                        update_mode=GridUpdateMode.MODEL_CHANGED,
                        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                        fit_columns_on_grid_load=False,
                    )

                    df = pd.DataFrame(response["selected_rows"])

                    st.subheader("Filtered data will appear below 👇 ")
                    st.text("")

                    if len(df):
                        df = df.set_index(df['date'])
                        df = df[['name', 'register-no', 'in-time', 'out-time', 'mobile']]
                        st.table(df)

                        st.text("")

                        c29, c30 = st.columns(2)
                        c29.download_button(
                            label="Download to CSV",
                            data=convert_df(df),
                            file_name="database.csv",
                            mime='text/csv',
                        )

                elif option == "Class Report":
                    st.subheader("Report")
                    st.write("Select a month to generate report :")
                    months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                              'October',
                              'November', 'December']
                    selected_month = st.selectbox("Select a Month", months)
                    selected_month = str(selected_month)
                    monthTable = getMonthDataAsTable(db, selected_month)
                    month_in_number = months.index(selected_month) + 1
                    month_in_number = f'{month_in_number:02}'

                    date_picked = st.date_input(f"Select a Date in {selected_month}",
                                                value=datetime(2022, int(month_in_number), 1),
                                                min_value=datetime(2022, int(month_in_number), 1),
                                                max_value=datetime(2022, int(month_in_number) + 1, 1))
                    date_picked = datetime.strptime(str(date_picked), "%Y-%m-%d").strftime("%d-%m-%Y")
                    st.write('Your Selected date is:', date_picked)
                    total_strength = 56

                    c1, c2 = st.columns(2)
                    if type(monthTable) != str and date_picked[3:5] == month_in_number:
                        st.subheader("Daily Report")
                        present_tb = monthTable[monthTable.index == date_picked]

                        if len(present_tb):
                            st.write(present_tb)
                            st.text('')

                            c1.metric(label='No of Students present',
                                      value=f'{len(present_tb)}',
                                      delta=f'{(len(present_tb) / total_strength * 100):.2f}%'
                                      )
                            c2.metric(label='No of Students absent',
                                      value=f'{total_strength - len(present_tb)}',
                                      delta=f'-{(total_strength - len(present_tb) / total_strength * 100):.2f}%'
                                      )
                            st.download_button(
                                label="Download daily data",
                                data=convert_df(present_tb),
                                file_name=f"{date_picked}_report.csv",
                                mime='text/csv',
                            )
                        else:
                            st.error(f"No Records Found on {date_picked}")
            else:
                st.error("Check your credentials. No user exists!!!")

    elif choice == 'Reset Password':
        email = st.sidebar.text_input('Enter your mail Id here').strip()
        reset = st.sidebar.button(label="Reset")
        if len(email) > 0:
            if reset:
                pbAuth.send_password_reset_email(email)
                st.sidebar.success("Check your inbox for reset link")
                time.sleep(2)
                st.sidebar.success("Reset and signin with your new password")
        else:
            st.sidebar.warning("Enter your mail to get reset link.")


if __name__ == "__main__":
    main()
