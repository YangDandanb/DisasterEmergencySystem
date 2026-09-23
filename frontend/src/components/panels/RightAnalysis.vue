<!-- RightAnalysis.vue — M6 空间分析 -->
<script setup>
import { ref } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import { ElMessage } from 'element-plus'
import Heatmap from 'ol/layer/Heatmap'
import VectorSource from 'ol/source/Vector'

const mapStore = useMapStore()

// ====== 最近设施 ======
const nearestType = ref('hospital')
const nearestResults = ref([])
const nearestVisible = ref(false)
const nearestPick = ref(false)
let nearestHandler = null

function startNearest() {
  const map = mapStore.map; if (!map) return
  if (nearestPick.value) { map.un('click', nearestHandler); nearestPick.value = false; return }
  nearestPick.value = true
  nearestHandler = async (evt) => {
    nearestPick.value = false; map.un('click', nearestHandler)
    import('ol/proj').then(async ({ toLonLat }) => {
      const [lon, lat] = toLonLat(evt.coordinate, 'EPSG:3857')
      try {
        const res = await fetch(`/api/analysis/nearest?lon=${lon}&lat=${lat}&type=${nearestType.value}&limit=5`)
        nearestResults.value = await res.json()
        nearestVisible.value = true
      } catch { ElMessage.error('查询失败') }
    })
  }
  map.on('click', nearestHandler)
}

// ====== 热力图 ======
let heatmapLayer = null
const heatActive = ref(false)
function toggleHeatmap() {
  const map = mapStore.map; if (!map) return
  if (heatmapLayer) { map.removeLayer(heatmapLayer); heatmapLayer = null; heatActive.value = false; ElMessage.info('已关闭'); return }
  const src = window.__landslideSrc; if (!src) { ElMessage.warning('无滑坡数据'); return }
  const heatSrc = new VectorSource()
  src.getFeatures().forEach(f => { const c = f.clone(); c.set('weight', 1); heatSrc.addFeature(c) })
  heatmapLayer = new Heatmap({ source: heatSrc, blur: 20, radius: 15, weight: 'weight' })
  map.addLayer(heatmapLayer); heatActive.value = true; ElMessage.success('生成完成')
}

// ====== 缓冲区分析 ======
const bufRadius = ref(5000)
const bufResults = ref([])
const bufVisible = ref(false)
const picking = ref(false)
let pickHandler = null

function startBuffer() {
  const map = mapStore.map; if (!map) return
  if (picking.value) { map.un('click', pickHandler); picking.value = false; return }
  picking.value = true
  pickHandler = async (evt) => {
    picking.value = false; map.un('click', pickHandler)
    import('ol/proj').then(async ({ toLonLat }) => {
      const [lon, lat] = toLonLat(evt.coordinate, 'EPSG:3857')
      try {
        const res = await fetch(`/api/analysis/buffer?lon=${lon}&lat=${lat}&radius=${bufRadius.value}`)
        bufResults.value = await res.json()
        bufVisible.value = true
        ElMessage.success(`找到 ${bufResults.value.length} 个设施`)
      } catch { ElMessage.error('分析失败') }
    })
  }
  map.on('click', pickHandler)
}
</script>

<template>
  <div>
    <!-- 缓冲区分析 -->
    <p style="color:var(--accent);font-size:12px;margin-bottom:6px;">🔵 缓冲区分析</p>
    <div style="display:flex;gap:4px;margin-bottom:4px;">
      <span style="color:var(--text-secondary);font-size:11px;line-height:24px;">半径(m)</span>
      <el-input-number v-model="bufRadius" :min="500" :max="50000" :step="500" size="small" style="flex:1;" />
    </div>
    <el-button size="small" @click="startBuffer" :type="picking ? 'warning' : 'default'" style="width:100%;margin-bottom:6px;">
      {{ picking ? '地图上点击...' : '点击地图选中心点' }}
    </el-button>

    <!-- 缓冲区结果 -->
    <el-dialog v-model="bufVisible" title="缓冲区分析结果" width="400px">
      <div v-if="bufResults.length" style="max-height:50vh;overflow-y:auto;">
        <table style="width:100%;font-size:12px;color:#222;background:#f8f9fa;border-collapse:collapse;">
          <tr style="background:#e9ecef;text-align:left;"><th style="padding:5px 8px;">类型</th><th style="padding:5px 8px;">名称</th><th style="padding:5px 8px;">距离</th></tr>
          <tr v-for="(r,i) in bufResults" :key="i" style="border-top:1px solid #dee2e6;">
            <td style="padding:4px 8px;">{{ r.type }}</td>
            <td style="padding:4px 8px;">{{ r.name }}</td>
            <td style="padding:4px 8px;">{{ (r.distance/1000).toFixed(1) }} km</td>
          </tr>
        </table>
      </div>
      <div v-else style="text-align:center;padding:20px;color:#6c757d;">该范围内无设施</div>
    </el-dialog>

    <!-- 最近设施 -->
    <p style="color:var(--accent);font-size:12px;margin-top:10px;margin-bottom:6px;">🎯 最近设施</p>
    <el-select v-model="nearestType" size="small" style="width:100%;margin-bottom:4px;">
      <el-option label="医院" value="hospital" />
      <el-option label="消防站" value="fire_station" />
      <el-option label="避难所" value="shelter" />
    </el-select>
    <el-button size="small" @click="startNearest" :type="nearestPick ? 'warning' : 'default'" style="width:100%;margin-bottom:6px;">
      {{ nearestPick ? '地图上点击...' : '点击地图选参考点' }}
    </el-button>
    <el-dialog v-model="nearestVisible" title="最近设施" width="380px">
      <div v-if="nearestResults.length" style="max-height:45vh;overflow-y:auto;">
        <table style="width:100%;font-size:12px;color:#222;background:#f8f9fa;border-collapse:collapse;">
          <tr style="background:#e9ecef;text-align:left;"><th style="padding:5px 8px;">#</th><th style="padding:5px 8px;">名称</th><th style="padding:5px 8px;">距离</th></tr>
          <tr v-for="(r,i) in nearestResults" :key="i" style="border-top:1px solid #dee2e6;">
            <td style="padding:4px 8px;">{{ i+1 }}</td>
            <td style="padding:4px 8px;">{{ r.name }}</td>
            <td style="padding:4px 8px;">{{ (r.distance/1000).toFixed(1) }} km</td>
          </tr>
        </table>
      </div>
    </el-dialog>

    <!-- 热力图 -->
    <p style="color:var(--accent);font-size:12px;margin-top:10px;margin-bottom:6px;">🔥 热力图</p>
    <el-button :type="heatActive ? 'danger' : 'primary'" size="small" @click="toggleHeatmap" style="width:100%;">
      {{ heatActive ? '关闭热力图' : '生成滑坡热力图' }}
    </el-button>
  </div>
</template>
