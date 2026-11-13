import { createRouter, createWebHistory } from "vue-router";
import { useUserStore } from "../stores/user";

const router = createRouter({
    history: createWebHistory(),
    routes: [
        { path: "/login", component: () =>
                import ("../views/LoginView.vue") },
        {
            path: "/",
            component: () =>
                import ("../layouts/MainLayout.vue"),
            children: [
                { path: "", redirect: "/chat" },
                { path: "chat", component: () =>
                        import ("../views/ChatView.vue") },
                { path: "kb", component: () =>
                        import ("../views/KbView.vue") },
                {
                    path: "summarize",
                    component: () =>
                        import ("../views/SummarizeView.vue"),
                },
            ],
        },
    ],
});

// 全局前置守卫：没登录全踢回 /login
router.beforeEach((to, from, next) => {
    const userStore = useUserStore();
    if (to.path !== "/login" && !userStore.token) {
        next("/login");
    } else if (to.path === "/login" && userStore.token) {
        next("/"); // 已登录就不让看登录页了
    } else {
        next();
    }
});

export default router;