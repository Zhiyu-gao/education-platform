<template>
  <div class="edu-screen">
    <div class="screen-bg"></div>
    <div class="screen-content">
      <header class="screen-header">
        <h1>2026 学年教学运营可视化大屏</h1>
        <p>大王集团 · 校区经营与教学质量总览</p>
      </header>

      <section class="metric-row">
        <div class="metric-card metric-orange">
          <span>年度作业提交量</span>
          <strong>{{ fmtNum(summary.homeworkSubmit) }}</strong>
        </div>
        <div class="metric-card metric-blue">
          <span>年度考试作答量</span>
          <strong>{{ fmtNum(summary.examSubmit) }}</strong>
        </div>
        <div class="metric-card metric-cyan">
          <span>平均完成率</span>
          <strong>{{ summary.completionRate }}%</strong>
        </div>
        <div class="metric-card metric-green">
          <span>同比增长</span>
          <strong>{{ summary.yoy }}%</strong>
        </div>
      </section>

      <section class="screen-grid">
        <el-card class="panel panel-a" shadow="never">
          <template #header>学校作业提交情况</template>
          <div ref="schoolBarRef" class="chart-box"></div>
        </el-card>

        <el-card class="panel panel-b" shadow="never">
          <template #header>各渠道目标完成进度</template>
          <div ref="channelBarRef" class="chart-box"></div>
        </el-card>

        <el-card class="panel panel-c" shadow="never">
          <template #header>任务类型占比</template>
          <div ref="typePieRef" class="chart-box"></div>
        </el-card>

        <el-card class="panel panel-d" shadow="never">
          <template #header>订单来源情况</template>
          <div ref="sourceStackRef" class="chart-box"></div>
        </el-card>

        <el-card class="panel panel-e" shadow="never">
          <template #header>月度趋势</template>
          <div ref="monthTrendRef" class="chart-box"></div>
        </el-card>

        <el-card class="panel panel-f" shadow="never">
          <template #header>与上年对比</template>
          <div ref="yearCompareRef" class="chart-box"></div>
        </el-card>

        <el-card class="panel panel-g" shadow="never">
          <template #header>教师完成榜（Top 8）</template>
          <el-table :data="teacherRank" height="280" size="small" stripe>
            <el-table-column prop="teacher" label="教师" min-width="80" />
            <el-table-column prop="className" label="班级" min-width="90" />
            <el-table-column prop="taskCount" label="任务量" width="80" />
            <el-table-column prop="score" label="完成分" width="90" />
          </el-table>
        </el-card>
      </section>
    </div>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import * as echarts from 'echarts'

const summary = {
  homeworkSubmit: 58200,
  examSubmit: 10280,
  completionRate: 93.4,
  yoy: 18.98
}

const teacherRank = [
  { teacher: '王晨', className: '一年级1班', taskCount: 430, score: 96 },
  { teacher: '李楠', className: '一年级2班', taskCount: 400, score: 95 },
  { teacher: '赵敏', className: '二年级1班', taskCount: 380, score: 94 },
  { teacher: '陈辉', className: '三年级2班', taskCount: 370, score: 92 },
  { teacher: '周婷', className: '四年级3班', taskCount: 360, score: 91 },
  { teacher: '林雪', className: '五年级1班', taskCount: 350, score: 90 },
  { teacher: '吴迪', className: '五年级2班', taskCount: 340, score: 90 },
  { teacher: '许彬', className: '三年级1班', taskCount: 330, score: 89 }
]

const schoolBarRef = ref(null)
const channelBarRef = ref(null)
const typePieRef = ref(null)
const sourceStackRef = ref(null)
const monthTrendRef = ref(null)
const yearCompareRef = ref(null)

let schoolBarChart = null
let channelBarChart = null
let typePieChart = null
let sourceStackChart = null
let monthTrendChart = null
let yearCompareChart = null

function fmtNum(value) {
  return Number(value || 0).toLocaleString('zh-CN')
}

function initCharts() {
  schoolBarChart = echarts.init(schoolBarRef.value)
  channelBarChart = echarts.init(channelBarRef.value)
  typePieChart = echarts.init(typePieRef.value)
  sourceStackChart = echarts.init(sourceStackRef.value)
  monthTrendChart = echarts.init(monthTrendRef.value)
  yearCompareChart = echarts.init(yearCompareRef.value)

  schoolBarChart.setOption({
    grid: { left: 40, right: 16, top: 24, bottom: 26 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['上海一小', '上海二小', '深圳总校', '杭州一小', '广州一小'] },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: [2312, 2146, 1920, 1780, 1650], barWidth: 34, itemStyle: { color: '#e7a678' } }]
  })

  channelBarChart.setOption({
    grid: { left: 90, right: 30, top: 24, bottom: 24 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: ['会员推荐', 'AI测评', '直播答疑', '家校会', '续费转化'] },
    series: [{ type: 'bar', data: [1650, 590, 2070, 1840, 640], itemStyle: { color: '#de9a6b' } }]
  })

  typePieChart.setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    series: [{
      type: 'pie',
      radius: ['48%', '72%'],
      center: ['50%', '46%'],
      data: [
        { name: '作业任务', value: 33.39 },
        { name: '考试任务', value: 29.68 },
        { name: '老师任务', value: 26.61 },
        { name: '复盘任务', value: 10.32 }
      ]
    }]
  })

  sourceStackChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { top: 0, right: 0 },
    grid: { left: 40, right: 20, top: 40, bottom: 24 },
    xAxis: { type: 'category', data: ['直播答疑', '家校展示', '会员推荐', '续费'] },
    yAxis: { type: 'value' },
    series: [
      { name: '线上', type: 'bar', stack: 'all', data: [1700, 1100, 900, 0], itemStyle: { color: '#69aee9' } },
      { name: '线下', type: 'bar', stack: 'all', data: [370, 740, 750, 640], itemStyle: { color: '#e2a37a' } }
    ]
  })

  monthTrendChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { top: 0, right: 0 },
    grid: { left: 40, right: 20, top: 38, bottom: 24 },
    xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'] },
    yAxis: { type: 'value' },
    series: [
      { name: '作业量', type: 'line', smooth: true, data: [280, 360, 600, 650, 760, 770, 930, 1000, 1180, 1200, 1280, 1400], areaStyle: {} },
      { name: '考试量', type: 'line', smooth: true, data: [120, 170, 320, 340, 390, 390, 470, 500, 600, 610, 650, 710], areaStyle: {} }
    ]
  })

  yearCompareChart.setOption({
    tooltip: { trigger: 'axis' },
    legend: { top: 0, right: 0 },
    grid: { left: 40, right: 20, top: 38, bottom: 24 },
    xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'] },
    yAxis: { type: 'value' },
    series: [
      { name: '上年任务', type: 'bar', data: [220, 300, 480, 420, 620, 720, 840, 900, 860, 1000, 1080, 1200], itemStyle: { color: '#77b4f0' } },
      { name: '本年任务', type: 'bar', data: [260, 340, 580, 640, 740, 770, 920, 990, 1200, 1220, 1300, 1380], itemStyle: { color: '#e4a479' } }
    ]
  })
}

function resizeCharts() {
  ;[schoolBarChart, channelBarChart, typePieChart, sourceStackChart, monthTrendChart, yearCompareChart].forEach((chart) => {
    if (chart) chart.resize()
  })
}

onMounted(() => {
  initCharts()
  window.addEventListener('resize', resizeCharts)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts)
  ;[schoolBarChart, channelBarChart, typePieChart, sourceStackChart, monthTrendChart, yearCompareChart].forEach((chart) => {
    if (chart) chart.dispose()
  })
})
</script>

<style scoped>
.edu-screen {
  position: relative;
  min-height: calc(100vh - 84px);
  padding: 16px;
  overflow: hidden;
  background: #f4f6fb;
}
.screen-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 18% 14%, rgba(254, 218, 205, 0.52), transparent 46%),
    radial-gradient(circle at 84% 12%, rgba(199, 224, 255, 0.48), transparent 46%),
    linear-gradient(180deg, #fdfcff 0%, #f4f6fb 100%);
}
.screen-content {
  position: relative;
  z-index: 1;
}
.screen-header {
  text-align: center;
  margin-bottom: 14px;
}
.screen-header h1 {
  margin: 0;
  font-size: 38px;
  font-weight: 700;
  color: #27262b;
  letter-spacing: 1px;
}
.screen-header p {
  margin: 6px 0 0;
  color: #6a7485;
}
.metric-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}
.metric-card {
  border-radius: 12px;
  padding: 18px 20px;
  color: #fff;
  min-height: 92px;
  box-shadow: 0 10px 22px rgba(65, 79, 117, 0.18);
  background-size: 220% 220%;
}
.metric-card span {
  font-size: 16px;
  opacity: 0.95;
}
.metric-card strong {
  display: block;
  margin-top: 10px;
  font-size: 42px;
  line-height: 1;
}
.metric-orange { background-image: linear-gradient(120deg, #f0a359, #eecf58); }
.metric-blue { background-image: linear-gradient(120deg, #4d77ee, #5ba8f2); }
.metric-cyan { background-image: linear-gradient(120deg, #42a6d6, #48d3cb); }
.metric-green { background-image: linear-gradient(120deg, #4cb9b4, #4fd186); }

.screen-grid {
  display: grid;
  grid-template-columns: 1.2fr 1.2fr 1fr;
  grid-template-rows: 248px 248px 248px;
  gap: 12px;
}
.panel {
  border-radius: 12px;
  border: 1px solid #e7ebf3;
  background: rgba(255, 255, 255, 0.82);
}
.panel-a { grid-column: 1; grid-row: 1; }
.panel-b { grid-column: 2; grid-row: 1; }
.panel-c { grid-column: 3; grid-row: 1; }
.panel-d { grid-column: 3; grid-row: 2; }
.panel-e { grid-column: 2; grid-row: 2 / 4; }
.panel-f { grid-column: 3; grid-row: 3; }
.panel-g { grid-column: 1; grid-row: 2 / 4; }
.chart-box {
  height: 180px;
}

:deep(.el-card__header) {
  padding: 12px 14px;
  font-size: 22px;
  font-weight: 700;
  color: #313846;
}
:deep(.el-card__body) {
  padding: 8px 10px 12px;
}

@media (max-width: 1400px) {
  .screen-grid {
    grid-template-columns: 1fr 1fr;
    grid-template-rows: auto;
  }
  .panel-a,
  .panel-b,
  .panel-c,
  .panel-d,
  .panel-e,
  .panel-f,
  .panel-g {
    grid-column: auto;
    grid-row: auto;
    width: auto;
    justify-self: stretch;
  }
}

@media (max-width: 900px) {
  .metric-row {
    grid-template-columns: 1fr 1fr;
  }
  .screen-grid {
    grid-template-columns: 1fr;
  }
  .screen-header h1 {
    font-size: 26px;
  }
  .metric-card strong {
    font-size: 32px;
  }
}
</style>
