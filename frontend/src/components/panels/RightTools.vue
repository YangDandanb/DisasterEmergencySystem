<!-- RightTools.vue — M4 工具箱 -->
<script setup>
import { ref, markRaw } from 'vue'
import { useMapStore } from '@/stores/mapStore'
import VectorLayer from 'ol/layer/Vector'
import VectorSource from 'ol/source/Vector'
import Draw from 'ol/interaction/Draw'
import { unByKey } from 'ol/Observable'
import Overlay from 'ol/Overlay'
import { getArea, getLength } from 'ol/sphere'
import Polygon from 'ol/geom/Polygon'
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style'
import { ElMessage } from 'element-plus'

const mapStore = useMapStore()

// ====== 测量 ======
const source = new VectorSource()
const vector = new VectorLayer({ source, style: { 'fill-color': 'rgba(255,255,255,0.2)', 'stroke-color': '#ffcc33', 'stroke-width': 2, 'circle-radius': 7, 'circle-fill-color': '#ffcc33' } })
const drawStyle = new Style({
  fill: new Fill({ color: 'rgba(255,255,255,0.2)' }),
  stroke: new Stroke({ color: 'rgba(0,0,0,0.5)', lineDash: [10, 10], width: 2 }),
  image: new CircleStyle({ radius: 5, stroke: new Stroke({ color: 'rgba(0,0,0,0.7)' }), fill: new Fill({ color: 'rgba(255,255,255,0.2)' }) }),
})

let sketch = null, draw = null, listener = null, added = false
let measureElement = null, measureOverlay = null

function ensureMeasureOverlay() {
  if (!measureOverlay) {
    measureElement = document.createElement('div')
    measureElement.className = 'ol-tooltip ol-tooltip-measure'
    measureOverlay = new Overlay({ element: measureElement, offset: [0, -15], positioning: 'bottom-center', stopEvent: false, insertFirst: false })
    mapStore.map.addOverlay(measureOverlay)
  }
}

function formatLen(line) { const l = getLength(line); return l > 100 ? (l/1000).toFixed(2)+' km' : l.toFixed(1)+' m' }
function formatArea(poly) { const a = getArea(poly); return a > 10000 ? (a/1e6).toFixed(2)+' km²' : a.toFixed(1)+' m²' }

function startMeasure(type) {
  stopDraw()
  if (draw) mapStore.map.removeInteraction(draw)
  if (!added) { mapStore.map.addLayer(vector); added = true }
  ensureMeasureOverlay()
  const geomType = type === 'area' ? 'Polygon' : 'LineString'
  draw = new Draw({ source, type: geomType, style: function(feature) { const gt = feature.getGeometry().getType(); if (gt === geomType || gt === 'Point') return drawStyle } })
  mapStore.map.addInteraction(draw)
  draw.on('drawstart', function(evt) { sketch = evt.feature; listener = sketch.getGeometry().on('change', function(evt) { const geom = evt.target; measureElement.innerHTML = geom instanceof Polygon ? formatArea(geom) : formatLen(geom); measureElement.className = 'ol-tooltip ol-tooltip-measure'; const coord = geom instanceof Polygon ? geom.getInteriorPoint().getCoordinates() : geom.getLastCoordinate(); measureOverlay.setPosition(coord) }) })
  draw.on('drawend', function() { measureElement.className = 'ol-tooltip ol-tooltip-static'; measureOverlay.setOffset([0, -7]); sketch = null; if (listener) { unByKey(listener); listener = null } })
}

function clearMeasure() {
  source.clear()
  if (measureOverlay) { measureOverlay.setPosition(undefined); measureElement.className = 'ol-tooltip ol-tooltip-measure'; measureElement.innerHTML = ''; measureOverlay.setOffset([0, -15]) }
}

// ====== 绘制（连续模式 + 双层弹窗） ======
const drawSrc = new VectorSource()
const drawVecStyle = new Style({
  fill: new Fill({ color: 'rgba(0,212,255,0.12)' }),
  stroke: new Stroke({ color: '#00d4ff', width: 2 }),
  image: new CircleStyle({ radius: 6, fill: new Fill({ color: '#00d4ff' }), stroke: new Stroke({ color: '#fff', width: 1.5 }) }),
})
const drawVec = new VectorLayer({ source: drawSrc, style: drawVecStyle })
let drawAdded = false, autoDraw = false, drawType = ''
const activeTool = ref('')

const stopVisible = ref(false)
const saveVisible = ref(false)
const saveName = ref('')
const addToPanel = ref(true)

function startDraw(type) {
  clearMeasure()
  stopDraw()
  if (draw) mapStore.map.removeInteraction(draw)
  if (!drawAdded) { mapStore.map.addLayer(drawVec); drawAdded = true }
  activeTool.value = 'draw-' + type
  drawType = type; autoDraw = true
  _newDraw()
}
function _newDraw() {
  if (!autoDraw) return
  draw = new Draw({ source: drawSrc, type: drawType, style: drawVecStyle })
  mapStore.map.addInteraction(draw)
  draw.on('drawend', () => { mapStore.map.removeInteraction(draw); draw = null; if (autoDraw) _newDraw() })
}
function stopDraw() { autoDraw = false; if (draw) { mapStore.map.removeInteraction(draw); draw = null } }
function openStopDialog() {
  // 先不停止，只弹窗确认
  if (drawSrc.getFeatures().length === 0) return
  stopVisible.value = true
}
function onContinue() {
  stopVisible.value = false
  // 重新激活绘制
  if (draw) mapStore.map.removeInteraction(draw)
  autoDraw = true; _newDraw()
}
function confirmStop() {
  stopDraw(); activeTool.value = ''
  stopVisible.value = false
  saveName.value = ''; addToPanel.value = true; saveVisible.value = true
}
function saveLayer() {
  if (!saveName.value.trim()) saveName.value = '未命名'
  const newSrc = new VectorSource()
  drawSrc.getFeatures().forEach(f => newSrc.addFeature(f))
  drawSrc.clear()
  const layer = new VectorLayer({ source: newSrc, style: drawVecStyle })
  if (addToPanel.value) mapStore.addUserLayer(saveName.value.trim(), markRaw(layer))
  mapStore.map.addLayer(layer)
  saveVisible.value = false; ElMessage.success('已保存')
}
function discardLayer() { drawSrc.clear(); saveVisible.value = false }

// ====== 新增滑坡点 ======
const pickingCoord = ref(false)
const newLon = ref(null), newLat = ref(null)
const newCity = ref(''), newTrigger = ref(''), newLevel = ref(''), newDeaths = ref(0)
let pickHandler = null

function startPickCoord() {
  if (pickingCoord.value) { // 取消
    if (pickHandler) { mapStore.map.un('click', pickHandler); pickHandler = null }
    pickingCoord.value = false; return
  }
  pickingCoord.value = true
  pickHandler = (evt) => {
    import('ol/proj').then(({ toLonLat }) => {
      const [lon, lat] = toLonLat(evt.coordinate, 'EPSG:3857')
      newLon.value = lon; newLat.value = lat
      pickingCoord.value = false
      mapStore.map.un('click', pickHandler)
    })
  }
  mapStore.map.on('click', pickHandler)
}

async function submitNewLandslide() {
  if (!newLon.value) return
  try {
    const res = await fetch('/api/landslides', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ lon: newLon.value, lat: newLat.value, city: newCity.value, trigger: newTrigger.value, level: newLevel.value, deaths: newDeaths.value }),
    })
    if (res.ok) {
      const data = await res.json()
      // 实时添加到地图
      import('ol/proj').then(({ fromLonLat }) => {
        import('ol/Feature').then(({ default: Feature }) => {
          import('ol/geom/Point').then(({ default: Point }) => {
            const f = new Feature({ geometry: new Point(fromLonLat([data.lon, data.lat], 'EPSG:3857')) })
            f.setProperties(data)
            if (window.__landslideSrc) window.__landslideSrc.addFeature(f)
          })
        })
      })
      ElMessage.success('滑坡点已添加')
      newLon.value = null; newCity.value = ''; newTrigger.value = ''; newLevel.value = ''; newDeaths.value = 0
    }
    else { ElMessage.error('添加失败') }
  } catch (e) { ElMessage.error('网络错误') }
}
</script>

<template>
  <div>
    <!-- 测量 -->
    <p style="color:var(--accent);font-size:12px;margin-bottom:6px;">📐 测量</p>
    <div class="tool-grid">
      <div class="tool-card" @click="startMeasure('distance')"><span class="t-icon">↕</span><span class="t-label">测距</span></div>
      <div class="tool-card" @click="startMeasure('area')"><span class="t-icon">◫</span><span class="t-label">测面积</span></div>
    </div>
    <el-button size="small" @click="clearMeasure" style="width:100%;margin-top:6px;">清除测量</el-button>

    <!-- 绘制 -->
    <!-- 新增滑坡 -->
    <p style="color:var(--accent);font-size:12px;margin:10px 0 6px;">📍 新增滑坡点</p>
    <div style="display:flex;gap:4px;margin-bottom:4px;">
      <el-input v-model.number="newLon" size="small" placeholder="经度" style="flex:1;" />
      <el-input v-model.number="newLat" size="small" placeholder="纬度" style="flex:1;" />
    </div>
    <el-button size="small" @click="startPickCoord" :type="pickingCoord ? 'warning' : 'default'" style="width:100%;margin-bottom:4px;">
      {{ pickingCoord ? '地图上点击...' : '或从地图上点击选坐标' }}
    </el-button>
    <el-input v-model="newCity" size="small" placeholder="城市" style="margin-bottom:4px;" />
    <el-input v-model="newTrigger" size="small" placeholder="诱因" style="margin-bottom:4px;" />
    <div style="display:flex;gap:4px;margin-bottom:4px;">
      <el-select v-model="newLevel" size="small" placeholder="等级" style="flex:1;">
        <el-option v-for="l in ['Ⅰ','Ⅱ','Ⅲ','Ⅳ']" :key="l" :label="l+'级'" :value="l" />
      </el-select>
      <el-input-number v-model="newDeaths" size="small" :min="0" placeholder="死亡" style="flex:1;" />
    </div>
    <el-button size="small" type="primary" @click="submitNewLandslide" :disabled="!newLon" style="width:100%;">② 提交新增</el-button>

    <p style="color:var(--accent);font-size:12px;margin:10px 0 6px;">✏️ 绘制</p>
    <div class="tool-grid">
      <div class="tool-card" :class="{ active: activeTool === 'draw-Point' }" @click="startDraw('Point')"><span class="t-icon">📍</span><span class="t-label">绘点</span></div>
      <div class="tool-card" :class="{ active: activeTool === 'draw-LineString' }" @click="startDraw('LineString')"><span class="t-icon">📏</span><span class="t-label">绘线</span></div>
      <div class="tool-card" :class="{ active: activeTool === 'draw-Polygon' }" @click="startDraw('Polygon')"><span class="t-icon">⬡</span><span class="t-label">绘面</span></div>
      <div class="tool-card" :class="{ active: activeTool === 'draw-Circle' }" @click="startDraw('Circle')"><span class="t-icon">⭕</span><span class="t-label">绘圆</span></div>
    </div>
    <el-button v-if="activeTool.startsWith('draw-')" size="small" type="danger" @click="openStopDialog" style="width:100%;margin-top:6px;">停止绘制</el-button>

    <!-- 第一层弹窗 -->
    <el-dialog v-model="stopVisible" title="停止绘制" width="280px">
      <p style="color:var(--text-secondary);font-size:13px;">已绘制 {{ drawSrc.getFeatures().length }} 个要素，确认停止？</p>
      <template #footer>
        <el-button size="small" @click="onContinue">继续</el-button>
        <el-button size="small" type="primary" @click="confirmStop">确认停止</el-button>
      </template>
    </el-dialog>

    <!-- 第二层弹窗 -->
    <el-dialog v-model="saveVisible" title="保存图层" width="300px">
      <el-input v-model="saveName" placeholder="输入图层名称..." size="small" style="margin-bottom:8px;" />
      <el-checkbox v-model="addToPanel" size="small" style="color:var(--text-secondary);">加入「图层管理」面板</el-checkbox>
      <template #footer>
        <el-button size="small" @click="discardLayer">丢弃</el-button>
        <el-button size="small" type="primary" @click="saveLayer">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.tool-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.tool-card { background: var(--bg-panel); border: 1px solid var(--border); border-radius: 5px; padding: 14px 8px; text-align: center; cursor: pointer; transition: all .2s; display: flex; flex-direction: column; align-items: center; gap: 4px; }
.tool-card:hover { border-color: var(--accent); }
.tool-card.active { border-color: var(--accent); box-shadow: 0 0 8px rgba(0,200,255,0.2); }
.t-icon { font-size: 22px; }
.t-label { font-size: 11px; color: var(--text-secondary); }
</style>
