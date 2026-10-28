# 企业数据智能体规划资料

本目录保存规划汇报、可编辑架构图及后续方案编写原则。当前项目仍仅建设数据资产智能体；三类九种Agent是目标能力布局。

## 当前维护入口

| 材料 | 版本与作用 | 入口 |
| --- | --- | --- |
| 方案编写原则 | 高度与细节贯通，作为后续修订与审阅标准 | [规划方案编写原则](规划方案编写原则.md) |
| 领导汇报 | V7，30页架构视觉版，含逐页提纲及构建源 | [PPT交付说明](hiagent-leadership-report/v7-illustrated/交付说明.md) |
| 独立规划图集 | V0.8，14页原生draw.io及SVG、PNG | [图集说明](hiagent-agent-landscape/v0.8/README.md) |
| 能力全景原始基准 | V0.3，保留原始内容、画布、分层与支撑列 | [V0.3说明与原图](hiagent-agent-landscape/v0.3/README.md) |

V0.3是能力全景的结构基准；V0.8在保留其238个对象的位置、分组、样式和连线的基础上，更新第06层“系统与平台”及相关文字。PPT面向讲述，draw.io面向完整架构审阅，分别编排、统一口径。

## 构建与验证

PPT构建源及依赖已集中于V7目录，不依赖未提交的中间版本。运行`hiagent-leadership-report/v7-illustrated/build_illustrated_deck.py`生成PPT和逐页提纲；通过LibreOffice导出内部校验PDF后，运行同目录`validate_render.py`检查实际文字与页面范围。

图集依次运行V0.8目录中的`build_landscape.py`和`build_atlas.py`。前者保留V0.3结构，后者从本目录内的基准快照和独立图源构建14页图集。使用Inkscape从SVG导出PNG，现有预览宽度3600像素。修改图源后应同步图片。

Python构建需要python-pptx、Pillow，渲染检查另需PyMuPDF；中文字体为Noto Sans CJK SC。内部qa目录及Python缓存不纳入版本管理。原始V0.3不随当前图集构建而覆盖。

本目录不替代当前正式数据资源智能体建设方案，不以本地构建结果推断HiAgent生产部署、接口联调或验收状态。
