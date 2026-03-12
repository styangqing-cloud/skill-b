# OpenClaw Skill Collection

精选 OpenClaw 技能合集 - 搜索、生产、审核、HR 四大类热门技能

---

## 📚 技能分类

### 🔍 01-skill-search - Skill 搜索类

| 技能名称 | 版本 | 功能说明 |
|---------|------|---------|
| **fitcheck-skill-search** | 1.1.0 | 关键词/语义/LLM 驱动的 skill 搜索工具 |
| **skill-search-optimizer** | 1.0.0 | skill 搜索优化和排名提升工具 |
| **firm-skill-loader-pack** | 1.0.0 | skill 懒加载和关键词搜索包 |

**使用场景：**
- 查找和检索可用技能
- 优化技能的可发现性
- 按需加载技能

---

### 🛠️ 02-skill-creator - Skill 生产类

| 技能名称 | 版本 | 功能说明 |
|---------|------|---------|
| **skill-creator-pro** | 1.0.0 | 专业版 skill 创建，支持 eval 驱动迭代 |
| **skill-creator-operator** | 1.0.1 | Premium 版本，带 setup wizard 模式 |
| **skill-creator-vault-enhancement** | 1.0.0 | 增强版，支持脚本/引用/资产 |

**使用场景：**
- 创建新技能
- 修改和优化现有技能
- 运行 eval 测试技能性能
- 优化技能描述以提高触发准确性

---

### ✅ 03-skill-reviewer - Skill 审核类

| 技能名称 | 版本 | 功能说明 |
|---------|------|---------|
| **skill-reviewer-pro** | 2.1.1 | 专业版审核，格式/内容/功能验证 |
| **openclaw-skill-reviewer** | 1.0.0 | OpenClaw 专用三级审核 |
| **skill-reviewer** | 1.0.0 | 通用 skill 审核器 |

**使用场景：**
- 发布前审查技能
- 审核他人的技能
- 评估技能质量
- 识别技能缺陷

---

### 🧑‍💼 04-employee-interview-generator - HR 访谈类 ⭐

| 技能名称 | 版本 | 功能说明 |
|---------|------|---------|
| **employee-interview-generator** | 2.0.0 | 互联网公司员工访谈提纲生成器 |

**核心功能：**
- 📝 支持 9 种访谈类型（入职/绩效/离职/晋升/职业发展/团队反馈/挽留/转岗/组织诊断）
- 📁 支持文件上传分析（Excel/PDF/PPTX/Word/TXT）
- 🔗 支持网页链接分析
- 📝 腾讯文档集成

**专业方法论支持：**
| 方法论 | 适用场景 |
|-------|---------|
| 韦斯伯德六个盒子模型 | 组织诊断访谈 |
| 推拉力理论 | 离职访谈 |
| 冰山模型 | 招聘需求访谈 |
| 吉尔伯特 BEM 模型 | 员工发展访谈 |
| 职业锚理论 + GROW 模型 | 职业发展访谈 |

**使用场景：**
- HR 访谈提纲生成
- 组织健康度诊断
- 离职原因分析
- 员工发展规划

---

## 📦 安装方式

### 方式 1：克隆后复制

```bash
# 克隆本仓库
git clone https://github.com/styangqing-cloud/skill.git

# 复制技能到 OpenClaw 技能目录
cp -r skill/skill-collection/* /root/.openclaw/workspace/skills/
```

### 方式 2：单个安装

```bash
# 使用 skillhub 安装
skillhub install fitcheck-skill-search
skillhub install skill-creator-pro
skillhub install skill-reviewer-pro
```

---

## 🚀 快速开始

### Skill 搜索

```
帮我搜索一下关于 HR 的技能
```

### Skill 生产

```
帮我创建一个新的技能，用于生成周报
```

### Skill 审核

```
帮我审查一下这个技能的质量
```

---

## 📊 技能统计

| 类别 | 技能数量 | 总版本 |
|-----|---------|-------|
| Skill 搜索 | 3 | 3.1.0 |
| Skill 生产 | 3 | 3.0.1 |
| Skill 审核 | 3 | 4.1.1 |
| HR 访谈 ⭐ | 1 | 2.0.0 |
| **总计** | **10** | **12.2.2** |

---

## 📝 许可协议

所有技能遵循各自的许可协议（通常为 Apache-2.0 或 MIT）。

---

## 🙏 致谢

感谢所有技能创作者的贡献！

- fitcheck-skill-search: fitcheck 团队
- skill-creator 系列：Anthropic/Operator 社区
- skill-reviewer 系列：OpenClaw 社区
- employee-interview-generator: tommyyang@tencent

---

**最后更新**：2026-03-12  
**维护者**：styangqing-cloud
