# STDD 研发工作流

产品、设计、研发和测试先从[角色导航](roles.md)打开同一份变更。仓库内还带有以下 Skill，接入支持 Agent Skills 的工具后可按任务调用。

## 使用顺序

从[项目入口](project.md)找到当前变更。项目已经生成首个变更时，可以直接确认规格和验收场景。以后开新需求或处理缺陷时，按图选入口。

```mermaid
flowchart TD
    Init["项目已初始化<br/>从项目入口找到当前变更"]
    Start["stdd-start<br/>为新需求建立变更和验收草稿"]
    Diagnose["stdd-diagnose<br/>复现缺陷并形成回归场景"]
    Spec["确认这次的规格与验收场景"]
    Delivery["stdd-delivery<br/>先写验收测试，再实现并复跑"]
    Report["stdd-test-report<br/>把实际结果写入 verification.md"]
    Review["stdd-review<br/>核对代码、规格和受测证据"]
    Wrap["stdd-wrap<br/>同步规格和任务，准备 PR 或交接"]
    Done["按项目流程合入或交接"]
    Release["stdd-release-notes<br/>按版本范围整理发布说明或迭代总结"]

    Init -->|继续已创建的首个变更| Spec
    Init -->|后续开新需求| Start
    Init -->|收到缺陷反馈| Diagnose
    Start --> Spec
    Diagnose -->|决定修复后| Spec
    Spec --> Delivery
    Delivery --> Report
    Report -->|关键场景通过| Review
    Report -->|发现实现问题| Delivery
    Review -->|需要修正实现| Delivery
    Review -->|评审通过| Wrap
    Wrap --> Done
    Done -.->|准备发版或总结迭代时| Release
```

团队先开 PR 时，可以先用 `stdd-wrap` 准备草稿，再在 PR 中用 `stdd-review`。

## 技能速查

| 阶段 | 技能 | 工作产物 |
| --- | --- | --- |
| 开工 | [$stdd-start](../../.agents/skills/stdd-start/SKILL.md) | 变更范围、规格、未决事项与第一项可执行任务 |
| 实现 | [$stdd-delivery](../../.agents/skills/stdd-delivery/SKILL.md) | 与确认的场景一致的用例、实现及运行结果 |
| 排查 | [$stdd-diagnose](../../.agents/skills/stdd-diagnose/SKILL.md) | 复现记录、影响范围及回归场景 |
| 验收 | [$stdd-test-report](../../.agents/skills/stdd-test-report/SKILL.md) | 按场景记录自动、手工及待验结果 |
| 审查 | [$stdd-review](../../.agents/skills/stdd-review/SKILL.md) | 对照规格、候选差异和受测证据的发现 |
| 收尾 | [$stdd-wrap](../../.agents/skills/stdd-wrap/SKILL.md) | 进度、证据和 PR 草稿 |
| 版本 | [$stdd-release-notes](../../.agents/skills/stdd-release-notes/SKILL.md) | 版本差异、影响、兼容及验收状态 |

从仓库根目录使用脚本。

```sh
python3 -B scripts/new_change.py 014-order-cancellation '订单取消' --roles
python3 -B scripts/check_traceability.py
python3 -B scripts/git_range.py --merge-base main HEAD
```

`new_change.py` 创建变更、任务与验证文件。加 `--roles` 会同时生成[规格草稿](templates/spec.md)、[体验设计](templates/ux-design.md)、[技术设计](templates/design.md)和[验收计划](templates/test-plan.md)。`check_traceability.py` 校验采用本脚手架格式、位于 `specs/` 中的现行规格 ID 和引用。`git_range.py` 使用本地 Git 引用，例中的 `main` 应替换为实际目标分支。项目的构建与测试使用仓库自己的命令，运费教学模式可以运行 `make check`。
