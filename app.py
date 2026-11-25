"""
PricePulse â€” Master Application Initializer
Usage:
    python app.py              # init DB + train models if needed, then exit
    python app.py --init-only  # same (for Docker)
    python app.py --retrain    # force retrain even if models exist
    python app.py --seed-only  # only seed DB, don't train

After running this, start the servers:
    uvicorn backend.main:app --reload --port 8000
    streamlit run frontend/dashboard.py --server.port 8501
"""
import os
import sys
import argparse

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)


def banner():
    print("""
+======================================================+
|   PricePulse  -  AI-Powered Dynamic Pricing Engine   |
|   Dynamic Pricing & Revenue Optimization Platform    |
+======================================================+
""")


def init_database():
    print("[DB]    Initializing database â€¦")
    from database.db import init_db
    init_db()
    print("[DB]    Tables created / verified.")


def seed_database(df):
    """Populate the DB with synthetic data."""
    print("[DB]    Seeding database with synthetic data â€¦")
    from database.db import SessionLocal
    from database import models as db_models
    from datetime import datetime

    db = SessionLocal()
    try:
        # Skip if already seeded
        if db.query(db_models.Product).count() > 0:
            print("[DB]    Database already seeded â€” skipping.")
            return

        from ml.feature_engineering import PRODUCTS, COMPETITORS
        import numpy as np
        rng = np.random.default_rng(42)

        # Insert products
        prod_map = {}
        for pid, (name, cat, base_p, min_p, max_p, seg) in enumerate(PRODUCTS, start=1):
            prod = db_models.Product(
                name=name, category=cat,
                current_price=base_p, min_price=min_p, max_price=max_p,
                inventory=int(rng.integers(80, 300)),
                rating=round(float(rng.uniform(3.5, 5.0)), 1),
                discount_pct=0.0,
                customer_segment=seg,
            )
            db.add(prod)
            db.flush()
            prod_map[pid] = prod.id

        db.commit()
        print(f"[DB]    Inserted {len(PRODUCTS)} products.")

        # Insert sales history (last 180 days per product, sampled)
        from datetime import timedelta
        import pandas as pd
        df_sample = df[df["date"] >= df["date"].max() - pd.Timedelta(days=180)].copy()
        # Map product_id from df (1-indexed) to actual DB ids
        sales_records = []
        for _, row in df_sample.iterrows():
            db_pid = prod_map.get(int(row["product_id"]))
            if db_pid is None:
                continue
            sh = db_models.SalesHistory(
                product_id=db_pid,
                date=row["date"],
                units_sold=int(row["units_sold"]),
                selling_price=float(row["selling_price"]),
                competitor_price=float(row["competitor_price"]),
                demand_level=row["demand_level"],
                seasonal_factor=float(row["seasonal_factor"]),
                discount_pct=float(row["discount_pct"]),
                revenue=float(row["revenue"]),
                inventory_at_time=int(row["inventory"]),
            )
            sales_records.append(sh)

        # Batch insert
        BATCH = 2000
        for i in range(0, len(sales_records), BATCH):
            db.bulk_save_objects(sales_records[i:i+BATCH])
            db.commit()
        print(f"[DB]    Inserted {len(sales_records):,} sales history records.")

        # Insert competitor prices (latest per product)
        latest_comp = df_sample.sort_values("date").groupby(["product_id","competitor_name"]).last().reset_index()
        for _, row in latest_comp.iterrows():
            db_pid = prod_map.get(int(row["product_id"]))
            if db_pid is None:
                continue
            cp = db_models.CompetitorPrice(
                product_id=db_pid,
                competitor_name=row["competitor_name"],
                price=float(row["competitor_price"]),
            )
            db.add(cp)
        db.commit()
        print(f"[DB]    Inserted competitor prices.")

        # Seed some initial alerts
        low_inv_products = db.query(db_models.Product).filter(db_models.Product.inventory < 30).all()
        for prod in low_inv_products:
            alert = db_models.Alert(
                product_id=prod.id,
                alert_type="LOW_INVENTORY",
                severity="High",
                message=f"{prod.name} has only {prod.inventory} units remaining.",
                recommended_action="Raise price by 10-15% and initiate restock order.",
            )
            db.add(alert)
        db.commit()
        print(f"[DB]    Seeded {len(low_inv_products)} inventory alerts.")

    finally:
        db.close()


def save_model_metrics_to_db(all_metrics: dict):
    """Store model training metrics in the DB."""
    from database.db import SessionLocal
    from database import models as db_models
    from datetime import datetime

    db = SessionLocal()
    try:
        db.query(db_models.ModelInfo).delete()
        db.commit()

        for task_key, task_label in [("price_prediction","price_prediction"),
                                      ("demand_forecasting","demand_forecast")]:
            task_m = all_metrics.get(task_key, {})
            is_best_set = False
            for model_name, m in task_m.items():
                is_best = not is_best_set and m.get("r2", 0) == max(
                    v.get("r2", 0) for v in task_m.values()
                )
                mi = db_models.ModelInfo(
                    model_name=model_name,
                    task=task_label,
                    mae=m.get("mae"),
                    mse=m.get("mse"),
                    rmse=m.get("rmse"),
                    r2=m.get("r2"),
                    is_active=is_best,
                )
                db.add(mi)
                if is_best:
                    is_best_set = True
        db.commit()
        print("[DB]    Model metrics saved to database.")
    finally:
        db.close()


def main():
    banner()
    parser = argparse.ArgumentParser(description="PricePulse Initializer")
    parser.add_argument("--retrain", action="store_true", help="Force retrain models")
    parser.add_argument("--init-only", action="store_true", help="Init DB and train, then exit")
    parser.add_argument("--seed-only", action="store_true", help="Only seed DB")
    args = parser.parse_args()

    # 1. Init DB
    init_database()

    # 2. Generate / load data
    from ml.feature_engineering import generate_synthetic_data
    import os
    csv_path = os.path.join(ROOT, "data", "synthetic_sales.csv")
    if os.path.exists(csv_path):
        import pandas as pd
        print("[DATA]  Loading cached synthetic data â€¦")
        df = pd.read_csv(csv_path, parse_dates=["date"])
        print(f"[DATA]  Loaded {len(df):,} rows.")
    else:
        print("[DATA]  Generating synthetic data â€¦")
        df = generate_synthetic_data(n_days=730)
        os.makedirs(os.path.join(ROOT, "data"), exist_ok=True)
        df.to_csv(csv_path, index=False)
        print(f"[DATA]  Saved {len(df):,} rows â†’ {csv_path}")

    # 3. Seed DB
    if not args.seed_only or True:  # always seed
        seed_database(df)

    if args.seed_only:
        print("\n[DONE]  Seed-only run complete.")
        return

    # 4. Train models (unless exist and not forced)
    from ml.train_model import models_exist, run_training_pipeline

    if models_exist() and not args.retrain:
        print("[ML]    Trained models found â€” skipping training.")
        print("[ML]    Use --retrain to force retraining.")
        import json
        metrics_path = os.path.join(ROOT, "models", "metrics.json")
        if os.path.exists(metrics_path):
            with open(metrics_path) as f:
                all_metrics = json.load(f)
        else:
            all_metrics = {}
    else:
        all_metrics = run_training_pipeline(save_data=False)
        save_model_metrics_to_db(all_metrics)

    print("""
+======================================================+
|  PricePulse initialization complete!                 |
|                                                      |
|  Start the application:                              |
|                                                      |
|  Terminal 1 (Backend API):                           |
|    uvicorn backend.main:app --reload --port 8000     |
|                                                      |
|  Terminal 2 (Frontend Dashboard):                    |
|    streamlit run frontend/dashboard.py               |
|                                                      |
|  Then open: http://localhost:8501                    |
|  API Docs:  http://localhost:8000/docs               |
+======================================================+
""")


if __name__ == "__main__":
    main()

