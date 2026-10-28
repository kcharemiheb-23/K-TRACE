#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.preprocessing import LabelEncoder

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

TRAIN = ROOT / "artifacts" / "phase8" / "output" / "split_train_runs.csv"
VAL = ROOT / "artifacts" / "phase8" / "output" / "split_val_runs.csv"
TEST = ROOT / "artifacts" / "phase8" / "output" / "split_test_runs.csv"
OUT = ROOT / "artifacts" / "phase9_v2" / "output" / "seed_robustness_results.csv"

META_COLS = ["run_id","class_label","scenario_family","subtype","intensity","benign_type","binary_label"]

def select_xy(df, task):
    y = df["binary_label"] if task == "binary" else df["class_label"]
    X = df[[c for c in df.columns if c not in META_COLS]]
    return X, y

rows = []
for task in ["binary", "multiclass"]:
    df_train = pd.read_csv(TRAIN)
    df_val = pd.read_csv(VAL)
    df_test = pd.read_csv(TEST)

    df_trainval = pd.concat([df_train, df_val], axis=0).reset_index(drop=True)

    X_trainval, y_trainval = select_xy(df_trainval, task)
    X_test, y_test = select_xy(df_test, task)

    le = LabelEncoder()
    y_trainval_enc = le.fit_transform(y_trainval)
    y_test_enc = le.transform(y_test)

    for seed in [1, 7, 21, 42, 99]:
        clf = RandomForestClassifier(
            n_estimators=400,
            random_state=seed,
            class_weight="balanced_subsample"
        )
        clf.fit(X_trainval, y_trainval_enc)
        pred = clf.predict(X_test)

        row = {
            "task": task,
            "seed": seed,
            "accuracy": accuracy_score(y_test_enc, pred),
            "precision_macro": precision_score(y_test_enc, pred, average="macro", zero_division=0),
            "recall_macro": recall_score(y_test_enc, pred, average="macro", zero_division=0),
            "f1_macro": f1_score(y_test_enc, pred, average="macro", zero_division=0),
        }

        if task == "binary":
            row["precision_binary"] = precision_score(y_test_enc, pred, average="binary", zero_division=0)
            row["recall_binary"] = recall_score(y_test_enc, pred, average="binary", zero_division=0)
            row["f1_binary"] = f1_score(y_test_enc, pred, average="binary", zero_division=0)

        rows.append(row)

pd.DataFrame(rows).to_csv(OUT, index=False)
print("WROTE:", OUT)
