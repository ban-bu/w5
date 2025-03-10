import streamlit as st
import pandas as pd
import os
import json

EMPLOYEES_FILE = "employees.csv"
MESSAGES_FILE = "messages.json"

# 加载员工数据
if "employees_df" not in st.session_state:
    if os.path.exists(EMPLOYEES_FILE):
        st.session_state.employees_df = pd.read_csv(EMPLOYEES_FILE, index_col=0)
    else:
        st.session_state.employees_df = None

# 加载消息数据
if "messages" not in st.session_state:
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
            st.session_state.messages = json.load(f)
    else:
        st.session_state.messages = []

st.title("Work Overview")

# 侧边栏：生成员工数据
st.sidebar.header("Settings")
num_employees = st.sidebar.number_input("Number of employees", min_value=1, max_value=999, value=5, step=1)
if st.sidebar.button("Generate Employees"):
    employees = []
    for i in range(num_employees):
        employees.append({
            "Employee #": f"{i+1:03d}",
            "Hours Worked": 0,
            "Bonus (HKD)": 0,
            "Night Shifts": 0
        })
    st.session_state.employees_df = pd.DataFrame(employees)
    st.session_state.employees_df.to_csv(EMPLOYEES_FILE)
    st.success("Employees generated successfully!")

if st.session_state.employees_df is not None:
    st.subheader("Update Employee Data")
    employee_list = st.session_state.employees_df["Employee #"].tolist()
    selected_employee = st.selectbox("Select an employee to update", employee_list)
    field_options = ["Hours Worked", "Bonus (HKD)", "Night Shifts"]
    selected_field = st.selectbox("Select a field to update", field_options)
    new_value = st.number_input("New value", value=0, step=1)

    if st.button("Update Data"):
        idx = st.session_state.employees_df[
            st.session_state.employees_df["Employee #"] == selected_employee
        ].index[0]
        st.session_state.employees_df.at[idx, selected_field] = new_value
        st.session_state.employees_df.to_csv(EMPLOYEES_FILE)
        st.success(f"Employee {selected_employee} - {selected_field} updated to {new_value}!")

    st.subheader("Employee Table")
    st.table(st.session_state.employees_df)

# 信息发送部分
st.subheader("Send Messages")
with st.form(key="message_form", clear_on_submit=True):
    message = st.text_input("Enter a message")
    submitted = st.form_submit_button("Send")
    if submitted and message:
        st.session_state.messages.append(message)
        with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
        st.success("Message sent!")

# 显示信息记录和清空按钮
st.subheader("Message Log")
if st.session_state.messages:
    # 添加清除对话按钮
    if st.button("Clear Messages"):
        st.session_state.messages = []
        with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
        st.success("Messages cleared!")
    # 显示所有消息，不带序号
    for msg in st.session_state.messages:
        st.write(msg)
