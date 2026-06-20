# 人脸识别考勤系统 — 实训论文项目

> 基于 FaceNet 的人脸识别考勤系统（后端魔改自 [waiterxiaoyy/waiter-facerecognition-python](https://github.com/waiterxiaoyy/waiter-facerecognition-python)）

---

## 目录

- [项目概述](#项目概述)
- [技术栈](#技术栈)
- [核心知识点（零基础友好）](#核心知识点零基础友好)
- [项目代码结构](#项目代码结构)
- [论文指导](#论文指导)
  - [论文题目建议](#论文题目建议)
  - [论文目录结构](#论文目录结构)
  - [论文插图清单](#论文插图清单)
- [开发计划](#开发计划)
- [参考资料](#参考资料)

---

## 项目概述

基于深度学习人脸识别技术的课堂考勤管理系统。用户通过摄像头或上传照片完成人脸识别，系统自动记录考勤信息。

**核心流程**：

```
摄像头/图片输入
       ↓
 人脸检测 + 对齐
       ↓
 FaceNet 提取 128维 特征向量（embedding）
       ↓
 余弦距离 / 欧氏距离 比对
       ↓
 判断是否匹配 → 记录考勤 → 数据库存日志
```

---

## 技术栈

| 类别 | 技术 | 说明 |
|------|------|------|
| 编程语言 | Python | 后端核心 |
| 深度学习框架 | TensorFlow / Keras（可切换 PyTorch） | 模型训练与推理 |
| 人脸识别算法 | **FaceNet**（MobileNet / Inception-ResNet-v1） | 特征提取 |
| 人脸检测 | MTCNN / OpenCV Haar Cascade | 检测人脸位置 |
| 数据库 | SQLite / MySQL | 存储人员信息与考勤记录 |
| 前端（待补充） | Flask / Streamlit / PyQt5 | 图形界面 |

---

## 核心知识点（零基础友好）

### 1. 人脸识别在干什么？

```
给你两张照片 → 判断是不是同一个人
```

深度学习方案：让神经网络自动学出有区分度的特征。

### 2. FaceNet — 灵魂算法

> 把人脸压缩成一个 **"特征向量"（embedding）**——比如 128 个浮点数。

- **同一个人**的照片 → embedding 距离很近（余弦相似度高）
- **不同的人** → embedding 距离很远

**直观理解**：

```
你的照片 A  →  [0.12, 0.87, -0.34, 0.56, ...]  (128个数字)
你的照片 B  →  [0.11, 0.88, -0.33, 0.55, ...]  ✅ 非常接近
别人照片    →  [-0.76, 0.21, 0.89, -0.45, ...]  ❌ 差很远
```

### 3. Triplet Loss — 怎么训练模型

每次给模型看三张图：

- **Anchor（锚点）**：目标人照片
- **Positive（正样本）**：目标人另一张照片
- **Negative（负样本）**：其他人的照片

训练目标：拉近 Anchor ↔ Positive，推远 Anchor ↔ Negative。

```
       Positive
        ↗
Anchor ———→ Negative（拉远）
        ↘
       （拉近）
```

### 4. 神经网络基础概念（论文第二章需要）

| 概念 | 一句话解释 |
|------|-----------|
| **卷积层（Convolution）** | 扫描图像提取特征，好比用不同滤镜看图片 |
| **池化层（Pooling）** | 压缩特征图尺寸，保留重要信息 |
| **激活函数（ReLU）** | 引入非线性，让网络能学复杂模式 |
| **全连接层（FC）** | 把特征映射到最终输出空间 |
| **Dropout** | 训练时随机丢弃部分神经元，防止过拟合 |

### 5. MobileNet — 轻量化主干网络

- 项目提供 MobileNet 和 Inception-ResNet-v1 两种主干
- **MobileNet**：用**深度可分离卷积**大幅减少参数量，在精度与速度间取得平衡
- LFW 准确率：MobileNet **97.86%** vs Inception-ResNet-v1 **99.02%**

### 6. LFW 数据集

- **Labeled Faces in the Wild**——人脸识别领域最经典的评测基准
- 包含 13,000+ 张网络收集的人脸图像
- 评价方式：人脸验证（判断两张是否为同一人）准确率

---

## 项目代码结构

```
F:\face-recognition\
├── waiter-facerecognition-python\/     # 克隆的后端仓库
│   ├── facenet.py                      # FaceNet 核心封装（加载模型 + 提取 embedding + 比对）
│   ├── main.py                         # 程序入口
│   ├── predict.py                      # 预测/推理（输入两张图片进行比对）
│   ├── train.py                        # 模型训练
│   ├── eval_LFW.py                     # LFW 数据集评估
│   ├── sql.py                          # 数据库操作
│   ├── txt_annotation.py               # 生成训练标注文件
│   ├── triplet_loss_test.py            # Triplet Loss 测试
│   ├── summary.py                      # 模型结构汇总
│   ├── cls_train.txt                   # 训练样本列表
│   ├── requirements.txt                # 依赖清单
│   ├── nets/                           # 网络结构定义（Inception-ResNet-v1 / MobileNet）
│   ├── utils/                          # 工具函数
│   ├── model_data/                     # 预训练权重存放
│   ├── img/                            # 测试图片
│   ├── lfw/                            # LFW 评估数据集
│   └── logs/                           # 训练日志
├── frontend/                           # 前端界面（待开发）
│   ├── app.py                          # Flask/Streamlit 入口
│   ├── templates/                      # HTML 模板
│   └── static/                         # 静态资源
├── docs/                               # 项目文档
│   └── project-overview.md             # 本文件
└── README.md                           # 项目说明
```

### 关键文件解读

| 文件 | 作用 |
|------|------|
| `facenet.py` | 加载预训练模型，提取人脸 embedding，计算两张人脸的相似度 |
| `sql.py` | 数据库 CRUD 操作（人员表、考勤表等） |
| `main.py` | 调度入口，串联识别流程 |
| `nets/` | 定义 MobileNet / Inception-ResNet-v1 网络结构 |
| `model_data/` | 放预训练权重（需下载） |

---

## 论文指导

### 论文题目建议

| 类型 | 题目 |
|------|------|
| **✅ 最稳妥** | **基于 FaceNet 的人脸识别考勤系统设计与实现** |
| 带对比 | 基于 FaceNet 与 ArcFace 的人脸识别考勤系统对比研究 |
| 带场景 | 基于深度学习人脸识别的课堂考勤管理系统 |
| 轻量化 | 基于 MobileNet 的轻量化人脸识别考勤系统 |

### 论文目录结构

```
摘要 + 关键词

第一章  绪论
  1.1  研究背景与意义
  1.2  国内外研究现状
  1.3  论文主要工作与章节安排

第二章  相关技术介绍            ← 核心知识章节
  2.1  深度学习基础
    2.1.1  卷积神经网络（CNN）
    2.1.2  激活函数与池化
  2.2  FaceNet 人脸识别算法
    2.2.1  网络结构
    2.2.2  Triplet Loss 原理
    2.2.3  损失函数与训练策略
  2.3  MobileNet 轻量化网络
    2.3.1  深度可分离卷积
    2.3.2  网络性能分析
  2.4  开发环境与工具

第三章  系统需求分析
  3.1  系统总体需求
  3.2  功能性需求            人脸录入、识别、考勤管理
  3.3  非功能性需求          实时性、准确率、可用性

第四章  系统设计与实现           ← 核心章节
  4.1  系统总体架构设计         架构图
  4.2  人脸识别模块设计         流程图 + FaceNet 调用详解
  4.3  数据库设计               ER 图 + 表结构说明
  4.4  系统界面设计             界面截图

第五章  实验与分析              ← 展示成果
  5.1  实验环境与数据集          LFW 数据集介绍
  5.2  评价指标                准确率、召回率、FAR/FRR
  5.3  实验结果分析             表格 + 柱状图 + Loss 曲线
  5.4  系统功能测试             界面演示截图

第六章  总结与展望
  6.1  工作总结
  6.2  不足与改进方向

参考文献
致谢
```

### 论文插图清单

| 图类型 | 出现章节 | 工具推荐 |
|--------|---------|---------|
| FaceNet 网络结构图 | 第二章 | draw.io / PPT |
| Triplet Loss 示意图 | 2.2.2 | draw.io |
| 系统架构图（模块分层） | 4.1 | draw.io |
| 人脸识别流程图 | 4.2 | 流程图工具 |
| 数据库 ER 图 | 4.3 | MySQL Workbench / draw.io |
| 系统界面截图 | 4.4 | 直接截图 |
| Loss 下降曲线（TensorBoard） | 5.3 | TensorBoard 导出 |
| 准确率对比柱状图 | 5.3 | Matplotlib / Excel |
| 混淆矩阵热力图 | 5.3 | Matplotlib seaborn |

---

## 开发计划

| 阶段 | 内容 | 预估 |
|------|------|------|
| **第一阶段** | 拉取后端代码，配置环境，跑通识别 Demo | 1-2 天 |
| **第二阶段** | 理解核心代码（facenet.py / sql.py / main.py） | 2-3 天 |
| **第三阶段** | 搭建前端界面（Flask / Streamlit / PyQt5） | 3-5 天 |
| **第四阶段** | 整合摄像头，完善考勤业务流程 | 2-3 天 |
| **第五阶段** | 写论文 + 准备答辩材料 | 并行进行 |

---

## 参考资料

1. **FaceNet 原论文**：Schroff, F., Kalenichenko, D., & Philbin, J. (2015). *FaceNet: A Unified Embedding for Face Recognition and Clustering*. CVPR.
2. **MobileNet 原论文**：Howard, A. G., et al. (2017). *MobileNets: Efficient Convolutional Neural Networks for Mobile Vision Applications*.
3. **原始仓库**：[waiterxiaoyy/waiter-facerecognition-python](https://github.com/waiterxiaoyy/waiter-facerecognition-python)
4. **timesler/facenet-pytorch**：[https://github.com/timesler/facenet-pytorch](https://github.com/timesler/facenet-pytorch)
5. **LFW 数据集**：[http://vis-www.cs.umass.edu/lfw/](http://vis-www.cs.umass.edu/lfw/)
6. **deepinsight/insightface**：[https://github.com/deepinsight/insightface](https://github.com/deepinsight/insightface)

---

> 创建时间：2026-06-16
> 项目路径：`F:\face-recognition`
