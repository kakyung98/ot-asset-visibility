import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler

# ==============================
# 1. 데이터 로드
# ==============================
file_path = r"C:\Users\user\Desktop\filtered_flow.csv"

df = pd.read_csv(
    file_path,
    dtype=str,
    encoding="utf-16",
    sep="\t"
)

# index 제거
if df.shape[1] == 7:
    df = df.iloc[:, 1:]

df.columns = ["src_ip", "dst_ip", "src_port", "dst_port", "protocol", "data"]

# 내부 트래픽만
df = df[
    df["src_ip"].str.startswith("172.18.") &
    df["dst_ip"].str.startswith("172.18.")
]

# ==============================
# 2. payload 있는 것만
# ==============================
df_payload = df[df["data"].notna()]
df_payload = df_payload[df_payload["data"] != ""]

# ==============================
# 3. Flow 생성
# ==============================
df_payload["flow"] = (
    df_payload["src_ip"] + "_" +
    df_payload["dst_ip"] + "_" +
    df_payload["src_port"] + "_" +
    df_payload["dst_port"] + "_" +
    df_payload["protocol"]
)

flows = df_payload.groupby("flow")["data"].apply(list)

# ==============================
# 4. Feature 생성
# ==============================
features = []

for flow, seq in flows.items():
    lengths = [len(x) for x in seq]

    avg_len = sum(lengths) / len(lengths) if len(lengths) > 0 else 0

    features.append({
        "flow": flow,
        "packet_count": len(seq),
        "avg_payload_len": avg_len
    })

feature_df = pd.DataFrame(features)

print("\n[Feature]")
print(feature_df)

# ==============================
# 5. DBSCAN
# ==============================
X = feature_df[["packet_count", "avg_payload_len"]].values

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

dbscan = DBSCAN(eps=0.8, min_samples=2)
labels = dbscan.fit_predict(X_scaled)

feature_df["cluster"] = labels

print("\n[DBSCAN 결과]")
print(feature_df)

# ==============================
# 6. 클러스터 해석
# ==============================
feature_df["src_ip"] = feature_df["flow"].apply(lambda x: x.split("_")[0])

cluster_summary = feature_df.groupby("cluster")["src_ip"].unique()

print("\n[클러스터별 IP]")
for cluster, ips in cluster_summary.items():
    print(f"Cluster {cluster}: {list(ips)}")