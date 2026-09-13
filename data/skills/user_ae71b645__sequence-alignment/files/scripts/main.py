#!/usr/bin/env python3
"""
使用 NCBI BLAST API 进行序列比对
支持核酸和蛋白序列比较
"""

import argparse
import json
import csv
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from xml.etree import ElementTree as ET


NCBI_BLAST_URL = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"
VALID_PROGRAMS = ['blastn', 'blastp', 'blastx', 'tblastn', 'tblastx']
VALID_DATABASES = ['nr', 'nt', 'swissprot', 'pdb', 'refseq_protein', 'refseq_rna', 'est', 'gss']


def submit_blast_request(sequence, program, database, evalue=10, max_hits=10):
    """
    向 NCBI API 提交 BLAST 搜索请求

    Args:
        sequence: 查询序列（DNA 或蛋白）
        program: BLAST 程序类型
        database: 目标数据库
        evalue: E-value 阈值
        max_hits: 最大命中数

    Returns:
        用于获取结果的请求 ID（RID）
    """
    if program not in VALID_PROGRAMS:
        raise ValueError(f"Invalid program: {program}. Valid options: {VALID_PROGRAMS}")
    if database not in VALID_DATABASES:
        raise ValueError(f"Invalid database: {database}. Valid options: {VALID_DATABASES}")

    # 准备请求参数
    params = {
        'CMD': 'Put',
        'PROGRAM': program,
        'DATABASE': database,
        'QUERY': sequence,
        'EXPECT': str(evalue),
        'HITLIST_SIZE': str(max_hits),
        'FORMAT_TYPE': 'XML'
    }

    # 添加程序专属参数
    if program in ['blastn', 'tblastx']:
        params['ENTREZ_QUERY'] = 'all [filter]'

    data = urllib.parse.urlencode(params).encode('utf-8')
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    # 带重试逻辑提交请求
    max_retries = 3
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(NCBI_BLAST_URL, data=data, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=60) as response:
                result = response.read().decode('utf-8')

            # 提取请求 ID（RID）
            rid_start = result.find('RID = ')
            if rid_start == -1:
                raise RuntimeError("Failed to get RID from BLAST response")
            rid = result[rid_start + 6:].split('\n')[0].strip()

            # 提取预计等待时间
            time_start = result.find('RTOE = ')
            if time_start != -1:
                estimated_time = int(result[time_start + 7:].split('\n')[0].strip())
            else:
                estimated_time = 30

            return rid, estimated_time

        except urllib.error.URLError as e:
            if attempt < max_retries - 1:
                time.sleep(5 * (attempt + 1))
            else:
                raise RuntimeError(f"Failed to submit BLAST request after {max_retries} attempts: {e}")

    raise RuntimeError("Failed to submit BLAST request")


def check_blast_status(rid):
    """
    检查 BLAST 搜索是否已完成

    Args:
        rid: 请求 ID

    Returns:
        已完成返回 True，否则返回 False
    """
    params = {'CMD': 'Get', 'RID': rid}
    data = urllib.parse.urlencode(params).encode('utf-8')

    try:
        req = urllib.request.Request(NCBI_BLAST_URL, data=data, method='POST')
        with urllib.request.urlopen(req, timeout=30) as response:
            result = response.read().decode('utf-8')

        # 检查状态标识
        if 'Status=WAITING' in result:
            return False
        elif 'Status=READY' in result or 'BlastOutput' in result:
            return True
        elif 'Status=FAILED' in result:
            raise RuntimeError("BLAST search failed on server")
        else:
            return False
    except urllib.error.URLError:
        return False


def retrieve_blast_results(rid):
    """
    获取 BLAST 搜索结果

    Args:
        rid: 请求 ID

    Returns:
        XML 结果字符串
    """
    params = {'CMD': 'Get', 'RID': rid, 'FORMAT_TYPE': 'XML'}
    data = urllib.parse.urlencode(params).encode('utf-8')

    req = urllib.request.Request(NCBI_BLAST_URL, data=data, method='POST')
    with urllib.request.urlopen(req, timeout=60) as response:
        result = response.read().decode('utf-8')

    return result


def parse_blast_xml(xml_content):
    """
    将 BLAST XML 输出解析为结构化数据

    Args:
        xml_content: BLAST 返回的 XML 字符串

    Returns:
        包含解析结果的字典
    """
    results = {
        'query': '',
        'program': '',
        'database': '',
        'hits': []
    }

    try:
        root = ET.fromstring(xml_content)

        # 提取查询信息
        blast_query = root.find('.//BlastOutput_query-def')
        if blast_query is not None:
            results['query'] = blast_query.text or 'User Query'

        blast_program = root.find('.//BlastOutput_program')
        if blast_program is not None:
            results['program'] = blast_program.text

        blast_db = root.find('.//BlastOutput_db')
        if blast_db is not None:
            results['database'] = blast_db.text

        # 提取命中序列
        for hit in root.findall('.//Hit'):
            hit_data = {
                'id': '',
                'definition': '',
                'accession': '',
                'length': 0,
                'hsps': []
            }

            hit_id = hit.find('Hit_id')
            if hit_id is not None:
                hit_data['id'] = hit_id.text

            hit_def = hit.find('Hit_def')
            if hit_def is not None:
                hit_data['definition'] = hit_def.text

            hit_acc = hit.find('Hit_accession')
            if hit_acc is not None:
                hit_data['accession'] = hit_acc.text

            hit_len = hit.find('Hit_len')
            if hit_len is not None:
                hit_data['length'] = int(hit_len.text)

            # 提取 HSP（High-Scoring Segment Pairs，高分片段对）
            for hsp in hit.findall('.//Hsp'):
                hsp_data = {
                    'bit_score': 0.0,
                    'score': 0,
                    'evalue': 0.0,
                    'identity': 0,
                    'positive': 0,
                    'gaps': 0,
                    'align_len': 0,
                    'query_seq': '',
                    'midline': '',
                    'hit_seq': '',
                    'query_from': 0,
                    'query_to': 0,
                    'hit_from': 0,
                    'hit_to': 0
                }

                bit_score = hsp.find('Hsp_bit-score')
                if bit_score is not None:
                    hsp_data['bit_score'] = float(bit_score.text)

                score = hsp.find('Hsp_score')
                if score is not None:
                    hsp_data['score'] = int(score.text)

                evalue = hsp.find('Hsp_evalue')
                if evalue is not None:
                    hsp_data['evalue'] = float(evalue.text)

                identity = hsp.find('Hsp_identity')
                if identity is not None:
                    hsp_data['identity'] = int(identity.text)

                positive = hsp.find('Hsp_positive')
                if positive is not None:
                    hsp_data['positive'] = int(positive.text)

                gaps = hsp.find('Hsp_gaps')
                if gaps is not None:
                    hsp_data['gaps'] = int(gaps.text)

                align_len = hsp.find('Hsp_align-len')
                if align_len is not None:
                    hsp_data['align_len'] = int(align_len.text)

                query_seq = hsp.find('Hsp_qseq')
                if query_seq is not None:
                    hsp_data['query_seq'] = query_seq.text

                midline = hsp.find('Hsp_midline')
                if midline is not None:
                    hsp_data['midline'] = midline.text

                hit_seq = hsp.find('Hsp_hseq')
                if hit_seq is not None:
                    hsp_data['hit_seq'] = hit_seq.text

                query_from = hsp.find('Hsp_query-from')
                if query_from is not None:
                    hsp_data['query_from'] = int(query_from.text)

                query_to = hsp.find('Hsp_query-to')
                if query_to is not None:
                    hsp_data['query_to'] = int(query_to.text)

                hit_from = hsp.find('Hsp_hit-from')
                if hit_from is not None:
                    hsp_data['hit_from'] = int(hit_from.text)

                hit_to = hsp.find('Hsp_hit-to')
                if hit_to is not None:
                    hsp_data['hit_to'] = int(hit_to.text)

                hit_data['hsps'].append(hsp_data)

            results['hits'].append(hit_data)

    except ET.ParseError as e:
        raise RuntimeError(f"Failed to parse BLAST XML: {e}")

    return results


def format_text_output(results):
    """
    将 BLAST 结果格式化为人类可读的文本

    Args:
        results: 解析后的结果字典

    Returns:
        格式化后的字符串
    """
    lines = []
    lines.append("=" * 80)
    lines.append("BLAST SEQUENCE ALIGNMENT RESULTS")
    lines.append("=" * 80)
    lines.append(f"Program: {results.get('program', 'N/A')}")
    lines.append(f"Database: {results.get('database', 'N/A')}")
    lines.append(f"Query: {results.get('query', 'N/A')}")
    lines.append("=" * 80)
    lines.append("")

    if not results['hits']:
        lines.append("No significant hits found.")
        return '\n'.join(lines)

    lines.append(f"Found {len(results['hits'])} hit(s):\n")

    for i, hit in enumerate(results['hits'], 1):
        lines.append(f"{'='*80}")
        lines.append(f"Hit #{i}")
        lines.append(f"{'='*80}")
        lines.append(f"ID:          {hit['id']}")
        lines.append(f"Accession:   {hit['accession']}")
        lines.append(f"Definition:  {hit['definition']}")
        lines.append(f"Length:      {hit['length']} bp/aa")
        lines.append("")

        for j, hsp in enumerate(hit['hsps'], 1):
            identity_pct = (hsp['identity'] / hsp['align_len'] * 100) if hsp['align_len'] > 0 else 0
            positive_pct = (hsp['positive'] / hsp['align_len'] * 100) if hsp['align_len'] > 0 else 0

            lines.append(f"  HSP #{j}")
            lines.append(f"  {'-'*60}")
            lines.append(f"  Score:     {hsp['score']} bits({hsp['bit_score']:.1f})")
            lines.append(f"  E-value:   {hsp['evalue']:.2e}")
            lines.append(f"  Identity:  {hsp['identity']}/{hsp['align_len']} ({identity_pct:.1f}%)")
            lines.append(f"  Positives: {hsp['positive']}/{hsp['align_len']} ({positive_pct:.1f}%)")
            lines.append(f"  Gaps:      {hsp['gaps']}/{hsp['align_len']}")
            lines.append("")

            # 比对详情
            lines.append(f"  Query  {hsp['query_from']:>4}  {hsp['query_seq']}  {hsp['query_to']}")
            lines.append(f"               {hsp['midline']}")
            lines.append(f"  Sbjct  {hsp['hit_from']:>4}  {hsp['hit_seq']}  {hsp['hit_to']}")
            lines.append("")

    return '\n'.join(lines)


def format_json_output(results):
    """
    将 BLAST 结果格式化为 JSON
    """
    return json.dumps(results, indent=2)


def format_csv_output(results):
    """
    将 BLAST 结果格式化为 CSV
    """
    output = []
    output.append(['Hit #', 'ID', 'Accession', 'Definition', 'Length',
                   'HSP #', 'Score', 'Bit Score', 'E-value', 'Identity %',
                   'Query From', 'Query To', 'Hit From', 'Hit To'])

    for i, hit in enumerate(results['hits'], 1):
        for j, hsp in enumerate(hit['hsps'], 1):
            identity_pct = (hsp['identity'] / hsp['align_len'] * 100) if hsp['align_len'] > 0 else 0
            output.append([
                i, hit['id'], hit['accession'], hit['definition'][:100], hit['length'],
                j, hsp['score'], hsp['bit_score'], hsp['evalue'], f"{identity_pct:.1f}%",
                hsp['query_from'], hsp['query_to'], hsp['hit_from'], hsp['hit_to']
            ])

    # 转换为 CSV 字符串
    import io
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerows(output)
    return csv_buffer.getvalue()


def run_blast(sequence, program, database, evalue=10, max_hits=10, output_format='text', output_file=None):
    """
    运行 BLAST 搜索并返回结果的主函数

    Args:
        sequence: 查询序列
        program: BLAST 程序
        database: 目标数据库
        evalue: E-value 阈值
        max_hits: 最大命中数
        output_format: 输出格式（text、json、csv）
        output_file: 输出文件路径

    Returns:
        格式化后的结果字符串
    """
    print(f"正在提交 BLAST 请求...", file=sys.stderr)
    print(f"  程序：  {program}", file=sys.stderr)
    print(f"  数据库：{database}", file=sys.stderr)
    print(f"  序列：  {sequence[:50]}{'...' if len(sequence) > 50 else ''}", file=sys.stderr)

    # 提交请求
    rid, estimated_time = submit_blast_request(sequence, program, database, evalue, max_hits)
    print(f"\n请求 ID：{rid}", file=sys.stderr)
    print(f"预计等待：约 {estimated_time} 秒", file=sys.stderr)

    # 轮询结果
    max_wait = 300  # 最长等待 5 分钟
    waited = 0
    check_interval = max(5, min(estimated_time // 3, 30))

    while waited < max_wait:
        time.sleep(check_interval)
        waited += check_interval

        if check_blast_status(rid):
            print(f"\n结果已就绪！（已等待 {waited} 秒）", file=sys.stderr)
            break
        else:
            print(f"  仍在处理中...（已等待 {waited} 秒）", file=sys.stderr)
    else:
        raise RuntimeError(f"Search timeout after {max_wait} seconds")

    # 获取结果
    print("\n正在获取结果...", file=sys.stderr)
    xml_content = retrieve_blast_results(rid)
    results = parse_blast_xml(xml_content)

    # 格式化输出
    if output_format == 'json':
        formatted = format_json_output(results)
    elif output_format == 'csv':
        formatted = format_csv_output(results)
    else:
        formatted = format_text_output(results)

    # 如指定了输出文件，写入文件
    if output_file:
        with open(output_file, 'w') as f:
            f.write(formatted)
        print(f"\n结果已保存至：{output_file}", file=sys.stderr)

    return formatted


def main():
    parser = argparse.ArgumentParser(
        description='使用 NCBI BLAST API 进行序列比对',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # DNA 序列检索
  python main.py --sequence "ATGGCCCTGTGGATGCGCTTCTTAGTCG" --program blastn --database nt

  # 蛋白序列检索
  python main.py --sequence "MKTAYIAKQRQISFVK" --program blastp --database swissprot

  # 保存到文件
  python main.py -s "ATGCGTACG" -p blastn -d nt -o results.txt
        """
    )

    parser.add_argument('-s', '--sequence', required=True,
                        help='查询序列（DNA 或蛋白）')
    parser.add_argument('-p', '--program', required=True, choices=VALID_PROGRAMS,
                        help='BLAST 程序类型')
    parser.add_argument('-d', '--database', required=True, choices=VALID_DATABASES,
                        help='目标数据库')
    parser.add_argument('-o', '--output',
                        help='输出文件路径')
    parser.add_argument('-f', '--format', default='text', choices=['text', 'json', 'csv'],
                        help='输出格式（默认：text）')
    parser.add_argument('-m', '--max_hits', type=int, default=10,
                        help='最大命中数（默认：10）')
    parser.add_argument('-e', '--evalue', type=float, default=10.0,
                        help='E-value 阈值（默认：10）')

    args = parser.parse_args()

    try:
        results = run_blast(
            sequence=args.sequence,
            program=args.program,
            database=args.database,
            evalue=args.evalue,
            max_hits=args.max_hits,
            output_format=args.format,
            output_file=args.output
        )
        print(results)
    except KeyboardInterrupt:
        print("\n\n搜索已被用户取消。", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\n错误：{e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
