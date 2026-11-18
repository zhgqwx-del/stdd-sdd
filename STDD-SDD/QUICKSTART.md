# 团队快速上手 init-stdd

`init-stdd` 可初始化新项目，也可以为已有项目补上规格、设计、验收、任务和研发技能。启动脚本需要 Python 3.9 或以上版本。

下载 [最新版 `init-stdd.zip`](https://github.com/zhgqwx-del/stdd-sdd/releases/latest/download/init-stdd.zip)。下面的命令适用于 macOS 和 Linux。若 ZIP 下载到了别处，请替换命令中的下载路径。

## 方式一：在项目外运行脚本（已有项目优先）

把 `stdd_target` 换成已有项目根目录的绝对路径。以下命令在 `~/stdd-tools/` 下新建解压目录，可从任意目录运行。

```sh
stdd_target="/path/to/existing-project"
stdd_tools="$HOME/stdd-tools"
mkdir -p "$stdd_tools"
stdd_bundle="$(mktemp -d "$stdd_tools/bundle.XXXXXX")"
unzip "$HOME/Downloads/init-stdd.zip" -d "$stdd_bundle"
stdd_script="$stdd_bundle/init-stdd/scripts/init_stdd.py"
python3 -B "$stdd_script" "$stdd_target" --dry-run
```

先看预览。`CREATE` 是将新增的文件，`KEEP` 是保留的同名文件，`BLOCKED` 是跳过的受阻路径。确认后在同一终端执行正式初始化。

```sh
python3 -B "$stdd_script" "$stdd_target"
```

默认 `team` + `all` 会把项目文档、模板、三个脚本、PR 模板和七个研发技能放入目标项目，供 Codex、Claude Code 和 Qoder 使用。`init-stdd` 本身留在解压目录，可给其他项目复用。准备开始首个需求时，在 Agent 里打开目标项目，用 `stdd-start` 核对现有行为和测试入口，再完善生成的首个变更草稿。

## 方式二：在项目里安装并调用技能

如果希望 Agent 根据业务目标一起起草规格和验收，可以把整个 `init-stdd` 目录放入目标项目的技能目录。在目标项目根目录执行以下命令。Codex 用 `.agents/skills`，Claude Code 换成 `.claude/skills`，Qoder 换成 `.qoder/skills`。已经解压到该目录的项目可以直接调用。

```sh
stdd_skills=".agents/skills"
mkdir -p "$stdd_skills"
unzip "$HOME/Downloads/init-stdd.zip" -d "$stdd_skills"
```

在 Agent 里打开目标项目根目录。Codex 用 `$init-stdd`，Claude Code 和 Qoder 用 `/init-stdd`。

> 用 `$init-stdd` 在当前目录初始化会议室预约项目。目标是员工可以按时段预约，同一会议室的预约不能重叠。先生成四个角色的协作入口，以及首个变更的规格、实施方案和验收草稿。

初始化完成后，如要统一维护，仍在目标项目根目录运行以下命令。按实际安装位置设置 `stdd_skills`。

```sh
stdd_skills=".agents/skills"
stdd_tools="$HOME/stdd-tools"
mkdir -p "$stdd_tools"
if [ -e "$stdd_tools/init-stdd" ] || [ -L "$stdd_tools/init-stdd" ]; then
  printf '%s\n' "已有 $stdd_tools/init-stdd，请将 stdd_tools 改成另一个项目外目录。" >&2
else
  mv "$stdd_skills/init-stdd" "$stdd_tools/"
fi
```

只移动 `init-stdd/` 整个目录。项目里的七个 `stdd-*` 技能、文档、变更目录、脚本和 PR 模板继续保留。 [多工具与已有项目接入说明](.agents/skills/init-stdd/references/usage.md)

## 初始化后查看七个技能的使用顺序

初始化后先打开项目的 **`docs/stdd/project.md`**，找到当前变更和四角色入口。然后打开 **`docs/stdd/workflows.md` →「使用顺序」**，查看七个研发技能的流程图和适用场景。 [查看演练项目里的工作流示例](../stdd-use-demo/docs/stdd/workflows.md#使用顺序)

确认规格、验收和实施方案后，用 `stdd-delivery` 先写验收测试，再实现。后续开新需求时用 `stdd-start`。
