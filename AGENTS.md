# stdd-sdd 仓库协作说明

## 项目定位与入口

本仓库维护 STDD/SDD 实践方法、`init-stdd` 初始化技能及配套演练。核心链路是 `REQ → AC → 测试 → 运行证据`，产品、设计、研发和测试共用需求及场景编号。

- [项目总览](README.md)：仓库用途和验证入口。
- [团队快速上手](STDD-SDD/QUICKSTART.md)：安装、接入与技能调用。
- [实践手册](<STDD-SDD/STDD 与 SDD 实践手册.md>)：方法、文档职责、人机分工和后续待办。
- [初始化器说明](STDD-SDD/.agents/skills/init-stdd/references/usage.md)：参数、配置、已有文件保留及升级方式。
- [运费演练](stdd-use-demo/README.md)：99 元门槛变为 129 元的完整交付记录。进入该目录工作时继续读取其 `AGENTS.md`。

## 源码与生成内容

`STDD-SDD/.agents/skills/init-stdd/` 是初始化技能分发内容的源码位置。

| 位置（相对技能目录） | 职责 |
| --- | --- |
| `VERSION` | 当前分发包的发布标签，须与 GitHub Release 标签一致 |
| `scripts/init_stdd.py` | 解析参数、渲染模板、规划初始化或升级文件 |
| `assets/base/` | 各配置共用的项目入口和工程约定，包含 `{{TOKEN}}` 占位符 |
| `assets/seed/` | 首个变更的 `change.md` 和 `spec.md` 草稿 |
| `assets/starter/` | 文档模板、七个研发技能、三个辅助脚本，以及教学代码、测试和 CI |
| `assets/team/` | 按技能安装目录渲染的工作流文档 |
| `references/` | 使用说明、已有项目接入及角色交接 |

- 三种配置为 `spec`、`team`、`demo`，默认 `team`；技能目录默认 `all`，另支持单工具、自动识别、便携目录及自定义目录。
- 常规初始化和 `--skills-only` 只新增缺失文件，保留已有同名文件。`--upgrade` 按项目根目录的 `.stdd-version` 获取旧包，也可用 `--from-bundle` 指定本地旧包。首次初始化或完整升级后记录采用的版本，旧项目可用 `--record-version` 补录。`--dry-run` 只预览。保持 `CREATE`、`KEEP`、`UNCHANGED`、`BLOCKED` 的语义。
- `assets/starter/` 中的运费基线为 99 元，`stdd-use-demo/` 是已完成 129 元变更的演练。同步通用技能、模板和脚本时核对两处；保留教学前后版本的预期差异。
- `STDD-SDD/init-stdd.zip` 分发完整的 `init-stdd/` 目录，按下方流程维护。

## 三个入口的同步与发布

每次更新 `init-stdd` 或其分发的 `stdd-*` 技能，按以下顺序完成交付。

1. 同步[实践手册](<STDD-SDD/STDD 与 SDD 实践手册.md>)和[技能源码](STDD-SDD/.agents/skills/init-stdd/)，核对技能行为、使用步骤和示例是否一致。涉及的快速上手、使用说明、生成模板和演练副本一并更新。
2. 将技能源码的 `VERSION` 更新为本次发布标签，再重新构建 [init-stdd.zip](STDD-SDD/init-stdd.zip)。运行下方的本地发布检查，通过后提交并推送这批更新。
3. 从 `main` 运行 [Release init-stdd](.github/workflows/release-init-stdd.yml)，填写相同的标签并勾选 `publish`。工作流先核对手册和下载入口、源码及 ZIP，再跑回归。通过后才创建或核对标签，上传仓库 ZIP，并发布为 Latest。
4. 同一工作流从快速上手的[下载最新版](https://github.com/zhgqwx-del/stdd-sdd/releases/latest/download/init-stdd.zip)链接实际下载，核对标签所指提交、发布附件和仓库 ZIP 的 SHA-256。交付时记录版本、提交、工作流和下载验证结果。复核已发布版本时保持 `publish` 未勾选。

从仓库根目录运行发布前检查和发布命令。

```sh
stdd_tag="$(cat STDD-SDD/.agents/skills/init-stdd/VERSION)"
python3 -B scripts/check_init_stdd_release.py --tag "$stdd_tag"
gh workflow run release-init-stdd.yml --ref main -f tag="$stdd_tag" -f publish=true
```

手动发布也会触发已发布附件的检查。若发布后检查失败，可在核对 GitHub Release 及其附件后运行只读复核。工作流会报告失败并保留发布现场。

仅修改 `AGENTS.md` 等仓库维护文档，且改动不影响技能源码或分发包时，提交并推送即可，无需重打包或更新 GitHub Releases。

## 维护约定

- 文档以中文为主。保持安装命令、参数默认值、流程图和模板之间一致。
- 保留独立仓库可用的相对路径；外部参考使用可访问来源，避免依赖原桌面工作区的本地资料。
- 行为变更先核对现行规格、验收场景及实施方案；会话或工单中已确认的同范围方案可直接沿用。
- 演练的 `specs/` 记录已交付行为，`changes/archive/` 保留历史变更；需求和场景 ID 保持稳定。归档时核对讨论、ADR 与变更的双向链接。
- `check_traceability.py` 检查现行规格中的编号和 `REQ → AC` 引用关系；测试覆盖、实际通过结果和受测版本由测试及验收证据说明。
- 实践手册第 7 节记录已接通的 ZIP 发布门禁，以及仍待完善的项目检查和验收证据门禁。

## 本地验证

需要 Python 3.9 或以上；脚本和运费演练使用 Python 标准库。以下命令从本仓库根目录运行：

```sh
make -C stdd-use-demo check
make -C stdd-use-demo test-acceptance
python3 -B STDD-SDD/.agents/skills/init-stdd/scripts/init_stdd.py --help
```

按改动范围选择验证：

- 演练规则或用例变动：运行定向验收和 `make check`，同步相关规格与记录。
- 初始化器或资源变动：在临时目录生成受影响配置；影响公共生成逻辑时覆盖三种配置，核对入口、技能目录及已有文件保留。生成的 `demo` 再运行 `make check`。
- 升级逻辑变动：运行 `python3 -B -m unittest discover -s tests -v`，并用历史 ZIP 核对升级预览和实际结果。
- 分发包变动：运行上文的发布前检查，核对文件清单、逐文件内容和解压后初始化结果。已发布版本可以给同一命令加 `--check-latest`，核对公开下载。
- 根级 Release init-stdd 的运行记录提供发包证据。子目录里的 `.github/workflows/check.yml` 用于教学项目。

Git 操作前核对当前分支、工作区及任务授权；保留已有改动，按实际受测内容报告结果。
