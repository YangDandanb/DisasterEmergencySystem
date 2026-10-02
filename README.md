# 地质灾害应急救援辅助决策 WebGIS 平台

面向 **四川省** 的滑坡地质灾害应急指挥 WebGIS 系统。以 DataV 大屏风格呈现，全屏地图 + 左右悬浮面板，将滑坡灾害点、医院、消防站、避难所等分散数据汇聚到一张实时地图上，支撑应急指挥决策。

## ✨ 核心功能

- **6 种底图切换**：天地图（矢量/影像）、高德、百度、OSM、ArcGIS，含 GCJ-02 / BD-09 动态投影坐标对齐
- **图层管理**：滑坡点、省界、医院、消防站、避难所，设施点聚合显示（Cluster + SVG 图标）
- **三类灾害查询**：点击查询（气泡详情）、条件筛选、框选查询
- **测量与绘制**：测距 / 测面积（球面），点 / 线 / 面 / 圆连续绘制
- **空间分析**：缓冲区、最近设施、热力图
- **二三维一体化**：OpenLayers（二维）+ Cesium（三维）分屏切换、视角双向同步
- **统计图表联动**：ECharts 四张图表（市州 / 诱因 / 等级 / 月度），点击联动地图高亮

## 🛠 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 · OpenLayers 10 · Cesium · ECharts · Element Plus · Pinia · Vite |
| 后端 | FastAPI · SQLAlchemy · geoalchemy2 |
| 数据库 | PostgreSQL 15 + PostGIS 3 |
| GIS 服务 | GeoServer 2.25（WFS / WMTS） |
| 坐标 | proj4（EPSG:4490 / BD09），WGS-84 ↔ GCJ-02 ↔ BD-09 互转 |

## 🏗 系统架构

数据只存一份在 PostgreSQL/PostGIS（7 张表），前端经两条通路读取：

```
展示层     Vue3 + OpenLayers / Cesium / ECharts
              │  ↑ WFS/WMTS          │  ↑ REST
服务层     GeoServer (8080)       FastAPI (8000)
              │  ↑                    │  ↑
              └──┴── 都读同一个 PostgreSQL/PostGIS ──┴──┘
存储层     PostgreSQL 15 + PostGIS（7 张表）
```

- **GeoServer**：负责空间数据发布（WFS 输出矢量 GeoJSON、WMTS 输出瓦片），供地图渲染
- **FastAPI**：负责业务逻辑（CRUD、统计、空间分析），共 15 个 RESTful 接口

## 🚀 快速启动

> 详细步骤见 [系统启动指南.md](系统启动指南.md)，这里给最小路径。

### 0. 环境变量配置（重要，密钥不随仓库提交）

```bash
# 前端：天地图 API Key
cd frontend && cp .env.example .env   # 然后编辑 .env 填入你的 VITE_TK

# 后端：数据库密码
cd ../backend && cp .env.example .env # 然后编辑 .env 填入 DB_PASSWORD
```

### 1. 启动 PostgreSQL（端口 5432）

```bash
net start postgresql-x64-15
```

### 2. 启动 GeoServer（端口 8080）

```bash
# 必须带 -DGEOSERVER_DATA_DIR 指向你的数据目录
java -DGEOSERVER_DATA_DIR="<你的data_dir路径>" -Djava.awt.headless=true -DSTOP.PORT=8079 -DSTOP.KEY=geoserver -jar start.jar
```

### 3. 启动后端 FastAPI（端口 8000）

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 4. 启动前端 Vite（端口 5173）

```bash
cd frontend
npm install
npm run dev
```

浏览器打开 **http://localhost:5173**

## 📁 目录结构

```
├── frontend/            # Vue3 + OpenLayers 前端
│   └── src/
│       ├── views/       # 主视图 MainView
│       ├── components/  # 面板组件（图层/查询/工具/分析…）
│       ├── stores/      # Pinia 状态管理
│       └── utils/       # 投影注册、坐标转换
├── backend/             # FastAPI 后端
│   └── app/
│       ├── api/         # 15 个 RESTful 接口
│       ├── models/      # ORM 模型
│       ├── schemas/     # Pydantic 校验
│       └── core/        # 配置、数据库连接
├── Data/                # 滑坡源数据（xlsx）
├── poi_data/            # 医院/消防站/避难所 CSV
└── 系统启动指南.md        # 完整启动文档
```

## 📊 数据清单

业务数据全部存入 PostgreSQL/PostGIS（7 张表）：

| 表 | 数据量 | 说明 |
|----|--------|------|
| landslide | 260 | 滑坡灾害点 |
| hospital / fire_station / shelter | 450 / 500 / 227 | 医院 / 消防站 / 避难所 |
| sichuan_boundary | 21 | 四川省边界 |
| road / water | 16 万 / 2.7 万 | 路网 / 水系 |

## 📝 说明

- 地图底图（天地图/高德/百度）为第三方服务，`VITE_TK` 需自行申请
- 滑坡数据来源于公开的"中国大陆高精度滑坡事件数据集（2008-2024）"
- 项目仅供学习与演示，地质灾害数据公开使用时请注意合规与脱敏
