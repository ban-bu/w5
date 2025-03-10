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

st.title("H&M Night Shift Crisis - Work Overview")

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
    # 生成 KILLER 员工（高工时、高风险、低奖金；Night Shifts 初始设为 0）
    for _ in range(num_killers):
        emp_id = f"{emp_counter:03d}"
        hours_worked = random.randint(16, 20)
        night_shifts = 0
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

    # 生成 DETECTIVE 员
