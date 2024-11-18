<!--
我们可以使用 v-model 指令在状态和表单输入之间创建双向绑定。
-->

<script setup>
import { ref } from 'vue'

const text = ref('Edit me')
const checked = ref(true)
const checkedNames = ref(['Jack'])
const picked = ref('One')
const selected = ref('A')
const multiSelected = ref(['A'])
</script>

<template>
  <h2>Login</h2>
  <h3>address</h3>
  <input v-model="user.address">
  <h3>private key</h3>
  <input
    type="password"
    placeholder="private key"
    autocomplete="off"
    v-model="user.key"
  />
  <h3></h3>
  <button @click="requestLogin">login</button>
</template>

<script>
export default {
  data() {
    return {
      data: null,
      user:this.$user
    };
  },
  methods: {
    requestLogin() {
      console.log("click requestlogin");
      this.$http.post('/login', {
        address: this.$user.address, // 使用 user.address
        key: this.$user.key          // 使用 user.key
      }).then(result => {
        console.log(result.data);
        console.log(result.status);
        this.$router.push('/board'); // 替换 '/another-page' 为目标路由路径
      }).catch(error => {
        if (error.response) {
          // 请求已发出，服务器响应了状态码
          console.log('Error data:', error.response.data); // 服务器返回的错误信息
          console.log('Error status:', error.response.status); // 状态码
          console.log('Error headers:', error.response.headers); // 响应头
        } else if (error.request) {
          // 请求已发出，但没有收到响应
          console.log('Error request:', error.request);
        } else {
          // 发生了其他错误
          console.log('Error message:', error.message);
        }
      });
    }
  }
};
</script>