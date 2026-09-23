<!-- TopBar.vue — 顶部栏：Logo + 菜单按钮 -->
<script setup>
import { useMapStore } from '@/stores/mapStore'
import { storeToRefs } from 'pinia'
const mapStore = useMapStore()
const { activeMenu } = storeToRefs(mapStore)
</script>

<template>
  <div class="top-bar">
    <div class="logo-row">
      <span class="logo-icon">🌍</span>
      <span class="logo-title">地质灾害应急救援辅助决策平台</span>
    </div>
    <div class="menu-row">
      <button class="menu-btn" :class="{ active: activeMenu === 'M1' }" @click="mapStore.setActiveMenu('M1')">图源</button>
      <button class="menu-btn" :class="{ active: activeMenu === 'M2' }" @click="mapStore.setActiveMenu('M2')">图层</button>
      <button class="menu-btn" :class="{ active: activeMenu === 'M3' }" @click="mapStore.setActiveMenu('M3')">查询</button>
      <span class="spacer">|</span>
      <button class="menu-btn" :class="{ active: activeMenu === 'M6' }" @click="mapStore.setActiveMenu('M6')">分析</button>
      <button class="menu-btn" :class="{ active: activeMenu === 'M4' }" @click="mapStore.setActiveMenu('M4')">工具</button>
      <button class="menu-btn" :class="{ active: activeMenu === 'M5' }" @click="mapStore.setActiveMenu('M5')">关于</button>
    </div>
  </div>
</template>

<style scoped>
.top-bar { position: absolute; top: 0; left: 0; right: 0; z-index: 20; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 8px 24px; background: transparent; pointer-events: none; gap: 6px; }
.top-bar > * { pointer-events: auto; }
.logo-row { display: flex; align-items: center; gap: 10px; }
.logo-icon { font-size: 26px; }
.logo-title { font-size: 18px; font-weight: bold; letter-spacing: 3px; background: linear-gradient(90deg, var(--accent), #60e8ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.menu-row { display: flex; align-items: center; gap: 15px; }
.menu-btn { padding: 6px 18px; color: rgba(200, 220, 240, 0.75); font-size: 13px; cursor: pointer; border: 1px solid rgba(255, 255, 255, 0.06); background: var(--bg-panel); border-radius: 6px; transition: all .2s; letter-spacing: 1px; }
.menu-btn:hover { color: #fff; background: rgba(0, 180, 240, 0.2); border-color: rgba(0, 200, 255, 0.3); }
.menu-btn.active { color: #00e5ff; background: rgba(0, 180, 240, 0.18); border-color: rgba(0, 200, 255, 0.35); box-shadow: 0 0 12px rgba(0, 180, 240, 0.2); }
.spacer { color: rgba(255, 255, 255, 0.08); font-size: 18px; }
</style>
