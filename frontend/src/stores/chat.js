import { defineStore } from "pinia";
import { ref } from "vue";
import request from "../api";

export const useChatStore = defineStore("chat", () => {
    const sessions = ref([]);
    const currentSessionId = ref(null);
    const chatHistory = ref([]);

    // 💡 终极剥离函数：无论套了几层 data，都能挖出底层的数组
    const extractArray = (res) => {
        let data = res;
        if (res && res.data) data = res.data;
        if (data && data.data) data = data.data;
        return Array.isArray(data) ? data : [];
    };

    const fetchSessions = async() => {
        try {
            const res = await request.get("/api/sessions");
            sessions.value = extractArray(res); // 强行挖出纯数组
            console.log("✅ 最终渲染的纯数组:", sessions.value);
        } catch (error) {
            console.error("获取会话失败", error);
        }
    };

    const loadSession = async(id) => {
        if (!id || id === "undefined") {
            console.warn("⚠️ 拦截到非法的会话 ID");
            return;
        }
        currentSessionId.value = id;
        try {
            const res = await request.get(`/api/sessions/${id}`);
            chatHistory.value = extractArray(res); // 强行挖出纯数组
        } catch (error) {
            console.error("加载消息失败", error);
        }
    };

    const startNewChat = () => {
        currentSessionId.value = null;
        chatHistory.value = [];
    };
    // 修改名称
    const updateSessionTitle = async(id, newTitle) => {
        try {
            // 1. 先在前端直接改掉（瞬间响应）
            const target = sessions.value.find((s) => s.id === id);
            if (target) {
                target.title = newTitle;
            }

            // 2. 后台静默发请求给数据库
            await request.put(`/api/sessions/${id}`, { title: newTitle });
            ElMessage.success("重命名成功");
        } catch (error) {
            ElMessage.error("修改失败");
            fetchSessions(); // 如果失败，拉取最新数据回滚
        }
    };

    // 删除会话
    const deleteSession = async(id) => {
        try {
            // 1. 先在前端直接过滤掉（瞬间消失）
            sessions.value = sessions.value.filter((s) => s.id !== id);

            // 2. 如果删的是当前窗口，直接清空聊天
            if (currentSessionId.value === id) {
                startNewChat();
            }

            // 3. 后台静默发请求
            await request.delete(`/api/sessions/${id}`);
            ElMessage.success("已删除");
        } catch (error) {
            ElMessage.error("删除失败");
            fetchSessions(); // 失败则拉取最新数据回滚
        }
    };
    return {
        sessions,
        currentSessionId,
        chatHistory,
        fetchSessions,
        loadSession,
        startNewChat,
        updateSessionTitle, // 新增
        deleteSession,
    };
});