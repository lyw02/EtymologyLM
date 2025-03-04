import networkx as nx
from networkx.algorithms import isomorphism
import matplotlib.pyplot as plt
import jsonlines
import re
from time import time


def extract_structure_content(file_path):
    structure_contents = []
    structure_pattern = re.compile(r"<structure>(.*?)</structure>", re.DOTALL)

    with jsonlines.open(file_path, "r") as reader:
        for obj in reader:
            if (
                "messages" in obj
                and isinstance(obj["messages"], list)
                and obj["messages"]
            ):
                content = obj["messages"][2]["content"]
                print(content)
                matches = structure_pattern.findall(content)
                structure_contents.extend(matches)

    return structure_contents


def split_string(input_string):
    # 定义正则表达式模式，匹配 '-' 或 '-<无空格内容>-'
    pattern = r" - | -\S+?- "
    lines = [line for line in input_string.splitlines() if line.strip()]
    # 对每一行应用分割规则，形成二维列表
    result = []
    for line in lines:
        # 使用 re.split() 方法按照模式分割字符串
        split_line = re.split(pattern, line)
        # 去除结果列表中的空字符串，并去除每个元素的首尾空格
        split_line = [s.strip() for s in split_line if s.strip()]
        result.append(split_line)
    return result


def parse_structure(input_string):
    """
    解析图结构，支持普通连接、特殊连接和子图。
    输入示例：
    A - B - (C + D)
    C - E
    返回节点集合和边列表。
    """
    def parse_line(line):
        # 分割字符串，捕获分隔符
        pattern = r'(\s-\s|\s-\S+-\s)'
        parts = re.split(pattern, line.strip())
        edges = []
        i = 0
        while i < len(parts) - 2:  # 确保有源节点、分隔符、目标节点
            source = parts[i].strip()
            target = parts[i + 2].strip()
            if target.startswith('(') and target.endswith(')'):
                # 处理子图
                subgraph_str = target[1:-1].strip()  # 移除括号
                subgraph_nodes = [node.strip() for node in subgraph_str.split(' + ')]
                for node in subgraph_nodes:
                    edges.append((node, source))  # 反转方向
            else:
                # 普通连接
                edges.append((target, source))  # 反转方向
            i += 2  # 跳到下一个源节点
        return edges

    # 分割输入字符串为行
    lines = [line.strip() for line in input_string.splitlines() if line.strip()]
    all_edges = []
    for line in lines:
        edges = parse_line(line)
        all_edges.extend(edges)

    # 提取节点
    nodes = set()
    for edge in all_edges:
        nodes.add(edge[0])  # 源节点
        nodes.add(edge[1])  # 目标节点

    # print(f">>>>{input_string}")
    # print(f"{all_edges}")
    return nodes, all_edges

def build_graph(nodes, edges):
    """构建有向图"""
    G = nx.DiGraph()
    for node in nodes:
        G.add_node(node, label=node)
    for edge in edges:
        if len(edge) == 2:
            G.add_edge(edge[0], edge[1])
        elif len(edge) == 3:
            G.add_edge(edge[0], edge[1], **edge[2])
    return G


def draw_graph(graph, ax):
    pos = nx.spring_layout(graph)
    nx.draw_networkx_nodes(graph, pos, ax=ax, node_color="lightblue", node_size=500)
    nx.draw_networkx_edges(
        graph, pos, ax=ax, edgelist=graph.edges(), arrowstyle="-|>", arrowsize=20
    )
    nx.draw_networkx_labels(graph, pos, ax=ax, font_size=12, font_color="black")


def show_graphs(g1, g2):
    _, (ax0, ax1) = plt.subplots(1, 2, figsize=(12, 6))

    draw_graph(g1, ax0)
    draw_graph(g2, ax1)

    plt.show()


# 定义节点匹配函数
def node_match(n1_attrs, n2_attrs):
    return n1_attrs["label"] == n2_attrs["label"]


if __name__ == "__main__":
    test_file_path = "test_set_large.jsonl"
    inference_file_path = "inference_gpt_4o_mini_large.jsonl"
    test_structure_list = extract_structure_content(test_file_path)
    inference_structure_list = extract_structure_content(inference_file_path)

    graphs = []
    inf_graphs = []

    for t, i in zip(test_structure_list, inference_structure_list):
        nodes1, edges1 = parse_structure(t)
        g1 = build_graph(nodes1, edges1)
        nodes2, edges2 = parse_structure(i)
        g2 = build_graph(nodes2, edges2)

        graphs.append(g1)
        inf_graphs.append(g2)

    # GED
    ged = []
    start_time = time()
    # for g1, g2 in zip(graphs, inf_graphs):
    #     ged.append(nx.graph_edit_distance(g1, g2, node_match=node_match))
    ged.append(nx.graph_edit_distance(graphs[3], inf_graphs[3], node_match=node_match))
    end_time = time()
    ged_avg = sum(ged) / len(ged)

    print(f"GED average: {ged_avg}")
    print(ged)
    print(f"Time: {end_time - start_time}")

    # MCS
    # start_time = time()
    # mcs = []
    # for g1, g2 in zip(graphs, inf_graphs):
    #     gm = isomorphism.DiGraphMatcher(g1, g2, node_match=node_match)
    #     subgraphs = list(gm.subgraph_isomorphisms_iter())
    #     if subgraphs:
    #         max_subgraph = max(subgraphs, key=len)
    #         mcs_size = len(max_subgraph)
    #     else:
    #         mcs_size = 0
    #     mcs.append(mcs_size)
    # end_time = time()
    # mcs_avg = sum(mcs) / len(mcs)

    # print(f"MCS average: {mcs_avg}")
    # print(mcs)
    # print(f"Time: {end_time - start_time}")

    # show_graphs(graphs[4], inf_graphs[4])
