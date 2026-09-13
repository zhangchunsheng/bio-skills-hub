#!/usr/bin/env python3
"""
Mind Map Generator Script
Generates hierarchical mind maps as PNG images using Graphviz.

Usage:
    python generate_mindmap.py "Central Topic" "Branch1:Item1,Item2" "Branch2:Item1,Item2" [-o output.png] [-c blues]

Dependencies:
    - Graphviz (system package): https://graphviz.gitlab.io/download/
    - Python packages: pip install graphviz
"""

import argparse
import os
import sys

try:
    from graphviz import Digraph
except ImportError:
    print("Error: graphviz Python package not installed.")
    print("Please run: pip install graphviz")
    sys.exit(1)


# Color schemes for mind map branches
COLOR_SCHEMES = {
    "blues": {
        "center": "#1a5276",
        "level1": "#2980b9",
        "level2": "#5dade2",
        "bg": "#f8fbfe"
    },
    "greens": {
        "center": "#1e8449",
        "level1": "#27ae60",
        "level2": "#58d68d",
        "bg": "#f4fcf6"
    },
    "warm": {
        "center": "#c0392b",
        "level1": "#e74c3c",
        "level2": "#f1948a",
        "bg": "#fef9f7"
    },
    "purple": {
        "center": "#6c3483",
        "level1": "#8e44ad",
        "level2": "#bb8fce",
        "bg": "#f8f4fc"
    },
    "mono": {
        "center": "#2c3e50",
        "level1": "#34495e",
        "level2": "#7f8c8d",
        "bg": "#ffffff"
    }
}


def parse_branch(branch_str):
    """
    Parse branch string in format 'BranchName:Item1,Item2,Item3'
    Returns tuple: (branch_name, [item1, item2, ...])
    """
    if ":" not in branch_str:
        return branch_str.strip(), []
    
    branch_name, items_str = branch_str.split(":", 1)
    items = [item.strip() for item in items_str.split(",") if item.strip()]
    return branch_name.strip(), items


def create_mindmap(topic, branches, output_path="mindmap.png", color_scheme="blues"):
    """
    Create a mind map diagram and save as PNG.
    
    Args:
        topic: Central topic text
        branches: List of branch strings in format 'BranchName:Item1,Item2,...'
        output_path: Output file path
        color_scheme: Color scheme name
    """
    # Get color scheme
    colors = COLOR_SCHEMES.get(color_scheme, COLOR_SCHEMES["blues"])
    
    # Create directed graph
    dot = Digraph(comment='Mind Map', format='png', engine='dot')
    
    # Graph settings
    dot.attr(
        rankdir='TB',
        splines='ortho',
        nodesep='0.6',
        ranksep='0.8',
        fontname='Microsoft YaHei, SimHei, Arial, sans-serif',
        bgcolor=colors["bg"],
        pad='0.5',
        dpi='150'
    )
    
    # Node settings
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='white')
    
    # Create center node
    dot.node('center', topic, 
             fillcolor=colors["center"], 
             fontcolor='white',
             fontsize='18',
             fontname='Microsoft YaHei, SimHei, Arial, sans-serif',
             penwidth='2')
    
    # Track all nodes for layout
    with dot.subgraph() as s:
        s.attr(rank='same')
        s.node('center', topic, fillcolor=colors["center"], fontcolor='white', fontsize='18')
    
    # Create branches
    for branch in branches:
        branch_name, items = parse_branch(branch)
        
        if not branch_name:
            continue
        
        # Create branch node
        branch_id = f"branch_{branch_name}"
        dot.node(branch_id, branch_name,
                fillcolor=colors["level1"],
                fontcolor='white',
                fontsize='14',
                penwidth='1.5')
        
        # Connect to center
        dot.edge('center', branch_id, color=colors["level1"])
        
        # Create sub-items
        if items:
            for i, item in enumerate(items):
                item_id = f"{branch_id}_item_{i}"
                dot.node(item_id, item,
                        fillcolor=colors["level2"],
                        fontcolor='#2c3e50',
                        fontsize='11',
                        penwidth='1')
                dot.edge(branch_id, item_id, color=colors["level2"])
    
    # Render
    try:
        # Ensure output has .png extension
        if not output_path.endswith('.png'):
            output_path += '.png'
        dot.render(output_path.replace('.png', ''), cleanup=True)
        print(f"Mind map saved to: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error rendering mind map: {e}")
        print("Make sure Graphviz is installed on your system.")
        print("Download from: https://graphviz.gitlab.io/download/")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='Generate a mind map from topics and branches',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python generate_mindmap.py "时间管理" "目标设定:SMART,拆解任务" "优先级:四象限,ABC法则" -o time_mgmt.png
  
  python generate_mindmap.py "前端开发" "基础知识:HTML,CSS,JavaScript" "框架:React,Vue" "工具:Git,Webpack"
        '''
    )
    
    parser.add_argument('topic', help='Central topic of the mind map')
    parser.add_argument('branches', nargs='*', help='Branches in format "Name:Item1,Item2,..."')
    parser.add_argument('-o', '--output', default='mindmap.png', help='Output file path (default: mindmap.png)')
    parser.add_argument('-c', '--color-scheme', default='blues',
                       choices=['blues', 'greens', 'warm', 'purple', 'mono'],
                       help='Color scheme (default: blues)')
    
    args = parser.parse_args()
    
    if not args.branches:
        print("Warning: No branches provided. Creating a simple node.")
        args.branches = []
    
    create_mindmap(args.topic, args.branches, args.output, args.color_scheme)


if __name__ == '__main__':
    main()
