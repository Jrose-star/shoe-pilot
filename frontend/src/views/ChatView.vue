<template>
  <div class="chat-container">
    <div class="chat-area" ref="chatBox">
      <div v-if="chatStore.chatHistory.length === 0" class="empty-state">
        <h2>👋 你好，我是 ShoePilot</h2>
        <p>你可以问我任何关于鞋类产品、售后、保养等问题。</p>
      </div>

      <div
        v-for="(msg, index) in chatStore.chatHistory"
        :key="index"
        :class="['msg-row', msg.role]"
      >
        <div class="msg-avatar">
          <span v-if="msg.role === 'user'">👤</span>
          <span v-else>🤖</span>
        </div>
        <div class="msg-content-wrapper">
          <div class="msg-bubble">
            <div class="msg-text">{{ msg.content }}</div>

            <div
              v-if="msg.citations && msg.citations.length > 0"
              class="citations-box"
            >
              <div class="citation-title">📚 参考知识库片段</div>
              <div
                v-for="(cite, i) in msg.citations"
                :key="i"
                class="citation-item"
              >
                {{ cite }}
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-if="loading" class="typing-indicator">
        <span></span><span></span><span></span> ShoePilot 正在思考...
      </div>
    </div>

    <div class="input-wrapper">
      <div class="input-box">
        <input
          v-model="question"
          @keyup.enter="sendMessage"
          placeholder="请输入您的问题，按 Enter 发送..."
        />
        <el-button
          type="primary"
          class="send-btn"
          @click="sendMessage"
          :loading="loading"
        >
          发送
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, watch } from "vue";
import { useChatStore } from "../stores/chat";
import { ElMessage } from "element-plus";

const chatStore = useChatStore();
const question = ref("");
const loading = ref(false);
const chatBox = ref(null);

const scrollToBottom = async () => {
  await nextTick();
  if (chatBox.value) chatBox.value.scrollTop = chatBox.value.scrollHeight;
};

// 监听 store 中的历史记录变化，自动滚到底部
watch(
  () => chatStore.chatHistory,
  () => {
    scrollToBottom();
  },
  { deep: true },
);

// const sendMessage = async () => {
//   if (!question.value || loading.value) return;
//   const currentQuestion = question.value;
//   question.value = "";
//   loading.value = true;

//   // 1. 加入用户消息
//   chatStore.chatHistory.push({ role: "user", content: currentQuestion });
//   scrollToBottom();

//   // 2. 准备 AI 消息占位
//   const aiMsgIndex =
//     chatStore.chatHistory.push({
//       role: "assistant",
//       content: "",
//       citations: [],
//     }) - 1;

//   try {
//     const response = await fetch("http://127.0.0.1:8000/api/chat", {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//         Authorization: `Bearer ${localStorage.getItem("token")}`,
//       },
//       body: JSON.stringify({
//         question: currentQuestion,
//         session_id: chatStore.currentSessionId,
//       }),
//     });

//     if (!response.ok) throw new Error("网络请求失败");

//     const reader = response.body.getReader();
//     const decoder = new TextDecoder("utf-8");

//     while (true) {
//       const { done, value } = await reader.read();
//       if (done) break;

//       const chunk = decoder.decode(value, { stream: true });
//       const lines = chunk.split("\n");
//       for (const line of lines) {
//         if (line.startsWith("data: ")) {
//           const dataStr = line.replace("data: ", "").trim();
//           if (dataStr === "[DONE]") continue;

//           try {
//             const data = JSON.parse(dataStr);

//             if (data.type === "meta" && !chatStore.currentSessionId) {
//               chatStore.currentSessionId = data.session_id;
//               chatStore.fetchSessions();
//             }

//             if (data.type === "content") {
//               chatStore.chatHistory[aiMsgIndex].content += data.text;
//             }
//           } catch (e) {
//             console.error("解析流失败", e);
//           }
//         }
//       }
//     }
//   } catch (error) {
//     ElMessage.error("连接断开");
//     chatStore.chatHistory[aiMsgIndex].content = "抱歉，服务器连接出现了问题。";
//   } finally {
//     loading.value = false;
//   }
// };
const sendMessage = async () => {
  if (!question.value || loading.value) return;
  const currentQuestion = question.value;
  question.value = "";
  loading.value = true;

  chatStore.chatHistory.push({ role: "user", content: currentQuestion });
  scrollToBottom();

  const aiMsgIndex =
    chatStore.chatHistory.push({
      role: "assistant",
      content: "",
      citations: [],
    }) - 1;

  try {
    const response = await fetch("http://127.0.0.1:8000/api/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("token")}`,
      },
      body: JSON.stringify({
        question: currentQuestion,
        session_id: chatStore.currentSessionId,
      }),
    });

    if (!response.ok) throw new Error("网络请求失败");

    const res = await response.json();

    // 打印确认一下结构
    console.log("后端返回的完整数据:", res);

    // 你的后端把真正的数据包在了 res.data 里面
    const realData = res.data;

    if (realData) {
      // 1. 更新 session_id
      if (!chatStore.currentSessionId && realData.session_id) {
        chatStore.currentSessionId = realData.session_id;
        chatStore.fetchSessions();
      }

      // 2. 赋值正确的回答文本
      chatStore.chatHistory[aiMsgIndex].content =
        realData.answer || "未收到有效回复";

      // 3. 赋值 citations (引用)
      if (realData.citations) {
        chatStore.chatHistory[aiMsgIndex].citations = realData.citations;
      }
    } else {
      chatStore.chatHistory[aiMsgIndex].content = "数据结构异常，请查看控制台";
    }
  } catch (error) {
    console.error("请求异常:", error);
    ElMessage.error("连接断开");
    chatStore.chatHistory[aiMsgIndex].content = "抱歉，服务器连接出现了问题。";
  } finally {
    loading.value = false;
    scrollToBottom();
  }
};

onMounted(() => {
  scrollToBottom();
});
</script>

<style scoped>
.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
  overflow: hidden;
  height: 100%;
}

.chat-area {
  flex: 1;
  padding: 30px 40px;
  overflow-y: auto;
  background: #fafbfc;
}

.empty-state {
  text-align: center;
  color: #8c95a1;
  margin-top: 20vh;
}
.empty-state h2 {
  color: #374151;
  margin-bottom: 10px;
  font-weight: 500;
}

/* 消息行布局 */
.msg-row {
  display: flex;
  margin-bottom: 32px;
  gap: 16px;
}
.msg-row.user {
  flex-direction: row-reverse;
}

.msg-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e5e7eb;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 20px;
  flex-shrink: 0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}
.user .msg-avatar {
  background: #dbeafe;
}

/* 消息内容区 */
.msg-content-wrapper {
  max-width: 75%;
  display: flex;
  flex-direction: column;
}
.user .msg-content-wrapper {
  align-items: flex-end;
}

.msg-bubble {
  padding: 16px 20px;
  border-radius: 12px;
  font-size: 16px;
  line-height: 1.7; /* 增加行高，更易读 */
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}
.user .msg-bubble {
  background: #2563eb;
  color: #fff;
  border-top-right-radius: 2px;
}
.assistant .msg-bubble {
  background: #fff;
  color: #1f2937;
  border-top-left-radius: 2px;
  border: 1px solid #eaeef2;
}

.msg-text {
  white-space: pre-wrap;
  word-break: break-word;
}

/* 引用框 */
.citations-box {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px dashed #d1d5db;
}
.citation-title {
  font-size: 13px;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 10px;
}
.citation-item {
  background: #f8fafc;
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
  color: #4b5563;
  margin-bottom: 8px;
  border-left: 4px solid #3b82f6;
}

/* 打字动画 */
.typing-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #6b7280;
  font-size: 14px;
  margin-left: 56px;
  margin-bottom: 32px;
}
.typing-indicator span {
  width: 6px;
  height: 6px;
  background: #9ca3af;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}
.typing-indicator span:nth-child(1) {
  animation-delay: -0.32s;
}
.typing-indicator span:nth-child(2) {
  animation-delay: -0.16s;
}
@keyframes bounce {
  0%,
  80%,
  100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* 底部输入区 */
.input-wrapper {
  padding: 20px 40px;
  background: #ffffff;
  border-top: 1px solid #f0f0f0;
}
.input-box {
  display: flex;
  gap: 12px;
  background: #f4f6f8;
  padding: 10px 10px 10px 20px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  transition: all 0.2s;
}
.input-box:focus-within {
  border-color: #3b82f6;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}
.input-box input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 16px;
  outline: none;
  padding: 10px 0;
}
.send-btn {
  padding: 0 24px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
}
</style>
