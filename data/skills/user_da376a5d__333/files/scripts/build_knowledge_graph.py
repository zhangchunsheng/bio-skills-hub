#!/usr/bin/env python3
"""
医学知识图谱构建器 v2.0
支持多文献合并、关系推断、对比分析
新增：Cypher导出、RDF/Turtle导出、图统计分析
"""

import sys
import json
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
import hashlib


@dataclass
class GraphNode:
    """图节点"""
    id: str
    label: str
    node_type: str
    properties: Dict = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)
    
    def to_dict(self):
        return asdict(self)


@dataclass
class GraphEdge:
    """图边"""
    source: str
    target: str
    relation_type: str
    properties: Dict = field(default_factory=dict)
    evidence: str = ""
    confidence: float = 1.0
    
    def to_dict(self):
        return asdict(self)


class MedicalKnowledgeGraph:
    """医学知识图谱构建器"""
    
    # 关系类型定义（中文）
    RELATION_TYPES = {
        '治疗': '治疗',
        '导致': '导致',
        '预防': '预防',
        '诊断': '诊断',
        '关联': '关联',
        '抑制': '抑制',
        '激活': '激活',
        '代谢': '代谢',
        '相互作用': '相互作用',
        '副作用': '副作用',
        '禁忌': '禁忌',
        '位于': '位于',
        '症状表现': '症状表现',
        '标志物': '标志物',
        '建模': '建模',
        '表达于': '表达于',
        '调控': '调控',
    }
    
    # 实体类型映射（中文）
    ENTITY_TYPE_MAP = {
        'diseases': '疾病',
        'drugs': '药物',
        'genes': '基因',
        'symptoms': '症状',
        'procedures': '医疗程序',
        'biomarkers': '生物标志物',
        'anatomy': '解剖结构',
        'populations': '研究人群',
        'animal_models': '实验动物',
        'cell_lines': '细胞系',
        'pathways': '信号通路',
        'metabolites': '代谢物',
        'devices': '器械仪器',
        'outcomes': '结局指标',
    }
    
    # 默认关系规则（禁用自动推断，改为仅使用显式关系）
    DEFAULT_RELATIONS = {}
    
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.entity_index: Dict[str, str] = {}  # 实体名 -> 节点ID
        
    def build_from_paper(self, entities: Dict[str, List[str]], 
                        relations: Optional[List[Dict]] = None,
                        paper_id: str = "") -> Dict:
        """
        从单篇论文构建知识图谱
        
        Args:
            entities: 提取的实体（按类型分组）
            relations: 显式关系列表（优先使用，不再自动推断）
            paper_id: 论文标识
            
        Returns:
            知识图谱数据
        """
        # 1. 注册实体节点（只注册有关系的实体）
        # 先收集关系中涉及的实体名称
        relation_entities = set()
        if relations:
            for rel in relations:
                relation_entities.add(rel.get('source', '').strip())
                relation_entities.add(rel.get('target', '').strip())
        
        for entity_type, entity_list in entities.items():
            if entity_type == 'relations':
                continue
            for entity_name in entity_list:
                # 只添加出现在关系中的实体；若无关系则添加全部（兜底）
                if not relations or entity_name.strip() in relation_entities:
                    self._add_node(entity_name.strip(), entity_type, paper_id)
        
        # 2. 添加显式关系（不自动推断）
        if relations:
            for rel in relations:
                source = rel.get('source', '').strip()
                target = rel.get('target', '').strip()
                rel_type = rel.get('type', '关联').strip()
                evidence = rel.get('evidence', '')
                if source and target:
                    # 确保关系中的实体节点存在
                    if source not in self.entity_index:
                        self._add_node(source, 'unknown', paper_id)
                    if target not in self.entity_index:
                        self._add_node(target, 'unknown', paper_id)
                    self._add_relation(source, target, rel_type, evidence=evidence, confidence=1.0)
        
        return self.export()
    
    def merge_with_existing(self, existing_graph: Dict) -> Dict:
        """
        与现有知识图谱合并
        
        Args:
            existing_graph: 现有的知识图谱数据
            
        Returns:
            合并后的知识图谱
        """
        # 加载现有节点
        for node_data in existing_graph.get('nodes', []):
            node_id = node_data['id']
            if node_id not in self.nodes:
                self.nodes[node_id] = GraphNode(**node_data)
        
        # 加载现有边
        for edge_data in existing_graph.get('edges', []):
            edge = GraphEdge(**edge_data)
            if not self._edge_exists(edge):
                self.edges.append(edge)
        
        return self.export()
    
    def _add_node(self, name: str, entity_type: str, source: str = "") -> str:
        """添加节点"""
        # 生成节点ID
        node_id = self._generate_node_id(name, entity_type)
        
        # 检查是否已存在
        if node_id in self.nodes:
            # 更新来源
            if source and source not in self.nodes[node_id].sources:
                self.nodes[node_id].sources.append(source)
            return node_id
        
        # 映射实体类型
        mapped_type = self.ENTITY_TYPE_MAP.get(entity_type, entity_type)
        
        # 创建新节点
        node = GraphNode(
            id=node_id,
            label=name,
            node_type=mapped_type,
            properties={
                'original_type': entity_type,
                'created_at': datetime.now().isoformat(),
            },
            sources=[source] if source else []
        )
        
        self.nodes[node_id] = node
        self.entity_index[name.lower()] = node_id
        
        return node_id
    
    def _add_relation(self, source: str, target: str, relation_type: str,
                     evidence: str = "", confidence: float = 1.0) -> bool:
        """添加关系"""
        # 查找节点ID
        source_id = self._find_node_id(source)
        target_id = self._find_node_id(target)
        
        if not source_id or not target_id:
            return False
        
        # 创建边
        edge = GraphEdge(
            source=source_id,
            target=target_id,
            relation_type=relation_type,
            evidence=evidence,
            confidence=confidence,
            properties={
                'created_at': datetime.now().isoformat(),
            }
        )
        
        # 检查是否已存在
        if not self._edge_exists(edge):
            self.edges.append(edge)
        
        return True
    
    def _infer_relations(self):
        """
        基于规则推断关系（保守策略）
        
        仅在实体数量较少时进行推断，避免产生大量噪声。
        当某类型实体超过阈值时跳过全连接，依赖 LLM 提取的精确关系。
        """
        MAX_CROSS_PRODUCT = 20  # 最多推断20条关系，超过则跳过
        
        nodes_by_type = {}
        for node in self.nodes.values():
            if node.node_type not in nodes_by_type:
                nodes_by_type[node.node_type] = []
            nodes_by_type[node.node_type].append(node)
        
        for (type1, type2), relation_type in self.DEFAULT_RELATIONS.items():
            nodes1 = nodes_by_type.get(type1, [])
            nodes2 = nodes_by_type.get(type2, [])
            
            # 跳过会产生过多关系的组合
            if len(nodes1) * len(nodes2) > MAX_CROSS_PRODUCT:
                continue
            
            # 仅在节点数量可控时推断
            for n1 in nodes1:
                for n2 in nodes2:
                    edge = GraphEdge(
                        source=n1.id,
                        target=n2.id,
                        relation_type=relation_type,
                        confidence=0.5,  # 推断关系置信度较低
                        properties={'inferred': True}
                    )
                    if not self._edge_exists(edge):
                        self.edges.append(edge)
    
    def _generate_node_id(self, name: str, entity_type: str) -> str:
        """生成节点ID"""
        # 使用类型和名称的哈希作为ID
        key = f"{entity_type}:{name.lower()}"
        return hashlib.md5(key.encode()).hexdigest()[:12]
    
    def _find_node_id(self, name: str) -> Optional[str]:
        """根据名称查找节点ID"""
        return self.entity_index.get(name.lower())
    
    def _edge_exists(self, edge: GraphEdge) -> bool:
        """检查边是否已存在"""
        for existing in self.edges:
            if (existing.source == edge.source and 
                existing.target == edge.target and
                existing.relation_type == edge.relation_type):
                return True
        return False
    
    def export(self, format: str = 'json') -> Dict:
        """
        导出知识图谱
        
        Args:
            format: 导出格式 ('json', 'cypher', 'turtle')
            
        Returns:
            知识图谱数据
        """
        graph_data = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'node_count': len(self.nodes),
                'edge_count': len(self.edges),
                'node_types': list(set(n.node_type for n in self.nodes.values())),
                'relation_types': list(set(e.relation_type for e in self.edges)),
            },
            'nodes': [node.to_dict() for node in self.nodes.values()],
            'edges': [edge.to_dict() for edge in self.edges],
        }
        
        if format == 'cypher':
            graph_data['cypher'] = self._to_cypher()
        elif format == 'turtle':
            graph_data['turtle'] = self._to_turtle()
        
        return graph_data
    
    def _to_cypher(self) -> str:
        """导出为 Cypher 格式（Neo4j）"""
        lines = []
        lines.append("// === 创建节点 ===")
        for node in self.nodes.values():
            props = f'id: "{node.id}", name: "{node.label}"'
            lines.append(f'CREATE (:{node.node_type} {{{props}}});')
        
        lines.append("\n// === 创建关系 ===")
        for edge in self.edges:
            source_label = self.nodes[edge.source].label if edge.source in self.nodes else edge.source
            target_label = self.nodes[edge.target].label if edge.target in self.nodes else edge.target
            props = f'confidence: {edge.confidence}'
            lines.append(
                f'MATCH (a {{id: "{edge.source}"}}), (b {{id: "{edge.target}"}}) '
                f'CREATE (a)-[:{edge.relation_type} {{{props}}}]->(b);'
            )
        
        return '\n'.join(lines)
    
    def _to_turtle(self) -> str:
        """导出为 Turtle/RDF 格式"""
        lines = [
            '@prefix med: <http://medical-kg.org/> .',
            '@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .',
            '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .',
            '',
        ]
        
        for node in self.nodes.values():
            safe_label = node.label.replace('"', '\\"')
            lines.append(f'med:{node.id} rdf:type med:{node.node_type} ;')
            lines.append(f'    rdfs:label "{safe_label}" .')
            lines.append('')
        
        for edge in self.edges:
            relation = edge.relation_type.lower()
            lines.append(f'med:{edge.source} med:{relation} med:{edge.target} .')
        
        return '\n'.join(lines)
    
    def get_statistics(self) -> Dict:
        """获取图谱统计信息（NEW）"""
        node_types = {}
        for node in self.nodes.values():
            node_types[node.node_type] = node_types.get(node.node_type, 0) + 1
        
        relation_types = {}
        for edge in self.edges:
            relation_types[edge.relation_type] = relation_types.get(edge.relation_type, 0) + 1
        
        # 计算度中心性
        degree = {}
        for edge in self.edges:
            degree[edge.source] = degree.get(edge.source, 0) + 1
            degree[edge.target] = degree.get(edge.target, 0) + 1
        
        top_nodes = sorted(degree.items(), key=lambda x: x[1], reverse=True)[:10]
        top_nodes_labeled = []
        for node_id, deg in top_nodes:
            label = self.nodes[node_id].label if node_id in self.nodes else node_id
            top_nodes_labeled.append({'id': node_id, 'label': label, 'degree': deg})
        
        return {
            'total_nodes': len(self.nodes),
            'total_edges': len(self.edges),
            'node_types': node_types,
            'relation_types': relation_types,
            'top_connected_nodes': top_nodes_labeled,
            'density': (2 * len(self.edges)) / (len(self.nodes) * (len(self.nodes) - 1)) if len(self.nodes) > 1 else 0,
        }
    
    def compare_graphs(self, other_graph: Dict) -> Dict:
        """
        与另一个图谱对比分析（NEW）
        
        Args:
            other_graph: 另一个图谱数据
            
        Returns:
            对比分析结果
        """
        other_nodes = {n['id']: n for n in other_graph.get('nodes', [])}
        other_edges = set()
        for e in other_graph.get('edges', []):
            other_edges.add((e['source'], e['target'], e.get('relation_type', '')))
        
        # 当前图谱的边
        current_edges = set()
        for e in self.edges:
            current_edges.add((e.source, e.target, e.relation_type))
        
        # 计算重叠
        shared_nodes = set(self.nodes.keys()) & set(other_nodes.keys())
        shared_edges = current_edges & other_edges
        unique_current_nodes = set(self.nodes.keys()) - set(other_nodes.keys())
        unique_other_nodes = set(other_nodes.keys()) - set(self.nodes.keys())
        
        return {
            'shared_nodes': len(shared_nodes),
            'shared_edges': len(shared_edges),
            'unique_to_current_nodes': len(unique_current_nodes),
            'unique_to_other_nodes': len(unique_other_nodes),
            'similarity_score': len(shared_nodes) / max(len(self.nodes), len(other_nodes)) if max(len(self.nodes), len(other_nodes)) > 0 else 0,
            'shared_node_list': [self.nodes[nid].label for nid in shared_nodes if nid in self.nodes],
        }


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python build_knowledge_graph.py <实体数据JSON> [--output <输出路径>]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(json.dumps({'error': f'读取输入文件失败: {str(e)}'}, ensure_ascii=False))
        sys.exit(1)
    
    # 从输入数据中分离实体和关系
    relations = data.pop('relations', None)
    
    # 也支持通过 --relations 参数传入独立的关系文件
    if '--relations' in sys.argv:
        rel_index = sys.argv.index('--relations')
        if rel_index + 1 < len(sys.argv):
            try:
                with open(sys.argv[rel_index + 1], 'r', encoding='utf-8') as f:
                    relations = json.load(f)
            except Exception as e:
                print(f"警告: 读取关系文件失败: {e}")
    
    # 确定输出路径
    output_path = None
    if '--output' in sys.argv:
        out_index = sys.argv.index('--output')
        if out_index + 1 < len(sys.argv):
            output_path = sys.argv[out_index + 1]
    
    # 构建知识图谱
    kg = MedicalKnowledgeGraph()
    graph_data = kg.build_from_paper(data, relations)
    
    result_json = json.dumps(graph_data, ensure_ascii=False, indent=2)
    
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result_json)
        print(f"知识图谱已保存至: {output_path}")
    else:
        print(result_json)


if __name__ == '__main__':
    main()
