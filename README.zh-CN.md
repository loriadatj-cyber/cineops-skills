# CineOps Skills

CineOps 是一个面向 AI 影视制作的开源生产控制工具包，由五个 Codex Skill 和一个可确定执行的校验 CLI 组成。它不是提示词合集，而是用稳定 ID、连续性台账、镜头状态边界和生成前门禁，减少剧本、分镜、提示词与成片之间的信息丢失。

## 快速开始

```bash
python -m pip install -e .
cineops init my-production
cineops validate my-production
cineops validate examples/glass-elevator
```

项目中的四个核心文件分别是 `project.json`、`continuity-ledger.json`、`shot-plan.json` 和 `readiness-report.json`。CLI 会检查重复或错误 ID、断开的引用、非法镜头时长、镜头顺序和缺失的生成前审查。

真实使用、使用失败和中途放弃的案例都有价值。提交前请阅读 [采用证据规则](docs/ADOPTION.md)，确保区分可观察证据与主观解释，并删除私人制作资料。

核心流程不绑定任何视频生成模型或制作平台。关于完整设计、贡献方式和路线图，请查看英文 [README](README.md)、[CONTRIBUTING.md](CONTRIBUTING.md) 和 [ROADMAP.md](ROADMAP.md)。
