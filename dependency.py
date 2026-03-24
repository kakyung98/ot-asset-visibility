import pandas as pd
import networkx as nx

# ==============================
# 1. 데이터 로드
# ==============================
file_path = r"C:\Users\user\Desktop\filtered_flow.csv"

df = pd.read_csv(
    file_path,
    dtype=str,
    encoding="utf-16",   # Excel 저장 대응
    sep="\t"             # 탭 구분 대응
)

# index 컬럼 제거 (있을 경우)
if df.shape[1] == 7:
    df = df.iloc[:, 1:]

df.columns = ["src_ip", "dst_ip", "src_port", "dst_port", "protocol", "data"]

print("df 개수:", len(df))
print(df.head())


# ==============================
# 2. 내부 ICS 트래픽만 필터링 (핵심)
# ==============================
df = df[
    df["src_ip"].str.startswith("172.18.") &
    df["dst_ip"].str.startswith("172.18.")
]

print("\n[내부 트래픽만]")
print("남은 패킷:", len(df))


# ==============================
# 3. 그래프 생성
# ==============================
G = nx.DiGraph()
G.add_edges_from(zip(df["src_ip"], df["dst_ip"]))

print("\n[그래프 정보]")
print("노드 수:", len(G.nodes))
print("엣지 수:", len(G.edges))


# ==============================
# 4. SCC 분석 (Tarjan)
# ==============================
scc = list(nx.strongly_connected_components(G))

print("\n[SCC 결과]")
for comp in scc:
    print(comp)


# ==============================
# 5. Centrality 계산
# ==============================
centrality = nx.betweenness_centrality(G)

print("\n[Centrality]")
for node, score in sorted(centrality.items(), key=lambda x: -x[1]):
    print(f"{node}: {score:.6f}")


# ==============================
# 6. 계층 분류
# ==============================
layer_result = {}

for node in G.nodes:
    in_deg = G.in_degree(node)
    out_deg = G.out_degree(node)
    total_deg = in_deg + out_deg

    print(f"{node} → in:{in_deg}, out:{out_deg}, total:{total_deg}")

    # 연결이 가장 많은 노드 → PLC
    if total_deg >= 4:
        layer_result[node] = "Control Layer (PLC)"
    else:
        layer_result[node] = "Field Layer (Process)"


# ==============================
# 7. 결과 출력
# ==============================
print("\n[계층 분류 결과]")
for node, layer in layer_result.items():
    print(f"{node} → {layer}")
