import streamlit as st
import pandas as pd
import os
import json

# 定义数据文件路径
EMPLOYEES_FILE = "employees.csv"
MESSAGES_FILE = "messages.json"

# 尝试加载员工数据到 session_state
if "employees_df" not in st.session_state:
    if os.path.exists(EMPLOYEES_FILE):
        st.session_state.employees_df = pd.read_csv(EMPLOYEES_FILE, index_col=0)
    else:
        st.session_state.employees_df = None

# 尝试加载消息数据到 session_state
if "messages" not in st.session_state:
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
            st.session_state.messages = json.load(f)
    else:
        st.session_state.messages = []

st.title("Work Overview")

# 侧边栏：生成员工数据（包含 4 个字段，初始值都为 0）
st.sidebar.header("Settings")
num_employees = st.sidebar.number_input("Number of employees", min_value=1, max_value=999, value=5, step=1)
if st.sidebar.button("Generate Employees"):
    employees = []
    for i in range(num_employees):
        employees.append({
            "Employee #": f"{i+1:03d}",  # 001, 002, ...
            "Hours Worked": 0,
            "Bonus (HKD)": 0,
            "Night Shifts": 0
        })
    st.session_state.employees_df = pd.DataFrame(employees)
    # 保存数据到文件
    st.session_state.employees_df.to_csv(EMPLOYEES_FILE)
    st.success("Employees generated successfully!")

# 显示员工信息表格
if st.session_state.employees_df is not None:
    st.subheader("Employee Table")
    st.table(st.session_state.employees_df)

    # 修改员工信息
    st.subheader("Update Employee Data")
    employee_list = st.session_state.employees_df["Employee #"].tolist()
    selected_employee = st.selectbox("Select an employee to update", employee_list)

    # 选择要修改的字段
    field_options = ["Hours Worked", "Bonus (HKD)", "Night Shifts"]
    selected_field = st.selectbox("Select a field to update", field_options)

    # 输入新的数值
    new_value = st.number_input("New value", value=0, step=1)

    # 点击按钮更新
    if st.button("Update Data"):
        # 找到对应员工在 DataFrame 中的行索引
        idx = st.session_state.employees_df[
            st.session_state.employees_df["Employee #"] == selected_employee
        ].index[0]

        # 更新指定字段
        st.session_state.employees_df.at[idx, selected_field] = new_value

        # 保存更新后的数据
        st.session_state.employees_df.to_csv(EMPLOYEES_FILE)
        st.success(f"Employee {selected_employee} - {selected_field} updated to {new_value}!")

        # 再次展示更新后的表格
        st.table(st.session_state.employees_df)

# 发送信息部分
st.subheader("Send Messages")
with st.form(key="message_form", clear_on_submit=True):
    message = st.text_input("Enter a message")
    submitted = st.form_submit_button("Send")
    if submitted and message:
        st.session_state.messages.append(message)
        # 保存消息到文件
        with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
        st.success("Message sent!")

# 显示所有发送过的信息
if st.session_state.messages:
    st.subheader("Message Log")
    for idx, msg in enumerate(st.session_state.messages, start=1):
        st.write(f"{idx}. {msg}")
