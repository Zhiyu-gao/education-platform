<template>
  <div class="app-container home">
    <el-row :gutter="20">
      <el-col :sm="24" :lg="24" style="text-align: center; margin-bottom: 30px;">
        <h1>融合rag的智能教育平台</h1>
        <p>致力于提供智能化的教育解决方案，助力学生成长和教师教学</p>
      </el-col>
    </el-row>
    
    <!-- 主要功能模块 -->
    <el-row :gutter="20" style="margin-bottom: 30px;">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <i class="el-icon-user-solid"></i>
              <span>学生信息管理</span>
            </div>
          </template>
          <div class="card-body">
            <ul>
              <li>学生信息录入与管理</li>
              <li>学习数据统计与分析</li>
              <li>个人档案管理</li>
            </ul>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <i class="el-icon-monitor"></i>
              <span>大屏可视化</span>
            </div>
          </template>
          <div class="card-body">
            <ul>
              <li>学生可视化自己的成绩</li>
              <li>教师可视化班级成绩</li>
              <li>数据图表动态展示</li>
            </ul>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <i class="el-icon-robot"></i>
              <span>教育智能助手</span>
            </div>
          </template>
          <div class="card-body">
            <ul>
              <li>自动识别数学公式</li>
              <li>批改作文和作业</li>
              <li>自动生成练习题</li>
              <li>实时解答问题和心理疏导</li>
            </ul>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <el-row :gutter="20" style="margin-bottom: 30px;">
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <i class="el-icon-data-analysis"></i>
              <span>教育情况预测</span>
            </div>
          </template>
          <div class="card-body">
            <ul>
              <li>输入相关信息，预测成绩</li>
              <li>预测学生毕业去向</li>
              <li>预警学生学习状态</li>
            </ul>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <i class="el-icon-folder-opened"></i>
              <span>资料圈</span>
            </div>
          </template>
          <div class="card-body">
            <ul>
              <li>学习资料分享</li>
              <li>评论与点赞</li>
              <li>资料收藏与粘贴</li>
            </ul>
          </div>
        </el-card>
      </el-col>
      
      <el-col :xs="24" :sm="12" :md="8">
        <el-card class="feature-card">
          <template #header>
            <div class="card-header">
              <i class="el-icon-upload"></i>
              <span>上传自定义题目</span>
            </div>
          </template>
          <div class="card-body">
            <ul>
              <li>支持上传自定义题目pk</li>
              <li>题目导入与管理</li>
              <li>个性化练习设置</li>
            </ul>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 技术栈 -->
    <el-row :gutter="20" style="margin-bottom: 30px;">
      <el-col :span="24">
        <el-card class="tech-stack">
          <template #header>
            <div class="card-header">
              <i class="el-icon-cpu"></i>
              <span>技术栈</span>
            </div>
          </template>
          <div class="card-body">
            <el-tag type="primary" v-for="tech in techStack" :key="tech" style="margin: 5px;">{{ tech }}</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 其他功能 -->
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="other-functions">
          <template #header>
            <div class="card-header">
              <i class="el-icon-menu"></i>
              <span>其他功能</span>
            </div>
          </template>
          <div class="card-body">
            <div class="function-grid">
              <el-button type="default" plain v-for="func in otherFunctions" :key="func.key" @click="goToFunction(func.key)">
                {{ func.name }}
              </el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup name="Index">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

const version = ref('1.0.0')
const techStack = ['tensorflow', 'vue3', 'elementplus', 'fastapi', 'langchain', 'LLM', 'RAG', 'nginx', 'docker']
const router = useRouter()

const otherFunctions = [
  { key: 'orgManage', name: '组织管理' },
  { key: 'userManage', name: '人员管理' },
  { key: 'classManage', name: '班级管理' },
  { key: 'pad', name: 'Pad端入口' },
  { key: 'login', name: '登录' },
  { key: 'register', name: '注册' },
  { key: 'punch', name: '打卡记录' },
  { key: 'searchNote', name: '搜索笔记' },
  { key: 'myNote', name: '我的笔记' },
  { key: 'questionRecord', name: '错题记录' },
  { key: 'myScore', name: '我的成绩' },
  { key: 'contactUs', name: '联系我们' },
  { key: 'feedback', name: '满意度调查' },
  { key: 'logout', name: '退出登录' }
]

function goTarget(url) {
  window.open(url, '__blank')
}

function goToFunction(key) {
  if (key === 'orgManage') {
    router.push('/system/dept')
    return
  }
  if (key === 'userManage') {
    router.push('/system/user')
    return
  }
  if (key === 'classManage') {
    router.push('/system/dept')
    return
  }
  if (key === 'pad') {
    router.push('/education/auth?redirect=/education/pad')
    return
  }
  // 这里可以根据实际路由进行跳转
  ElMessage(`正在跳转到${otherFunctions.find(f => f.key === key)?.name}功能`)
  // 实际项目中可以使用 router.push 进行跳转
}
</script>

<style scoped lang="scss">
.home {
  padding: 24px;
  font-family: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  color: #334155;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.62);
  border: 1px solid rgba(15, 23, 42, 0.06);
  
  h1 {
    font-size: 36px;
    margin-bottom: 10px;
    color: #0b3b51;
  }
  
  h2 {
    font-size: 24px;
    margin-bottom: 15px;
    color: #163f57;
  }
  
  .feature-card {
    height: 100%;
    transition: all 0.3s ease;
    
    &:hover {
      box-shadow: 0 10px 24px rgba(15, 23, 42, 0.1);
      transform: translateY(-4px);
    }
    
    .card-header {
      display: flex;
      align-items: center;
      font-size: 18px;
      font-weight: 500;
      color: #0f172a;
      
      i {
        margin-right: 8px;
        color: #0284c7;
      }
    }
    
    .card-body {
      padding: 15px 0;
      
      ul {
        list-style: none;
        padding: 0;
        margin: 0;
        
        li {
          padding: 8px 0;
          padding-left: 20px;
          position: relative;
          
          &::before {
            content: "•";
            color: #0f766e;
            position: absolute;
            left: 0;
            font-size: 18px;
          }
        }
      }
    }
  }
  
  .tech-stack {
    .card-body {
      display: flex;
      flex-wrap: wrap;
      justify-content: center;
    }
  }
  
  .other-functions {
    .function-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
      gap: 10px;
    }
  }
}
</style>
