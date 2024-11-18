<template>
<el-form ref="registerForm" :model="registerForm" :rules="registerRules" class="register-form">
	// 用户名
	<el-form-item prop="username">
          <el-input v-model="registerForm.username" type="text" placeholder="账号">
            <svg-icon slot="prefix" icon-class="user" class="el-input__icon input-icon" />
          </el-input>
    </el-form-item>
    // 密码
	<el-form-item prop="password">
          <el-input
            v-model="registerForm.password"
            type="password"
            auto-complete="off"
            placeholder="密码"
            @keyup.enter.native="handleRegister"
          >
            <svg-icon slot="prefix" icon-class="password" class="el-input__icon input-icon" />
          </el-input>
    </el-form-item>
    // 确认密码
    <el-form-item prop="confirmPassword">
          <el-input
            v-model="registerForm.confirmPassword"
            type="password"
            auto-complete="off"
            placeholder="确认密码"
            @keyup.enter.native="handleRegister"
          >
            <svg-icon slot="prefix" icon-class="password" class="el-input__icon input-icon" />
          </el-input>
   	</el-form-item>
   	<el-form-item prop="phonenumber">
          <el-input
            v-model="registerForm.phonenumber"
            maxlength="11"
            placeholder="请输入手机号"
            @keyup.enter.native="handleRegister"
          >
            <svg-icon slot="prefix" icon-class="el-icon-phone" class="el-input__icon input-icon" />
          </el-input>
    </el-form-item>
    // 验证码
    <el-form-item prop="code" v-if="captchaEnabled">
          <el-input
            v-model="registerForm.code"
            auto-complete="off"
            placeholder="验证码"
            style="width: 70%"
            @keyup.enter.native="handleRegister"
          >
            <svg-icon slot="prefix" icon-class="validCode" class="el-input__icon input-icon" />
          </el-input>
          <div class="register-code">
          	// 验证码图片
            <img :src="codeUrl" @click="getCode" class="register-code-img"/>
          </div>
     </el-form-item>
     // 注册按钮
     <el-form-item style="width:100%;">
          <el-button
            :loading="loading"
            size="medium"
            type="primary"
            style="width:100%;"
            @click.native.prevent="handleRegister"
          >
            <span v-if="!loading">注 册</span>
            <span v-else>注 册 中...</span>
          </el-button>
          <div style="float: right;">
            <router-link class="link-type" :to="'/login'">使用已有账户登录</router-link>
          </div>
    </el-form-item>
</el-form>
</template>
<script>
export default {
	data() {
		const equalToPassword = (rule, value, callback) => {
	      if (this.registerForm.password !== value) {
	        callback(new Error("两次输入的密码不一致"));
	      } else {
	        callback();
	      }
	    };
	    // 密码校验 长度不能小于8位且不能大于20位字符,必须包含大写字母、小写字母、数字和特殊符号
	    var ISPWD =/^(?=.*[0-9])(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$%^&*,\._\+(){}])[0-9a-zA-Z!@#$%^&*,\\._\+(){}]{8,20}$/;
	    // 密码校验
	    const validatePassword = (rule, value, callback) =>{
	      if (!ISPWD.test(this.registerForm.password)) {
	        callback(new Error("用户密码必须包含大写字母、小写字母、数字和特殊符号"));
	      } else {
	        callback();
	      }
	    }
	    return {
	    	registerForm: { // 注册接口传参
		        username: "",  // 用户名
		        password: "",  // 密码
		        confirmPassword: "",  // 确认密码
		        phonenumber:'', // 手机号
		        deptId:'',
		        code: "", // 验证码
		        uuid: ""
		      },
		      // 校验
		      registerRules: {
		        username: [
		          { required: true, trigger: "blur", message: "请输入您的账号" },
		          { min: 2, max: 20, message: '用户账号长度必须介于 2 和 20 之间', trigger: 'blur' }
		        ],
		        // 密码校验
		        password: [
		          { required: true, trigger: "blur", message: "请输入您的密码" },
		          { min: 8, max: 20, message: '用户密码长度必须介于 8 和 20 之间', trigger: 'blur' },
		          { required: true, validator: validatePassword, trigger: 'blur' }
		        ],
		        // 手机号校验
		        phonenumber:[
		          {
		            pattern: /^1[3|4|5|6|7|8|9][0-9]\d{8}$/, message: "请输入正确的手机号码", trigger: "blur"
		          }
		        ],
		        // 确认密码校验
		        confirmPassword: [
		          { required: true, trigger: "blur", message: "请再次输入您的密码" },
		          { required: true, validator: equalToPassword, trigger: "blur" }
		        ],
		        // 验证码校验
		        code: [{ required: true, trigger: "change", message: "请输入验证码" }]
		      },
		      loading: false,
              captchaEnabled: true
	    }
	},
	methods: {
		// 获取验证码图片
		getCode() {
	      getCodeImg().then(res => {
	        this.captchaEnabled = res.captchaEnabled === undefined ? true : res.captchaEnabled;
	        if (this.captchaEnabled) {
	          this.codeUrl = "data:image/gif;base64," + res.img;
	          this.registerForm.uuid = res.uuid;
	        }
	      });
	    }
	}
}
</script>
        
