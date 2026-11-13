<template>
  <el-container class="layout-container">
    <!-- 左侧侧边栏 (融合了导航与历史会话) -->
    <el-aside width="260px" class="sidebar">
      <div class="logo">
        <span style="font-size: 24px; margin-right: 8px">👟</span> ShoePilot
      </div>

      <!-- 顶部功能导航 -->
      <el-menu
        :default-active="route.path"
        router
        background-color="#111827"
        text-color="#9ca3af"
        active-text-color="#ffffff"
        style="border-right: none"
      >
        <el-menu-item index="/chat">💬 智能问答</el-menu-item>
        <el-menu-item index="/kb">📁 知识库管理</el-menu-item>
        <el-menu-item index="/summarize">📝 文档摘要</el-menu-item>
      </el-menu>

      <!-- 只有在问答页才显示历史记录 -->
      <div v-if="route.path === '/chat'" class="history-section">
        <div class="history-header">
          <span>最近对话</span>
          <el-button type="primary" size="small" round @click="handleNewChat"
            >+ 新建</el-button
          >
        </div>

        <!-- 历史记录滚动区 -->
        <div class="history-list">
          <div
            v-for="sess in chatStore.sessions"
            :key="sess.id"
            class="session-item"
            :class="{ active: chatStore.currentSessionId === sess.id }"
            @click="handleSelectSession(sess.id)"
          >
            <el-icon style="margin-right: 8px; flex-shrink: 0"
              ><ChatDotRound
            /></el-icon>
            <span class="title">{{ sess.title }}</span>

            <!-- 悬浮操作区：直接用两个图标 -->
            <div class="action-menu" @click.stop>
              <el-icon @click="handleRename(sess)" class="action-icon edit-icon"
                ><Edit
              /></el-icon>
              <el-icon
                @click="handleDelete(sess)"
                class="action-icon delete-icon"
                ><Delete
              /></el-icon>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部退出按钮 -->
      <div class="sidebar-footer">
        <el-button type="danger" text style="width: 100%" @click="handleLogout">
          <el-icon style="margin-right: 5px"><SwitchButton /></el-icon> 退出登录
        </el-button>
      </div>
    </el-aside>

    <!-- 右侧主内容区 -->
    <el-main class="main-content">
      <router-view />
    </el-main>
  </el-container>
</template>

<script setup>
import { useRoute, useRouter } from "vue-router";
import { useUserStore } from "../stores/user";
import { useChatStore } from "../stores/chat";
import { onMounted } from "vue";
import { ElMessageBox, ElMessage } from "element-plus";
import {
  ChatDotRound,
  SwitchButton,
  Edit,
  Delete,
} from "@element-plus/icons-vue"; // 换成这两个图标

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const chatStore = useChatStore();

onMounted(() => {
  chatStore.fetchSessions();
});

const handleLogout = () => {
  userStore.logout();
  router.push("/login");
};

const handleRename = (sess) => {
  ElMessageBox.prompt("请输入新的会话名称", "重命名", {
    confirmButtonText: "确定",
    cancelButtonText: "取消",
    inputValue: sess.title,
    inputValidator: (value) => {
      if (!value || !value.trim()) return "名称不能为空";
      if (value.length > 20) return "名称不能超过20个字";
      return true;
    },
  })
    .then(async ({ value }) => {
      await chatStore.updateSessionTitle(sess.id, value);
    })
    .catch(() => {});
};

const handleDelete = (sess) => {
  ElMessageBox.confirm("确定要删除这个会话吗？聊天记录将无法恢复。", "警告", {
    confirmButtonText: "删除",
    cancelButtonText: "取消",
    type: "warning",
    confirmButtonClass: "el-button--danger",
  })
    .then(() => {
      chatStore.deleteSession(sess.id);
    })
    .catch(() => {});
};

const handleNewChat = () => {
  chatStore.startNewChat();
  if (route.path !== "/chat") router.push("/chat");
};

const handleSelectSession = (id) => {
  chatStore.loadSession(id);
  if (route.path !== "/chat") router.push("/chat");
};
</script>

<style scoped>
/* 修改已有的 session-item */
.session-item {
  position: relative;
  display: flex;
  align-items: center;
  padding: 12px 15px;
  border-radius: 8px;
  cursor: pointer;
  color: #9ca3af;
  font-size: 14px;
  margin-bottom: 4px;
  transition: all 0.2s;
  /* 右侧留出空间给操作图标 */
  padding-right: 70px;
}
.session-item:hover {
  background: #1f2937;
  color: #fff;
}
.session-item.active {
  background: #2563eb;
  color: #fff;
}

.title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

/* 悬浮图标区 */
.action-menu {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  gap: 8px;
  opacity: 0; /* 默认隐藏 */
  transition: opacity 0.2s;
  background: inherit; /* 继承当前背景色（深色或蓝色），防止字从底下透出来 */
  padding-left: 10px;
}

/* 鼠标悬浮行时，显示图标 */
.session-item:hover .action-menu {
  opacity: 1;
}

.action-icon {
  cursor: pointer;
  font-size: 15px;
  color: #9ca3af;
  transition: color 0.2s;
}
.action-icon:hover {
  color: #fff;
}
.delete-icon:hover {
  color: #ef4444; /* 悬浮删除时变红 */
}
.layout-container {
  height: 100vh;
  width: 100vw;
  overflow: hidden;
}
.sidebar {
  background-color: #111827;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #1f2937;
}

.logo {
  height: 64px;
  line-height: 64px;
  text-align: center;
  color: #ffffff;
  font-size: 20px;
  font-weight: 600;
  background: #0f172a;
  letter-spacing: 1px;
  border-bottom: 1px solid #1f2937;
}

/* 历史记录区：占据剩余全部空间 */
.history-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* 防止撑破 */
  border-top: 1px solid #1f2937;
  margin-top: 10px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px 10px;
  color: #6b7280;
  font-size: 13px;
}

/* 核心：这里控制从下往上堆叠和滑动 */
.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 0 10px;
  display: flex;
  flex-direction: column;
  /* 保证内容少的时候，依然贴着下面，但为了看着顺眼，还是从上往下排列 */
}

/* 滚动条美化 */
.history-list::-webkit-scrollbar {
  width: 4px;
}
.history-list::-webkit-scrollbar-thumb {
  background: #374151;
  border-radius: 4px;
}

.session-item {
  display: flex;
  align-items: center;
  padding: 12px 15px;
  border-radius: 8px;
  cursor: pointer;
  color: #9ca3af;
  font-size: 14px;
  margin-bottom: 4px;
  transition: all 0.2s;
}
.session-item:hover {
  background: #1f2937;
  color: #fff;
}
.session-item.active {
  background: #2563eb;
  color: #fff;
}
.title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

.sidebar-footer {
  padding: 15px;
  border-top: 1px solid #1f2937;
}

.main-content {
  padding: 24px;
  background-color: #f3f4f6;
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 0; /* 添加这一行，完美解决右侧文字跑出屏幕的问题 */
  box-sizing: border-box;
}
</style>
