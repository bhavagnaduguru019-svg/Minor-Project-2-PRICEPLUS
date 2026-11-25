# 💹 PricePulse — AI-Powered Dynamic Pricing & Revenue Optimization Engine

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.40-red?logo=streamlit)](https://streamlit.io)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.5-orange?logo=scikit-learn)](https://scikit-learn.org)
[![XGBoost](https://img.shields.io/badge/XGBoost-2.1-blue)](https://xgboost.ai)
[![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey?logo=sqlite)](https://sqlite.org)

---

## 🎯 Project Overview

**PricePulse** is a production-ready, AI-powered dynamic pricing platform for e-commerce businesses. It analyzes demand patterns, competitor prices, inventory levels, seasonal factors, and customer segments to recommend optimal product prices in real-time.

### Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Price Optimization** | Random Forest & XGBoost models predict optimal prices |
| 🔮 **Demand Forecasting** | ML-powered daily/weekly/monthly demand predictions |
| ⚔️ **Competitor Analysis** | Real-time price gap monitoring and market positioning |
| ⚡ **Flash Sale Detection** | Statistical anomaly detection (Z-score) for demand spikes |
| 💰 **Revenue Analytics** | Revenue trends, optimization potential, and product profitability |
| 📦 **Product Management** | Full CRUD with searchable, filterable product catalogue |
| 📊 **Business Intelligence** | Interactive Plotly dashboards with premium dark-mode UI |

---

## 🛠️ Technology Stack

```
Frontend:   Streamlit + Plotly + Custom CSS (Inter font, dark-mode)
Backend:    FastAPI + Uvicorn + SQLAlchemy + SQLite
ML Models:  Scikit-learn (Random Forest) + XGBoost (Tuned) + Joblib
Data:       Synthetic 2-year e-commerce dataset (50 products, 36,500 rows)
```

---

## 📁 Project Structure

```
PricePulse/
├── app.py                      # Master initializer (DB + data + training)
├── requirements.txt
├── Dockerfile
├── .gitignore
│
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── routes.py               # All REST API endpoints
│   └── schemas.py              # Pydantic request/response models
│
├── frontend/
│   ├── dashboard.py            # Streamlit router & sidebar
│   ├── components.py           # Reusable UI components & CSS
│   └── pages/
│       ├── overview.py         # Overview Dashboard
│       ├── products.py         # Product Management
│       ├── price_optimization.py # AI Price Optimization
│       ├── demand_forecasting.py # Demand Forecasting
│       ├── competitor_analysis.py # Competitor Analysis
│       ├── flash_sale_alerts.py   # Flash Sale Alerts
│       ├── revenue_analytics.py   # Revenue Analytics
│       └── settings.py            # Settings & Model Performance
│
├── ml/
│   ├── feature_engineering.py  # Data generation + feature pipeline
│   ├── train_model.py          # RF + XGBoost training pipeline
│   ├── price_predictor.py      # PricePredictor class
│   ├── demand_forecasting.py   # DemandForecaster + anomaly detection
│   ├── price_optimizer.py      # Revenue optimization engine
│   └── evaluation.py          # MAE, MSE, RMSE, R² metrics
│
├── database/
│   ├── db.py                   # SQLAlchemy engine & session
│   └── models.py               # ORM table definitions (7 tables)
│
├── data/
│   └── synthetic_sales.csv     # Generated after first run
│
├── models/                     # Joblib model files (created after training)
│   ├── price_randomforest.joblib
│   ├── price_xgboost.joblib
│   ├── demand_randomforest.joblib
│   ├── demand_xgboost.joblib
│   ├── metrics.json
│   └── price_best_model.txt
│
└── utils/
    └── helpers.py              # Formatting & utility functions
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip

### 1. Clone & Install

```bash
git clone https://github.com/yourusername/pricepulse.git
cd pricepulse
pip install -r requirements.txt
```

### 2. Initialize (First Run)

```bash
python app.py
```

This will:
- Create SQLite database (`pricepulse.db`)
- Generate 2-year synthetic e-commerce dataset (50 products)
- Train Random Forest & XGBoost models (~2-5 min)
- Seed all database tables
- Print model evaluation metrics

### 3. Start Backend API

```bash
# Terminal 1
uvicorn backend.main:app --reload --port 8000
```

API will be available at: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

### 4. Start Frontend Dashboard

```bash
# Terminal 2
streamlit run frontend/dashboard.py
```

Dashboard will open at: `http://localhost:8501`

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Backend health check |
| GET | `/products` | List all products |
| POST | `/products` | Add new product |
| PUT | `/products/{id}` | Update product |
| DELETE | `/products/{id}` | Deactivate product |
| POST | `/predict-price` | AI price recommendation |
| POST | `/forecast-demand` | Demand forecast |
| GET | `/analytics` | Dashboard analytics |
| GET | `/competitors` | Competitor price data |
| GET | `/alerts` | Flash sale & inventory alerts |
| GET | `/model/metrics` | ML evaluation metrics |
| GET | `/revenue/trends` | Revenue trend data |
| GET | `/revenue/by-category` | Category revenue breakdown |

---

## 🤖 Machine Learning

### Models
- **Random Forest Regressor** — 200 trees, max_depth=12
- **XGBoost Regressor** — Hyperparameter-tuned via RandomizedSearchCV (15 iterations, 3-fold CV)

### Features Used (Price Prediction)
```
current_price, competitor_price, discount_pct, inventory, units_sold,
seasonal_factor, rating, day_of_week, month, quarter, is_weekend,
price_ratio, price_vs_min, demand_score, inv_ratio, rolling_7d_demand,
rolling_30d_revenue, elasticity_proxy, category_enc, segment_enc
```

### Evaluation Metrics
Real metrics are displayed in the **Settings → Model Performance** tab after training.

---

## 📊 Dataset

**Synthetic e-commerce dataset** generated with realistic patterns:
- **50 products** across 8 categories (Electronics, Sports, Health, Fashion, Kitchen, Home, Books)
- **730 days** of data (~36,500 rows)
- Seasonal demand patterns (Diwali, Summer, New Year)
- Price elasticity demand model (log-linear)
- Competitor price simulation (5 competitors)
- Gradual price drift with business constraints

---

## 🐳 Docker

```bash
docker build -t pricepulse .
docker run -p 8000:8000 -p 8501:8501 pricepulse
```

---

## 🎨 Dashboard Pages

| Page | Description |
|------|-------------|
| 📊 Overview | KPIs, revenue trends, demand heatmap, category charts |
| 📦 Products | Full CRUD product management with search & filter |
| 🤖 AI Optimization | Product-level price analysis with ML recommendations |
| 🔮 Forecasting | Daily/weekly/monthly demand forecasts with confidence bands |
| ⚔️ Competitors | Price gap analysis, scatter plots, market positioning |
| ⚡ Flash Sales | Z-score spike detection, inventory warnings, flash candidates |
| 💰 Revenue | Trend analysis, optimization potential, profitability table |
| ⚙️ Settings | Model metrics, pricing config, system health, retrain |

---

## ⚠️ Disclaimer

All price recommendations are **model-based estimates** for decision support only. The system does not automatically change product prices. All revenue improvement figures are projections based on historical patterns and price-elasticity models.

---

## 👨‍💻 Author

Built as an AI/ML internship portfolio project demonstrating:
- End-to-end ML pipeline (data → features → model → API → UI)
- FastAPI REST backend architecture
- Streamlit dashboard development
- SQLAlchemy database integration
- Statistical anomaly detection
- Revenue optimization algorithms
