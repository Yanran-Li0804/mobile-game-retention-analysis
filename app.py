import streamlit as st
# python -m streamlit run app.py
st.title("🎮 Mobile Game Retention & Engagement Dashboard")

st.markdown("""
This dashboard analyzes player behavior in a mobile game, focusing on:
- User retention over time
- Engagement patterns
- Player segmentation

The goal is to understand how players interact with the game and where drop-offs occur.
""")

st.markdown("""
### Dataset Overview

This analysis is based on two datasets:

- **Users table**: user_id, install_date  
- **Events table**: user_id, event_date, event_type (session_start)

Each session_start event represents one gameplay session.  
Retention is calculated based on user activity after install date.
""")

# Step 3：读取数据
import pandas as pd

kpi = pd.read_csv(r"C:\Users\lyrgl\Desktop\mobile game data\kpi.csv")
retention = pd.read_csv(r"C:\Users\lyrgl\Desktop\mobile game data\retention_curve.csv")
heatmap = pd.read_csv(r"C:\Users\lyrgl\Desktop\mobile game data\cohort_heatmap.csv", index_col=0)
segment = pd.read_csv(r"C:\Users\lyrgl\Desktop\mobile game data\segment_distribution.csv")
user_activity = pd.read_csv("user_activity.csv")
seg_retention = pd.read_csv("seg_retention.csv")
# Step 4：做 KPI（第一行）
st.subheader("Key Metrics Overview")
st.markdown("High-level indicators of game scale and early retention performance.")
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("DAU", int(kpi.loc[kpi['metric']=="dau", 'value'].values[0]))
col2.metric("MAU", int(kpi.loc[kpi['metric']=="mau", 'value'].values[0]))
col3.metric("Day 1 Retention", round(kpi.loc[kpi['metric']=="d1_retention", 'value'].values[0], 3))
col4.metric("Day 7 Retention", round(kpi.loc[kpi['metric']=="d7_retention", 'value'].values[0], 3))
col5.metric("Day 30 Retention", round(kpi.loc[kpi['metric']=="d30_retention", 'value'].values[0], 3))

# Step 5：Retention Curve（主图）
import matplotlib.pyplot as plt
st.subheader("1. Retention Behavior Over Time")
st.markdown("#### Retention Curve")
st.markdown("Retention shows how quickly players drop off after install.")

fig, ax = plt.subplots()
ax.plot(retention['days_since_install'], retention['retention_rate'])

ax.set_xlabel("Days Since Install")
ax.set_ylabel("Retention Rate")

st.pyplot(fig)

#Step 6：Cohort Heatmap
import seaborn as sns

st.markdown("#### Cohort Retention Heatmap")
st.markdown("""
Each row represents a cohort of users who installed the game on the same date.  
Each column represents days since install.  
Color intensity shows retention rate.
""")

fig, ax = plt.subplots(figsize=(12,6))
sns.heatmap(heatmap, ax=ax, cmap="YlOrRd")

ax.set_xlabel("Days Since Install")
ax.set_ylabel("Cohort (Install Date)")

st.pyplot(fig)


# Step 7：Segment 分布

st.subheader("2. Player Engagement Segments")

st.markdown("""
Players are grouped based on total number of session_start events per user (proxy for engagement frequency).
This shows how engagement is distributed across the player base.
""")

# =========================
# 两列布局
# =========================
col1, col2 = st.columns(2)

# =========================
# 1️⃣ Engagement Distribution
# =========================
with col1:
    st.markdown("#### Engagement Distribution")

    fig1, ax1 = plt.subplots()

    ax1.hist(user_activity['total_sessions'], bins=30)

    ax1.set_title("Sessions per User Distribution")
    ax1.set_xlabel("Sessions per User")
    ax1.set_ylabel("Number of Users")

    st.pyplot(fig1)


# =========================
# 2️⃣ Segment Distribution
# =========================
with col2:
    st.markdown("#### Segment Distribution")

    segment_map = {
        "low": "Low Engagement (1–2 sessions)",
        "medium": "Medium Engagement (3–6 sessions)",
        "high": "High Engagement (7+ sessions)"
    }

    segment_display = segment.copy()
    segment_display["segment"] = segment_display["segment"].map(segment_map)

    fig2, ax2 = plt.subplots()

    ax2.bar(segment_display["segment"], segment_display["count"])

    ax2.set_title("User Segment Breakdown")
    ax2.set_xlabel("Segment")
    ax2.set_ylabel("Number of Users")

    plt.xticks(rotation=20)

    st.pyplot(fig2)

# Retention by Player Segment
st.markdown("### 3. Retention by Player Segment")

st.markdown("""
This shows how retention differs across player engagement levels.
It helps identify whether high-engagement users retain better over time.
""")


# test

overall_curve = seg_retention.groupby('days_since_install')['retention_rate'].mean()
import matplotlib.pyplot as plt


fig, ax = plt.subplots(figsize=(10,6))

# ======================
# 1️⃣ Overall baseline（背景）
# ======================
ax.plot(
    overall_curve.index,
    overall_curve.values,
    color="gray",
    alpha=0.3,
    linewidth=3,
    label="Overall Average"
)

# ======================
# 2️⃣ Segment curves（主线）
# ======================
for seg in seg_retention['segment'].unique():
    temp = seg_retention[seg_retention['segment'] == seg]
    avg_curve = temp.groupby('days_since_install')['retention_rate'].mean()

    ax.plot(
        avg_curve.index,
        avg_curve.values,
        linewidth=2,
        label=seg
    )

# ======================
# 3️⃣ 美化
# ======================
ax.set_title("Retention Curve: Segment vs Overall")
ax.set_xlabel("Days Since Install")
ax.set_ylabel("Retention Rate")
ax.legend()

st.pyplot(fig)

# Step 8：Insights（最后一块）

st.subheader("3. Key Insights")

st.markdown("""
- Retention drops sharply within the first 2–3 days, indicating weak early engagement beyond onboarding  
- A small portion of users (high segment) drives most long-term activity  
- Engagement is highly skewed, suggesting potential for better mid-core progression systems  
""")