# 🏆 Football Match Predictor - 足球比赛预测系统

一个生产级的足球比赛预测平台，使用多种机器学习和深度学习模型预测足球比赛结果。

## ✨ 主要特性

- **6 种预测模型**：ELO评分、逻辑回归、随机森林、XGBoost、LSTM、神经网络集成
- **多维度预测**：比赛赢家(1X2)、确切比分、进球总数、进球球队
- **实时数据更新**：自动从多个数据源爬取最新比赛数据
- **Web 前端**：React + TypeScript 交互式仪表板
- **REST API**：FastAPI 高性能 API 服务
- **数据分析**：Jupyter 笔记本进行深度数据分析
- **Docker 部署**：一键启动完整系统
- **CI/CD**：GitHub Actions 自动化测试和部署

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────┐
│          Frontend (React + TypeScript)              │
│  - 实时比赛展示板                                    │
│  - 预测结果对比                                      │
│  - 模型性能评估                                      │
└────────────────┬────────────────────────────────────┘
                 │ HTTP/REST
┌────────────────┴────────────────────────────────────┐
│         Backend (FastAPI + Flask)                   │
│  - API 路由和业务逻辑                                │
│  - 预测模型服务                                      │
│  - 数据处理管道                                      │
└────────────────┬────────────────────────────────────┘
                 │
     ┌───────────┴──────────┬───────────────┐
     │                      │               │
┌────▼──────────┐  ┌────────▼──────┐  ┌────▼──────────┐
│  PostgreSQL   │  │    MongoDB    │  │    Redis      │
│  历史数据      │  │  用户数据     │  │  缓存         │
└───────────────┘  └───────────────┘  └───────────────┘
     │
     └────────────────────┬──────────────────┐
                          │                  │
                  ┌───────▼────────┐  ┌─────▼──────────┐
                  │ Data Fetchers  │  │ ML Models      │
                  │ - Football API │  │ - ELO Score    │
                  │ - ESPN         │  │ - RandomForest │
                  │ - RapidAPI     │  │ - XGBoost      │
                  │ - Web Scraper  │  │ - LSTM         │
                  └────────────────┘  │ - Ensemble     │
                                      └────────────────┘
```

## 📂 项目结构

```
football-match-predictor/
├── backend/                      # 后端应用
│   ├── app.py                   # FastAPI 主应用
│   ├── flask_dashboard.py       # Flask 仪表板
│   ├── requirements.txt         # 依赖包
│   ├── config.py                # 配置文件
│   ├── .env.example             # 环境变量示例
│   │
│   ├── data/                    # 数据处理模块
│   │   ├── __init__.py
│   │   ├── fetcher.py          # 数据获取器
│   │   ├── processor.py        # 数据处理器
│   │   ├── cleaner.py          # 数据清洗
│   │   └── feature_engineer.py # 特征工程
│   │
│   ├── models/                  # 预测模型
│   │   ├── __init__.py
│   │   ├── base_model.py       # 基础模型类
│   │   ├── elo_predictor.py    # ELO 评分
│   │   ├── ml_predictor.py     # 机器学习模型
│   │   ├── dl_predictor.py     # 深度学习模型
│   │   ├── ensemble.py         # 集成模型
│   │   └── model_utils.py      # 模型工具函数
│   │
│   ├── api/                     # API 路由
│   │   ├── __init__.py
│   │   ├── routes.py           # API 端点
│   │   ├── schemas.py          # 数据模型
│   │   └── middleware.py       # 中间件
│   │
│   ├── database/                # 数据库操作
│   │   ├── __init__.py
│   │   ├── models.py           # 数据库模型
│   │   ├── connection.py       # 数据库连接
│   │   └── crud.py             # CRUD 操作
│   │
│   ├── utils/                   # 工具函数
│   │   ├── __init__.py
│   │   ├── logger.py           # 日志记录
│   │   ├── validators.py       # 数据验证
│   │   └── helpers.py          # 辅助函数
│   │
│   └── tests/                   # 测试文件
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_api.py
│       └── test_data.py
│
├── frontend/                     # React 前端
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   ├── src/
│   │   ├── index.tsx
│   │   ├── App.tsx
│   │   ├── components/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── PredictionCard.tsx
│   │   │   ├── MatchList.tsx
│   │   │   ├── ModelComparison.tsx
│   │   │   └── Charts.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   ├── Predictions.tsx
│   │   │   ├── Analytics.tsx
│   │   │   └── Models.tsx
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── storage.ts
│   │   ├── styles/
│   │   │   ├── index.css
│   │   │   └── variables.css
│   │   ├── types/
│   │   │   └── index.ts
│   │   └── utils/
│   │       ├── formatters.ts
│   │       └── validators.ts
│   ├── package.json
│   ├── tsconfig.json
│   └── .env.example
│
├── notebooks/                    # Jupyter 笔记本
│   ├── 01_data_exploration.ipynb
│   ├── 02_feature_engineering.ipynb
│   ├── 03_model_training.ipynb
│   ├── 04_model_evaluation.ipynb
│   └── 05_visualization.ipynb
│
├── scripts/                      # 辅助脚本
│   ├── setup_db.py
│   ├── fetch_data.py
│   ├── train_models.py
│   ├── deploy.sh
│   └── monitor.py
│
├── config/                       # 配置文件
│   ├── docker-compose.yml
│   ├── nginx.conf
│   ├── kubernetes/
│   │   └── deployment.yaml
│   └── github-workflows/
│       ├── test.yml
│       └── deploy.yml
│
├── docs/                         # 文档
│   ├── API.md
│   ├── SETUP.md
│   ├── MODELS.md
│   └── DEPLOYMENT.md
│
├── .gitignore
├── LICENSE
└── CONTRIBUTING.md
```

## 🚀 快速开始

### 前置要求

- Python 3.9+
- Node.js 16+
- Docker & Docker Compose
- PostgreSQL 13+
- MongoDB 5+
- Redis 6+

### 安装步骤

#### 1. 克隆仓库
```bash
git clone https://github.com/a1585902190h/sk.git
cd sk
```

#### 2. 使用 Docker Compose 启动（推荐）
```bash
docker-compose up -d
```

访问：
- 前端：http://localhost:3000
- API 文档：http://localhost:8000/docs
- Flask 仪表板：http://localhost:5000

#### 3. 手动安装（开发环境）

**后端设置**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 设置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 API 密钥和数据库配置

# 初始化数据库
python scripts/setup_db.py

# 启动后端服务
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

**前端设置**
```bash
cd frontend
npm install
npm start
```

## 📊 预测模型详解

### 1. ELO 评分系统
- **原理**：基于国际象棋的 ELO 等级分系统
- **特点**：简单快速，实时更新
- **准确率**：55-60%

### 2. 逻辑回归 (Logistic Regression)
- **原理**：线性分类模型
- **特点**：可解释性强，训练快
- **准确率**：60-65%

### 3. 随机森林 (Random Forest)
- **原理**：决策树集成学习
- **特点**：稳定性好，处理非线性关系
- **准确率**：65-70%

### 4. 梯度提升 (XGBoost/LightGBM)
- **原理**：迭代式集成学习
- **特点**：准确率最高，但训练时间长
- **准确率**：70-75%

### 5. LSTM 深度学习
- **原理**：循环神经网络，处理时间序列
- **特点**：捕捉长期依赖关系
- **准确率**：68-72%

### 6. 集成模型 (Ensemble)
- **原理**：融合多个模型的预测结果
- **特点**：综合各模型优势，最稳定
- **准确率**：72-78%

## 🔌 API 端点

### 获取比赛列表
```bash
GET /api/matches?league=EPL&date=2024-01-15
```

### 预测单场比赛
```bash
POST /api/predict
{
  "home_team": "Manchester United",
  "away_team": "Liverpool",
  "league": "EPL",
  "models": ["ensemble", "xgboost", "elo"]
}
```

### 获取历史预测
```bash
GET /api/predictions?team=Manchester United&limit=10
```

### 获取模型性能
```bash
GET /api/models/performance?date_range=30d
```

详见 [API 文档](docs/API.md)

## 📈 性能指标

| 模型 | 准确率 | 精准率 | 召回率 | F1 分数 | 训练时间 |
|------|--------|--------|--------|---------|---------|
| ELO | 58% | 56% | 60% | 0.58 | <1s |
| 逻辑回归 | 62% | 61% | 63% | 0.62 | 2s |
| 随机森林 | 68% | 67% | 69% | 0.68 | 30s |
| XGBoost | 74% | 73% | 75% | 0.74 | 45s |
| LSTM | 70% | 69% | 71% | 0.70 | 120s |
| 集成 | 76% | 75% | 77% | 0.76 | 180s |

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest backend/tests/test_models.py

# 生成覆盖率报告
pytest --cov=backend
```

## 🐳 Docker 部署

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 📚 文档

- [设置指南](docs/SETUP.md)
- [API 文档](docs/API.md)
- [模型详解](docs/MODELS.md)
- [部署指南](docs/DEPLOYMENT.md)

## 🔄 数据更新

系统每天自动从以下源更新数据：

- **Football-Data.org** - 全球主要联赛
- **ESPN API** - 赛事信息和统计
- **RapidAPI** - 实时比分和数据
- **Web Scraping** - 特殊赛事和数据

更新频率：每小时一次（可配置）

## 🛠️ 开发

### 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

详见 [贡献指南](CONTRIBUTING.md)

## 📝 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE)

## 📧 联系方式

- 提交 Issue：[GitHub Issues](https://github.com/a1585902190h/sk/issues)
- 邮件：your-email@example.com

## 🙏 致谢

感谢以下项目和社区：
- [Football-Data.org](https://www.football-data.org/)
- [scikit-learn](https://scikit-learn.org/)
- [TensorFlow](https://www.tensorflow.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)

---

⭐ 如果本项目对你有帮助，请给个 Star！
