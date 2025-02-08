# 赞同按钮（仅当未投票时可见）
if file not in st.session_state.voted_images:
    upvote_button = st.button(f"👍 Upvote {image_number}", key=f"upvote_{file}")
    if upvote_button:
        st.session_state.vote_count[file]["upvotes"] += 1
        st.session_state.voted_images.add(file)
        st.success(f"✅ You upvoted {image_number}!")
