<!-- LeftPanel.vue — 左侧统计分析面板（可滚动 + 4张交互图表） -->
<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import * as echarts from 'echarts'
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style'

const mapStore = useMapStore()
// 面板宽度拖拽
let dragging = false, startX = 0, startW = 0
function onDragStart(e) { dragging = true; startX = e.clientX; startW = leftPanel.value?.offsetWidth || 330; document.addEventListener('mousemove', onDrag); document.addEventListener('mouseup', onDragEnd) }
function onDrag(e) { if (dragging) leftWidth.value = Math.max(200, Math.min(500, startW + e.clientX - startX)) }
function onDragEnd() { dragging = false; document.removeEventListener('mousemove', onDrag); document.removeEventListener('mouseup', onDragEnd) }

// 原始数据
let rawData = []

// ====== 图表实例 ======
let charts = []
const containerRef = ref(null)

function initCharts() {
  if (!containerRef.value) return
  // 4个图表的容器
  const ids = ['chart1', 'chart2', 'chart3', 'chart4']
  ids.forEach((id, i) => {
    const el = document.getElementById(id)
    if (!el) return
    const chart = echarts.init(el)
    charts[i] = chart
    // resize
    window.addEventListener('resize', () => chart.resize())
  })
  renderAll()
}

function renderAll() {
  if (charts.length < 4 || !statsData) return
  renderCityChart()
  renderTriggerChart()
  renderLevelChart()
  renderYearChart()
}

// ====== 数据统计 ======
function countBy(arr, key) {
  const map = {}
  arr.forEach(item => {
    let v = item[key]
    if (!v || v === 'NA' || v === '未知') v = '未知'
    map[v] = (map[v] || 0) + 1
  })
  return Object.entries(map).sort((a, b) => b[1] - a[1])
}

// ====== 地图联动：点击图表 → 高亮匹配的滑坡点 ======
function highlightOnMap(filterKey, filterVal) {
  // 清除之前的筛选
  if (window.__highlightClear) window.__highlightClear()

  const src = window.__landslideSrc
  if (!src) return

  const redStyle = new Style({ image: new CircleStyle({ radius: 9, fill: new Fill({ color: '#FF0000' }), stroke: new Stroke({ color: '#fff', width: 2.5 }) }) })
  const dimStyle = new Style({ image: new CircleStyle({ radius: 4, fill: new Fill({ color: '#333' }), stroke: new Stroke({ color: '#555', width: 0.5 }) }) })
  const normalStyle = new Style({ image: new CircleStyle({ radius: 7, fill: new Fill({ color: '#3399CC' }), stroke: new Stroke({ color: '#fff', width: 1.5 }) }) })

  src.forEachFeature(f => {
    let rawVal = f.get(filterKey) || '未知'
    if (filterKey === 'level') rawVal = rawVal.charAt(0)
    const match = filterVal === 'all' || rawVal === filterVal || (filterKey === 'level' && rawVal === filterVal.charAt(0))
    f.setStyle(match ? redStyle : dimStyle)
  })

  window.__highlightClear = () => { src.forEachFeature(f => f.setStyle(normalStyle)) }

  // 3秒后自动恢复
  clearTimeout(window.__highlightTimer)
  window.__highlightTimer = setTimeout(() => {
    if (window.__highlightClear) { window.__highlightClear(); window.__highlightClear = null }
  }, 4000)
}

// ====== 图表1: 市州横向柱状图（Top 8） ======
function renderCityChart() {
  const data = (statsData?.city || []).slice(0, 8)
  const names = data.map(d => d.name)
  const values = data.map(d => d.value)
  charts[0].setOption({
    tooltip: { trigger: 'axis', formatter: '{b}: {c} 个' },
    grid: { left: 70, right: 40, top: 5, bottom: 5 },
    xAxis: { type: 'value', axisLabel: { color: '#8899cc', fontSize: 9 }, splitLine: { lineStyle: { color: 'rgba(0,212,255,0.08)' } } },
    yAxis: { type: 'category', data: names, axisLabel: { color: '#c0d0e8', fontSize: 10 }, inverse: true, axisLine: { show: false }, axisTick: { show: false } },
    series: [{
      type: 'bar', data: values,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [{ offset: 0, color: '#1a80ff' }, { offset: 1, color: '#00d4ff' }]),
        borderRadius: [0, 4, 4, 0],
      },
      barWidth: 14,
      label: { show: true, position: 'right', color: '#00d4ff', fontSize: 10, formatter: '{c}' },
    }],
  })
  charts[0].off('click')
  charts[0].on('click', (p) => highlightOnMap('city', p.name))
}

// ====== 图表2: 滑坡诱因环形图 ======
function renderTriggerChart() {
  const data = statsData?.trigger || []
  charts[1].setOption({
    tooltip: { trigger: 'item' },
    legend: { bottom: 0, textStyle: { color: '#8899cc', fontSize: 10 } },
    series: [{
      type: 'pie', radius: ['50%', '75%'], center: ['50%', '45%'], label: { color: '#8899cc', fontSize: 10 },
      data: data.map((d, i) => ({ name: d.name, value: d.value, itemStyle: { color: ['#ff6b6b', '#ffaa33', '#ffd93d', '#00d4ff', '#00ff88'][i % 5] } })),
    }],
  })
  charts[1].off('click')
  charts[1].on('click', (p) => highlightOnMap('trigger', p.name))
}

// ====== 图表3: 灾害等级柱状图 ======
function renderLevelChart() {
  const data = statsData?.level || []
  const colors = ['#ff6b6b', '#ffaa33', '#ffd93d', '#00d4ff', '#8899cc']
  charts[2].setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 80, right: 20, top: 5, bottom: 5 },
    xAxis: { type: 'category', data: data.map(d => d.name), axisLabel: { color: '#8899cc', fontSize: 9 } },
    yAxis: { type: 'value', axisLabel: { color: '#8899cc', fontSize: 9 } },
    series: [{ type: 'bar', data: data.map((d, i) => ({ value: d.value, itemStyle: { color: colors[i % colors.length] } })), barWidth: '40%' }],
  })
  charts[2].off('click')
  charts[2].on('click', (p) => highlightOnMap('level', p.name))
}

// ====== 图表4: 月度滑坡趋势 ======
function renderYearChart() {
  const months = statsData?.month || Array(12).fill(0)
  const labels = ['1月','2月','3月','4月','5月','6月','7月','8月','9月','10月','11月','12月']
  charts[3].setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 20, top: 5, bottom: 5 },
    xAxis: { type: 'category', data: labels, axisLabel: { color: '#8899cc', fontSize: 9 } },
    yAxis: { type: 'value', axisLabel: { color: '#8899cc', fontSize: 9 } },
    series: [{
      type: 'line', data: months, smooth: true,
      lineStyle: { color: '#00d4ff', width: 2 },
      itemStyle: { color: '#00d4ff' },
      areaStyle: { color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: 'rgba(0,212,255,0.3)' }, { offset: 1, color: 'rgba(0,212,255,0.02)' }]) },
      markLine: { silent: true, data: [{ type: 'average', name: '均值', label: { color: '#ffaa33', fontSize: 9 } }], lineStyle: { color: '#ffaa33', type: 'dashed' } },
    }],
  })
}

// ====== API 数据缓存 ======
let statsData = null

// ====== 加载数据（从统计 API） ======
onMounted(async () => {
  try {
    const [city, trigger, level, month] = await Promise.all([
      fetch('/api/statistics/by-city').then(r => r.json()),
      fetch('/api/statistics/by-trigger').then(r => r.json()),
      fetch('/api/statistics/by-level').then(r => r.json()),
      fetch('/api/statistics/by-month').then(r => r.json()),
    ])
    statsData = { city, trigger, level, month }
    await nextTick(); initCharts()
  } catch (e) { console.error('统计API失败', e) }
})
</script>

<template>
  <div class="panel-left" ref="containerRef">
    <div class="chart-card">
      <div class="chart-header">📊 各市州滑坡数量</div>
      <div id="chart1" class="chart-box"></div>
    </div>
    <div class="chart-card">
      <div class="chart-header">🌧️ 滑坡诱因统计</div>
      <div id="chart2" class="chart-box"></div>
    </div>
    <div class="chart-card">
      <div class="chart-header">⚠️ 灾害等级统计</div>
      <div id="chart3" class="chart-box"></div>
    </div>
    <div class="chart-card">
      <div class="chart-header">📈 月度滑坡趋势</div>
      <div id="chart4" class="chart-box"></div>
    </div>
  </div>
</template>

<style scoped>
.panel-left { position: absolute; top: 0; left: 0; bottom: 0; width: 19%; min-width: 260px; max-width: 330px; z-index: 15; overflow-y: auto; padding: 8px; background: var(--bg-panel); display: flex; flex-direction: column; gap: 8px; }
.chart-card { background: var(--bg-panel); border: 1px solid var(--border); border-radius: 5px; overflow: hidden; min-height: 220px; display: flex; flex-direction: column; }
.chart-header { padding: 8px 12px; font-size: 13px; font-weight: 600; color: var(--accent); border-bottom: 1px solid var(--border); display: flex; align-items: center; gap: 6px; }
.chart-header::before { content: ''; width: 3px; height: 13px; background: var(--accent); border-radius: 2px; box-shadow: 0 0 6px var(--accent); }
.chart-box { flex: 1; min-height: 180px; }
</style>
