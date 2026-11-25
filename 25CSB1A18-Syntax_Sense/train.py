
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import sys
import os

from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import GroupShuffleSplit
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix
)


INPUT_CSV     = "features.csv"
MODEL_OUT     = "model.pkl"
SCALER_OUT    = "scaler.pkl"
LABEL_ENC_OUT = "label_encoder.pkl"
CM_OUT        = "confusion_matrix.png"
FI_OUT        = "feature_importance.png"
RANDOM_STATE  = 42
TEST_SIZE     = 0.15
VAL_SIZE      = 0.15


print("=" * 60)
print("  RANDOM FOREST — C++ SYNTAX ERROR CLASSIFIER")
print("=" * 60)

if not os.path.exists(INPUT_CSV):
    print(f"ERROR: {INPUT_CSV} not found.")
    sys.exit(1)

df = pd.read_csv(INPUT_CSV)
print(f"\n[INFO] Loaded {INPUT_CSV}  shape={df.shape}")

print(f"\n[INFO] Class distribution:")
for cls, cnt in df["label"].value_counts().sort_index().items():
    print(f"        {cls:<30} : {cnt}")

feature_cols = [c for c in df.columns if c not in ("file_name", "label")]
X = df[feature_cols].values
y = df["label"].values


# Warning-only check: repeated vectors can make a dataset appear larger than
# its effective feature diversity.
unique_vector_count = len(df[feature_cols].drop_duplicates())
unique_vector_ratio = unique_vector_count / len(df)
unique_vectors_per_label = df.groupby("label")[feature_cols].apply(
    lambda label_features: len(label_features.drop_duplicates())
)

print("\n[INFO] Feature diversity check (warning only):")
print(f"        Total rows                 : {len(df)}")
print(f"        Unique feature vectors     : {unique_vector_count}")
for label, vector_count in unique_vectors_per_label.sort_index().items():
    print(f"        {label:<30} : {vector_count} unique vector(s)")
    if vector_count == 1:
        print(f"[WARNING] {label} has only one unique feature vector.")

if unique_vector_ratio < 0.10:
    print(
        "[WARNING] Overall feature diversity is suspiciously low: "
        f"{unique_vector_count}/{len(df)} unique vectors "
        f"({unique_vector_ratio:.2%})."
    )


def source_family_id(file_name, label):
    """Remove the final dataset label suffix from a generated filename."""
    stem = os.path.splitext(os.path.basename(file_name))[0]
    suffix = f"_{label}"
    if not stem.endswith(suffix):
        raise ValueError(f"Filename does not end with its label suffix: {file_name}")
    return stem[:-len(suffix)]


groups = np.array([
    source_family_id(file_name, label)
    for file_name, label in zip(df["file_name"], y)
])

le = LabelEncoder()
y_enc = le.fit_transform(y)

print(f"\n[INFO] Features : {len(feature_cols)}")
print(f"[INFO] Classes  : {list(le.classes_)}")


train_val_splitter = GroupShuffleSplit(
    n_splits=1, test_size=TEST_SIZE, random_state=RANDOM_STATE
)
train_val_idx, test_idx = next(train_val_splitter.split(X, y_enc, groups))

val_rel = VAL_SIZE / (1 - TEST_SIZE)
train_splitter = GroupShuffleSplit(
    n_splits=1, test_size=val_rel, random_state=RANDOM_STATE
)
train_rel_idx, val_rel_idx = next(train_splitter.split(
    X[train_val_idx], y_enc[train_val_idx], groups[train_val_idx]
))

train_idx = train_val_idx[train_rel_idx]
val_idx = train_val_idx[val_rel_idx]

X_train, X_val, X_test = X[train_idx], X[val_idx], X[test_idx]
y_train, y_val, y_test = y_enc[train_idx], y_enc[val_idx], y_enc[test_idx]

train_families = set(groups[train_idx])
val_families = set(groups[val_idx])
test_families = set(groups[test_idx])
assert train_families.isdisjoint(val_families)
assert train_families.isdisjoint(test_families)
assert val_families.isdisjoint(test_families)


def feature_vectors(indices):
    return {tuple(row) for row in X[indices]}


train_vectors = feature_vectors(train_idx)
val_vectors = feature_vectors(val_idx)
test_vectors = feature_vectors(test_idx)
duplicate_vector_overlaps = {
    "train/validation": train_vectors & val_vectors,
    "train/test": train_vectors & test_vectors,
    "validation/test": val_vectors & test_vectors,
}

print(f"\n[INFO] Split → Train:{len(X_train)}  Val:{len(X_val)}  Test:{len(X_test)}")
print(
    "[INFO] Families → "
    f"Train:{len(train_families)}  Val:{len(val_families)}  Test:{len(test_families)}"
)
for split_pair, overlaps in duplicate_vector_overlaps.items():
    if overlaps:
        print(
            f"[WARNING] {len(overlaps)} duplicate feature vector(s) cross "
            f"the {split_pair} split. Family leakage is prevented, but feature "
            "duplication remains."
        )


scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_val_s   = scaler.transform(X_val)
X_test_s  = scaler.transform(X_test)


print(f"\n[INFO] Training Random Forest (200 trees)...")
rf = RandomForestClassifier(
    n_estimators=200,
    max_depth=None,
    max_features="sqrt",
    random_state=RANDOM_STATE,
    n_jobs=-1
)
rf.fit(X_train_s, y_train)
print(f"[INFO] Done.")


val_acc  = accuracy_score(y_val,  rf.predict(X_val_s))
test_acc = accuracy_score(y_test, rf.predict(X_test_s))

print(f"\n{'=' * 60}")
print(f"  Validation Accuracy : {val_acc  * 100:.2f}%")
print(f"  Test Accuracy       : {test_acc * 100:.2f}%")
print(f"{'=' * 60}")

print(f"\n[INFO] Per-class report (Test):")
print(classification_report(
    y_test, rf.predict(X_test_s),
    target_names=le.classes_
))


cm = confusion_matrix(y_test, rf.predict(X_test_s))
plt.figure(figsize=(14, 10))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=le.classes_, yticklabels=le.classes_)
plt.title("Confusion Matrix — Random Forest\nC++ Syntax Error Classifier", fontsize=14)
plt.xlabel("Predicted", fontsize=11)
plt.ylabel("True", fontsize=11)
plt.xticks(rotation=45, ha="right", fontsize=8)
plt.yticks(rotation=0, fontsize=8)
plt.tight_layout()
plt.savefig(CM_OUT, dpi=150)
plt.close()
print(f"[INFO] Saved → {CM_OUT}")


fi_df = pd.DataFrame({
    "feature": feature_cols,
    "importance": rf.feature_importances_
}).sort_values("importance", ascending=False)

print(f"\n[INFO] Top 10 features:")
for _, row in fi_df.head(10).iterrows():
    print(f"        {row['feature']:<35} : {row['importance']:.4f}")

top20 = fi_df.head(20)
plt.figure(figsize=(12, 7))
plt.barh(top20["feature"][::-1], top20["importance"][::-1], color="steelblue")
plt.xlabel("Importance Score")
plt.title("Top 20 Feature Importances — Random Forest")
plt.tight_layout()
plt.savefig(FI_OUT, dpi=150)
plt.close()
print(f"[INFO] Saved → {FI_OUT}")


joblib.dump(rf, MODEL_OUT)
joblib.dump(scaler, SCALER_OUT)
joblib.dump(le, LABEL_ENC_OUT)

print(f"\n[INFO] model.pkl         → saved")
print(f"[INFO] scaler.pkl        → saved")
print(f"[INFO] label_encoder.pkl → saved")

print(f"\n{'=' * 60}")
print(f"  DONE  |  Test Accuracy: {test_acc * 100:.2f}%")
print(f"{'=' * 60}")
print(f"\nNext: python3 predict.py your_file.cpp")
