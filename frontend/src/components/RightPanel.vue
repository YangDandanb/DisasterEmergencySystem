<!-- RightPanel.vue — 右侧面板：v-show 切换 6 个子面板 -->
<script setup>
import { useMapStore } from '@/stores/mapStore'
import { storeToRefs } from 'pinia'
import RightBaseMap from './panels/RightBaseMap.vue'
import RightLayers from './panels/RightLayers.vue'
import RightQuery from './panels/RightQuery.vue'
import RightTools from './panels/RightTools.vue'
import RightAbout from './panels/RightAbout.vue'
import RightAnalysis from './panels/RightAnalysis.vue'

const mapStore = useMapStore()
const { activeMenu } = storeToRefs(mapStore)
</script>

<template>
  <div class="panel-right" v-show="activeMenu">
    <div class="card" style="flex:1;display:flex;flex-direction:column;">
      <div class="card-header">
        <span class="hd-left">{{ { M1: '图源切换', M2: '图层管理', M3: '灾害查询', M4: '工具箱', M5: '关于平台', M6: '空间分析' }[activeMenu] }}</span>
        <button @click="mapStore.closePanel()" class="close-btn">✕</button>
      </div>
      <div class="card-body">
        <RightBaseMap v-show="activeMenu === 'M1'" />
        <RightLayers v-show="activeMenu === 'M2'" />
        <RightQuery v-show="activeMenu === 'M3'" />
        <RightTools v-show="activeMenu === 'M4'" />
        <RightAbout v-show="activeMenu === 'M5'" />
        <RightAnalysis v-show="activeMenu === 'M6'" />
        <div v-if="!['M1','M2','M3','M4','M5','M6'].includes(activeMenu)" class="empty">点击菜单选择功能</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.panel-right { position: absolute; top: 0; right: 0; bottom: 0; width: 19%; min-width: 260px; max-width: 330px; z-index: 15; overflow-y: auto; padding: 0; background: var(--bg-panel); }
.card { background: var(--bg-panel); border: 1px solid var(--border); }
.card-header { display: flex; align-items: center; justify-content: space-between; padding: 8px 12px; font-size: 13px; font-weight: 600; color: var(--accent); border-bottom: 1px solid var(--border); }
.card-header .hd-left { display: flex; align-items: center; gap: 6px; }
.card-header .hd-left::before { content: ''; width: 3px; height: 13px; background: var(--accent); border-radius: 2px; box-shadow: 0 0 6px var(--accent); }
.card-body { padding: 8px 12px; flex: 1; overflow-y: auto; }
.close-btn { background: none; border: none; color: var(--text-secondary); cursor: pointer; font-size: 15px; }
.empty { display: flex; align-items: center; justify-content: center; height: 200px; color: var(--text-secondary); }
</style>
