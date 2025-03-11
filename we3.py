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

# 定义公平度计算函数
def calc_fairness(hours, bonus, night_shifts):
    potential = hours * 50 + night_shifts * 20
    return bonus / potential if potential > 0 else 0

# 定义重新分配角色的函数
def recalc_roles(df):
    # 重新计算每个员工的 Fairness
    df["Fairness"] = df.apply(lambda row: calc_fairness(row["Hours Worked"], row["Bonus (HKD)"], row["Night Shifts"]), axis=1)
    # 按 Fairness 升序排序，Fairness 越低说明待遇越差
    df_sorted = df.sort_values(by="Fairness", ascending=True).reset_index(drop=True)
    # 固定将最低的 2 人标记为 KILLER
    df_sorted.loc[:1, "Role"] = "KILLER"
    # 固定将排序中第 3、4 名标记为 DOCTOR（如果员工数足够）
    if len(df_sorted) >= 4:
        df_sorted.loc[2:3, "Role"] = "DOCTOR"
    # 剩余员工从索引 4 开始，随机分配：若随机数 < 0.1 则为 DETECTIVE，否则为 CIVILIAN
    for idx in range(4, len(df_sorted)):
        r = random.random()
        if r < 0.1:
            df_sorted.at[idx, "Role"] = "DETECTIVE"
        else:
            df_sorted.at[idx, "Role"] = "CIVILIAN"
    # 返回按员工编号排序的 DataFrame
    return df_sorted.sort_values(by="Employee #").reset_index(drop=True)

# -------------------------
# 侧边栏：生成员工数据
# -------------------------
st.sidebar.header("Settings")
num_employees = st.sidebar.number_input("Number of employees", min_value=1, max_value=999, value=30, step=1)

if st.sidebar.button("Generate Employees"):
    employees = []
    for i in range(num_employees):
        emp_id = f"{i+1:03d}"
        # 模拟“待遇差”的概率：20% 的员工生成较高工时和低奖金；其余生成较好待遇
        if random.random() < 0.2:
            hours_worked = random.randint(16, 20)
            bonus = random.randint(0, hours_worked * 20)
        else:
            hours_worked = random.randint(5, 15)
            bonus = random.randint(hours_worked * 40, hours_worked * 50)
        night_shifts = 0  # 初始均为 0，由你手动更新
        fairness = calc_fairness(hours_worked, bonus, night_shifts)
        employees.append({
            "Employee #": emp_id,
            "Hours Worked": hours_worked,
            "Bonus (HKD)": bonus,
            "Night Shifts": night_shifts,
            "Fairness": fairness  # 内部记录，不显示
        })
    df = pd.DataFrame(employees)
    # 根据 Fairness 重新分配角色
    df = recalc_roles(df)
    st.session_state.employees_df = df
    df.to_csv(EMPLOYEES_FILE, index=False)
    st.sidebar.success("Employees generated with fairness-based role assignment!")

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
        # 重新计算公平度并重新分配角色
        df = recalc_roles(df)
        st.session_state.employees_df = df
        df.to_csv(EMPLOYEES_FILE, index=False)
        st.success(f"Employee {selected_employee}'s {selected_field} updated to {new_value} and roles recalculated!")

    st.subheader("Employee Table")
    # 显示时去除 Fairness 列，但保留 Role 列
    display_df = st.session_state.employees_df.drop(columns=["Fairness"])
    st.table(display_df)

# -------------------------
# 信息发送部分（带时间戳）
# -------------------------
st.subheader("Send Messages")
with st.form(key="message_form", clear_on_submit=True):
    message = st.text_input("Enter a message")
    submitted = st.form_submit_button("Send")
    if submitted and message:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
