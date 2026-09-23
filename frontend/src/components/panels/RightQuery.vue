<!-- RightQuery.vue — M3 灾害查询 -->
<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useMapStore } from '@/stores/mapStore'
import DragBox from 'ol/interaction/DragBox'
import { platformModifierKeyOnly } from 'ol/events/condition'

const mapStore = useMapStore()

// ====== 查询条件 ======
const levelFilter = ref('')
const cityFilter = ref('')
const triggerFilter = ref('')
const yearStart = ref('')
const yearEnd = ref('')
const searchDone = ref(false)
const results = ref([])

// ====== 搜索（调用 API） ======
async function doSearch() {
  const params = new URLSearchParams()
  if (levelFilter.value) params.set('level', levelFilter.value)
  if (cityFilter.value) params.set('city', cityFilter.value)
  if (triggerFilter.value) params.set('trigger', triggerFilter.value)
  if (yearStart.value) params.set('year_from', yearStart.value)
  if (yearEnd.value) params.set('year_to', yearEnd.value)
  params.set('limit', '50')
  try {
    const res = await fetch('/api/landslides?' + params.toString())
    results.value = await res.json()
    searchDone.value = true
  } catch (e) { console.error('查询失败', e) }
}

// ====== 点击定位 ======
function locate(item) {
  const map = mapStore.map
  if (!map) return
  import('ol/proj').then(({ fromLonLat }) => {
    map.getView().animate({ center: fromLonLat([item.lon, item.lat], 'EPSG:3857'), zoom: 13, duration: 600 })
  })
}

// ====== 下拉选项（从 API 获取） ======
const cities = ref([])
const triggers = ref([])
fetch('/api/statistics/by-city').then(r => r.json()).then(d => { cities.value = d.map(x => x.name) })
fetch('/api/statistics/by-trigger').then(r => r.json()).then(d => { triggers.value = d.map(x => x.name) })

// ====== 框选查询 ======
const boxActive = ref(false)
const boxResults = ref([])
const boxVisible = ref(false)
let dragBox = null

function toggleBoxSelect() {
  const map = mapStore.map; if (!map) return
  if (boxActive.value) {
    if (dragBox) { map.removeInteraction(dragBox); dragBox = null }
    boxActive.value = false; return
  }
  boxActive.value = true
  dragBox = new DragBox({})
  map.addInteraction(dragBox)
  dragBox.on('boxend', () => {
    const extent = dragBox.getGeometry().getExtent()
    const items = []
    // 查滑坡
    const lsSrc = window.__landslideSrc
    if (lsSrc) lsSrc.forEachFeatureInExtent(extent, f => {
      items.push({ type: '滑坡', name: f.get('city') + (f.get('county') || ''), deaths: f.get('deaths') || 0, level: f.get('level') || '', lon: 0, lat: 0, id: f.get('id') })
    })
    // 查设施
    map.getLayers().forEach(l => {
      const s = l.getSource?.()
      if (!s || !s.getSource) return // 跳过非 cluster 源
      const inner = s.getSource()
      const title = l.get('title') || ''
      if (!title.includes('医院') && !title.includes('消防') && !title.includes('避难')) return
      let typeName = title.includes('医院') ? '医院' : title.includes('消防') ? '消防站' : '避难所'
      inner.forEachFeatureInExtent(extent, f => {
        const props = f.getProperties()
        items.push({
          type: typeName,
          name: props.name || props.Nom || props.名称 || '-',
          deaths: 0, level: '',
          capacity: props.capacity || props.capacidad || 0,
          address: props.address || props.addr_street || '',
          lon: 0, lat: 0, id: 0,
        })
      })
    })
    boxResults.value = items
    boxVisible.value = true
    map.removeInteraction(dragBox); dragBox = null; boxActive.value = false
  })
  dragBox.on('boxcancel', () => {
    map.removeInteraction(dragBox); dragBox = null; boxActive.value = false
  })
}

async function deleteLandslide(item) {
  try {
    const res = await fetch('/api/landslides/' + item.id, { method: 'DELETE' })
    if (res.ok) {
      results.value = results.value.filter(r => r.id !== item.id)
      // 同步从地图上移除
      const src = window.__landslideSrc
      if (src) {
        const f = src.getFeatures().find(f => f.get('id') === item.id)
        if (f) src.removeFeature(f)
      }
      ElMessage.success('已删除')
    }
    else ElMessage.error('删除失败')
  } catch (e) { ElMessage.error('网络错误') }
}
</script>

<template>
  <div>
    <!-- 查询表单 -->
    <el-select v-model="levelFilter" size="small" placeholder="灾害等级" clearable style="width:100%;margin-bottom:6px;">
      <el-option v-for="l in ['Ⅰ','Ⅱ','Ⅲ','Ⅳ']" :key="l" :label="l + '级'" :value="l" />
    </el-select>
    <el-select v-model="cityFilter" size="small" placeholder="城市" clearable filterable style="width:100%;margin-bottom:6px;">
      <el-option v-for="c in cities" :key="c" :label="c" :value="c" />
    </el-select>
    <el-select v-model="triggerFilter" size="small" placeholder="诱因" clearable style="width:100%;margin-bottom:6px;">
      <el-option v-for="t in triggers" :key="t" :label="t" :value="t" />
    </el-select>
    <div style="display:flex;gap:4px;margin-bottom:6px;">
      <el-input v-model="yearStart" size="small" placeholder="起始年" style="flex:1;" />
      <el-input v-model="yearEnd" size="small" placeholder="结束年" style="flex:1;" />
    </div>
    <el-button size="small" type="primary" @click="doSearch" style="width:100%;">查询</el-button>
    <div class="box-btn" :class="{ active: boxActive }" @click="toggleBoxSelect" style="margin-top:4px;">
      <span class="box-icon">⬛</span>
      <span>{{ boxActive ? '拖拽地图框选...' : '框选查询' }}</span>
    </div>

    <!-- 结果列表 -->
    <div v-if="searchDone" style="margin-top:8px;font-size:11px;color:var(--text-secondary);">
      共 {{ results.length }} 条结果
    </div>
    <div v-if="results.length" style="margin-top:4px;max-height:50vh;overflow-y:auto;">
      <div v-for="r in results" :key="r.id" class="result-row" @click="locate(r)">
        <span class="lv-tag" :style="{ background: { 'Ⅰ':'#FF0000','Ⅱ':'#FF6600','Ⅲ':'#FFCC00','Ⅳ':'#3399CC' }[r.level] || '#999' }">{{ r.level || '?' }}</span>
        <span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px;">{{ r.city }}{{ r.county ? '·' + r.county : '' }}</span>
        <span style="color:var(--text-secondary);font-size:10px;">{{ r.year }}</span>
      <span @click.stop="deleteLandslide(r)" style="cursor:pointer;color:var(--danger);font-size:12px;" title="删除">🗑</span>
      </div>
    </div>
    <div v-if="searchDone && results.length === 0" style="color:var(--text-secondary);font-size:12px;text-align:center;padding:20px;">无匹配结果</div>

    <!-- 框选结果弹窗 -->
    <el-dialog v-model="boxVisible" title="框选查询结果" width="480px" :z-index="2000">
      <div style="max-height:55vh;overflow-y:auto;">
        <table v-if="boxResults.length" style="width:100%;border-collapse:collapse;font-size:12px;color:#222;background:#f8f9fa;border-radius:4px;">
          <thead>
            <tr style="background:#e9ecef;text-align:left;">
              <th style="padding:6px 8px;">类型</th>
              <th style="padding:6px 8px;">名称</th>
              <th style="padding:6px 8px;">等级</th>
              <th style="padding:6px 8px;">详情</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r,i) in boxResults" :key="i" style="border-top:1px solid #dee2e6;">
              <td style="padding:5px 8px;">{{ r.type }}</td>
              <td style="padding:5px 8px;">{{ r.name }}</td>
              <td style="padding:5px 8px;">
                <span v-if="r.level" style="display:inline-block;width:22px;height:18px;line-height:18px;text-align:center;color:#fff;font-size:10px;font-weight:bold;border-radius:3px;" :style="{ background: { 'Ⅰ':'#FF0000','Ⅱ':'#FF6600','Ⅲ':'#FFCC00','Ⅳ':'#3399CC' }[r.level] || '#999' }">{{ r.level }}</span>
              </td>
              <td style="padding:5px 8px;">{{ r.deaths ? '死亡'+r.deaths : r.capacity ? '容纳'+r.capacity : (r.address || '-') }}</td>
            </tr>
          </tbody>
        </table>
        <div v-else style="text-align:center;padding:20px;color:#6c757d;">该区域无数据</div>
      </div>
    </el-dialog>
  </div>
</template>

<style scoped>
.result-row { display:flex; align-items:center; gap:8px; padding:6px 8px; border-bottom:1px solid var(--border); cursor:pointer; transition:background .15s; }
.result-row:hover { background:rgba(0,212,255,0.06); }
.lv-tag { display:inline-block; width:22px; height:18px; line-height:18px; text-align:center; color:#fff; font-size:10px; font-weight:bold; border-radius:3px; flex-shrink:0; }
.box-btn { display:flex; align-items:center; justify-content:center; gap:6px; padding:6px 0; border-radius:4px; cursor:pointer; font-size:12px; color:var(--text-secondary); background:var(--bg-panel); border:1px solid var(--border); transition:all .2s; }
.box-btn:hover { color:var(--accent); border-color:var(--accent); }
.box-btn.active { color:var(--accent); border-color:var(--accent); background:rgba(0,212,255,0.08); }
.box-icon { font-size:15px; }
</style>
