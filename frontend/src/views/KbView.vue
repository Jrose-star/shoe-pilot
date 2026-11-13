<template>
  <div class="view-container">
    <div class="header">
      <h2>知识库管理</h2>
      <p>管理智能助手的底层知识资产，支持 PDF, Word, TXT, Markdown 格式。</p>
    </div>

    <!-- 上传区域 -->
    <div class="upload-card">
      <div class="upload-info">
        <h3>上传新文档</h3>
      </div>
      <div class="upload-action">
        <input
          type="file"
          ref="fileInput"
          accept=".pdf,.docx,.txt,.md"
          style="display: none"
          @change="handleFileChange"
        />
        <el-button @click="fileInput.click()">浏览文件</el-button>
        <span class="file-name">{{ selectedFileName || "未选择文件" }}</span>
        <el-button
          type="primary"
          @click="uploadFile"
          :loading="uploading"
          :disabled="!selectedFile"
        >
          {{ uploading ? "解析入库中..." : "开始上传" }}
        </el-button>
      </div>
    </div>

    <!-- 文档列表 -->
    <div class="list-container">
      <h3>
        已入库文档
        <el-tag size="small" type="info" round>{{ documents.length }}</el-tag>
      </h3>
      <el-table
        :data="documents"
        style="width: 100%"
        v-loading="loadingList"
        border
        stripe
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        <el-table-column
          prop="title"
          label="文件名"
          min-width="200"
          show-overflow-tooltip
        />
        <el-table-column
          prop="source_type"
          label="格式"
          width="100"
          align="center"
        >
          <template #default="scope">
            <el-tag size="small" effect="plain">{{
              scope.row.source_type
            }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="120" align="center">
          <template #default="scope">
            <el-tag
              :type="scope.row.status === 'processed' ? 'success' : 'warning'"
              size="small"
            >
              {{ scope.row.status === "processed" ? "已就绪" : "处理中" }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import request from "../api";
import { ElMessage } from "element-plus";

const documents = ref([]);
const loadingList = ref(false);
const fileInput = ref(null);
const selectedFile = ref(null);
const selectedFileName = ref("");
const uploading = ref(false);

const loading = ref(false); // 确保你定义了 loading 变量

const loadDocuments = async () => {
  loading.value = true; // 开始转圈
  try {
    const res = await request.get("/api/kb/documents");
    console.log("后端返回的原始 res：", res);
    // 核心注意点：要看你的 api/index.js 拦截器有没有返回 res.data
    // 如果拦截器里 return 的是 response，这里就是 res.data.data
    // 如果拦截器里 return 的是 response.data，这里就是 res.data
    // 结合你之前的截图，接口返回的是 { code: 0, data: [] }
    // 所以这里很可能是：
    documents.value = res.data.data || [];
  } catch (error) {
    console.error(error);
  } finally {
    loading.value = false; // 关键：无论成功失败，结束转圈！
  }
};

const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (file) {
    selectedFile.value = file;
    selectedFileName.value = file.name;
  } else {
    selectedFile.value = null;
    selectedFileName.value = "";
  }
};

const uploadFile = async () => {
  if (!selectedFile.value) return ElMessage.warning("请先选择文件");
  uploading.value = true;

  const formData = new FormData();
  formData.append("file", selectedFile.value);

  try {
    const res = await request.post("/api/kb/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    ElMessage.success(res.message);
    // 清空选择状态
    selectedFile.value = null;
    selectedFileName.value = "";
    if (fileInput.value) fileInput.value.value = "";
    // 刷新列表
    loadDocuments();
  } catch (error) {
  } finally {
    uploading.value = false;
  }
};

onMounted(() => {
  loadDocuments();
});
</script>

<style scoped>
.view-container {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  height: 100%;
  box-sizing: border-box;
  overflow-y: auto;
}
.header {
  margin-bottom: 24px;
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

.upload-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px dashed #c0c4cc;
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 24px;
}
.upload-info h3 {
  margin: 0;
  color: #303133;
  font-size: 16px;
}
.upload-action {
  display: flex;
  align-items: center;
  gap: 12px;
}
.file-name {
  font-size: 14px;
  color: #606266;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.list-container h3 {
  margin: 0 0 16px 0;
  color: #303133;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
</style>
