<!-- RightAbout.vue — M5 关于平台 -->
<template>
  <div style="color:var(--text-secondary);font-size:13px;line-height:2;">
    <p><b style="color:var(--accent);">平台名称</b><br/>
      地质灾害应急救援辅助决策WebGIS平台</p>
    <p style="margin-top:8px;"><b style="color:var(--accent);">研究范围</b><br/>四川省</p>
    <p style="margin-top:8px;"><b style="color:var(--accent);">技术栈</b><br/>
      前端：Vue3 + OpenLayers + Cesium + Element Plus + ECharts + Pinia<br/>
      后端：FastAPI + PostgreSQL + PostGIS<br/>
      服务：GeoServer（WMS/WMTS/WFS）</p>
    <p style="margin-top:8px;"><b style="color:var(--accent);">数据来源</b><br/>
      国家地球系统科学数据中心（滑坡数据）<br/>
      OpenStreetMap（路网/水系/医院/消防站）<br/>
      阿里云 DataV（行政边界）<br/>
      高德 API（避难所 POI）</p>
    <p style="margin-top:8px;"><b style="color:var(--accent);">主要功能</b><br/>
      6 种底图动态切换 · 动态投影（WGS-84/GCJ-02/BD-09）<br/>
      地图控件（缩放/比例尺/鹰眼/坐标）<br/>
      图层管理（5 层 WFS 服务）<br/>
      统计分析（4 张 ECharts 交互图表）<br/>
      灾害查询 + 框选查询<br/>
      测量工具 + 绘制工具<br/>
      空间分析（缓冲区/最近设施/热力图）<br/>
      二三维一体化（OpenLayers + Cesium 分屏 + 视角同步）<br/>
      GeoServer 发布 OGC 标准服务</p>
    <p style="margin-top:8px;"><b style="color:var(--accent);">开发者</b><br/>WebGIS 课程作业 · 2026</p>
  </div>
</template>
