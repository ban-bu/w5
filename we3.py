import streamlit as st
import pandas as pd

# 初始化 session_state 变量
if "employees_df" not in st.session_state:
    st.session_state.employees_df = None
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("天黑请闭眼 - 公屏展示")

# 侧边栏设置：输入员工数量并生成初始 KPI 列表（KPI 均为 0）
st.sidebar.header("设置")
num_employees = st.sidebar.number_input("请输入员工数量", min_value=1, max_value=100, value=10, step=1)
if st.sidebar.button("生成员工KPI"):
    employees = []
    for i in range(num_employees):
        name = f"员工 {i+1}"
        kpi = 0  # 初始 KPI 都为 0
        employees.append({"姓名": name, "KPI": kpi})
    st.session_state.employees_df = pd.DataFrame(employees)

# 显示生成的员工 KPI 公屏
if st.session_state.employees_df is not None:
    st.subheader("员工 KPI 列表")
    st.table(st.session_state.employees_df)

    # 修改 KPI 部分
    st.subheader("修改 KPI")
    # 选择员工
    employee_names = st.session_state.employees_df["姓名"].tolist()
    selected_employee = st.selectbox("选择要修改的员工", employee_names)
    new_kpi = st.number_input("设置新的 KPI 值", value=0, step=1)
    if st.button("更新 KPI"):
        # 查找该员工对应的索引并更新 KPI
        idx = st.session_state.employees_df[st.session_state.employees_df["姓名"] == selected_employee].index[0]
        st.session_state.employees_df.at[idx, "KPI"] = new_kpi
        st.success(f"{selected_employee} 的 KPI 已更新为 {new_kpi}")
        st.table(st.session_state.employees_df)

# 信息发送部分
st.subheader("发送信息")
with st.form(key="message_form", clear_on_submit=True):
    message = st.text_input("输入信息")
    submitted = st.form_submit_button("发送信息")
    if submitted and message:
        st.session_state.messages.append(message)

# 显示所有发送过的信息
if st.session_state.messages:
    st.subheader("信息记录")
    for idx, msg in enumerate(st.session_state.messages, start=1):
        st.write(f"{idx}. {msg}")
