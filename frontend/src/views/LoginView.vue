<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2 style="text-align: center; margin-bottom: 30px">
        👟 ShoePilot 企业智库
      </h2>
      <el-tabs v-model="activeTab" stretch>
        <el-tab-pane label="登录" name="login">
          <el-form :model="form" label-width="80px">
            <el-form-item label="账号">
              <el-input v-model="form.username" placeholder="请输入账号" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                show-password
              />
            </el-form-item>
            <el-button
              type="primary"
              style="width: 100%; margin-top: 10px"
              @click="handleLogin"
              :loading="loading"
              >登 录</el-button
            >
          </el-form>
        </el-tab-pane>
        <el-tab-pane label="注册" name="register">
          <el-form :model="form" label-width="80px">
            <el-form-item label="账号">
              <el-input v-model="form.username" placeholder="设置账号" />
            </el-form-item>
            <el-form-item label="密码">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="设置密码"
                show-password
              />
            </el-form-item>
            <el-button
              type="success"
              style="width: 100%; margin-top: 10px"
              @click="handleRegister"
              :loading="loading"
              >注 册</el-button
            >
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useRouter } from "vue-router";
import { useUserStore } from "../stores/user";
import request from "../api";
import { ElMessage } from "element-plus";

const activeTab = ref("login");
const loading = ref(false);
const router = useRouter();
const userStore = useUserStore();

const form = reactive({ username: "", password: "" });

const handleLogin = async () => {
  if (!form.username || !form.password) return ElMessage.warning("请填写完整");
  loading.value = true;
  try {
    // 登录接口必须使用 x-www-form-urlencoded 格式
    const params = new URLSearchParams();
    params.append("username", form.username);
    params.append("password", form.password);

    const res = await request.post("/api/auth/login", params);
    console.log("登录接口返回的数据：", res);
    userStore.setToken(res.data.access_token);
    ElMessage.success("登录成功");
    router.push("/");
  } catch (error) {
    // 错误已被拦截器处理
  } finally {
    loading.value = false;
  }
};

const handleRegister = async () => {
  if (!form.username || !form.password) return ElMessage.warning("请填写完整");
  loading.value = true;
  try {
    const res = await request.post("/api/auth/register", form);
    userStore.setToken(res.access_token);
    ElMessage.success("注册成功，已自动登录");
    router.push("/");
  } catch (error) {
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
}
.login-card {
  width: 400px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}
</style>
