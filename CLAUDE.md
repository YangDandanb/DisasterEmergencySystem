# 地质灾害应急救援辅助决策WebGIS平台

## 项目概述
Vue3 + OpenLayers 滑坡地质灾害应急 WebGIS 系统，**研究范围：四川省**。DataV 大屏风格，全屏地图 + 左右悬浮面板。目前纯前端，后端待重建。

## 技术栈
- **前端**: Vue 3 / JavaScript / Vite 5 / OpenLayers 10 / Element Plus 2 / ECharts 5 / Pinia 2 / proj4js
- **后端**: FastAPI (Python) — 待重建
- **数据库**: PostgreSQL 15 + PostGIS 3 — 待重建
- **GIS服务**: GeoServer 2.25 — 待重建

## 项目结构
```
地质灾害应急系统/
├── CLAUDE.md                       # 本文档
├── 系统功能全景介绍.txt             # 大白话功能介绍
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js              # Vite配置 + API代理
│   └── src/
│       ├── main.js                 # 入口
│       ├── App.vue
│       ├── assets/base.css         # 全局样式（DataV暗色主题）
│       ├── views/
│       │   └── MainView.vue        # 主视图：顶栏 + 地图 + 左右面板
│       ├── components/
│       │   ├── TopBar.vue                   # 顶部栏（Logo + 菜单按钮）
│       │   ├── LeftPanel.vue                # 左侧面板容器
│       │   ├── RightPanel.vue               # 右侧面板容器（v-show切换）
│       │   ├── FloatingToolbar.vue           # 浮动工具栏（待填充）
│       │   └── panels/
│       │       ├── LeftStats.vue             #   左侧：统计卡片
│       │       ├── LeftMonitor.vue            #   左侧：监测+饼图
│       │       ├── LeftList.vue              #   左侧：灾害点列表
│       │       ├── RightBaseMap.vue ✅       #   M1：图源切换
│       │       ├── RightLayers.vue           #   M2：图层管理
│       │       ├── RightQuery.vue            #   M3：灾害查询
│       │       ├── RightTools.vue            #   M4：工具箱
│       │       ├── RightAbout.vue            #   M5：关于平台
│       │       └── RightAnalysis.vue         #   M6：空间分析
│       ├── stores/
│       │   └── mapStore.js         # Pinia：map实例, activeMenu, currentBaseMap
│       ├── utils/
│       │   ├── projections.js      # proj4投影注册 (EPSG:4490/BD09)
│       │   └── coordTransform.js   # 坐标转换 (WGS84↔GCJ02↔BD09)
│       └── router/index.js         # 单路由 -> MainView
```

## 已实现功能

### ✅ 底图切换（M1 图源面板）
- **实现方式**: 6种底图在 `MainView.vue` 初始化时一次性创建，全部加入地图。切换时调用 `useBaseMap.switchTo(id)`，只改 `setVisible()`，不做 add/remove。
- **6种底图**: 高德(默认)、天地图矢量、天地图影像、百度、OpenStreetMap、ArcGIS影像
- **天地图**: 使用 `vec_w`/`img_w` (球面墨卡托 EPSG:3857)，key=`VITE_TK`（环境变量，见 `frontend/.env.example`）
- **百度地图**: 自定义 TileGrid + tileUrlFunction（BD-09 坐标系处理）
- **文件**: [MainView.vue](frontend/src/views/MainView.vue) | [RightBaseMap.vue](frontend/src/components/panels/RightBaseMap.vue) | [mapStore.js](frontend/src/stores/mapStore.js)

### ✅ 地图控件
- Zoom（缩放）、ScaleLine（比例尺）、OverviewMap（鹰眼图/默认折叠）、MousePosition（鼠标坐标 EPSG:4326）

### ✅ 坐标系统
- proj4js 注册 EPSG:4490（CGCS2000）+ EPSG:BD09
- WGS84 ↔ GCJ02 ↔ BD09 互转工具

### ✅ 二三维一体化（Cesium）
- 浮动工具栏按钮切换：二维 / 二三维 / 三维
- 二三维模式：OpenLayers 占左 50% + Cesium 占右 50%，固定分屏
- 三维数据与二维共用 GeoServer WFS（滑坡点+省界）
- 视角同步开关（🔗 按钮），OL ↔ Cesium 双向联动
- Cesium 组件在 `FloatingToolbar.vue` 中通过 Teleport 管理

### ✅ GeoServer OGC 服务
- 6 种底图 + 动态投影（WGS/GCJ/BD09 坐标转换）

**验证方法（页面自动打印）**：
在 `MainView.vue` 的 `onMounted` 中加了自动验证代码。刷新页面后 F12 控制台会输出：
1. EPSG:4490 / BD09 投影是否注册
2. 北京天安门 WGS-84 → GCJ-02 → BD-09 转换链
3. 偏移距离（北京约 710m）
4. GCJ-02 → WGS-84 逆转换精确度

**验证结果（2026-06-27）**：两个投影均已注册，转换链正常，偏移量符合预期，逆转换精确可逆。

### ✅ 布局
- 全屏地图底色 + absolute悬浮面板
- 顶栏透明，菜单按钮悬浮，Logo两行居上
- 左右面板 19%宽，背景 #043776e6
- 面板四角青色发光装饰线

### ✅ 数据格式转换（2026-07-01）
- 滑坡 xlsx → GeoJSON（已加灾害等级列）
- 医院/消防站/路网/水系 SHP → GeoJSON（geopandas + ogr2ogr）
- GeoJSON → PostgreSQL/PostGIS（7 张表），已发布 GeoServer，前端改走 WFS/API，本地 `public/data/` 已清空

## 布局架构
```
┌──────────────────────────────────────────────┐
│   🌍 地质灾害应急救援辅助决策平台              │ 透明顶栏
│   图源 图层 查询  │  分析 工具 关于             │ 毛玻璃按钮
├────────┬───────────────────────┬──────────────┤
│ 左侧   │                       │  右侧面板     │
│ 统计   │    OpenLayers 地图    │  M1-M6 ✅     │
│ 面板   │                       │  全部完成      │
│ 4张   │    [浮动工具栏]        │               │
│ 图表   │    2D|2+3|3D 🔗      │               │
└────────┴───────────────────────┴──────────────┘
```
```

## 数据清单（2026-09-19 更新）
业务数据已全部迁入 PostgreSQL/PostGIS，经 GeoServer WFS / FastAPI 对外提供；本地 GeoJSON 与冗余栅格已清理，仅保留少量源数据：

| 数据 | 存储位置 | 本地源文件 |
|------|---------|-----------|
| 滑坡 260 条 | PostgreSQL `landslide` | `Data/滑坡3.0.xlsx` |
| 医院 450 / 消防站 500 / 避难所 227 | PostgreSQL `hospital` / `fire_station` / `shelter` | `poi_data/*.csv` |
| 四川边界 21 | PostgreSQL `sichuan_boundary` | — |
| 路网 16 万 / 水系 2.7 万 | PostgreSQL（GeoServer WFS 提供） | `路网，水系，应急点资源（医院消防等）数据.qgz` |
| 四川 DEM | 本地 `Sichuan_DEM.tif` (873MB) | 风险区划图原料 |

## 已完成功能（2026-07-03）
1. ✅ 底图切换 + 动态投影（6种底图，WGS/GCJ/BD坐标偏移）
2. ✅ 地图控件（Zoom/ScaleLine/OverviewMap/MousePosition）
3. ✅ 坐标系统（WGS-84↔GCJ-02↔BD-09）
4. ✅ 图层管理 M2（5层WFS + 1层WMS，含设施SVG图标+聚合+用户层）
5. ✅ 左侧统计分析面板（4张ECharts交互图表，点击联动地图）
6. ✅ Popup气泡弹窗（点击滑坡点显示详情+删除）
7. ✅ 查询面板 M3（条件筛选+框选查询+结果列表定位）
8. ✅ 测量工具（测距/测面积，参照官方ol/sphere示例）
9. ✅ 绘制工具 M4（点/线/面/圆 + 连续绘制 + 双层弹窗保存）
10. ✅ 新增滑坡点（点选坐标+填表提交，写入PostgreSQL）
11. ✅ 空间分析 M6（缓冲区/最近设施/热力图）
12. ✅ 二三维一体化（Cesium浮层+50/50分屏+视角同步开关）
13. ✅ 后端 FastAPI（CRUD+统计+空间分析）
14. ✅ GeoServer WFS/WMS 全5层发布
15. ✅ PostgreSQL/PostGIS 7张表（滑坡260/医院450/消防站500/避难所227/边界21/路网16万/水系2.7万）

## 待完成
- 风险区划图（QGIS制作DEM坡度+水系+历史密度→GeoJSON→发布；DEM/坡度栅格已清理，仅留 `Sichuan_DEM.tif`）
- 路径规划（pgRouting，可选）

## 下一步计划（2026-07-01）
1. **搭建 layerStore.js**：统一管理平台层和用户层，是 M2 和 M4 的共同底座
2. **实现 M2 图层管理面板**：显示图层列表 + 可见开关，先接入四川省边界验证
3. **加载业务数据**：滑坡点 + 医院 + 消防站，按设计规范配色渲染
4. **左侧面板填充**：LeftStats 数字卡片 + LeftMonitor ECharts 饼图 + LeftList 可搜索列表

## 关键约定
- 地图实例: `window.__map`（全局访问）
- 所有底图层: `useMap().baseLayers` 返回 `{ gaode, tianditu_vec, ... }`
- 右侧面板: `mapStore.activeMenu` 控制 (''=关闭, 'M1'~'M6')
- CSS变量: `base.css` 的 `:root` 中定义
- 面板宽度: 19% (min 260px, max 330px)
- 代码: 纯 JavaScript（已从 TS 转过一次）
- ⚠️ 不要再引入 TypeScript
- **读 Pinia state 必须用 `storeToRefs` 解构**：`const { xxx } = storeToRefs(mapStore)`，不能直接 `mapStore.xxx`，否则在异步组件（如 defineAsyncComponent）中响应式会断开
- ⚠️ **实施新功能时绝对不能删除其他已有功能的代码**。如果新代码和旧代码冲突，把旧代码**注释掉**而非删除，标注清楚原因。这是血的教训——重写 RightTools 测量部分时把绘制工具代码删了，导致功能丢失

## 踩坑记录

### 1. TS → JS 转换
- 全项目 `.ts` → `.js`，`.vue` 去掉 `lang="ts"`
- `defineProps<{ visible: boolean }>()` → `defineProps(['visible'])`
- `(window as any).__map` → `window.__map`
- `vite.config.ts` → `vite.config.js`
- `package.json` 的 build 命令去掉 `vue-tsc -b`

### 2. 底图切换
**错误做法**: 切换时 add/remove 图层。URL 中 `{a-d}` 子域名语法不兼容，`vec_c`/`img_c` 是经纬度投影（EPSG:4326），和主地图 EPSG:3857 不匹配。
**正确做法**: 6个底图提前创建存入 `layerPool` 对象，初始只放默认底图到地图。切换时 `map.removeLayer(old)` + `map.addLayer(new)`。
- 高德 URL: `http://webrd0{1-4}.is.autonavi.com/...`
- 天地图用 `vec_w`/`img_w`（球面墨卡托，匹配 EPSG:3857），key 在 `mapConfig.js`
- 百度需自定义 TileGrid + tileUrlFunction（Y轴翻转）

### 3. 地图控件不显示
**三个原因**:
1. 没导入 `ol/ol.css` → main.js 要加 `import 'ol/ol.css'`
2. 控件应通过 `map.addControl()` 添加，不能在 Map 构造函数的 `controls` 里传
3. 左右面板（z-index:15-20）盖住了控件 → CSS 里用 `left:calc(19%+16px)` 等方式把控件往中间推

### 4. 鹰眼图（OverviewMap）
**错误**: 主地图切底图后鹰眼图没跟着变
**正确**: 底图切换时调用 `overviewCtrl.setLayers([new TileLayer({ source: newLayer.getSource() })])` 同步更新鹰眼图层源

### 5. 比例尺 ScaleLine 不显示
**症状**: 比例尺控件加了 `className: 'custom-scale-line'` 后变成竖条或完全不显示
**根因**: 
1. 自定义 className 会**替换** OL 默认的 `ol-scale-line` 类，导致内部横条样式（border/margin/颜色）全部丢失
2. OL 控件 DOM 是动态创建的，Vue 的 `<style scoped>` + `:deep()` 选择器不一定能命中
**正确做法**:
- 不使用 `className`，保留 `ol-scale-line` 默认类名
- `new ScaleLine({ units: 'metric' })` 参数越简单越好，不要加 `bar`/`steps`/`minWidth` 等
- 控件定位 CSS 写在 **非 scoped** 的 `<style>` 块里（因为 OL DOM 不受 Vue 作用域约束）
- 用 `!important` 覆盖 OL 默认的 `left`/`bottom` 内联样式

### 6. Pinia 响应式断开（底图选中标识不更新）
**症状**: 点击其他底图卡片，地图切换了，但选中发光标识一直固定在高德上
**原因**: `defineAsyncComponent` 懒加载的组件里，直接读 `mapStore.currentBaseMap` 时响应式链条断开
**解决**: 用 `storeToRefs` 解构 — `const { currentBaseMap } = storeToRefs(mapStore)`，模板里直接用 `currentBaseMap`

### 7. 动态投影（矢量数据跟随底图偏移）

**为什么会偏移？**

GPS 采集的坐标是 WGS-84（地球真实经纬度），中国的地图厂商不能直接用，国家对地图数据有加密要求。于是：

- 高德/腾讯在 WGS-84 上加了一层偏移算法，搞出了 GCJ-02（俗称"火星坐标系"）。同一个物理位置，GCJ-02 坐标比 WGS-84 偏了 100~700 米。
- 百度更狠，在 GCJ-02 上又加了一层自己的偏移，搞出了 BD-09。
- 天地图和 OSM 用的是 WGS-84，不偏移。

所以你的滑坡数据（WGS-84 经纬度）直接画在高德底图上，会偏几百米——因为高德底图的瓦片是按 GCJ-02 切的，OpenLayers 以为它按 WGS-84 切的。百度偏得更厉害。

**怎么解决？**

本质就是：切换底图时，把所有矢量图层的坐标也同步偏移。

具体做法（代码在 `RightBaseMap.vue` 第 68~90 行的 `onSwitch` 函数里）：

1. **第一次切换时**：把 feature 当前的坐标反算回 WGS-84（经纬度），存到 `feature.set('_wgs84', [lon, lat])` 里——这是"锚点"，永远不变。
2. **之后每次切换**：从 `_wgs84` 取原始经纬度，根据目标底图计算应该偏移多少：
   - 切到高德 → `wgs84ToGcj02()` 偏移后再投到地图上
   - 切到百度 → `wgs84ToGcj02()` + `gcj02ToBd09()` + 百度自己的墨卡托投影
   - 切回天地图/OSM → 直接用原始 WGS-84，不偏移
3. **不是 Point 怎么办**：行政区边界是 LineString/Polygon，不能直接改坐标——用 `geom.translate(dx, dy)` 整体平移。

**为什么必须用 `_wgs84` 缓存？**

因为如果不用缓存，每次切换都在"当前坐标"上再做一次偏移——来回切几次底图，浮点误差越积越多，点就不知道飘哪去了。有了 `_wgs84` 锚点，每次都是从原点出发算，切多少次都不会漂移。

### 8. 百度瓦片 CORS 跨域错误
**症状**: 百度瓦片加载失败，控制台报 `Access-Control-Allow-Origin` 错误
**原因**: XYZ source 加了 `crossOrigin: 'anonymous'`，百度服务器不返回 CORS 头
**解决**: 百度 source 不加 `crossOrigin`，直接加载瓦片（不需要像素操作）

### 9. RightLayers 图层加载时序问题
**症状**: 页面加载后四川省边界和滑坡点不显示，但无报错
**原因**: RightLayers 用 `v-show` 始终挂载，`onMounted` 在 MainView 创建地图之前执行，此时 `mapStore.map` 为 null
**解决**: 用 `watch(() => mapStore.map, callback, { immediate: true })` 替代 `onMounted`，等 map 就绪后再创建图层

### 10. 设施点图层重复代码重构
**症状**: 医院、消防站、避难所三个图层代码几乎一模一样（Cluster + SVG图标），维护困难
**解决**: 抽成 `createFacilityLayer(url, svgPath, clusterColor)` 函数，一行调用替代 30 行重复代码

### 11. 测距/测面积（ol/sphere）
**踩坑**:
1. 不能给 `getLength()`/`getArea()` 传 `{ projection: 'EPSG:4326' }`——Draw 产生的几何在 EPSG:3857，传错了参数导致测量结果完全错误。参照官方示例不传参，让函数自动处理
2. 测量图层（VectorLayer）必须 `map.addLayer()` 才能看到绘制的线/面，只创建 VectorSource 不够
3. 官方示例的 `drawend` 只改 tooltip 样式，不清除 feature——我之前加 `measureSource.clear()` 把刚画的线删了

### 12. Icon 导入路径
**症状**: `import { Icon } from 'ol/style'` 在 Vite 打包时找不到导出
**原因**: OL 的 `ol/style` 聚合模块不重新导出 `Icon`
**解决**: 照官方示例用 `import Icon from 'ol/style/Icon'`（独立路径）

### 13. 测量 Tooltip 气泡残留（清除不干净）
**症状**: 点"清除测量"后图形没了，但气泡标签还残留在地图上
**原因**: 
1. 每次 `drawend` 把 `tipEl` 设为 `null` 再调用 `createTip()` 新建 tooltip——旧 tooltip 的 DOM 元素成了孤儿，`source.clear()` 删不掉
2. 清除时只调了 `source.clear()`，没有处理 Overlay 对象
**正确做法**:
- 使用**单例 Overlay**（`ensureMeasureOverlay()`），创建一次、反复复用，不销毁重建
- 清除时调用 `measureOverlay.setPosition(undefined)` 隐藏气泡 + 重置 className 和 innerHTML，**不删 DOM**
- 关键：不新建不销毁，只隐藏和重置状态

### 14. 第二阶段：数据库 + 后端重建（2026-07-02）
**过程**: 
1. ogr2ogr 导入 GeoJSON 报错 `Unable to find driver 'PostgreSQL'` → 改用 Python geopandas 的 `to_postgis()` 一行代码完成
2. geopandas 默认几何列名为 `geometry` 而非 `geom`——建空间索引时报错，查 `information_schema.columns` 确认列名后修正
**结果**: 5 张表（滑坡 260 / 医院 450 / 消防站 500 / 避难所 227 / 边界 21）全部导入，带 GIST 空间索引。FastAPI 启动后前端 GeoJSON URL 改为 `/api/landslides/export`，一行代码不动、功能无缝切换
