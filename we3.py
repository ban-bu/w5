import streamlit as st

st.set_page_config(page_title="天黑请闭眼 - KPI 公屏", layout="centered")
st.title("天黑请闭眼：KPI 公屏系统")

# 初始化状态（只初始化一次）
if "initialized" not in st.session_state:
    st.session_state.players = {}
    st.session_state.player_count = 0
    st.session_state.messages = []
    st.session_state.initialized = True

# 输入人数并生成员工
st.subheader("【主持人操作：生成员工编号】")
player_count = st.number_input("请输入参与学生人数", min_value=4, max_value=30, value=8)
if st.button("生成员工编号"):
    st.session_state.player_count = player_count
    st.session_state.players = {
        f"{i+1:03d}": {"KPI": 0, "status": "在岗"}
        for i in range(player_count)
    }
    st.success(f"已生成 {player_count} 名员工，KPI 初始为 0。")

# 公屏：显示员工 KPI 和状态
st.subheader("【 公屏：员工 KPI 状态 】")
if st.session_state.players:
    for pid, info in st.session_state.players.items():
        st.markdown(f"- 员工 {pid} | KPI：{info['KPI']} | 状态：**{info['status']}**")
else:
    st.info("请先生成员工编号。")

# 公屏：公告显示
st.subheader("【 公屏公告 】")
if st.session_state.messages:
    for msg in reversed(st.session_state.messages[-10:]):
        if msg["type"] == "host":
            st.info(f"[主持人公告] {msg['text']}")
        elif msg["type"] == "player":
            st.warning(f"[玩家发言] {msg['text']}")
else:
    st.write("（暂无公告）")

# 主持人更新员工信息
st.subheader("【主持人面板：编辑 KPI 与状态】")
with st.form("update_form"):
    target_id = st.text_input("员工编号（如 005）")
    new_kpi = st.number_input("新的 KPI 值", min_value=0, max_value=999, value=100)
    new_status = st.selectbox("新的状态", ["在岗", "已淘汰", "弃权"])
    submit_update = st.form_submit_button("更新员工信息")
    if submit_update:
        if target_id in st.session_state.players:
            st.session_state.players[target_id]["KPI"] = new_kpi
            st.session_state.players[target_id]["status"] = new_status
            st.success(f"员工 {target_id} 信息已更新。")
        else:
            st.warning("该员工编号不存在，请检查输入。")

# 主持人公告
st.subheader("【主持人公告发布】")
with st.form("host_message_form"):
    host_msg = st.text_area("输入主持人公告内容：", height=100)
    send_host = st.form_submit_button("发送公告")
    if send_host and host_msg.strip():
        st.session_state.messages.append({"type": "host", "text": host_msg.strip()})
        st.success("主持人公告已发送。")

# 玩家公告
st.subheader("【玩家匿名发言】")
with st.form("player_message_form"):
    player_msg = st.text_area("输入公告（匿名）：", height=80)
    send_player = st.form_submit_button("提交发言")
    if send_player and player_msg.strip():
        st.session_state.messages.append({"type": "player", "text": player_msg.strip()})
        st.success("你的发言已发布到公屏。")

st.markdown("---")
st.caption("教学用途 - KPI 公屏系统 | Powered by Streamlit")
