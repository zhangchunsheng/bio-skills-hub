#!/usr/bin/env python3
"""
知识图谱可视化脚本
生成交互式HTML图谱
"""

import sys
import json
from pathlib import Path
from typing import Dict, List


def load_template() -> str:
    """加载HTML模板"""
    template_path = Path(__file__).parent.parent / 'assets' / 'graph_template.html'
    if template_path.exists():
        return template_path.read_text(encoding='utf-8')
    
    # 如果模板不存在，使用内置的简化模板
    return get_default_template()


def get_default_template() -> str:
    """获取默认HTML模板（当模板文件不存在时使用）"""
    return '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}}</title>
    <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, 'Microsoft YaHei', sans-serif; background: #f5f7fa; padding: 20px; color: #1a1a2e; }
        .container { max-width: 1280px; margin: 0 auto; }
        .header { background: white; border-radius: 12px; padding: 24px 28px; margin-bottom: 18px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); border-top: 4px solid #4f46e5; }
        .header h1 { font-size: 22px; font-weight: 700; }
        .stats-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 18px; }
        .stat-card { background: white; border-radius: 10px; padding: 16px; text-align: center; border: 1px solid #e5e7eb; }
        .stat-number { font-size: 30px; font-weight: 700; color: #4f46e5; }
        .stat-label { font-size: 13px; color: #64748b; margin-top: 4px; }
        .controls { background: white; border-radius: 10px; padding: 12px 16px; margin-bottom: 14px; display: flex; gap: 12px; align-items: center; flex-wrap: wrap; border: 1px solid #e5e7eb; }
        .controls input { padding: 6px 10px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 13px; outline: none; width: 200px; }
        .btn { padding: 6px 12px; border: 1px solid #d1d5db; background: white; border-radius: 6px; cursor: pointer; font-size: 13px; }
        .btn:hover { border-color: #4f46e5; color: #4f46e5; }
        .btn-primary { background: #4f46e5; color: white; border-color: #4f46e5; }
        .graph-wrapper { background: white; border-radius: 12px; border: 1px solid #e5e7eb; overflow: hidden; margin-bottom: 18px; }
        #graph { width: 100%; height: 700px; display: block; background: white; }
        .legend-box { background: white; border-radius: 12px; padding: 16px 20px; border: 1px solid #e5e7eb; }
        .legend-grid { display: flex; flex-wrap: wrap; gap: 16px; }
        .legend-item { display: flex; align-items: center; gap: 8px; font-size: 13px; color: #475569; }
        .legend-dot { width: 14px; height: 14px; border-radius: 50%; }
        .tooltip { position: fixed; padding: 8px 12px; background: rgba(15,23,42,0.95); color: white; border-radius: 6px; font-size: 12px; pointer-events: none; opacity: 0; transition: opacity 0.15s; z-index: 1000; }
        .tooltip.visible { opacity: 1; }
        .node-label { font-size: 12px; font-weight: 600; fill: #1a1a2e; pointer-events: none; text-anchor: middle; }
        .edge-label { font-size: 11px; fill: #64748b; pointer-events: none; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><h1>{{TITLE}}</h1></div>
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-number">{{NODE_COUNT}}</div><div class="stat-label">实体节点</div></div>
            <div class="stat-card"><div class="stat-number">{{EDGE_COUNT}}</div><div class="stat-label">关系连接</div></div>
            <div class="stat-card"><div class="stat-number">{{TYPE_COUNT}}</div><div class="stat-label">实体类型</div></div>
            <div class="stat-card"><div class="stat-number">{{RELATION_COUNT}}</div><div class="stat-label">关系类型</div></div>
        </div>
        <div class="controls">
            <input type="text" id="searchInput" placeholder="搜索实体..." oninput="searchNodes(this.value)">
            <button class="btn" onclick="resetView()">重置</button>
            <button class="btn btn-primary" onclick="exportImage()">导出 SVG</button>
        </div>
        <div class="graph-wrapper"><svg id="graph"></svg></div>
        <div class="legend-box"><div class="legend-grid" id="legend"></div></div>
    </div>
    <div class="tooltip" id="tooltip"></div>
    <script>
        const graphData = {{GRAPH_DATA}};
        const nodeColors = {
            '疾病':     { fill: '#dc2626', stroke: '#991b1b', label: '疾病' },
            '药物':     { fill: '#10b981', stroke: '#047857', label: '药物' },
            '基因':     { fill: '#8b5cf6', stroke: '#5b21b6', label: '基因/蛋白' },
            '症状':     { fill: '#f59e0b', stroke: '#b45309', label: '症状' },
            '医疗程序': { fill: '#14b8a6', stroke: '#0f766e', label: '医疗程序' },
            '生物标志物':{ fill: '#3b82f6', stroke: '#1d4ed8', label: '生物标志物' },
            '解剖结构': { fill: '#0ea5e9', stroke: '#0369a1', label: '解剖结构' },
            '研究人群': { fill: '#84cc16', stroke: '#4d7c0f', label: '研究人群' },
            '实验动物': { fill: '#f97316', stroke: '#c2410c', label: '实验动物' },
            '细胞系':   { fill: '#e879f9', stroke: '#a21caf', label: '细胞系' },
            '信号通路': { fill: '#06b6d4', stroke: '#0e7490', label: '信号通路' },
            '代谢物':   { fill: '#22c55e', stroke: '#15803d', label: '代谢物' },
            '器械仪器': { fill: '#64748b', stroke: '#334155', label: '器械仪器' },
            '结局指标': { fill: '#f43f5e', stroke: '#be123c', label: '结局指标' },
            'Unknown':  { fill: '#94a3b8', stroke: '#475569', label: '其他' }
        };
        const nodes = graphData.nodes.map(n => ({...n, color: nodeColors[n.type] || nodeColors['Unknown']}));
        const edges = graphData.edges.map(e => ({...e}));
        const usedTypes = [...new Set(nodes.map(n => n.type))];

        // 图例
        const legend = document.getElementById('legend');
        usedTypes.forEach(t => {
            const c = nodeColors[t] || nodeColors['Unknown'];
            const item = document.createElement('div');
            item.className = 'legend-item';
            item.innerHTML = '<span class="legend-dot" style="background:' + c.fill + '"></span><span>' + c.label + '</span>';
            legend.appendChild(item);
        });

        const svg = d3.select('#graph');
        const container = svg.append('g');
        const width = svg.node().getBoundingClientRect().width;
        const height = 700;
        svg.attr('viewBox', '0 0 ' + width + ' ' + height);

        // 类型聚类布局
        const clusterRadius = Math.min(width, height) * 0.32;
        const typeFoci = {};
        usedTypes.forEach((type, i) => {
            const angle = (i / Math.max(1, usedTypes.length)) * 2 * Math.PI - Math.PI / 2;
            typeFoci[type] = { x: width / 2 + clusterRadius * Math.cos(angle), y: height / 2 + clusterRadius * Math.sin(angle) };
        });

        // 节点大小按度数
        const degree = {};
        edges.forEach(e => {
            const sId = typeof e.source === 'object' ? e.source.id : e.source;
            const tId = typeof e.target === 'object' ? e.target.id : e.target;
            degree[sId] = (degree[sId] || 0) + 1;
            degree[tId] = (degree[tId] || 0) + 1;
        });
        const maxDeg = Math.max(...Object.values(degree), 1);
        nodes.forEach(n => { n.radius = 12 + Math.min(18, (degree[n.id] || 0) / maxDeg * 18); });

        const simulation = d3.forceSimulation(nodes)
            .force('link', d3.forceLink(edges).id(d => d.id).distance(d => d.source.type === d.target.type ? 50 : 130).strength(0.4))
            .force('charge', d3.forceManyBody().strength(-300))
            .force('center', d3.forceCenter(width / 2, height / 2).strength(0.05))
            .force('collision', d3.forceCollide().radius(d => d.radius + 6))
            .force('x', d3.forceX(d => typeFoci[d.type] ? typeFoci[d.type].x : width / 2).strength(0.6))
            .force('y', d3.forceY(d => typeFoci[d.type] ? typeFoci[d.type].y : height / 2).strength(0.6));

        const zoom = d3.zoom().scaleExtent([0.2, 4]).on('zoom', e => container.attr('transform', e.transform));
        svg.call(zoom);

        // 箭头
        svg.append('defs').append('marker').attr('id', 'arrow').attr('viewBox', '0 -5 10 10')
            .attr('refX', 22).attr('refY', 0).attr('markerWidth', 6).attr('markerHeight', 6).attr('orient', 'auto')
            .append('path').attr('d', 'M0,-5L10,0L0,5').attr('fill', '#cbd5e1');

        const links = container.append('g').selectAll('line').data(edges).enter().append('line')
            .attr('stroke', '#cbd5e1').attr('stroke-width', 1.5).attr('stroke-opacity', 0.7).attr('marker-end', 'url(#arrow)');

        const edgeLabels = container.append('g').selectAll('g').data(edges).enter().append('g');
        edgeLabels.append('text').attr('class', 'edge-label').attr('text-anchor', 'middle').attr('dy', '0.3em').text(d => d.type || '');

        const nodeGroups = container.append('g').selectAll('g').data(nodes).enter().append('g').style('cursor', 'pointer')
            .call(d3.drag()
                .on('start', (e, d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
                .on('drag', (e, d) => { d.fx = e.x; d.fy = e.y; })
                .on('end', (e, d) => { if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }));

        nodeGroups.append('circle').attr('r', d => d.radius).attr('fill', d => d.color.fill)
            .attr('stroke', d => d.color.stroke).attr('stroke-width', 2)
            .on('mouseover', (e, d) => {
                const t = document.getElementById('tooltip');
                t.innerHTML = '<strong>' + d.label + '</strong> · ' + d.color.label;
                t.classList.add('visible');
                t.style.left = (e.clientX + 12) + 'px';
                t.style.top = (e.clientY + 12) + 'px';
            })
            .on('mousemove', (e) => {
                const t = document.getElementById('tooltip');
                t.style.left = (e.clientX + 12) + 'px';
                t.style.top = (e.clientY + 12) + 'px';
            })
            .on('mouseout', () => document.getElementById('tooltip').classList.remove('visible'));

        nodeGroups.append('text').attr('class', 'node-label').attr('dy', d => d.radius + 14).text(d => d.label);
            links.attr('x1', d => d.source.x).attr('y1', d => d.source.y).attr('x2', d => d.target.x).attr('y2', d => d.target.y);
            edgeLabels.attr('transform', d => 'translate(' + ((d.source.x + d.target.x) / 2) + ',' + ((d.source.y + d.target.y) / 2) + ')');
            nodeGroups.attr('transform', d => 'translate(' + d.x + ',' + d.y + ')');
        });

        function searchNodes(term) {
            const t = (term || '').toLowerCase();
            nodeGroups.style('opacity', d => !t || d.label.toLowerCase().includes(t) ? 1 : 0.15);
            links.style('opacity', d => !t || d.source.label.toLowerCase().includes(t) || d.target.label.toLowerCase().includes(t) ? 0.9 : 0.05);
            edgeLabels.style('opacity', d => !t || d.source.label.toLowerCase().includes(t) || d.target.label.toLowerCase().includes(t) ? 1 : 0.05);
        }
        function resetView() {
            svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity);
            nodeGroups.style('opacity', 1); links.style('opacity', 0.7); edgeLabels.style('opacity', 1);
            document.getElementById('searchInput').value = '';
        }
        function exportImage() {
            const svgEl = document.getElementById('graph');
            const clone = svgEl.cloneNode(true);
            const bg = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            bg.setAttribute('width', '100%'); bg.setAttribute('height', '100%'); bg.setAttribute('fill', 'white');
            clone.insertBefore(bg, clone.firstChild);
            const data = new XMLSerializer().serializeToString(clone);
            const url = URL.createObjectURL(new Blob([data], { type: 'image/svg+xml;charset=utf-8' }));
            const a = document.createElement('a'); a.href = url; a.download = 'graph.svg'; a.click();
            URL.revokeObjectURL(url);
        }
    </script>
</body>
</html>'''


def generate_html_visualization(graph_data: Dict, output_path: str, title: str = "医学知识图谱") -> str:
    """
    生成知识图谱的HTML可视化
    
    Args:
        graph_data: 知识图谱数据
        output_path: 输出HTML文件路径
        title: 页面标题
        
    Returns:
        生成的HTML文件路径
    """
    # 加载模板
    html_template = load_template()
    
    # 准备图谱数据（转换为JSON字符串）
    graph_json = {
        'nodes': [],
        'edges': []
    }
    
    # 处理节点数据
    for node in graph_data.get('nodes', []):
        graph_json['nodes'].append({
            'id': node.get('id', ''),
            'label': node.get('label', ''),
            'type': node.get('node_type', 'Unknown'),
        })
    
    # 处理边数据
    for edge in graph_data.get('edges', []):
        # 支持 type 或 relation_type 两种字段名
        edge_type = edge.get('type', '') or edge.get('relation_type', '')
        graph_json['edges'].append({
            'source': edge.get('source', ''),
            'target': edge.get('target', ''),
            'type': edge_type,
        })
    
    # 统计信息
    node_count = len(graph_json['nodes'])
    edge_count = len(graph_json['edges'])
    type_count = len(set(n['type'] for n in graph_json['nodes']))
    relation_count = len(set(e['type'] for e in graph_json['edges']))
    
    # 替换模板中的占位符
    html_content = html_template
    html_content = html_content.replace('{{TITLE}}', title.replace('<', '&lt;').replace('>', '&gt;'))
    html_content = html_content.replace('{{NODE_COUNT}}', str(node_count))
    html_content = html_content.replace('{{EDGE_COUNT}}', str(edge_count))
    html_content = html_content.replace('{{TYPE_COUNT}}', str(type_count))
    html_content = html_content.replace('{{RELATION_COUNT}}', str(relation_count))
    # 使用 json.dumps 确保安全转义（处理 </script> 等特殊字符）
    graph_json_str = json.dumps(graph_json, ensure_ascii=False)
    graph_json_str = graph_json_str.replace('</script>', '<\\/script>')
    graph_json_str = graph_json_str.replace('<!--', '<\\!--')
    html_content = html_content.replace('{{GRAPH_DATA}}', graph_json_str)
    
    # 确保输出目录存在
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # 写入文件
    Path(output_path).write_text(html_content, encoding='utf-8')
    
    return output_path


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python visualize_graph.py <知识图谱JSON> [--output <输出路径>] [--title <标题>]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    # 确定输出路径
    output_path = 'knowledge_graph.html'
    if '--output' in sys.argv:
        output_index = sys.argv.index('--output')
        if output_index + 1 < len(sys.argv):
            output_path = sys.argv[output_index + 1]
    
    # 确定标题
    title = "医学知识图谱"
    if '--title' in sys.argv:
        title_index = sys.argv.index('--title')
        if title_index + 1 < len(sys.argv):
            title = sys.argv[title_index + 1]
    
    try:
        # 读取知识图谱数据
        with open(input_file, 'r', encoding='utf-8') as f:
            graph_data = json.load(f)
        
        # 生成可视化
        result_path = generate_html_visualization(graph_data, output_path, title)
        
        print(json.dumps({
            'success': True,
            'output_path': result_path,
            'node_count': len(graph_data.get('nodes', [])),
            'edge_count': len(graph_data.get('edges', [])),
        }, ensure_ascii=False))
        
    except Exception as e:
        print(json.dumps({
            'success': False,
            'error': str(e)
        }, ensure_ascii=False))
        sys.exit(1)


if __name__ == '__main__':
    main()
