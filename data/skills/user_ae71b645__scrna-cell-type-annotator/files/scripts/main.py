#!/usr/bin/env python3
"""
scRNA 细胞类型注释器
自动注释单细胞RNA数据中的细胞簇。
"""

import argparse
import pandas as pd


class CellTypeAnnotator:
    """从 scRNA 数据中注释细胞类型。"""

    MARKER_DATABASE = {
        "CD4 T cell": ["CD3D", "CD4", "IL7R"],
        "CD8 T cell": ["CD3D", "CD8A", "CD8B"],
        "B cell": ["CD79A", "CD79B", "MS4A1"],
        "Monocyte": ["CD14", "LYZ", "S100A9"],
        "NK cell": ["NKG7", "GNLY", "KLRD1"],
        "Dendritic cell": ["FCER1A", "CST3", "CLEC10A"]
    }

    def score_cell_type(self, cluster_markers, cell_type_markers):
        """评分细胞簇与细胞类型的匹配程度。"""
        matches = sum(1 for m in cell_type_markers if m in cluster_markers)
        return matches / len(cell_type_markers)

    def annotate_cluster(self, cluster_markers, top_n=3):
        """根据标志基因注释细胞簇。"""
        scores = []

        for cell_type, markers in self.MARKER_DATABASE.items():
            score = self.score_cell_type(cluster_markers, markers)
            scores.append((cell_type, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_n]

    def annotate_all_clusters(self, cluster_markers_dict):
        """注释所有细胞簇。"""
        annotations = {}

        for cluster_id, markers in cluster_markers_dict.items():
            annotations[cluster_id] = self.annotate_cluster(markers)

        return annotations


def main():
    parser = argparse.ArgumentParser(description="scRNA Cell Type Annotator")
    parser.add_argument("--markers", "-m", help="CSV with cluster markers")
    parser.add_argument("--demo", action="store_true", help="Run demo")

    args = parser.parse_args()

    annotator = CellTypeAnnotator()

    if args.demo:
        # 演示数据
        cluster_markers = {
            "Cluster 0": ["CD3D", "CD4", "IL7R", "LTB"],
            "Cluster 1": ["CD79A", "CD79B", "MS4A1"],
            "Cluster 2": ["CD14", "LYZ", "S100A9"]
        }

        annotations = annotator.annotate_all_clusters(cluster_markers)

        print(f"\n{'='*60}")
        print("CELL TYPE ANNOTATIONS")
        print(f"{'='*60}\n")

        for cluster, predictions in annotations.items():
            print(f"{cluster}:")
            for cell_type, score in predictions:
                print(f"  {cell_type}: {score:.2f}")
            print()

        print(f"{'='*60}\n")
    else:
        print("Use --demo to see example output")


if __name__ == "__main__":
    main()
