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

默认 `team` + `all` 会把项目文档、模板、三个脚本、PR 模板和七个研发技能放入目标项目，供 Codex、Claude Code 和 Qoder 使用。首次初始化成功后，项目根目录的 `.stdd-version` 会记录采用的发布标签，可随项目提交。`init-stdd` 本身留在解压目录，可给其他项目复用。准备开始首个需求时，在 Agent 里打开目标项目，用 `stdd-start` 核对现有行为和测试入口，再完善生成的首个变更草稿。

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

## 升级已初始化的项目

以下命令在 macOS 或 Linux 的同一个终端里分步执行。需要 `curl`、`unzip` 和 Python 3.9 或以上。

### 1. 填目标项目路径，下载并解压新版

把 `stdd_target` 改成**已初始化项目根目录的绝对路径**。如果终端已在该项目根目录，可以用 `stdd_target="$(pwd -P)"`。其余变量会指向这次新建的临时目录。

```sh
stdd_target="$HOME/projects/my-project"
stdd_upgrade_dir="$(mktemp -d)"
stdd_new_zip="$stdd_upgrade_dir/init-stdd-latest.zip"
stdd_script="$stdd_upgrade_dir/new/init-stdd/scripts/init_stdd.py"
curl -fL 'https://github.com/zhgqwx-del/stdd-sdd/releases/latest/download/init-stdd.zip' -o "$stdd_new_zip" &&
  unzip -q "$stdd_new_zip" -d "$stdd_upgrade_dir/new"
```

### 2. 预览差异

脚本会读取项目根目录的 `.stdd-version`，并从 GitHub 下载记录所指的旧包。目标项目没有这个文件时，先按下文为旧项目补录。预览会获取用于比对的 ZIP，项目文件保持原样。

```sh
python3 -B "$stdd_script" "$stdd_target" --upgrade --dry-run
```

`UPDATE` 和 `CREATE` 分别是可自动更新和新增的文件。`MERGE` 表示项目已有定制且上游也有改动，预览会显示上游差异，供你手动合并。自定义技能目录可在预览和正式执行时用 `--skills-dir` 明确指定。

### 3. 确认后执行升级

```sh
python3 -B "$stdd_script" "$stdd_target" --upgrade
```

升级完整应用后，脚本会更新 `.stdd-version`。如果仍有 `MERGE`、`BLOCKED`、`CHANGED`，或者只升级了部分已安装的技能目录，脚本会保留原记录。处理完待办并运行项目检查后，可以重新升级，或用 `--record-version` 确认已采用的版本。新版的发布标签可用 `cat "$stdd_upgrade_dir/new/init-stdd/VERSION"` 查看。 [升级范围与状态说明](.agents/skills/init-stdd/references/usage.md#升级已初始化的项目)

### 已初始化的旧项目补录版本

从初始化提交、上次升级 PR 或团队安装记录确认项目上一次实际采用的发布标签。把下列命令中的 `v1.4.0` 换成该标签，补录后回到第 2 步。即使旧 ZIP 已删除，脚本也会按标签重新下载。 [GitHub 历史发布](https://github.com/zhgqwx-del/stdd-sdd/releases)

```sh
python3 -B "$stdd_script" "$stdd_target" --record-version v1.4.0
```

如果已经有对应的旧 ZIP，或升级环境无法连到 GitHub，可在第 2、3 步使用 `--from-bundle`。把 `stdd_previous_zip` 改为旧 ZIP 的绝对路径，直接传入 ZIP 即可。

```sh
stdd_previous_zip="$HOME/Downloads/init-stdd-v1.4.0.zip"
python3 -B "$stdd_script" "$stdd_target" --upgrade --from-bundle "$stdd_previous_zip" --dry-run
```

### 旧包删了，版本也找不到

无法确认发布标签，或该版本的附件已不可用时，用第 1 步解压的新版生成临时参考项目，再逐项比对和合并。自动升级需要可信的旧包来判断哪些内容是项目定制。

以下以原项目采用 `team` 和 Codex 为例。按实际配置替换 `--profile` 和 `--agent`，并按项目中的技能位置调整对照路径。

```sh
stdd_reference="$stdd_upgrade_dir/reference"
python3 -B "$stdd_script" "$stdd_reference" --profile team --agent codex
git diff --no-index -- "$stdd_target/docs/stdd/templates" "$stdd_reference/docs/stdd/templates"
git diff --no-index -- "$stdd_target/.agents/skills/stdd-wrap" "$stdd_reference/.agents/skills/stdd-wrap"
```

`git diff --no-index` 找到差异时会返回状态码 1。逐项合入需要的模板、技能和工作流并通过项目检查后，用 `--record-version` 记录实际采用的新版标签。

## 初始化后查看七个技能的使用顺序

初始化后先打开项目的 **`docs/stdd/project.md`**，找到当前变更和四角色入口。然后打开 **`docs/stdd/workflows.md` →「使用顺序」**，查看七个研发技能的流程图和适用场景。 [查看演练项目里的工作流示例](../stdd-use-demo/docs/stdd/workflows.md#使用顺序)

确认规格、验收和实施方案后，用 `stdd-delivery` 先写验收测试，再实现。后续开新需求时用 `stdd-start`。

准备提交或 PR 时，用 `stdd-wrap` 刷新真实合入目标，按项目策略快进或 rebase，处理冲突后复跑检查并记录受测版本。共享历史、脏工作区、离线或中途交接按项目约定处理。 [详细说明](.agents/skills/init-stdd/references/usage.md#方案和-git-工作方式)

项目按自己的测试、联调和交付流程执行验收。本仓库的 ZIP 发布通过 GitHub Actions 校验，项目检查和验收证据门禁仍在完善。 [门禁状态与当前做法](<STDD 与 SDD 实践手册.md#7-后续待完善的测试与门禁>)
