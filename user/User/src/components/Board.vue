<template>
  <div>
    <h1>balance</h1>
    <h2>token</h2>
    <p>{{ balance.token }}</p>
    <h2>electricity</h2>
    <p>{{ balance.electricity }}</p>

    <h1>Order</h1>
    <form @submit.prevent="submitOrder">
      <div>
        <label for="price">price</label>
        <input type="number" v-model="order.price" required />
      </div>
      <div>
        <label for="quantity">quantity:</label>
        <input type="number" v-model="order.quantity" required min="1" />
      </div>
      <div>
        <label>type:</label>
        <div>
          <label>
            <input type="radio" value=1 v-model="order.is_bid" />
            buy
          </label>
          <label>
            <input type="radio" value=0 v-model="order.is_bid" />
            sell
          </label>
        </div>
      </div>
      <button type="submit">submit</button>
    </form>

    <button @click="verify">verify</button>

    <div v-if="verifyMessage" class="verify">
      <h2>verification result:</h2>
      <p>{{ verifyMessage }}</p>
    </div>

    <div v-if="resultMessage" class="result">
      <h2>submit result:</h2>
      <p>{{ resultMessage }}</p>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      // user:this.$user,
      balance: {
        token: 0,
        electricity: 0
      },
      order:{
        quantity:0,
        price:0,
        is_bid:0
      },
      resultMessage:'',
      verifyMessage: "",
      intervalId: null
    };
  },
  methods: {
    async fetchBalance() {
      try {
        const response = await this.$http.get('board',{ params: { method: 'balance',user: this.$user.address } }); // 使用 this.$http
        this.balance.token = response.data.balance.token; // 假设响应中包含 balance 字段
        this.balance.electricity = response.data.balance.electricity; // 假设响应中包含 balance 字段
      } catch (error) {
        console.error('获取余额失败:', error);
      }
    },
    async submitOrder() {
      try {
        // 假设你有一个 API 接口用于提交订单
        console.log('submit order:');
        const response = await this.$http.post('board', { method: 'order',user: this.$user.address,order:this.order });
        console.log('submit order:2');
        // 处理成功响应
        this.resultMessage = `order submit success: `;
        setTimeout(() => {
          this.resultMessage = ""; // Clear the message after 3 seconds
        }, 3000);
      } catch (error) {
        // 处理错误响应
        console.error('Error:', error.response.data.msg);
        this.resultMessage = `order submit fail: ${error.response.data.msg || 'unknown error'}`;
      }
    },
    verify() {
      this.verifyMessage = "verify pass";
      setTimeout(() => {
        this.verifyMessage = ""; // Clear the message after 3 seconds
      }, 3000);
    }
  },
  mounted() {
    this.fetchBalance(); // 初次请求余额
    this.intervalId = setInterval(this.fetchBalance, 20000); // 每10秒请求一次余额
  },
  beforeDestroy() {
    clearInterval(this.intervalId); // 清理定时器
  }
};
</script>