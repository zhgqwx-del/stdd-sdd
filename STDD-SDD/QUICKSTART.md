# 团队快速上手 init-stdd

`init-stdd` 可初始化新项目，也可以为已有项目补上规格、设计、验收、任务和研发技能。启动脚本需要 Python 3.9 或以上版本。

## 1. 下载并解压到项目

下载 [最新版 `init-stdd.zip`](https://github.com/zhgqwx-del/stdd-sdd/releases/latest/download/init-stdd.zip)。用 Codex 时，将解压后的整个 `init-stdd` 文件夹放到**目标项目根目录**的 `.agents/skills/`，确认文件路径是 `.agents/skills/init-stdd/SKILL.md`。

macOS 或 Linux 也可以在目标项目根目录运行以下命令。将 ZIP 路径替换成你的实际下载位置。

```sh
mkdir -p .agents/skills
unzip "$HOME/Downloads/init-stdd.zip" -d .agents/skills
```

Claude Code 对应的技能目录是 `.claude/skills/`，Qoder 是 `.qoder/skills/`。将同一个 `init-stdd` 文件夹放到对应目录即可。 [多工具安装说明](.agents/skills/init-stdd/references/usage.md)

## 2. 打开项目并调用技能

在 Agent 里打开目标项目根目录。Codex 用 `$init-stdd`，Claude Code 和 Qoder 用 `/init-stdd`。下面是一条可直接发送给 Codex 的指令。

> 用 `$init-stdd` 在当前目录初始化会议室预约项目。目标是员工可以按时段预约，同一会议室的预约不能重叠。先生成四个角色的协作入口，以及首个变更的规格、实施方案和验收草稿。

已有代码的项目可以将开头换成「用 `$init-stdd` 给当前项目接入 STDD，先核对现有行为和测试入口」。初始化器会保留已有同名文件。默认配置为 `team` + `all`，会带上团队协作模板、脚本，并为 Codex、Claude Code 和 Qoder 布置后续技能。

## 3. 查看七个技能的使用顺序

初始化后先打开项目的 **`docs/stdd/project.md`**，找到当前变更和四角色入口。然后打开 **`docs/stdd/workflows.md` →「使用顺序」**，查看七个研发技能的流程图和适用场景。 [查看演练项目里的工作流示例](../stdd-use-demo/docs/stdd/workflows.md#使用顺序)

首个变更已有草稿。确认规格、验收和实施方案后，用 `stdd-delivery` 先写验收测试，再实现。后续开新需求时用 `stdd-start`。
