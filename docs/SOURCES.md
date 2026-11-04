# 素材来源与处理

采集日期：2026-11-04。

## 简历

来源为题目仓库的「脱敏资料(1).zip」。前端两个样例分别来自 resume_01.pdf、resume_02.pdf。
使用 pypdf 提取文本，人工检查内容；移除了联系信息占位字段、跟踪水印与无意义空白。
保留原有教育、工作、项目和技能内容，不添加经历、成绩或能力。
PDF 原件仅保存在本地忽略目录，仓库仅提交已复核的脱敏文本。
这些素材含有工作经验，是题目提供的演示材料，并非声称它们是应届学生简历。

## JD

- [沐瞳科技 2027 届后端开发](https://moonton.jobs.feishu.cn/campus/position/7668255125144176937/detail)
- [海康机器人 Web 前端实习生](https://talent.hikvision.com/home/socity/position?postId=1E0D3816A278D4E7636422677FD43088)

预置内容为与匹配分析相关的招聘要求节选整理，保留技术名、必备/加分的区别与来源链接，不宣称是完整原文。
岗位有时效性；应以原招聘页面为准。用户可以自行粘贴完整 JD 进行分析。

## 模型

用户在实施阶段明确指定 DeepSeek。依照 [DeepSeek 官方文档](https://api-docs.deepseek.com/)配置：
base URL 为 https://api.deepseek.com，模型为 deepseek-flash；关闭 thinking 使用非思考模式。
这与题目提及的 GPT/Claude 品牌不同，但使用相同 OpenAI-compatible 接口；属于用户明确选择，保留为答辩说明。
