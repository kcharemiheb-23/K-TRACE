#!/usr/bin/env python3
import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

TRAIN = ROOT / "artifacts" / "phase8" / "output" / "split_train_runs.csv"
VAL = ROOT / "artifacts" / "phase8" / "output" / "split_val_runs.csv"
TEST = ROOT / "artifacts" / "phase8" / "output" / "split_test_runs.csv"

OUTDIR = ROOT / "artifacts" / "phase9_v2" / "output"
PLOTDIR = ROOT / "artifacts" / "phase9_v2" / "plots"
REPORTDIR = ROOT / "artifacts" / "phase9_v2" / "reports"

META_COLS = ["run_id","class_label","scenario_family","subtype","intensity","benign_type","binary_label"]

def load_rows(path):
    return pd.read_csv(path)

def select_xy(df, task):
    y = df["binary_label"].copy() if task == "binary" else df["class_label"].copy()
    feature_cols = [c for c in df.columns if c not in META_COLS]
    X = df[feature_cols].copy()
    return X, y, feature_cols

def build_models():
    return {
        "LogisticRegression": Pipeline([
            ("scale", StandardScaler()),
            ("clf", LogisticRegression(max_iter=3000, class_weight="balanced", random_state=42))
        ]),
        "DecisionTree": DecisionTreeClassifier(random_state=42, class_weight="balanced"),
        "RandomForest": RandomForestClassifier(n_estimators=400, random_state=42, class_weight="balanced_subsample"),
        "ExtraTrees": ExtraTreesClassifier(n_estimators=400, random_state=42, class_weight="balanced_subsample"),
        "HistGradientBoosting": HistGradientBoostingClassifier(random_state=42, max_depth=8),
        "SVC": Pipeline([
            ("scale", StandardScaler()),
            ("clf", SVC(probability=True, class_weight="balanced", random_state=42))
        ]),
        "GaussianNB": GaussianNB(),
    }

def save_confusion_matrix(cm, labels, out_png, title):
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(cm)
    ax.set_title(title)
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right")
    ax.set_yticklabels(labels)
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, cm[i, j], ha="center", va="center")
    fig.colorbar(im)
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()

def save_bar_plot(df, xcol, ycol, out_png, title):
    fig, ax = plt.subplots(figsize=(10, 5))
    order = df.sort_values(ycol, ascending=False)
    ax.bar(order[xcol], order[ycol])
    ax.set_title(title)
    ax.set_ylabel(ycol)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()

def get_feature_importance(model, feature_cols):
    clf = model
    if hasattr(model, "named_steps"):
        clf = model.named_steps["clf"]

    if hasattr(clf, "feature_importances_"):
        return pd.Series(clf.feature_importances_, index=feature_cols).sort_values(ascending=False)

    if hasattr(clf, "coef_"):
        vals = np.abs(clf.coef_)
        if vals.ndim == 2:
            vals = vals.mean(axis=0)
        return pd.Series(vals, index=feature_cols).sort_values(ascending=False)

    return None

def save_feature_importance(series, out_png, title, top_n=20):
    top = series.head(top_n)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top.index[::-1], top.values[::-1])
    ax.set_title(title)
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()

def save_grouped_source_importance(series, out_png, title):
    groups = {"Envoy": 0.0, "Falco": 0.0, "Prometheus": 0.0, "Other": 0.0}
    for k, v in series.items():
        if k.startswith("envoy_") or k.startswith("status_") or k.startswith("method_") or k.startswith("payload_") or k.startswith("pod_"):
            groups["Envoy"] += float(v)
        elif k.startswith("falco_"):
            groups["Falco"] += float(v)
        elif k.startswith("prom_"):
            groups["Prometheus"] += float(v)
        else:
            groups["Other"] += float(v)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.bar(groups.keys(), groups.values())
    ax.set_title(title)
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()

def maybe_predict_proba(model, X):
    if hasattr(model, "predict_proba"):
        return model.predict_proba(X)
    return None

def save_binary_curves(model, X, y_enc, model_name):
    proba = maybe_predict_proba(model, X)
    if proba is None:
        return None

    scores = proba[:, 1]

    fpr, tpr, _ = roc_curve(y_enc, scores)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(fpr, tpr)
    ax.plot([0, 1], [0, 1], linestyle="--")
    ax.set_title(f"Binary ROC - {model_name}")
    ax.set_xlabel("FPR")
    ax.set_ylabel("TPR")
    plt.tight_layout()
    plt.savefig(PLOTDIR / f"binary_roc_{model_name}.png", dpi=200)
    plt.close()

    prec, rec, _ = precision_recall_curve(y_enc, scores)
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot(rec, prec)
    ax.set_title(f"Binary PR Curve - {model_name}")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    plt.tight_layout()
    plt.savefig(PLOTDIR / f"binary_pr_{model_name}.png", dpi=200)
    plt.close()

    return {
        "roc_auc": roc_auc_score(y_enc, scores),
        "pr_auc": average_precision_score(y_enc, scores),
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task", choices=["binary", "multiclass"], required=True)
    args = parser.parse_args()
    task = args.task

    df_train = load_rows(TRAIN)
    df_val = load_rows(VAL)
    df_test = load_rows(TEST)

    X_train, y_train, feature_cols = select_xy(df_train, task)
    X_val, y_val, _ = select_xy(df_val, task)
    X_test, y_test, _ = select_xy(df_test, task)

    le = LabelEncoder()
    y_train_enc = le.fit_transform(y_train)
    y_val_enc = le.transform(y_val)
    y_test_enc = le.transform(y_test)
    labels = list(le.classes_)

    models = build_models()
    rows = []
    fitted_val_models = {}

    for name, model in models.items():
        model.fit(X_train, y_train_enc)
        fitted_val_models[name] = model
        pred_val = model.predict(X_val)

        row = {
            "task": task,
            "model": name,
            "val_accuracy": accuracy_score(y_val_enc, pred_val),
            "val_precision_macro": precision_score(y_val_enc, pred_val, average="macro", zero_division=0),
            "val_recall_macro": recall_score(y_val_enc, pred_val, average="macro", zero_division=0),
            "val_f1_macro": f1_score(y_val_enc, pred_val, average="macro", zero_division=0),
        }

        if task == "binary":
            row["val_precision_binary"] = precision_score(y_val_enc, pred_val, average="binary", zero_division=0)
            row["val_recall_binary"] = recall_score(y_val_enc, pred_val, average="binary", zero_division=0)
            row["val_f1_binary"] = f1_score(y_val_enc, pred_val, average="binary", zero_division=0)

            proba_stats = save_binary_curves(model, X_val, y_val_enc, name)
            if proba_stats is not None:
                row["val_roc_auc"] = proba_stats["roc_auc"]
                row["val_pr_auc"] = proba_stats["pr_auc"]
            else:
                row["val_roc_auc"] = np.nan
                row["val_pr_auc"] = np.nan

        rows.append(row)

    results_df = pd.DataFrame(rows)
    results_df.to_csv(OUTDIR / f"{task}_validation_metrics_v2.csv", index=False)

    if task == "binary":
        save_bar_plot(results_df, "model", "val_f1_binary", PLOTDIR / "binary_model_comparison_f1.png", "Binary Model Comparison (F1)")
        save_bar_plot(results_df, "model", "val_roc_auc", PLOTDIR / "binary_model_comparison_roc_auc.png", "Binary Model Comparison (ROC-AUC)")
    else:
        save_bar_plot(results_df, "model", "val_f1_macro", PLOTDIR / "multiclass_model_comparison_macro_f1.png", "Multiclass Model Comparison (Macro F1)")

    primary = "val_f1_binary" if task == "binary" else "val_f1_macro"
    best_name = results_df.sort_values(primary, ascending=False).iloc[0]["model"]
    best_model = build_models()[best_name]

    df_trainval = pd.concat([df_train, df_val], axis=0).reset_index(drop=True)
    X_trainval, y_trainval, feature_cols = select_xy(df_trainval, task)
    y_trainval_enc = le.fit_transform(y_trainval)
    y_test_enc = le.transform(y_test)

    best_model.fit(X_trainval, y_trainval_enc)
    pred_test = best_model.predict(X_test)

    report_txt = REPORTDIR / f"{task}_best_model_test_report_v2.txt"
    with open(report_txt, "w") as f:
        f.write(f"task: {task}\n")
        f.write(f"best_model: {best_name}\n\n")
        f.write(classification_report(y_test_enc, pred_test, target_names=list(le.classes_), zero_division=0))

    summary = {
        "task": task,
        "best_model": best_name,
        "test_accuracy": accuracy_score(y_test_enc, pred_test),
        "test_precision_macro": precision_score(y_test_enc, pred_test, average="macro", zero_division=0),
        "test_recall_macro": recall_score(y_test_enc, pred_test, average="macro", zero_division=0),
        "test_f1_macro": f1_score(y_test_enc, pred_test, average="macro", zero_division=0),
    }

    # Plot expansion: create confusion matrices for multiple models on TEST
    if task == "binary":
        plot_models = ["LogisticRegression", "DecisionTree", "RandomForest", "ExtraTrees", "SVC"]
    else:
        plot_models = ["DecisionTree", "RandomForest", "ExtraTrees", "HistGradientBoosting"]

    for model_name in plot_models:
        model = build_models()[model_name]
        model.fit(X_trainval, y_trainval_enc)
        pred = model.predict(X_test)
        cm = confusion_matrix(y_test_enc, pred)
        save_confusion_matrix(
            cm,
            labels=list(le.classes_),
            out_png=PLOTDIR / f"{task}_confusion_matrix_{model_name}.png",
            title=f"{task} confusion matrix - {model_name}"
        )

        if task == "binary":
            save_binary_curves(model, X_test, y_test_enc, model_name)

    # Best-model named clean PNGs
    cm = confusion_matrix(y_test_enc, pred_test)
    save_confusion_matrix(
        cm,
        labels=list(le.classes_),
        out_png=PLOTDIR / f"{task}_confusion_matrix_{best_name}.png",
        title=f"{task} confusion matrix - {best_name}"
    )

    fi = get_feature_importance(best_model, feature_cols)
    if fi is not None:
        save_feature_importance(fi, PLOTDIR / f"{task}_feature_importance_{best_name}.png", f"{task} top feature importance - {best_name}")
        save_grouped_source_importance(fi, PLOTDIR / f"{task}_source_importance_{best_name}.png", f"{task} grouped source importance - {best_name}")
        fi.head(50).to_csv(OUTDIR / f"{task}_top_feature_importance_{best_name}_v2.csv", header=["importance"])

    pred_df = pd.DataFrame({
        "run_id": df_test["run_id"],
        "true_label": y_test,
        "pred_label": le.inverse_transform(pred_test),
    })
    pred_df.to_csv(OUTDIR / f"{task}_test_predictions_{best_name}_v2.csv", index=False)

    if task == "binary":
        summary["test_precision_binary"] = precision_score(y_test_enc, pred_test, average="binary", zero_division=0)
        summary["test_recall_binary"] = recall_score(y_test_enc, pred_test, average="binary", zero_division=0)
        summary["test_f1_binary"] = f1_score(y_test_enc, pred_test, average="binary", zero_division=0)

        proba = maybe_predict_proba(best_model, X_test)
        if proba is not None:
            scores = proba[:, 1]
            summary["test_roc_auc"] = roc_auc_score(y_test_enc, scores)
            summary["test_pr_auc"] = average_precision_score(y_test_enc, scores)

    else:
        rep = classification_report(y_test_enc, pred_test, target_names=list(le.classes_), output_dict=True, zero_division=0)
        class_rows = []
        for label in le.classes_:
            class_rows.append({
                "class_label": label,
                "precision": rep[label]["precision"],
                "recall": rep[label]["recall"],
                "f1-score": rep[label]["f1-score"],
                "support": rep[label]["support"],
            })
        class_df = pd.DataFrame(class_rows)
        class_df.to_csv(OUTDIR / f"multiclass_per_class_metrics_{best_name}_v2.csv", index=False)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(class_df["class_label"], class_df["f1-score"])
        ax.set_title(f"Multiclass Per-Class F1 - {best_name}")
        ax.set_ylabel("F1-score")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(PLOTDIR / f"multiclass_per_class_f1_{best_name}.png", dpi=200)
        plt.close()

    pd.DataFrame([summary]).to_csv(OUTDIR / f"{task}_best_model_summary_v2.csv", index=False)

    print("TASK:", task)
    print("BEST_MODEL:", best_name)
    print("VALIDATION_CSV:", OUTDIR / f"{task}_validation_metrics_v2.csv")
    print("TEST_REPORT:", report_txt)

if __name__ == "__main__":
    main()
