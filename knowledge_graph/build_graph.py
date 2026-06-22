#!/usr/bin/env python3
"""
机器学习课程知识图谱构建脚本
基于周志华《机器学习》（西瓜书）课程体系

生成内容：
1. nodes.json — 全部知识点节点
2. relationships.json — 全部关系
3. import.cypher — Neo4j 导入用的 Cypher 脚本
"""

import json
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ═══════════════════════════════════════════════════════════
# 第一部分：节点定义
# 每个节点包含: id, label(类型), name, description, chapter
# ═══════════════════════════════════════════════════════════

nodes = []


def add(label, name, desc, chapter=""):
    """添加一个知识节点"""
    nodes.append({
        "id": f"{label}_{name}",
        "label": label,
        "name": name,
        "description": desc,
        "chapter": chapter,
    })


# ── 第1章：绪论 ──────────────────────────────────────────

add("Chapter", "绪论", "机器学习的基本概念与发展历程", "1")

add("Concept", "机器学习", "研究如何让计算机从数据中自动学习规律并改善自身性能的一门学科", "1")
add("Concept", "数据集", "一组记录的集合，每条记录描述一个事件或对象", "1")
add("Concept", "样本", "数据集中的每条记录，也称实例或数据点", "1")
add("Concept", "特征", "描述样本某方面性质的属性或变量", "1")
add("Concept", "标记", "样本的预期输出或目标值，也称标签", "1")
add("Concept", "训练集", "用于训练模型的数据子集", "1")
add("Concept", "测试集", "用于评估模型泛化能力的数据子集", "1")
add("Concept", "假设空间", "所有可能的模型或假设的集合", "1")
add("Concept", "版本空间", "与训练数据一致的所有假设构成的子集", "1")
add("Concept", "归纳偏好", "学习算法在学习过程中对某种类型假设的偏好", "1")

add("Task", "监督学习", "利用带标记的训练数据学习输入到输出映射关系的学习范式", "1")
add("Task", "无监督学习", "从无标记数据中发现隐含结构或模式的学习范式", "1")
add("Task", "分类", "预测样本属于哪个离散类别的监督学习任务", "1")
add("Task", "回归", "预测样本连续数值输出的监督学习任务", "1")
add("Task", "聚类", "将数据自动划分为若干组的无监督学习任务", "1")

add("Concept", "奥卡姆剃刀", "在多个假设与观测一致时，选择最简单的那个", "1")
add("Concept", "没有免费的午餐定理", "不存在对所有问题都最优的算法，算法性能与问题相关", "1")

# ── 第2章：模型评估与选择 ──────────────────────────────────

add("Chapter", "模型评估与选择", "如何科学地评估和选择机器学习模型", "2")

add("Concept", "过拟合", "模型在训练集上表现好但泛化能力差，学到了数据中的噪声", "2")
add("Concept", "欠拟合", "模型在训练集上表现也不好，未能学到数据的真实规律", "2")
add("Concept", "泛化能力", "模型在未见过的数据上的预测能力", "2")
add("Concept", "偏差-方差分解", "将泛化误差分解为偏差、方差和噪声三部分", "2")
add("Concept", "偏差", "模型预测值的期望与真实值之间的差距，反映模型的拟合能力", "2")
add("Concept", "方差", "模型在不同训练集上预测结果的波动程度，反映模型的稳定性", "2")

add("Method", "留出法", "将数据集划分为互斥的训练集和测试集", "2")
add("Method", "交叉验证", "将数据集分成k折，轮流用其中一折做测试集，其余做训练集", "2")
add("Method", "自助法", "有放回地从数据集中采样构建训练集，适用于小数据集", "2")

add("Metric", "准确率", "分类正确的样本占总样本的比例: (TP+TN)/(TP+TN+FP+FN)", "2")
add("Metric", "精确率", "预测为正的样本中真正为正的比例: TP/(TP+FP)", "2")
add("Metric", "召回率", "真正为正的样本中被正确预测的比例: TP/(TP+FN)", "2")
add("Metric", "F1分数", "精确率和召回率的调和平均: 2*P*R/(P+R)", "2")
add("Metric", "ROC曲线", "以假正率为横轴、真正率为纵轴绘制的曲线", "2")
add("Metric", "AUC", "ROC曲线下的面积，值越大模型性能越好", "2")
add("Metric", "均方误差", "回归任务中预测值与真实值差值的平方的均值", "2")
add("Metric", "混淆矩阵", "展示分类结果中各类别正确和错误预测数量的矩阵", "2")

# ── 第3章：线性模型 ────────────────────────────────────────

add("Chapter", "线性模型", "基于输入特征线性组合的基本模型族", "3")

add("Algorithm", "线性回归", "通过线性函数拟合输入与连续输出之间关系的回归方法", "3")
add("Algorithm", "对数几率回归", "用Sigmoid函数将线性输出映射为概率，用于二分类问题", "3")
add("Algorithm", "感知机", "最简单的线性分类器，通过超平面划分两类数据", "3")
add("Algorithm", "线性判别分析", "寻找使类间距离最大、类内距离最小的投影方向", "3")
add("Algorithm", "最小二乘法", "通过最小化误差平方和求解线性回归参数的经典方法", "3")
add("Algorithm", "多分类 OvO", "将多分类问题拆分为多个一对一的二分类问题", "3")
add("Algorithm", "多分类 OvR", "将每个类别与其余所有类别做二分类", "3")

add("Method", "梯度下降", "沿损失函数梯度的反方向迭代更新参数的优化方法", "3")
add("Method", "正则化", "在损失函数中加入惩罚项以限制模型复杂度，防止过拟合", "3")

add("Concept", "超平面", "n维空间中维度为n-1的子空间，线性模型的决策边界", "3")

# ── 第4章：决策树 ──────────────────────────────────────────

add("Chapter", "决策树", "基于树形结构进行决策的可解释性模型", "4")

add("Algorithm", "ID3", "使用信息增益作为划分准则的决策树算法", "4")
add("Algorithm", "C4.5", "使用信息增益比作为划分准则，支持连续值和缺失值处理", "4")
add("Algorithm", "CART", "使用基尼指数作为划分准则，生成二叉决策树", "4")

add("Concept", "信息熵", "度量样本集合纯度的指标，熵越小纯度越高: -Σp·log(p)", "4")
add("Concept", "信息增益", "划分前后信息熵的减少量，值越大说明该特征的区分能力越强", "4")
add("Concept", "信息增益比", "信息增益与特征固有值的比值，克服信息增益偏好多值特征的缺点", "4")
add("Concept", "基尼指数", "度量样本集合不纯度的指标，基尼指数越小纯度越高", "4")
add("Concept", "剪枝", "通过去除部分节点来简化决策树，防止过拟合", "4")
add("Concept", "预剪枝", "在决策树生成过程中提前停止分裂", "4")
add("Concept", "后剪枝", "先生成完整决策树，再自底向上剪去不必要的子树", "4")
add("Method", "连续值处理", "对连续属性进行离散化或二分法处理", "4")
add("Method", "缺失值处理", "对含缺失值样本进行权重调整或概率分配", "4")

# ── 第5章：神经网络 ────────────────────────────────────────

add("Chapter", "神经网络", "模拟生物神经系统的非线性学习模型", "5")

add("Concept", "神经元", "神经网络的基本计算单元，对输入做加权求和后经激活函数输出", "5")
add("Concept", "激活函数", "引入非线性变换的函数，使网络能拟合复杂函数", "5")
add("Concept", "Sigmoid函数", "将输入映射到(0,1)区间的S型激活函数: 1/(1+e^(-x))", "5")
add("Concept", "ReLU函数", "取输入与0的较大值的激活函数: max(0,x)，训练效率高", "5")
add("Concept", "Tanh函数", "将输入映射到(-1,1)区间的激活函数，比Sigmoid收敛更快", "5")
add("Concept", "Softmax函数", "将输出向量转化为概率分布的激活函数，常用于多分类", "5")
add("Concept", "反向传播", "通过链式法则从输出层向输入层逐层计算梯度的算法", "5")
add("Concept", "损失函数", "度量模型预测值与真实值之间差距的目标函数", "5")

add("Algorithm", "多层感知机", "包含一个或多个隐藏层的前馈神经网络", "5")
add("Algorithm", "卷积神经网络", "利用卷积操作提取局部特征的深度网络，擅长图像处理", "5")
add("Algorithm", "循环神经网络", "具有循环连接的网络，擅长处理序列数据", "5")
add("Algorithm", "LSTM", "通过门控机制解决长程依赖问题的改进型RNN", "5")
add("Algorithm", "GRU", "LSTM的简化版本，门控更少但效果相当", "5")
add("Algorithm", "生成对抗网络", "由生成器和判别器对抗训练的生成模型", "5")
add("Algorithm", "Transformer", "基于自注意力机制的序列模型架构，NLP和CV领域主流", "5")

add("Method", "Dropout", "训练时随机丢弃部分神经元，防止过拟合的正则化方法", "5")
add("Method", "批归一化", "对每一层的输入做归一化处理，加速训练并提升稳定性", "5")
add("Method", "迁移学习", "将在一个任务上学到的知识迁移到另一个相关任务", "5")

add("Concept", "注意力机制", "使模型能够动态关注输入中重要部分的加权机制", "5")
add("Concept", "池化操作", "对特征图进行下采样以降低维度和计算量的操作", "5")
add("Concept", "卷积核", "在CNN中滑动并与输入做点积运算的小矩阵，用于特征提取", "5")
add("Concept", "门控机制", "LSTM/GRU中控制信息流通的遗忘门、输入门和输出门", "5")
add("Concept", "过拟合与正则化", "通过正则化、早停、Dropout等手段控制模型复杂度", "5")

# ── 第6章：支持向量机 ──────────────────────────────────────

add("Chapter", "支持向量机", "基于最大间隔原理的分类与回归模型", "6")

add("Algorithm", "SVM", "寻找最大间隔超平面的分类算法，具有良好的泛化能力", "6")
add("Algorithm", "软间隔SVM", "允许部分样本违反间隔约束的SVM变体，提高实用性", "6")
add("Algorithm", "支持向量回归", "将SVM思想扩展到回归任务，容忍一定误差的回归方法", "6")
add("Algorithm", "SMO算法", "将大规模QP问题分解为小规模子问题迭代求解的高效算法", "6")

add("Concept", "间隔", "分类超平面到最近训练样本的距离，SVM最大化此间隔", "6")
add("Concept", "支持向量", "距离分类超平面最近的训练样本，决定了决策边界", "6")
add("Concept", "核函数", "将低维输入映射到高维空间的隐式映射函数", "6")
add("Concept", "核技巧", "通过核函数在高维空间计算内积而无需显式映射", "6")
add("Concept", "对偶问题", "将SVM原始优化问题转化为更易求解的对偶形式", "6")
add("Concept", "RBF核", "径向基核函数，最常用的核函数，能处理非线性分类", "6")
add("Concept", "多项式核", "基于多项式展开的核函数，适合特定结构的数据", "6")

# ── 第7章：贝叶斯分类器 ──────────────────────────────────

add("Chapter", "贝叶斯分类器", "基于概率论和贝叶斯定理的分类方法", "7")

add("Concept", "贝叶斯定理", "描述后验概率与先验概率、似然之间关系的基本定理", "7")
add("Concept", "先验概率", "在观测到数据之前，基于已有知识对参数的概率估计", "7")
add("Concept", "后验概率", "在观测到数据之后，对参数更新后的概率估计", "7")
add("Concept", "极大似然估计", "选择使观测数据出现概率最大的参数值的估计方法", "7")
add("Concept", "条件独立性假设", "假设在给定类别的条件下，各特征之间相互独立", "7")

add("Algorithm", "朴素贝叶斯", "基于条件独立性假设的简单高效贝叶斯分类器", "7")
add("Algorithm", "高斯朴素贝叶斯", "假设连续特征服从高斯分布的朴素贝叶斯变体", "7")
add("Algorithm", "多项式朴素贝叶斯", "适用于离散特征计数数据的朴素贝叶斯变体", "7")
add("Algorithm", "贝叶斯网络", "用有向无环图表示变量间条件依赖关系的概率图模型", "7")
add("Algorithm", "半朴素贝叶斯", "放宽条件独立性假设，允许特征间存在有限依赖", "7")
add("Algorithm", "EM算法", "在含隐变量的概率模型中交替执行期望步和最大化步的迭代算法", "7")

add("Method", "拉普拉斯平滑", "对概率估计加一个小常数，避免因零概率导致整体概率为零", "7")

# ── 第8章：集成学习 ────────────────────────────────────────

add("Chapter", "集成学习", "通过组合多个基学习器来提升整体性能的方法", "8")

add("Concept", "集成学习", "构建并组合多个学习器来完成学习任务的方法论", "8")
add("Concept", "基学习器", "集成系统中的单个学习模型，通常为弱学习器", "8")
add("Concept", "多样性", "基学习器之间的差异性，集成效果好坏的关键因素", "8")

add("Algorithm", "Bagging", "基于自助采样的并行式集成方法，降低方差", "8")
add("Algorithm", "随机森林", "以决策树为基学习器的Bagging变体，额外引入特征随机选择", "8")
add("Algorithm", "AdaBoost", "自适应提升算法，每轮调整样本权重聚焦难分样本", "8")
add("Algorithm", "梯度提升", "在残差梯度方向上逐步添加新模型的Boosting方法", "8")
add("Algorithm", "XGBoost", "梯度提升的高效实现，加入正则化和二阶优化", "8")
add("Algorithm", "LightGBM", "微软提出的高效梯度提升框架，支持直方图算法和叶子生长策略", "8")
add("Algorithm", "Stacking", "用元学习器组合多个基学习器预测结果的分层集成方法", "8")
add("Algorithm", "投票法", "通过多数投票或加权投票组合多个分类器结果的简单集成策略", "8")

add("Method", "Bootstrap采样", "有放回地从原始数据集中随机采样，构建多样化的训练子集", "8")
add("Method", "误差修正输出码", "将多分类问题编码为多个二分类问题的编码集成方法", "8")

# ── 第9章：聚类 ────────────────────────────────────────────

add("Chapter", "聚类", "将数据自动分组的无监督学习方法", "9")

add("Algorithm", "K-Means", "基于距离的迭代聚类算法，将数据划分为K个簇", "9")
add("Algorithm", "K-Medoids", "用实际数据点作为簇中心的K-Means变体，对异常值更鲁棒", "9")
add("Algorithm", "层次聚类", "通过逐层合并或分裂构建层次化聚类结构", "9")
add("Algorithm", "DBSCAN", "基于密度的聚类算法，能发现任意形状的簇并识别噪声点", "9")
add("Algorithm", "高斯混合模型", "假设数据由多个高斯分布混合生成的概率聚类模型", "9")
add("Algorithm", "谱聚类", "基于图拉普拉斯矩阵特征分解的聚类方法", "9")

add("Concept", "簇", "聚类结果中同一组的数据点集合", "9")
add("Concept", "簇中心", "代表一个簇位置的点，如K-Means中的均值点", "9")
add("Concept", "肘部法则", "通过观察聚类数增加时指标变化趋势来选择最佳K值", "9")

add("Metric", "轮廓系数", "衡量样本与自身簇和其他簇的距离之比，取值[-1,1]", "9")
add("Metric", "Davies-Bouldin指数", "簇内距离与簇间距离之比的均值，越小越好", "9")
add("Metric", "纯度", "簇中占比最大的真实类别比例，衡量聚类与真实标签的一致性", "9")

# ── 第10章：降维与度量学习 ────────────────────────────────

add("Chapter", "降维与度量学习", "降低数据维度和学习合适距离度量的方法", "10")

add("Algorithm", "PCA", "通过正交变换将数据投影到方差最大的方向上实现降维", "10")
add("Algorithm", "核PCA", "利用核技巧在非线性空间中进行主成分分析", "10")
add("Algorithm", "LDA降维", "在有监督条件下寻找最佳投影方向实现降维", "10")
add("Algorithm", "t-SNE", "将高维数据映射到低维空间并保持局部邻域结构的可视化方法", "10")
add("Algorithm", "LLE", "保持局部线性关系的非线性降维方法", "10")
add("Algorithm", "MDS", "保持样本间距离关系的经典降维方法", "10")
add("Algorithm", "KNN", "基于K个最近邻投票的分类算法，属于惰性学习", "10")

add("Concept", "维度灾难", "随着维度增加，数据变得极度稀疏，距离度量失效的现象", "10")
add("Concept", "流形学习", "假设高维数据位于低维流形上的非线性降维思想", "10")
add("Concept", "度量学习", "从数据中学习合适的距离度量函数的方法", "10")

add("Method", "距离度量", "衡量两个样本间相似程度的数学函数", "10")
add("Method", "欧氏距离", "最常用的距离度量，两点间直线距离", "10")
add("Method", "曼哈顿距离", "各维度差的绝对值之和，也称城市街区距离", "10")
add("Method", "余弦相似度", "通过向量夹角的余弦值衡量方向相似性，忽略大小", "10")

# ── 第11章：特征选择与稀疏学习 ────────────────────────────

add("Chapter", "特征选择与稀疏学习", "从原始特征中筛选有用特征和学习稀疏表示的方法", "11")

add("Concept", "特征选择", "从原始特征集合中选择最相关特征子集的过程", "11")
add("Concept", "特征工程", "通过领域知识构造新特征以提升模型性能的实践", "11")
add("Concept", "稀疏性", "数据或模型中大部分元素为零的性质，有助于降维和可解释性", "11")
add("Concept", "字典学习", "学习一组基向量使得数据可以用稀疏线性组合表示", "11")

add("Method", "过滤式选择", "根据特征的统计特性独立于模型进行特征评分和选择", "11")
add("Method", "包裹式选择", "以学习器性能为评价准则，通过搜索策略选择特征子集", "11")
add("Method", "嵌入式选择", "在模型训练过程中自动完成特征选择的方法", "11")

add("Algorithm", "LASSO", "采用L1正则化实现特征选择和稀疏化的回归方法", "11")
add("Algorithm", "Ridge回归", "采用L2正则化缓解多重共线性问题的回归方法", "11")
add("Algorithm", "弹性网络", "同时使用L1和L2正则化的回归方法，兼具LASSO和Ridge优点", "11")

# ── 第12章：计算学习理论 ──────────────────────────────────

add("Chapter", "计算学习理论", "从理论角度分析学习算法的可行性和复杂度", "12")

add("Concept", "PAC学习", "可能近似正确学习框架，分析学习算法在有限样本下的可行性", "12")
add("Concept", "VC维", "衡量假设空间复杂度的指标，定义为能被shatter的最大样本数", "12")
add("Concept", "Rademacher复杂度", "基于随机噪声衡量假设空间复杂度的指标，比VC维更精细", "12")
add("Concept", "泛化误差界", "以高概率保证的泛化误差上界，指导模型选择", "12")
add("Concept", "结构风险最小化", "在经验风险基础上加入复杂度惩罚项的模型选择原则", "12")

# ── 第13章：半监督学习 ────────────────────────────────────

add("Chapter", "半监督学习", "同时利用有标记和无标记数据的学习范式", "13")

add("Concept", "半监督学习", "利用少量有标记数据和大量无标记数据共同训练的学习范式", "13")
add("Concept", "直推式学习", "仅针对特定无标记样本进行预测，不学习通用模型", "13")

add("Algorithm", "协同训练", "利用多视图数据，两个分类器互相为对方提供伪标记", "13")
add("Algorithm", "生成式半监督学习", "基于生成模型假设，用EM算法同时估计标记和模型参数", "13")
add("Algorithm", "半监督SVM", "在SVM目标中加入无标记数据的低密度分隔约束", "13")
add("Algorithm", "图半监督学习", "将数据构建为图，利用图结构传播标记信息", "13")
add("Algorithm", "自训练", "用已有模型预测无标记数据的伪标记，迭代扩充训练集", "13")

# ── 第14章：概率图模型 ────────────────────────────────────

add("Chapter", "概率图模型", "用图结构表示变量间概率依赖关系的模型", "14")

add("Concept", "概率图模型", "用图表示随机变量间条件依赖关系的概率模型框架", "14")
add("Concept", "有向图模型", "用有向边表示因果关系的概率图模型，也称贝叶斯网络", "14")
add("Concept", "无向图模型", "用无向边表示相关关系的概率图模型，也称马尔可夫随机场", "14")
add("Concept", "条件随机场", "在给定输入序列条件下对输出序列建模的判别式图模型", "14")
add("Concept", "马尔可夫毯", "使一个节点与图中其余节点条件独立的邻居节点集合", "14")

add("Algorithm", "隐马尔可夫模型", "含隐状态序列的经典有向图模型，广泛用于序列标注", "14")
add("Algorithm", "变量消元法", "通过逐步消去变量来精确计算边缘概率的推断算法", "14")
add("Algorithm", "信念传播", "在图上传递消息来近似计算边缘概率的推断算法", "14")
add("Algorithm", "MCMC", "通过构造马尔可夫链来近似采样和推断的随机方法", "14")
add("Algorithm", "变分推断", "用优化方法寻找最接近后验分布的简单分布族来近似推断", "14")
add("Algorithm", "吉布斯采样", "每次只采样一个变量的MCMC方法，实现简单", "14")

# ── 第15章：规则学习 ──────────────────────────────────────

add("Chapter", "规则学习", "学习由规则集构成的可解释模型", "15")

add("Concept", "规则学习", "从数据中学习一组if-then规则来进行预测的方法", "15")
add("Concept", "序贯覆盖法", "逐条学习规则，每学一条就覆盖已匹配的样本", "15")

add("Algorithm", "Apriori", "利用频繁项集性质的经典关联规则挖掘算法", "15")
add("Algorithm", "FP-Growth", "基于FP-tree结构的高效频繁项集挖掘算法", "15")

add("Concept", "关联规则", "描述数据项之间共现关系的规则，如{尿布}→{啤酒}", "15")
add("Concept", "支持度", "项集在所有事务中出现的频率", "15")
add("Concept", "置信度", "在前提出现条件下结论也出现的条件概率", "15")

# ── 第16章：强化学习 ──────────────────────────────────────

add("Chapter", "强化学习", "通过与环境交互获得奖励来学习最优策略的方法", "16")

add("Concept", "强化学习", "智能体通过与环境交互，最大化累积奖励的学习范式", "16")
add("Concept", "马尔可夫决策过程", "强化学习的数学框架，包含状态、动作、转移概率和奖励", "16")
add("Concept", "状态", "环境中某个时刻的完整描述信息", "16")
add("Concept", "动作", "智能体在某个状态下可以执行的操作", "16")
add("Concept", "奖励", "环境对智能体动作的即时反馈信号", "16")
add("Concept", "策略", "从状态到动作的映射，智能体的行为规则", "16")
add("Concept", "值函数", "从某个状态出发的期望累积奖励，衡量状态的长期价值", "16")
add("Concept", "Q值函数", "在某状态执行某动作后的期望累积奖励", "16")
add("Concept", "探索与利用", "尝试新动作(探索)与选择已知最优动作(利用)之间的权衡", "16")

add("Algorithm", "Q-learning", "基于时序差分的无模型强化学习算法，学习最优Q值", "16")
add("Algorithm", "Sarsa", "基于时序差分的同策略强化学习算法", "16")
add("Algorithm", "策略梯度", "直接参数化并优化策略函数的强化学习方法", "16")
add("Algorithm", "DQN", "用深度神经网络近似Q值函数的深度强化学习算法", "16")
add("Algorithm", "Actor-Critic", "结合策略梯度和值函数方法的混合架构", "16")

# ── 通用优化方法（跨章节） ────────────────────────────────

add("Method", "SGD", "随机梯度下降，每次用一个或小批量样本更新参数", "")
add("Method", "小批量梯度下降", "每次用一小批样本计算梯度，兼顾效率和稳定性", "")
add("Method", "动量法", "引入历史梯度累积项加速收敛并减少震荡", "")
add("Method", "Adam优化器", "结合动量和自适应学习率的优化算法，目前最常用", "")
add("Method", "学习率衰减", "训练过程中逐步减小学习率以提高收敛精度", "")
add("Method", "早停法", "在验证集误差不再下降时提前终止训练，防止过拟合", "")

add("Concept", "交叉熵损失", "分类任务中最常用的损失函数，衡量预测分布与真实分布的差异", "")
add("Concept", "Hinge损失", "SVM使用的损失函数，惩罚间隔内的所有预测", "")
add("Concept", "对数损失", "对数几率回归使用的损失函数，等价于交叉熵的二分类形式", "")
add("Concept", "Huber损失", "结合了MSE和MAE的优点，对异常值更鲁棒", "")

add("Concept", "超参数", "在训练之前需要人工设定的模型配置参数", "")
add("Concept", "学习率", "控制每次参数更新步幅大小的超参数", "")
add("Concept", "批大小", "每次梯度更新使用的样本数量", "")
add("Concept", "训练轮次", "整个训练集被完整遍历的次数", "")
add("Concept", "验证集", "用于调整超参数和模型选择的数据子集，不参与训练", "")

add("Concept", "特征缩放", "将不同量纲的特征缩放到相近范围，加速收敛", "")
add("Method", "标准化", "将特征缩放为均值0方差1的分布，也称Z-score归一化", "")
add("Method", "最小-最大归一化", "将特征线性缩放到[0,1]区间", "")
add("Method", "独热编码", "将类别变量转化为二进制向量表示", "")
add("Method", "数据增强", "通过对已有数据做变换来扩充训练集规模", "")

add("Concept", "交叉验证调参", "用交叉验证评估不同超参数组合的性能", "")
add("Method", "网格搜索", "穷举搜索指定超参数空间的所有组合", "")
add("Method", "随机搜索", "在超参数空间中随机采样进行评估", "")
add("Method", "贝叶斯优化", "用代理模型指导超参数搜索方向的智能调参方法", "")

# ── 第5章补充：深度学习进阶概念 ──────────────────────────────

add("Concept", "残差连接", "将输入直接跳过若干层加到输出上，解决深层网络退化问题", "5")
add("Algorithm", "ResNet", "利用残差连接构建的超深卷积网络，ImageNet冠军架构", "5")
add("Concept", "自注意力", "序列中每个位置关注所有其他位置来捕获全局依赖", "5")
add("Concept", "多头注意力", "并行运行多组自注意力以捕获不同子空间的关系", "5")
add("Concept", "位置编码", "为Transformer输入添加位置信息以弥补无序列归纳偏置", "5")
add("Algorithm", "BERT", "基于Transformer编码器的预训练语言模型，双向上下文", "5")
add("Algorithm", "GPT", "基于Transformer解码器的自回归语言模型", "5")
add("Method", "预训练与微调", "先在大规模数据上预训练，再在下游任务上微调的范式", "5")
add("Concept", "梯度消失", "深层网络中梯度逐层衰减导致浅层参数难以更新", "5")
add("Concept", "梯度爆炸", "深层网络中梯度逐层放大导致参数更新不稳定", "5")

# ── 第6章补充：SVM 进阶 ──────────────────────────────────

add("Concept", "KKT条件", "约束优化问题最优解的必要条件，SVM对偶问题求解的基础", "6")
add("Concept", "松弛变量", "软间隔SVM中允许样本违反约束的变量", "6")
add("Concept", "惩罚参数C", "控制软间隔SVM中误分类惩罚力度的超参数", "6")

# ── 第9章补充：聚类进阶 ──────────────────────────────────

add("Concept", "密度直达", "DBSCAN中从核心对象出发直接密度可达的关系", "9")
add("Concept", "密度可达", "DBSCAN中通过密度直达关系传递连接的点集", "9")
add("Concept", "核心对象", "DBSCAN中邻域内点数大于MinPts的数据点", "9")
add("Algorithm", "OPTICS", "DBSCAN的扩展，自动发现不同密度的聚类结构", "9")
add("Algorithm", "层次聚类-凝聚", "自底向上逐步合并最近簇的层次聚类方法", "9")
add("Algorithm", "层次聚类-分裂", "自顶向下逐步分裂的层次聚类方法", "9")


# ═══════════════════════════════════════════════════════════
# 第二部分：关系定义
# ═══════════════════════════════════════════════════════════

relationships = []


def rel(src_label, src_name, rel_type, dst_label, dst_name, props=None):
    """添加一条关系"""
    r = {
        "src_label": src_label,
        "src_name": src_name,
        "type": rel_type,
        "dst_label": dst_label,
        "dst_name": dst_name,
    }
    if props:
        r["props"] = props
    relationships.append(r)


# ── 章节包含概念/算法 ──

# 第1章
rel("Chapter", "绪论", "CONTAINS", "Concept", "机器学习")
rel("Chapter", "绪论", "CONTAINS", "Concept", "数据集")
rel("Chapter", "绪论", "CONTAINS", "Concept", "样本")
rel("Chapter", "绪论", "CONTAINS", "Concept", "特征")
rel("Chapter", "绪论", "CONTAINS", "Concept", "标记")
rel("Chapter", "绪论", "CONTAINS", "Concept", "训练集")
rel("Chapter", "绪论", "CONTAINS", "Concept", "测试集")
rel("Chapter", "绪论", "CONTAINS", "Concept", "假设空间")
rel("Chapter", "绪论", "CONTAINS", "Concept", "版本空间")
rel("Chapter", "绪论", "CONTAINS", "Concept", "归纳偏好")
rel("Chapter", "绪论", "CONTAINS", "Concept", "奥卡姆剃刀")
rel("Chapter", "绪论", "CONTAINS", "Concept", "没有免费的午餐定理")
rel("Chapter", "绪论", "CONTAINS", "Task", "监督学习")
rel("Chapter", "绪论", "CONTAINS", "Task", "无监督学习")
rel("Chapter", "绪论", "CONTAINS", "Task", "分类")
rel("Chapter", "绪论", "CONTAINS", "Task", "回归")
rel("Chapter", "绪论", "CONTAINS", "Task", "聚类")

# 第2章
rel("Chapter", "模型评估与选择", "CONTAINS", "Concept", "过拟合")
rel("Chapter", "模型评估与选择", "CONTAINS", "Concept", "欠拟合")
rel("Chapter", "模型评估与选择", "CONTAINS", "Concept", "泛化能力")
rel("Chapter", "模型评估与选择", "CONTAINS", "Concept", "偏差-方差分解")
rel("Chapter", "模型评估与选择", "CONTAINS", "Method", "留出法")
rel("Chapter", "模型评估与选择", "CONTAINS", "Method", "交叉验证")
rel("Chapter", "模型评估与选择", "CONTAINS", "Method", "自助法")
rel("Chapter", "模型评估与选择", "CONTAINS", "Metric", "准确率")
rel("Chapter", "模型评估与选择", "CONTAINS", "Metric", "精确率")
rel("Chapter", "模型评估与选择", "CONTAINS", "Metric", "召回率")
rel("Chapter", "模型评估与选择", "CONTAINS", "Metric", "F1分数")
rel("Chapter", "模型评估与选择", "CONTAINS", "Metric", "ROC曲线")
rel("Chapter", "模型评估与选择", "CONTAINS", "Metric", "AUC")
rel("Chapter", "模型评估与选择", "CONTAINS", "Metric", "均方误差")
rel("Chapter", "模型评估与选择", "CONTAINS", "Metric", "混淆矩阵")

# 第3-16章的章节包含关系
for chap_name, items in [
    ("线性模型", [
        ("Algorithm", "线性回归"), ("Algorithm", "对数几率回归"),
        ("Algorithm", "感知机"), ("Algorithm", "线性判别分析"),
        ("Algorithm", "最小二乘法"), ("Method", "梯度下降"),
        ("Method", "正则化"), ("Concept", "超平面"),
    ]),
    ("决策树", [
        ("Algorithm", "ID3"), ("Algorithm", "C4.5"), ("Algorithm", "CART"),
        ("Concept", "信息熵"), ("Concept", "信息增益"),
        ("Concept", "信息增益比"), ("Concept", "基尼指数"),
        ("Concept", "剪枝"), ("Method", "连续值处理"),
    ]),
    ("神经网络", [
        ("Algorithm", "多层感知机"), ("Algorithm", "卷积神经网络"),
        ("Algorithm", "循环神经网络"), ("Algorithm", "LSTM"),
        ("Algorithm", "Transformer"), ("Concept", "反向传播"),
        ("Concept", "激活函数"), ("Method", "Dropout"),
        ("Method", "批归一化"), ("Method", "迁移学习"),
    ]),
    ("支持向量机", [
        ("Algorithm", "SVM"), ("Algorithm", "软间隔SVM"),
        ("Algorithm", "支持向量回归"), ("Algorithm", "SMO算法"),
        ("Concept", "间隔"), ("Concept", "支持向量"),
        ("Concept", "核函数"), ("Concept", "核技巧"),
        ("Concept", "RBF核"),
    ]),
    ("贝叶斯分类器", [
        ("Algorithm", "朴素贝叶斯"), ("Algorithm", "贝叶斯网络"),
        ("Algorithm", "EM算法"), ("Concept", "贝叶斯定理"),
        ("Concept", "先验概率"), ("Concept", "后验概率"),
        ("Concept", "极大似然估计"), ("Method", "拉普拉斯平滑"),
    ]),
    ("集成学习", [
        ("Algorithm", "Bagging"), ("Algorithm", "随机森林"),
        ("Algorithm", "AdaBoost"), ("Algorithm", "梯度提升"),
        ("Algorithm", "XGBoost"), ("Algorithm", "Stacking"),
        ("Concept", "集成学习"), ("Concept", "基学习器"),
        ("Concept", "多样性"), ("Method", "Bootstrap采样"),
    ]),
    ("聚类", [
        ("Algorithm", "K-Means"), ("Algorithm", "层次聚类"),
        ("Algorithm", "DBSCAN"), ("Algorithm", "高斯混合模型"),
        ("Concept", "簇"), ("Metric", "轮廓系数"),
    ]),
    ("降维与度量学习", [
        ("Algorithm", "PCA"), ("Algorithm", "t-SNE"),
        ("Algorithm", "KNN"), ("Concept", "维度灾难"),
        ("Concept", "流形学习"), ("Concept", "度量学习"),
    ]),
    ("特征选择与稀疏学习", [
        ("Algorithm", "LASSO"), ("Algorithm", "Ridge回归"),
        ("Concept", "特征选择"), ("Concept", "特征工程"),
        ("Concept", "稀疏性"),
    ]),
    ("计算学习理论", [
        ("Concept", "PAC学习"), ("Concept", "VC维"),
        ("Concept", "Rademacher复杂度"), ("Concept", "泛化误差界"),
    ]),
    ("半监督学习", [
        ("Concept", "半监督学习"), ("Algorithm", "协同训练"),
        ("Algorithm", "自训练"), ("Algorithm", "图半监督学习"),
    ]),
    ("概率图模型", [
        ("Algorithm", "隐马尔可夫模型"), ("Algorithm", "信念传播"),
        ("Algorithm", "MCMC"), ("Algorithm", "变分推断"),
        ("Concept", "概率图模型"), ("Concept", "条件随机场"),
    ]),
    ("规则学习", [
        ("Algorithm", "Apriori"), ("Algorithm", "FP-Growth"),
        ("Concept", "关联规则"), ("Concept", "支持度"), ("Concept", "置信度"),
    ]),
    ("强化学习", [
        ("Algorithm", "Q-learning"), ("Algorithm", "DQN"),
        ("Algorithm", "策略梯度"), ("Concept", "强化学习"),
        ("Concept", "马尔可夫决策过程"), ("Concept", "Q值函数"),
        ("Concept", "探索与利用"),
    ]),
]:
    for lbl, name in items:
        rel("Chapter", chap_name, "CONTAINS", lbl, name)

# 补充章节包含关系：新增的章节内节点
for chap_name, items in [
    ("神经网络", [
        ("Concept", "残差连接"), ("Algorithm", "ResNet"),
        ("Concept", "自注意力"), ("Concept", "多头注意力"),
        ("Concept", "位置编码"), ("Algorithm", "BERT"), ("Algorithm", "GPT"),
        ("Method", "预训练与微调"), ("Concept", "梯度消失"), ("Concept", "梯度爆炸"),
    ]),
    ("支持向量机", [
        ("Concept", "KKT条件"), ("Concept", "松弛变量"), ("Concept", "惩罚参数C"),
    ]),
    ("聚类", [
        ("Concept", "密度直达"), ("Concept", "密度可达"), ("Concept", "核心对象"),
        ("Algorithm", "OPTICS"), ("Algorithm", "层次聚类-凝聚"), ("Algorithm", "层次聚类-分裂"),
    ]),
]:
    for lbl, name in items:
        rel("Chapter", chap_name, "CONTAINS", lbl, name)


# ── 章节前置关系（学习顺序） ──

rel("Chapter", "绪论", "PREREQUISITE_OF", "Chapter", "模型评估与选择")
rel("Chapter", "绪论", "PREREQUISITE_OF", "Chapter", "线性模型")
rel("Chapter", "线性模型", "PREREQUISITE_OF", "Chapter", "决策树")
rel("Chapter", "线性模型", "PREREQUISITE_OF", "Chapter", "神经网络")
rel("Chapter", "线性模型", "PREREQUISITE_OF", "Chapter", "支持向量机")
rel("Chapter", "绪论", "PREREQUISITE_OF", "Chapter", "贝叶斯分类器")
rel("Chapter", "模型评估与选择", "PREREQUISITE_OF", "Chapter", "集成学习")
rel("Chapter", "绪论", "PREREQUISITE_OF", "Chapter", "聚类")
rel("Chapter", "线性模型", "PREREQUISITE_OF", "Chapter", "降维与度量学习")
rel("Chapter", "线性模型", "PREREQUISITE_OF", "Chapter", "特征选择与稀疏学习")
rel("Chapter", "模型评估与选择", "PREREQUISITE_OF", "Chapter", "计算学习理论")
rel("Chapter", "贝叶斯分类器", "PREREQUISITE_OF", "Chapter", "概率图模型")
rel("Chapter", "绪论", "PREREQUISITE_OF", "Chapter", "半监督学习")
rel("Chapter", "绪论", "PREREQUISITE_OF", "Chapter", "规则学习")
rel("Chapter", "神经网络", "PREREQUISITE_OF", "Chapter", "强化学习")

# ── 概念/算法间的前置与依赖关系 ──

# 基础概念链
rel("Concept", "机器学习", "PREREQUISITE_OF", "Task", "监督学习")
rel("Concept", "机器学习", "PREREQUISITE_OF", "Task", "无监督学习")
rel("Concept", "数据集", "PART_OF", "Concept", "样本")
rel("Concept", "样本", "PART_OF", "Concept", "特征")
rel("Concept", "样本", "PART_OF", "Concept", "标记")
rel("Concept", "训练集", "USED_IN", "Task", "监督学习")
rel("Concept", "测试集", "USED_IN", "Method", "留出法")

# 模型评估
rel("Concept", "过拟合", "COMPARE_WITH", "Concept", "欠拟合")
rel("Concept", "泛化能力", "EVALUATED_BY", "Metric", "准确率")
rel("Concept", "偏差-方差分解", "PART_OF", "Concept", "偏差")
rel("Concept", "偏差-方差分解", "PART_OF", "Concept", "方差")
rel("Method", "留出法", "COMPARE_WITH", "Method", "交叉验证")
rel("Method", "交叉验证", "COMPARE_WITH", "Method", "自助法")
rel("Metric", "精确率", "PART_OF", "Metric", "F1分数")
rel("Metric", "召回率", "PART_OF", "Metric", "F1分数")
rel("Metric", "ROC曲线", "PART_OF", "Metric", "AUC")
rel("Metric", "混淆矩阵", "PART_OF", "Metric", "准确率")
rel("Metric", "混淆矩阵", "PART_OF", "Metric", "精确率")
rel("Metric", "混淆矩阵", "PART_OF", "Metric", "召回率")

# 线性模型
rel("Algorithm", "线性回归", "USED_IN", "Task", "回归")
rel("Algorithm", "对数几率回归", "USED_IN", "Task", "分类")
rel("Algorithm", "感知机", "USED_IN", "Task", "分类")
rel("Algorithm", "线性判别分析", "USED_IN", "Task", "分类")
rel("Algorithm", "最小二乘法", "USED_IN", "Algorithm", "线性回归")
rel("Method", "梯度下降", "USED_IN", "Algorithm", "线性回归")
rel("Method", "正则化", "USED_IN", "Concept", "过拟合")
rel("Concept", "超平面", "USED_IN", "Algorithm", "感知机")
rel("Concept", "超平面", "USED_IN", "Algorithm", "SVM")

# 决策树
rel("Concept", "信息熵", "USED_IN", "Algorithm", "ID3")
rel("Concept", "信息增益", "USED_IN", "Algorithm", "ID3")
rel("Concept", "信息增益比", "USED_IN", "Algorithm", "C4.5")
rel("Concept", "基尼指数", "USED_IN", "Algorithm", "CART")
rel("Concept", "剪枝", "PART_OF", "Concept", "预剪枝")
rel("Concept", "剪枝", "PART_OF", "Concept", "后剪枝")
rel("Concept", "剪枝", "USED_IN", "Concept", "过拟合")
rel("Algorithm", "ID3", "COMPARE_WITH", "Algorithm", "C4.5")
rel("Algorithm", "C4.5", "COMPARE_WITH", "Algorithm", "CART")

# 神经网络
rel("Concept", "激活函数", "PART_OF", "Concept", "Sigmoid函数")
rel("Concept", "激活函数", "PART_OF", "Concept", "ReLU函数")
rel("Concept", "激活函数", "PART_OF", "Concept", "Tanh函数")
rel("Concept", "激活函数", "PART_OF", "Concept", "Softmax函数")
rel("Concept", "神经元", "PREREQUISITE_OF", "Algorithm", "多层感知机")
rel("Concept", "反向传播", "USED_IN", "Algorithm", "多层感知机")
rel("Concept", "损失函数", "PREREQUISITE_OF", "Concept", "反向传播")
rel("Algorithm", "卷积神经网络", "PREREQUISITE_OF", "Concept", "卷积核")
rel("Algorithm", "卷积神经网络", "PREREQUISITE_OF", "Concept", "池化操作")
rel("Algorithm", "LSTM", "PREREQUISITE_OF", "Concept", "门控机制")
rel("Algorithm", "GRU", "PREREQUISITE_OF", "Concept", "门控机制")
rel("Algorithm", "循环神经网络", "PREREQUISITE_OF", "Algorithm", "LSTM")
rel("Algorithm", "循环神经网络", "PREREQUISITE_OF", "Algorithm", "GRU")
rel("Algorithm", "Transformer", "PREREQUISITE_OF", "Concept", "注意力机制")
rel("Method", "Dropout", "USED_IN", "Concept", "过拟合")
rel("Algorithm", "多层感知机", "PREREQUISITE_OF", "Algorithm", "卷积神经网络")
rel("Algorithm", "多层感知机", "PREREQUISITE_OF", "Algorithm", "循环神经网络")

# 支持向量机
rel("Concept", "间隔", "PREREQUISITE_OF", "Algorithm", "SVM")
rel("Concept", "支持向量", "PREREQUISITE_OF", "Algorithm", "SVM")
rel("Algorithm", "SVM", "PREREQUISITE_OF", "Algorithm", "软间隔SVM")
rel("Concept", "核函数", "USED_IN", "Algorithm", "SVM")
rel("Concept", "核技巧", "USED_IN", "Concept", "核函数")
rel("Concept", "RBF核", "PART_OF", "Concept", "核函数")
rel("Concept", "多项式核", "PART_OF", "Concept", "核函数")
rel("Algorithm", "SMO算法", "USED_IN", "Algorithm", "SVM")
rel("Algorithm", "SVM", "USED_IN", "Task", "分类")
rel("Algorithm", "支持向量回归", "USED_IN", "Task", "回归")

# 贝叶斯
rel("Concept", "贝叶斯定理", "PREREQUISITE_OF", "Algorithm", "朴素贝叶斯")
rel("Concept", "条件独立性假设", "PREREQUISITE_OF", "Algorithm", "朴素贝叶斯")
rel("Algorithm", "朴素贝叶斯", "PREREQUISITE_OF", "Algorithm", "高斯朴素贝叶斯")
rel("Algorithm", "朴素贝叶斯", "PREREQUISITE_OF", "Algorithm", "多项式朴素贝叶斯")
rel("Algorithm", "朴素贝叶斯", "PREREQUISITE_OF", "Algorithm", "半朴素贝叶斯")
rel("Algorithm", "朴素贝叶斯", "USED_IN", "Task", "分类")
rel("Method", "拉普拉斯平滑", "USED_IN", "Algorithm", "朴素贝叶斯")
rel("Concept", "极大似然估计", "PREREQUISITE_OF", "Algorithm", "EM算法")

# 集成学习
rel("Algorithm", "Bagging", "PREREQUISITE_OF", "Algorithm", "随机森林")
rel("Algorithm", "AdaBoost", "PREREQUISITE_OF", "Algorithm", "梯度提升")
rel("Algorithm", "梯度提升", "PREREQUISITE_OF", "Algorithm", "XGBoost")
rel("Algorithm", "梯度提升", "PREREQUISITE_OF", "Algorithm", "LightGBM")
rel("Algorithm", "Bagging", "COMPARE_WITH", "Algorithm", "AdaBoost")
rel("Method", "Bootstrap采样", "USED_IN", "Algorithm", "Bagging")
rel("Algorithm", "随机森林", "USED_IN", "Task", "分类")
rel("Algorithm", "XGBoost", "USED_IN", "Task", "分类")
rel("Concept", "多样性", "PREREQUISITE_OF", "Concept", "集成学习")

# 聚类
rel("Algorithm", "K-Means", "USED_IN", "Task", "聚类")
rel("Algorithm", "层次聚类", "USED_IN", "Task", "聚类")
rel("Algorithm", "DBSCAN", "USED_IN", "Task", "聚类")
rel("Algorithm", "K-Means", "COMPARE_WITH", "Algorithm", "DBSCAN")
rel("Concept", "簇", "PREREQUISITE_OF", "Algorithm", "K-Means")
rel("Algorithm", "K-Means", "EVALUATED_BY", "Metric", "轮廓系数")
rel("Algorithm", "高斯混合模型", "PREREQUISITE_OF", "Algorithm", "EM算法")

# 降维
rel("Algorithm", "PCA", "PREREQUISITE_OF", "Algorithm", "核PCA")
rel("Concept", "维度灾难", "PREREQUISITE_OF", "Concept", "流形学习")
rel("Algorithm", "PCA", "COMPARE_WITH", "Algorithm", "t-SNE")
rel("Algorithm", "KNN", "USED_IN", "Task", "分类")
rel("Method", "欧氏距离", "PART_OF", "Concept", "距离度量")
rel("Method", "曼哈顿距离", "PART_OF", "Concept", "距离度量")
rel("Method", "余弦相似度", "PART_OF", "Concept", "距离度量")
rel("Concept", "距离度量", "USED_IN", "Algorithm", "KNN")
rel("Concept", "距离度量", "USED_IN", "Algorithm", "K-Means")

# 特征选择
rel("Algorithm", "LASSO", "COMPARE_WITH", "Algorithm", "Ridge回归")
rel("Algorithm", "弹性网络", "PART_OF", "Algorithm", "LASSO")
rel("Algorithm", "弹性网络", "PART_OF", "Algorithm", "Ridge回归")
rel("Method", "过滤式选择", "COMPARE_WITH", "Method", "包裹式选择")
rel("Method", "嵌入式选择", "USED_IN", "Algorithm", "LASSO")

# 概率图模型
rel("Concept", "概率图模型", "PART_OF", "Concept", "有向图模型")
rel("Concept", "概率图模型", "PART_OF", "Concept", "无向图模型")
rel("Algorithm", "隐马尔可夫模型", "PART_OF", "Concept", "有向图模型")
rel("Algorithm", "信念传播", "USED_IN", "Concept", "概率图模型")
rel("Algorithm", "MCMC", "USED_IN", "Concept", "概率图模型")
rel("Algorithm", "变分推断", "COMPARE_WITH", "Algorithm", "MCMC")
rel("Algorithm", "吉布斯采样", "PART_OF", "Algorithm", "MCMC")

# 规则学习
rel("Algorithm", "Apriori", "USED_IN", "Concept", "关联规则")
rel("Algorithm", "FP-Growth", "USED_IN", "Concept", "关联规则")
rel("Algorithm", "Apriori", "COMPARE_WITH", "Algorithm", "FP-Growth")
rel("Concept", "支持度", "USED_IN", "Concept", "关联规则")
rel("Concept", "置信度", "USED_IN", "Concept", "关联规则")

# 强化学习
rel("Concept", "强化学习", "PREREQUISITE_OF", "Concept", "马尔可夫决策过程")
rel("Concept", "Q值函数", "PREREQUISITE_OF", "Algorithm", "Q-learning")
rel("Algorithm", "Q-learning", "PREREQUISITE_OF", "Algorithm", "DQN")
rel("Concept", "探索与利用", "PREREQUISITE_OF", "Algorithm", "Q-learning")
rel("Algorithm", "Q-learning", "COMPARE_WITH", "Algorithm", "Sarsa")
rel("Algorithm", "DQN", "PART_OF", "Algorithm", "卷积神经网络")

# ── 算法/模型与任务的关系 ──

rel("Algorithm", "对数几率回归", "EVALUATED_BY", "Metric", "准确率")
rel("Algorithm", "SVM", "EVALUATED_BY", "Metric", "准确率")
rel("Algorithm", "随机森林", "EVALUATED_BY", "Metric", "准确率")
rel("Algorithm", "K-Means", "EVALUATED_BY", "Metric", "轮廓系数")
rel("Algorithm", "线性回归", "EVALUATED_BY", "Metric", "均方误差")

# 半监督与监督的关系
rel("Concept", "半监督学习", "PREREQUISITE_OF", "Algorithm", "协同训练")
rel("Concept", "半监督学习", "PREREQUISITE_OF", "Algorithm", "自训练")
rel("Concept", "半监督学习", "PREREQUISITE_OF", "Algorithm", "图半监督学习")

# 计算学习理论
rel("Concept", "PAC学习", "PREREQUISITE_OF", "Concept", "VC维")
rel("Concept", "VC维", "PREREQUISITE_OF", "Concept", "泛化误差界")
rel("Concept", "泛化误差界", "PREREQUISITE_OF", "Concept", "结构风险最小化")

# ── 通用优化方法与训练 ──

rel("Method", "梯度下降", "PREREQUISITE_OF", "Method", "SGD")
rel("Method", "SGD", "PREREQUISITE_OF", "Method", "小批量梯度下降")
rel("Method", "SGD", "PREREQUISITE_OF", "Method", "动量法")
rel("Method", "动量法", "PREREQUISITE_OF", "Method", "Adam优化器")
rel("Method", "Adam优化器", "USED_IN", "Algorithm", "多层感知机")
rel("Method", "Adam优化器", "USED_IN", "Algorithm", "卷积神经网络")
rel("Method", "Adam优化器", "USED_IN", "Algorithm", "Transformer")
rel("Method", "SGD", "USED_IN", "Algorithm", "线性回归")
rel("Method", "SGD", "USED_IN", "Algorithm", "对数几率回归")
rel("Method", "学习率衰减", "USED_IN", "Method", "Adam优化器")
rel("Method", "早停法", "USED_IN", "Concept", "过拟合")
rel("Concept", "学习率", "PART_OF", "Concept", "超参数")
rel("Concept", "批大小", "PART_OF", "Concept", "超参数")
rel("Concept", "训练轮次", "PART_OF", "Concept", "超参数")
rel("Concept", "学习率", "USED_IN", "Method", "梯度下降")
rel("Concept", "验证集", "USED_IN", "Method", "交叉验证")
rel("Concept", "验证集", "USED_IN", "Method", "早停法")
rel("Concept", "验证集", "COMPARE_WITH", "Concept", "测试集")

# ── 损失函数体系 ──

rel("Concept", "交叉熵损失", "USED_IN", "Algorithm", "对数几率回归")
rel("Concept", "交叉熵损失", "USED_IN", "Algorithm", "多层感知机")
rel("Concept", "Hinge损失", "USED_IN", "Algorithm", "SVM")
rel("Concept", "对数损失", "USED_IN", "Algorithm", "对数几率回归")
rel("Concept", "Huber损失", "USED_IN", "Algorithm", "线性回归")
rel("Concept", "交叉熵损失", "COMPARE_WITH", "Concept", "Hinge损失")
rel("Concept", "损失函数", "PART_OF", "Concept", "交叉熵损失")
rel("Concept", "损失函数", "PART_OF", "Concept", "Hinge损失")
rel("Concept", "损失函数", "PART_OF", "Concept", "对数损失")
rel("Concept", "损失函数", "PART_OF", "Concept", "Huber损失")
rel("Concept", "损失函数", "PREREQUISITE_OF", "Concept", "反向传播")
rel("Concept", "均方误差", "PART_OF", "Concept", "损失函数")

# ── 特征工程与数据预处理 ──

rel("Method", "标准化", "PART_OF", "Concept", "特征缩放")
rel("Method", "最小-最大归一化", "PART_OF", "Concept", "特征缩放")
rel("Method", "独热编码", "USED_IN", "Concept", "特征工程")
rel("Method", "数据增强", "USED_IN", "Algorithm", "卷积神经网络")
rel("Concept", "特征缩放", "USED_IN", "Algorithm", "SVM")
rel("Concept", "特征缩放", "USED_IN", "Algorithm", "KNN")
rel("Concept", "特征缩放", "USED_IN", "Algorithm", "PCA")
rel("Concept", "特征缩放", "USED_IN", "Algorithm", "K-Means")
rel("Concept", "特征工程", "PREREQUISITE_OF", "Concept", "特征选择")

# ── 超参数调优 ──

rel("Method", "网格搜索", "USED_IN", "Concept", "交叉验证调参")
rel("Method", "随机搜索", "USED_IN", "Concept", "交叉验证调参")
rel("Method", "贝叶斯优化", "USED_IN", "Concept", "交叉验证调参")
rel("Method", "网格搜索", "COMPARE_WITH", "Method", "随机搜索")
rel("Method", "随机搜索", "COMPARE_WITH", "Method", "贝叶斯优化")
rel("Concept", "交叉验证调参", "USED_IN", "Method", "交叉验证")
rel("Concept", "惩罚参数C", "USED_IN", "Algorithm", "软间隔SVM")

# ── 深度学习进阶（第5章补充） ──

rel("Concept", "残差连接", "USED_IN", "Algorithm", "ResNet")
rel("Algorithm", "ResNet", "PREREQUISITE_OF", "Algorithm", "卷积神经网络")
rel("Algorithm", "Transformer", "PREREQUISITE_OF", "Concept", "自注意力")
rel("Concept", "自注意力", "PREREQUISITE_OF", "Concept", "多头注意力")
rel("Concept", "自注意力", "PREREQUISITE_OF", "Concept", "位置编码")
rel("Algorithm", "Transformer", "PREREQUISITE_OF", "Algorithm", "BERT")
rel("Algorithm", "Transformer", "PREREQUISITE_OF", "Algorithm", "GPT")
rel("Algorithm", "BERT", "COMPARE_WITH", "Algorithm", "GPT")
rel("Method", "迁移学习", "PREREQUISITE_OF", "Method", "预训练与微调")
rel("Method", "预训练与微调", "USED_IN", "Algorithm", "BERT")
rel("Method", "预训练与微调", "USED_IN", "Algorithm", "GPT")
rel("Concept", "梯度消失", "COMPARE_WITH", "Concept", "梯度爆炸")
rel("Concept", "梯度消失", "USED_IN", "Algorithm", "LSTM")
rel("Concept", "残差连接", "USED_IN", "Concept", "梯度消失")
rel("Algorithm", "多层感知机", "PREREQUISITE_OF", "Algorithm", "ResNet")
rel("Method", "批归一化", "USED_IN", "Concept", "梯度消失")

# ── SVM 进阶（第6章补充） ──

rel("Concept", "KKT条件", "PREREQUISITE_OF", "Concept", "对偶问题")
rel("Concept", "松弛变量", "USED_IN", "Algorithm", "软间隔SVM")
rel("Concept", "惩罚参数C", "PART_OF", "Algorithm", "软间隔SVM")
rel("Algorithm", "SVM", "PREREQUISITE_OF", "Algorithm", "核PCA")
rel("Concept", "核技巧", "USED_IN", "Algorithm", "核PCA")

# ── 聚类进阶（第9章补充） ──

rel("Concept", "核心对象", "PREREQUISITE_OF", "Concept", "密度直达")
rel("Concept", "密度直达", "PREREQUISITE_OF", "Concept", "密度可达")
rel("Algorithm", "DBSCAN", "PREREQUISITE_OF", "Concept", "核心对象")
rel("Algorithm", "DBSCAN", "PREREQUISITE_OF", "Algorithm", "OPTICS")
rel("Algorithm", "DBSCAN", "EVALUATED_BY", "Metric", "轮廓系数")
rel("Algorithm", "层次聚类-凝聚", "PART_OF", "Algorithm", "层次聚类")
rel("Algorithm", "层次聚类-分裂", "PART_OF", "Algorithm", "层次聚类")
rel("Algorithm", "层次聚类-凝聚", "COMPARE_WITH", "Algorithm", "层次聚类-分裂")
rel("Algorithm", "OPTICS", "USED_IN", "Task", "聚类")
rel("Algorithm", "谱聚类", "USED_IN", "Task", "聚类")
rel("Algorithm", "K-Medoids", "USED_IN", "Task", "聚类")
rel("Algorithm", "K-Medoids", "COMPARE_WITH", "Algorithm", "K-Means")
rel("Algorithm", "高斯混合模型", "EVALUATED_BY", "Metric", "Davies-Bouldin指数")
rel("Metric", "Davies-Bouldin指数", "COMPARE_WITH", "Metric", "轮廓系数")
rel("Metric", "纯度", "USED_IN", "Task", "聚类")

# ── 跨章节重要关联（提升 RAG 检索连通性） ──

rel("Algorithm", "SVM", "COMPARE_WITH", "Algorithm", "对数几率回归")
rel("Algorithm", "SVM", "COMPARE_WITH", "Algorithm", "KNN")
rel("Algorithm", "随机森林", "COMPARE_WITH", "Algorithm", "SVM")
rel("Algorithm", "随机森林", "COMPARE_WITH", "Algorithm", "KNN")
rel("Algorithm", "卷积神经网络", "COMPARE_WITH", "Algorithm", "SVM")
rel("Algorithm", "朴素贝叶斯", "COMPARE_WITH", "Algorithm", "KNN")
rel("Algorithm", "线性回归", "COMPARE_WITH", "Algorithm", "LASSO")
rel("Algorithm", "线性回归", "COMPARE_WITH", "Algorithm", "Ridge回归")
rel("Algorithm", "PCA", "USED_IN", "Algorithm", "K-Means")
rel("Algorithm", "PCA", "USED_IN", "Algorithm", "KNN")
rel("Method", "正则化", "USED_IN", "Algorithm", "LASSO")
rel("Method", "正则化", "USED_IN", "Algorithm", "Ridge回归")
rel("Method", "正则化", "USED_IN", "Algorithm", "XGBoost")
rel("Method", "正则化", "USED_IN", "Algorithm", "卷积神经网络")
rel("Algorithm", "XGBoost", "COMPARE_WITH", "Algorithm", "随机森林")
rel("Algorithm", "LightGBM", "COMPARE_WITH", "Algorithm", "XGBoost")
rel("Algorithm", "t-SNE", "USED_IN", "Algorithm", "K-Means")
rel("Concept", "流形学习", "PREREQUISITE_OF", "Algorithm", "t-SNE")
rel("Concept", "流形学习", "PREREQUISITE_OF", "Algorithm", "LLE")
rel("Method", "距离度量", "USED_IN", "Algorithm", "DBSCAN")
rel("Method", "距离度量", "USED_IN", "Algorithm", "层次聚类")
rel("Algorithm", "对数几率回归", "PREREQUISITE_OF", "Algorithm", "多层感知机")
rel("Algorithm", "线性判别分析", "COMPARE_WITH", "Algorithm", "PCA")
rel("Concept", "条件独立性假设", "USED_IN", "Algorithm", "贝叶斯网络")
rel("Algorithm", "EM算法", "USED_IN", "Algorithm", "高斯混合模型")
rel("Algorithm", "策略梯度", "PREREQUISITE_OF", "Algorithm", "Actor-Critic")
rel("Algorithm", "Q-learning", "PREREQUISITE_OF", "Algorithm", "Actor-Critic")
rel("Algorithm", "DQN", "PREREQUISITE_OF", "Algorithm", "卷积神经网络")
rel("Concept", "值函数", "PART_OF", "Concept", "Q值函数")
rel("Concept", "状态", "USED_IN", "Concept", "马尔可夫决策过程")
rel("Concept", "动作", "USED_IN", "Concept", "马尔可夫决策过程")
rel("Concept", "奖励", "USED_IN", "Concept", "马尔可夫决策过程")
rel("Concept", "策略", "USED_IN", "Concept", "马尔可夫决策过程")
rel("Algorithm", "Actor-Critic", "COMPARE_WITH", "Algorithm", "DQN")
rel("Concept", "序列覆盖法", "USED_IN", "Algorithm", "Apriori")


# ═══════════════════════════════════════════════════════════
# 第三部分：生成输出文件
# ═══════════════════════════════════════════════════════════

# 1. 输出 nodes.json
nodes_path = os.path.join(OUTPUT_DIR, "nodes.json")
with open(nodes_path, "w", encoding="utf-8") as f:
    json.dump(nodes, f, ensure_ascii=False, indent=2)
print(f"✅ 节点数据已保存: {nodes_path}  ({len(nodes)} 个节点)")

# 2. 输出 relationships.json
rels_path = os.path.join(OUTPUT_DIR, "relationships.json")
with open(rels_path, "w", encoding="utf-8") as f:
    json.dump(relationships, f, ensure_ascii=False, indent=2)
print(f"✅ 关系数据已保存: {rels_path}  ({len(relationships)} 条关系)")

# 3. 生成 Cypher 导入脚本
cypher_lines = []
cypher_lines.append("// ═══════════════════════════════════════════════════════════")
cypher_lines.append("// 机器学习课程知识图谱 — Neo4j 导入脚本")
cypher_lines.append(f"// 节点数: {len(nodes)}  关系数: {len(relationships)}")
cypher_lines.append("// 生成方式: python3 build_graph.py")
cypher_lines.append("// 使用方法: 在 Neo4j Browser 中粘贴执行，或逐段执行")
cypher_lines.append("// ═══════════════════════════════════════════════════════════")
cypher_lines.append("")
cypher_lines.append("// 清空现有数据（首次导入时执行）")
cypher_lines.append("MATCH (n) DETACH DELETE n;")
cypher_lines.append("")

# 创建约束和索引
cypher_lines.append("// ── 创建索引（提升查询性能） ──")
cypher_labels = set(n["label"] for n in nodes)
for lbl in sorted(cypher_labels):
    cypher_lines.append(f"CREATE CONSTRAINT IF NOT EXISTS FOR (n:{lbl}) REQUIRE n.name IS UNIQUE;")
cypher_lines.append("")

# 分批创建节点
cypher_lines.append("// ── 创建节点 ──")
label_groups = {}
for n in nodes:
    lbl = n["label"]
    if lbl not in label_groups:
        label_groups[lbl] = []
    label_groups[lbl].append(n)

for lbl in sorted(label_groups.keys()):
    group = label_groups[lbl]
    cypher_lines.append(f"// [{lbl}] {len(group)} 个节点")
    cypher_lines.append("UNWIND [")
    for i, n in enumerate(group):
        desc_escaped = n["description"].replace("'", "\\'")
        name_escaped = n["name"].replace("'", "\\'")
        line = f"  {{name: '{name_escaped}', description: '{desc_escaped}', chapter: '{n['chapter']}'}}"
        if i < len(group) - 1:
            line += ","
        cypher_lines.append(line)
    cypher_lines.append(f"] AS props CREATE (n:{lbl}) SET n = props;")
    cypher_lines.append("")

# 创建关系
cypher_lines.append("// ── 创建关系 ──")
rel_type_groups = {}
for r in relationships:
    rt = r["type"]
    if rt not in rel_type_groups:
        rel_type_groups[rt] = []
    rel_type_groups[rt].append(r)

for rt in sorted(rel_type_groups.keys()):
    group = rel_type_groups[rt]
    cypher_lines.append(f"// [{rt}] {len(group)} 条关系")
    cypher_lines.append("UNWIND [")
    for i, r in enumerate(group):
        src_escaped = r["src_name"].replace("'", "\\'")
        dst_escaped = r["dst_name"].replace("'", "\\'")
        line = f"  {{src: '{src_escaped}', dst: '{dst_escaped}'}}"
        if i < len(group) - 1:
            line += ","
        cypher_lines.append(line)
    cypher_lines.append(f"] AS pair")
    cypher_lines.append(f"MATCH (a {{name: pair.src}}), (b {{name: pair.dst}})")
    cypher_lines.append(f"CREATE (a)-[:{rt}]->(b);")
    cypher_lines.append("")

# 统计查询
cypher_lines.append("// ── 统计验证 ──")
cypher_lines.append("MATCH (n) RETURN labels(n)[0] AS 节点类型, count(n) AS 数量 ORDER BY 数量 DESC;")
cypher_lines.append("MATCH ()-[r]->() RETURN type(r) AS 关系类型, count(r) AS 数量 ORDER BY 数量 DESC;")
cypher_lines.append("")
cypher_lines.append("// ── 示例查询 ──")
cypher_lines.append("// 查询某概念的所有前置知识")
cypher_lines.append("MATCH path = (start)-[:PREREQUISITE_OF*]->(end {name: '卷积神经网络'}) RETURN path;")
cypher_lines.append("")
cypher_lines.append("// 查询某章节包含的所有知识点")
cypher_lines.append("MATCH (c:Chapter {name: '神经网络'})-[:CONTAINS]->(n) RETURN n;")
cypher_lines.append("")
cypher_lines.append("// 查询可用于分类任务的算法")
cypher_lines.append("MATCH (a)-[:USED_IN]->(t:Task {name: '分类'}) RETURN a.name AS 分类算法;")
cypher_lines.append("")
cypher_lines.append("// 查询两个概念之间的最短学习路径")
cypher_lines.append("MATCH path = shortestPath((a {name: '机器学习'})-[*]->(b {name: 'Transformer'})) RETURN path;")
cypher_lines.append("")
cypher_lines.append("// 查询与SVM相关的对比算法")
cypher_lines.append("MATCH (a {name: 'SVM'})-[:COMPARE_WITH]-(b) RETURN a.name, b.name AS 对比算法;")

cypher_path = os.path.join(OUTPUT_DIR, "import.cypher")
with open(cypher_path, "w", encoding="utf-8") as f:
    f.write("\n".join(cypher_lines))
print(f"✅ Cypher 导入脚本已生成: {cypher_path}")

# 统计信息
print(f"\n{'='*50}")
print(f"知识图谱统计")
print(f"{'='*50}")
print(f"节点总数: {len(nodes)}")
for lbl in sorted(label_groups.keys()):
    print(f"  {lbl}: {len(label_groups[lbl])} 个")
print(f"关系总数: {len(relationships)}")
for rt in sorted(rel_type_groups.keys()):
    print(f"  {rt}: {len(rel_type_groups[rt])} 条")
print(f"覆盖章节: {len(set(n['chapter'] for n in nodes if n['chapter']))} 章")
