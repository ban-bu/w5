import streamlit as st
import pandas as pd
import os
import json
import random
import datetime

EMPLOYEES_FILE = "employees.csv"
MESSAGES_FILE = "messages.json"

# -------------------------
# 加载员工数据
# -------------------------
if "employees_df" not in st.session_state:
    if os.path.exists(EMPLOYEES_FILE):
        st.session_state.employees_df = pd.read_csv(EMPLOYEES_FILE)
    else:
        st.session_state.employees_df = None

# -------------------------
# 加载消息数据
# -------------------------
if "messages" not in st.session_state:
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE, "r", encoding="utf-8") as f:
            try:
                st.session_state.messages = json.load(f)
            except Exception:
                st.session_state.messages = []
    else:
        st.session_state.messages = []

st.title("H&M Night Shift Crisis - Role Assignment & Work Overview")

# -------------------------
# 侧边栏：生成员工数据
# -------------------------
st.sidebar.header("Settings")
num_employees = st.sidebar.number_input("Number of employees", min_value=1, max_value=999, value=30, step=1)

if st.sidebar.button("Generate Employees"):
    # 固定比例
    killer_ratio = 0.2      # 20%
    detective_ratio = 0.1   # 10%
    doctor_ratio = 0.1      # 10%
    total = num_employees
    num_killers = max(1, round(total * killer_ratio))
    num_detectives = max(1, round(total * detective_ratio))
    num_doctors = max(1, round(total * doctor_ratio))
    num_civilians = total - num_killers - num_detectives - num_doctors

    employees = []
    emp_counter = 1
    # 生成 KILLER 员工（高工时、高夜班、低奖金）
    for _ in range(num_killers):
        emp_id = f"{emp_counter:03d}"
        hours_worked = random.randint(16, 20)
        night_shifts = random.randint(4, 6)
        bonus = random.randint(0, 50)
        unfairness = (hours_worked * 50 + night_shifts * 20) - bonus
        employees.append({
            "Employee #": emp_id,
            "Hours Worked": hours_worked,
            "Bonus (HKD)": bonus,
            "Night Shifts": night_shifts,
            "Unfairness": unfairness,
            "Role": "KILLER"
        })
        emp_counter += 1

    # 生成 DETECTIVE 员工（中等工时、适中奖金、少量夜班）
    for _ in range(num_detectives):
        emp_id = f"{emp_counter:03d}"
        hours_worked = random.randint(8, 15)
        night_shifts = random.randint(1, 3)
        bonus = random.randint(100, 200)
        unfairness = (hours_worked * 50 + night_shifts * 20) - bonus
        employees.append({
            "Employee #": emp_id,
            "Hours Worked": hours_worked,
            "Bonus (HKD)": bonus,
            "Night Shifts": night_shifts,
            "Unfairness": unfairness,
            "Role": "DETECTIVE"
        })
        emp_counter += 1

    # 生成 DOCTOR 员工（参数与侦探类似）
    for _ in range(num_doctors):
        emp_id = f"{emp_counter:03d}"
        hours_worked = random.randint(8, 15)
        night_shifts = random.randint(1, 3)
        bonus = random.randint(100, 200)
        unfairness = (hours_worked * 50 + night_shifts * 20) - bonus
        employees.append({
            "Employee #": emp_id,
            "Hours Worked": hours_worked,
            "Bonus (HKD)": bonus,
            "Night Shifts": night_shifts,
            "Unfairness": unfairness,
            "Role": "DOCTOR"
        })
        emp_counter += 1

    # 生成 CIVILIAN 员工（低工时、低夜班、高奖金）
    for _ in range(num_civilians):
        emp_id = f"{emp_counter:03d}"
        hours_worked = random.randint(5, 12)
        night_shifts = random.randint(0, 2)
        bonus = random.randint(150, 300)
        unfairness = (hours_worked * 50 + night_shifts * 20) - bonus
        employees.append({
            "Employee #": emp_id,
            "Hours Worked": hours_worked,
            "Bonus (HKD)": bonus,
            "Night Shifts": night_shifts,
            "Unfairness": unfairness,
            "Role": "CIVILIAN"
        })
        emp_counter += 1

    df = pd.DataFrame(employees)
    df = df.sort_values(by="Employee #").reset_index(drop=True)
    st.session_state.employees_df = df
    df.to_csv(EMPLOYEES_FILE, index=False)
    st.sidebar.success("Employees generated with differentiated initial values!")

# -------------------------
# 员工数据修改功能
# -------------------------
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
        # 重新计算不公平度（保持原角色不变，可按需重新分配角色）
        df.at[idx, "Unfairness"] = (df.at[idx, "Hours Worked"] * 50 + df.at[idx, "Night Shifts"] * 20) - df.at[idx, "Bonus (HKD)"]
        st.session_state.employees_df = df
        df.to_csv(EMPLOYEES_FILE, index=False)
        st.success(f"Employee {selected_employee}'s {selected_field} updated to {new_value}!")

    st.subheader("Employee Table")
    st.table(st.session_state.employees_df)

# -------------------------
# 信息发送部分（带时间戳）
# -------------------------
st.subheader("Send Messages")
with st.form(key="message_form", clear_on_submit=True):
    message = st.text_input("Enter a message")
    submitted = st.form_submit_button("Send")
    if submitted and message:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 这里可以根据需要扩展，例如增加发送者姓名
        st.session_state.messages.append({"time": timestamp, "message": message})
        with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
        st.success("Message sent!")

# -------------------------
# 消息记录显示及清空功能（显示时间）
# -------------------------
st.subheader("Message Log")
if st.session_state.messages:
    if st.button("Clear Messages"):
        st.session_state.messages = []
        with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
        st.success("Messages cleared!")
    for msg in st.session_state.messages:
        st.write(f"{msg['time']}: {msg['message']}")
