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

st.title("天黑请闭眼 - 公屏展示")

# 侧边栏：生成员工KPI（初始均为 0）
st.sidebar.header("设置")
num_employees = st.sidebar.number_input("请输入员工数量", min_value=1, max_value=100, value=10, step=1)
if st.sidebar.button("生成员工KPI"):
    employees = []
    for i in range(num_employees):
        name = f"员工 {i+1}"
        kpi = 0  # 初始 KPI 均为 0
        employees.append({"姓名": name, "KPI": kpi})
    st.session_state.employees_df = pd.DataFrame(employees)
    # 保存数据到文件
    st.session_state.employees_df.to_csv(EMPLOYEES_FILE)
    st.success("员工KPI已生成")

# 显示员工 KPI 公屏
if st.session_state.employees_df is not None:
    st.subheader("员工 KPI 列表")
    st.table(st.session_state.employees_df)

    # 修改 KPI 部分
    st.subheader("修改 KPI")
    employee_names = st.session_state.employees_df["姓名"].tolist()
    selected_employee = st.selectbox("选择要修改的员工", employee_names)
    new_kpi = st.number_input("设置新的 KPI 值", value=0, step=1)
    if st.button("更新 KPI"):
        idx = st.session_state.employees_df[st.session_state.employees_df["姓名"] == selected_employee].index[0]
        st.session_state.employees_df.at[idx, "KPI"] = new_kpi
        # 更新后保存数据
        st.session_state.employees_df.to_csv(EMPLOYEES_FILE)
        st.success(f"{selected_employee} 的 KPI 已更新为 {new_kpi}")
        st.table(st.session_state.employees_df)

# 信息发送部分
st.subheader("发送信息")
with st.form(key="message_form", clear_on_submit=True):
    message = st.text_input("输入信息")
    submitted = st.form_submit_button("发送信息")
    if submitted and message:
        st.session_state.messages.append(message)
        # 保存消息到文件
        with open(MESSAGES_FILE, "w", encoding="utf-8") as f:
            json.dump(st.session_state.messages, f, ensure_ascii=False, indent=2)
        st.success("信息已发送")

# 显示所有发送过的信息
if st.session_state.messages:
    st.subheader("信息记录")
    for idx, msg in enumerate(st.session_state.messages, start=1):
        st.write(f"{idx}. {msg}")
