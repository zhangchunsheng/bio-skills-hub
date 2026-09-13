#!/usr/bin/env python3
"""
protein-struct-viz：生成用于高亮特定蛋白质残基的 PyMOL 脚本。

用法：
    python main.py --pdb <pdb_file_or_id> --residues <residue_list> [options]

示例：
    python main.py --pdb 1mbn --residues "A:64:HIS,A:93:VAL" --style sticks --output result.pml
"""

import argparse
import sys
from pathlib import Path
from typing import List, Tuple, Optional


class PyMOLScriptGenerator:
    """生成用于蛋白质残基可视化的 PyMOL 脚本。"""

    # 预定义配色方案
    COLOR_SCHEMES = {
        "rainbow": "cmd.spectrum()",
        "chain": "cmd.color('chainbow', 'all')",
        "element": "util.cbc()",
        "secondary": "cmd.dss(); cmd.color('secondary', 'all')",
        "gray": "cmd.color('gray70', 'all')",
        "white": "cmd.color('white', 'all')",
        "blue_red": "cmd.spectrum('b', 'blue_red')",
    }

    # 用于高亮的标准残基颜色
    RESIDUE_COLORS = [
        "red", "blue", "green", "yellow", "magenta", "cyan",
        "orange", "salmon", "lime", "pink", "slate", "teal"
    ]

    def __init__(self, pdb_source: str, residues: List[str], style: str = "sticks",
                 color_scheme: str = "gray", highlight_colors: Optional[List[str]] = None,
                 output: str = "output.pml", ray_trace: bool = False):
        """
        初始化生成器。

        参数：
            pdb_source: PDB 文件路径或 PDB ID
            residues: 残基规格列表（chain:resnum:resname）
            style: 高亮残基的可视化样式
            color_scheme: 全局配色方案
            highlight_colors: 高亮残基使用的自定义颜色
            output: 输出脚本文件名
            ray_trace: 是否包含用于高质量图像的光线追踪命令
        """
        self.pdb_source = pdb_source
        self.residues = residues
        self.style = style
        self.color_scheme = color_scheme
        self.highlight_colors = highlight_colors or self.RESIDUE_COLORS
        self.output = output
        self.ray_trace = ray_trace

    def _parse_residue(self, residue_spec: str) -> Tuple[Optional[str], str, Optional[str]]:
        """
        解析残基规格字符串。

        支持的格式：
            - chain:resnum:resname（A:145:ASP）
            - chain:resnum（A:145）
            - resnum（145，默认使用链 A 或第一条链）

        返回：
            (chain, resnum, resname) 元组
        """
        parts = residue_spec.split(":")

        if len(parts) == 3:
            return parts[0], parts[1], parts[2]
        elif len(parts) == 2:
            return parts[0], parts[1], None
        elif len(parts) == 1:
            return None, parts[0], None
        else:
            raise ValueError(f"无效的残基规格：{residue_spec}")

    def _generate_selection_string(self, chain: Optional[str], resnum: str,
                                   resname: Optional[str]) -> str:
        """为某个残基生成 PyMOL 选择字符串。"""
        parts = []
        if chain:
            parts.append(f"chain {chain}")
        parts.append(f"resi {resnum}")
        if resname:
            parts.append(f"resn {resname}")
        return " and ".join(parts)

    def _get_load_command(self) -> str:
        """生成结构加载命令。"""
        # 判断 pdb_source 是否为 PDB ID（4 个字符的字母数字组合）
        if len(self.pdb_source) == 4 and self.pdb_source.isalnum():
            return f"fetch {self.pdb_source}, async=0"
        else:
            return f"load {self.pdb_source}"

    def generate_script(self) -> str:
        """生成完整的 PyMOL 脚本。"""
        lines = []

        # 头部信息
        lines.append("# 由 protein-struct-viz 生成的 PyMOL 脚本")
        lines.append(f"# 目标结构: {self.pdb_source}")
        lines.append(f"# 高亮残基: {', '.join(self.residues)}")
        lines.append("")

        # 加载结构
        lines.append("# 加载结构")
        lines.append(self._get_load_command())
        lines.append("")

        # 基本设置
        lines.append("# 可视化设置")
        lines.append("bg_color white")
        lines.append("set antialias, 2")
        lines.append("set ray_shadows, 0")
        lines.append("")

        # 全局表示样式
        lines.append("# 全局表示样式")
        lines.append("hide everything")
        lines.append("show cartoon")
        lines.append("")

        # 应用配色方案
        lines.append("# 配色方案")
        if self.color_scheme in self.COLOR_SCHEMES:
            lines.append(self.COLOR_SCHEMES[self.color_scheme])
        else:
            lines.append(f"cmd.color('{self.color_scheme}', 'all')")
        lines.append("")

        # 高亮指定残基
        lines.append("# 高亮指定残基")
        for i, residue_spec in enumerate(self.residues):
            try:
                chain, resnum, resname = self._parse_residue(residue_spec)
                selection = self._generate_selection_string(chain, resnum, resname)
                sel_name = f"residue_{i+1}"
                color = self.highlight_colors[i % len(self.highlight_colors)]

                lines.append(f"# {residue_spec}")
                lines.append(f"select {sel_name}, {selection}")
                lines.append(f"show {self.style}, {sel_name}")
                lines.append(f"color {color}, {sel_name}")
                lines.append("")
            except ValueError as e:
                lines.append(f"# 解析 {residue_spec} 出错: {e}")
                lines.append("")

        # 将视角居中到高亮残基
        if self.residues:
            lines.append("# 将视角居中到高亮残基")
            lines.append("center sele")
            lines.append("zoom sele, 10")
            lines.append("")

        # 用于高质量渲染的光线追踪
        if self.ray_trace:
            lines.append("# 高质量渲染")
            lines.append("set ray_trace_mode, 1")
            lines.append("set ray_trace_gain, 0.01")
            lines.append("ray 2400, 2400")
            lines.append("")

        # 残基标签选项
        lines.append("# 可选：残基标签（取消注释以启用）")
        lines.append("# label sele and name CA, '%s-%s' % (resn, resi)")
        lines.append("")

        return "\n".join(lines)

    def save(self) -> str:
        """生成脚本并保存到文件。"""
        script_content = self.generate_script()
        output_path = Path(self.output)
        output_path.write_text(script_content)
        return str(output_path.absolute())


def main():
    parser = argparse.ArgumentParser(
        description="生成用于蛋白质残基可视化的 PyMOL 脚本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 用棒状（sticks）表示高亮指定残基
  python main.py --pdb 1mbn --residues "A:64:HIS,A:93:VAL" --style sticks

  # 使用 PDB ID 和自定义配色方案
  python main.py --pdb 1abc --residues "B:23:LYS,B:45:ASP" --color_scheme chain

  # 生成高质量图像脚本
  python main.py --pdb protein.pdb --residues "156,202,245" --ray_trace --output hq.pml
        """
    )

    parser.add_argument("--pdb", required=True,
                        help="PDB 文件路径或 PDB ID（4 字母代码）")
    parser.add_argument("--residues", required=True,
                        help="逗号分隔的残基规格（例如：'A:64:HIS,A:93:VAL'）")
    parser.add_argument("--style", default="sticks",
                        choices=["sticks", "spheres", "surface", "cartoon", "lines", "mesh"],
                        help="高亮残基的表示样式（默认：sticks）")
    parser.add_argument("--color_scheme", default="gray",
                        help="全局配色方案：rainbow、chain、element、secondary、gray、white，或颜色名称")
    parser.add_argument("--output", default="output.pml",
                        help="输出脚本文件名（默认：output.pml）")
    parser.add_argument("--ray_trace", action="store_true",
                        help="包含用于高质量图像的光线追踪命令")

    args = parser.parse_args()

    # 解析残基列表
    residue_list = [r.strip() for r in args.residues.split(",")]

    # 创建生成器
    generator = PyMOLScriptGenerator(
        pdb_source=args.pdb,
        residues=residue_list,
        style=args.style,
        color_scheme=args.color_scheme,
        output=args.output,
        ray_trace=args.ray_trace
    )

    # 生成并保存脚本
    try:
        output_path = generator.save()
        print(f"PyMOL 脚本生成成功: {output_path}")
        print(f"\n使用方法:")
        print(f"  pymol {args.output}")
        print(f"  # 或在 PyMOL 内部执行:")
        print(f"  @ {args.output}")
    except Exception as e:
        print(f"生成脚本时出错: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
