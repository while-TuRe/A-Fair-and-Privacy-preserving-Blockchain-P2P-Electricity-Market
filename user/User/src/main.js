import './assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'


const app = createApp(App)

app.config.globalProperties.$http  = axios;
app.config.globalProperties.$user  = {
    address: '',
    key: ''
  };
// 配置 axios 默认的根路径
axios.defaults.baseURL = "http://127.0.0.1:5123";
// 可以在此处配置请求头、超时等
axios.defaults.headers.common['Authorization'] = 'Bearer token';
axios.defaults.timeout = 1000;

app.use(router)

app.mount('#app')
