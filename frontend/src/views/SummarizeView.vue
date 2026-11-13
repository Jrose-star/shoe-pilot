<template>
  <div class="view-container">
    <div class="header">
      <h2>智能摘要与纪要生成</h2>
      <p>支持长文档、工作记录和会议记录的一键提炼。</p>
    </div>

    <div class="toolbar">
      <el-select
        v-model="summaryType"
        placeholder="选择摘要类型"
        style="width: 240px"
      >
        <el-option label="📄 长文档摘要（一页读懂）" value="document" />
        <el-option label="📅 工作记录转周报" value="weekly" />
        <el-option label="🤝 会议记录转纪要" value="meeting" />
      </el-select>
      <el-button type="primary" @click="doSummarize" :loading="summarizing">
        {{ summarizing ? "✨ AI 提炼中..." : "✨ 开始生成" }}
      </el-button>
    </div>

    <div class="split-view">
      <!-- 左侧输入 -->
      <div class="col">
        <label>输入源文本</label>
        <el-input
          v-model="sourceText"
          type="textarea"
          :rows="18"
          placeholder="请粘贴长文档内容或工作记录..."
          resize="none"
        />
      </div>
      <!-- 右侧输出 -->
      <div class="col">
        <label style="color: #409eff">✨ AI 生成结果</label>
        <div
          class="result-box"
          v-loading="summarizing"
          element-loading-text="AI 正在深度阅读并提炼..."
        >
          <div v-if="!summaryResult" class="placeholder">
            生成结果将在这里展示...
          </div>
          <div v-else class="content">{{ summaryResult }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import request from "../api";
import { ElMessage } from "element-plus";

const sourceText = ref("");
const summaryType = ref("document");
const summaryResult = ref("");
const summarizing = ref(false);

const doSummarize = async () => {
  if (!sourceText.value.trim())
    return ElMessage.warning("请输入需要摘要的文本");

  summarizing.value = true;
  summaryResult.value = "";

  try {
    const res = await request.post("/summarize", {
      text: sourceText.value,
      summary_type: summaryType.value,
    });
    summaryResult.value = res.data.result;
  } catch (error) {
    summaryResult.value = "生成失败，请检查后端终端是否报错。";
  } finally {
    summarizing.value = false;
  }
};
</script>

<style scoped>
.view-container {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}
.header {
  margin-bottom: 20px;
}
.header h2 {
  margin: 0 0 8px 0;
  color: #303133;
}
.header p {
  margin: 0;
  color: #909399;
  font-size: 14px;
}
.toolbar {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
}
.split-view {
  flex: 1;
  display: flex;
  gap: 20px;
  min-height: 0;
}
.col {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.col label {
  font-weight: bold;
  margin-bottom: 10px;
  color: #606266;
  font-size: 14px;
}
/* 覆盖 el-input 的默认高度让它撑满 */
:deep(.el-textarea__inner) {
  height: 100%;
  font-family: inherit;
  font-size: 14px;
}
.result-box {
  flex: 1;
  border: 1px solid #e4e7ed;
  background: #f8f9fa;
  border-radius: 4px;
  padding: 15px;
  overflow-y: auto;
}
.placeholder {
  color: #909399;
  text-align: center;
  margin-top: 40px;
}
.content {
  white-space: pre-wrap;
  line-height: 1.6;
  color: #303133;
  font-size: 14px;
}
</style>
