import streamlit as st
import pandas as pd
import os
import json
import random

EMPLOYEES_FILE = "employees.csv"
MESSAGES_FILE = "messages.json"

# 加载员工数据
if "employees_df" not in st.session_state:
    if os.path.exists(EMPLOYEES_FILE):
        st.session_state.employees_df = pd.read_csv(EMPLOYEES_FILE, index_col=0)
    else:
        st.session_state.employees_df = None

# 加载消息数据（兼容旧格式）
if "messages" not in st.session_state:
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                # 若是旧格式，转换为新结构
                if isinstance(data, list) and all(isinstance(item, str) for item in data):
                    st.session_state.messages = [{"name": "System", "message": msg} for msg in data]
                else:
                    st.session_state.messages = data
            except Exception:
                st.session_state.messages = []
    else:
        st.session_state.messages = []

st.title("Work Overview & Role Assignment")

# 侧边栏：员工数量设置
st.sidebar.header("Settings")
num_employees = st.sidebar.number_input("Number of employees", min_value=1, max_value=999, value=10, step=1)

# 生成员工数据与角色分配
if st.sidebar.button("Generate Employees"):
    killer_ratio = 0.2
    detective_ratio = 0.1
    doctor_ratio = 0.1

    employees = []
    for i in range(num_employees):
        emp_id = f"{i+1:03d}"
        hours_worked = random.randint(5, 20)
        night_shifts = random.randint(0, 6)
        base_bonus = hours_worked * 50 + night_shifts * 20
        bonus = max(0, base_bonus - random.randint(0, 300))

        employees.append({
            "Employee #": emp_id,
            "Hours Worked": hours_worked,
            "Bonus (HKD)": bonus,
            "Night Shifts": night_shifts
        })

    df = pd.DataFrame(employees)
    df["Unfairness"] = (df["Hours Worked"] * 50 + df["Night Shifts"] * 20) - df["Bonus (HKD)"]
    df["Role"] = "Civilian"

    df = df.sort_values(by="Unfairness", ascending=False).reset_index(drop=True)
    num_killers = max(1, round(num_employees * killer_ratio))
    num_detectives = max(1, round(num_employees * detective_ratio))
    num_doctors = max(1, round(num_employees * doctor_ratio))

    df.loc[:num_killers - 1, "Role"] = "Killer"
    df.loc[num_killers:num_killers + num_detectives - 1, "Role"] = "Detective"
    df.loc[num_killers + num_detectives:num_killers + num_detectives + num_doctors - 1, "Role"] = "Doctor"

    df = df.sort_values(by="Employee #").reset_index(drop=True)

    st.session_state.employees_df = df
    df.to_csv(EMPLOYEES_FILE)
    st.success("Employees generated and roles assigned!")

# 员工数据修改功能
if st.session_state.employees_df is not None:
    st.subheader("Update Employee Data")
    employee_list = st.session_state.employees_df["Employee #"].tolist()
    selected_employee = st.selectbox("Select an employee to update", employee_list)
    field_options = ["Hours Worked", "Bonus (HKD)", "Night Shifts"]
    selected_field = st.selectbox("Select a field to update", field_options)
    new_value = st.number_input("New value", value=0, step=1)

    if st.button("Update Data"):
        df = st.session_state.employees_df
        idx = df[df["Employee #"] == selected_employee].index[0]
        df.at[idx, selected_field] = new_value

        # 重新计算不公平度与角色分配
        df["Unfairness"] = (df["Hours Worked"] * 50 + df["Night Shifts"] * 20) - df["Bonus (HKD)"]
        df["Role"] = "Civilian"
        df = df.sort_values(by="Unfairness", ascending=False).reset_index(drop=True)

        num_killers = max(1, round(len(df) * 0.2))
        num_detectives = max(1, round(len(df) * 0.1))
        num_doctors = max(1, round(len(df) * 0.1))

        df.loc[:num_killers - 1, "Role"] = "Killer"
        df.loc[num_killers:num_killers + num_detectives - 1, "Role"] = "Detective"
        df.loc[num_killers + num_detectives:num_killers + num_detectives + num_doctors - 1, "Role"] = "Doctor"

        df = df.sort_values(by="Employee #").reset_index(drop=True)
        st.session_state.employees_df = df
        df.to_csv(EMPLOYEES_FILE)
        st.success(f"Updated {selected_employee}'s {selected_field} to {new_value} and roles recalculated!")

    st.subheader("Employee Table")
    st.table(st.session_state.employees_df)

# 信息发送功能（带姓名）
st.subheader("Send Messages")
with st.form(key="message_form", clear_on_submit=True):
    sender_name = st.text_input("Your Name")
    message = st.text_input("Message")
    submitted = st.form_submit_button("Send")
    if submitted and sender_name and message:
        st.session_state.messages.append({"name": sender_name, "message": message})
        with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
        st.success("Message sent!")

# 信息记录展示（带姓名）
if st.session_state.messages:
    st.subheader("Message Log")
    for idx, item in enumerate(st.session_state.messages, start=1):
     