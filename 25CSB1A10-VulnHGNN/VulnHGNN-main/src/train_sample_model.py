"""Train a small demonstration model from the bundled C test files."""

import argparse
import os
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import torch
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader

from ir_parser import parse_ll_file
from pyg_dataset import build_function_graph, NUM_CLASSES
from pyg_model import build_pyg_model


def label_for_file(filename: str) -> np.ndarray:
    label = np.zeros(NUM_CLASSES, dtype=np.float32)
    if "test_01_clean" in filename:
        label[0] = 1.0
        return label
    for marker, index in (("CWE476", 1), ("CWE191", 2), ("CWE190", 3), ("CWE369", 4)):
        if marker in filename.upper():
            label[index] = 1.0
    return label


def build_graphs(test_dir: Path) -> list[Data]:
    graphs = []
    for source_path in sorted(test_dir.glob("*.c")):
        with tempfile.NamedTemporaryFile(suffix=".ll", delete=False) as temp:
            ll_path = Path(temp.name)
        try:
            result = subprocess.run(
                ["clang", "-S", "-emit-llvm", "-g", "-O0", "-Xclang",
                 "-disable-O0-optnone", "-w", "-o", str(ll_path), str(source_path)],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(result.stderr[:400])
            ir_data = parse_ll_file(str(ll_path))
            label = label_for_file(source_path.name)
            for function in ir_data.get("functions", []):
                if function.get("is_declaration"):
                    continue
                blocks = function.get("blocks", [])
                if sum(len(block.get("instructions", [])) for block in blocks) < 3:
                    continue
                graph = build_function_graph(function, label)
                if graph is not None and graph.edge_index.size(1) > 0:
                    graphs.append(graph)
        finally:
            if ll_path.exists():
                ll_path.unlink()
    return graphs


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--test-dir", type=Path, default=Path("test_files"))
    parser.add_argument("--out", type=Path, default=Path("results/pyg_gnn_v9"))
    parser.add_argument("--epochs", type=int, default=80)
    args = parser.parse_args()

    torch.manual_seed(42)
    np.random.seed(42)
    graphs = build_graphs(args.test_dir)
    if not graphs:
        raise RuntimeError("No graphs were built from the test files.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    loader = DataLoader(graphs, batch_size=min(8, len(graphs)), shuffle=True)
    model = build_pyg_model().to(device)
    labels = torch.cat([graph.y for graph in graphs], dim=0)
    positives = labels.sum(dim=0)
    negatives = len(graphs) - positives
    weights = (negatives / positives.clamp(min=1)).clamp(max=3.0).to(device)
    criterion = torch.nn.BCEWithLogitsLoss(pos_weight=weights)
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-3, weight_decay=1e-4)

    args.out.mkdir(parents=True, exist_ok=True)
    best_loss = float("inf")
    for epoch in range(1, args.epochs + 1):
        model.train()
        total_loss = 0.0
        for batch in loader:
            batch = batch.to(device)
            optimizer.zero_grad()
            logits = model(batch.x, batch.edge_index, batch.edge_attr, batch.batch)
            loss = criterion(logits, batch.y.squeeze(1))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()
            total_loss += loss.item()
        average_loss = total_loss / len(loader)
        if average_loss < best_loss:
            best_loss = average_loss
            torch.save({
                "epoch": epoch,
                "model_state": model.state_dict(),
                "val_f1": 0.0,
                "args": vars(args),
            }, args.out / "best_pyg_model.pt")
        if epoch == 1 or epoch % 10 == 0:
            print(f"epoch={epoch:03d} loss={average_loss:.4f}")

    print(f"Built {len(graphs)} graphs.")
    print(f"Saved demonstration model to {args.out / 'best_pyg_model.pt'}")


if __name__ == "__main__":
    main()