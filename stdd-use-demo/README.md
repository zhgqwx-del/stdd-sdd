# STDD 运费报价演练

这个本地项目演示怎样用 `init-stdd` 从零搭好协作目录，再完成第一项变更。脚手架的起始规则为满 99 元免运费，演练将门槛提高到 129 元。低于门槛收 8 元，金额以整数分传入和返回。

## 先看已完成的结果

从克隆后的仓库根目录运行以下命令，需要 Python 3.9 或以上和 Make。

```sh
cd stdd-use-demo
make check
python3 -B -c 'from shipping.quote import quote_shipping; print(*(quote_shipping(n) for n in (12899, 12900, 12901)))'
```

四个测试方法应全部通过。最后一行输出 `800 0 0`，依次对应门槛前一分、刚好达到和超过一分的运费。 [本地验收记录](changes/archive/002-free-shipping-threshold/verification.md)

## 第一步 初始化一个练习副本

从仓库根目录运行以下命令，在仓库外创建独立练习副本。先验证 99 元免邮规则，将生成的骨架和变更模板提交到练习副本的本地 `main` 作为基线。

```sh
stdd_demo_source="$(pwd -P)/stdd-use-demo"
stdd_demo_target="$(mktemp -d)/stdd-use-demo-replay"
python3 -B STDD-SDD/.agents/skills/init-stdd/scripts/init_stdd.py "$stdd_demo_target" \
  --profile demo \
  --name 'STDD 运费报价演练' \
  --change-id 002-free-shipping-threshold \
  --change-title '将免运费门槛调整到 129 元'
cd "$stdd_demo_target"
make check
git init -b main
git add .
git -c user.name='STDD Demo' -c user.email='stdd-demo@example.com' commit -m '记录 99 元免邮演练基线'
```

也可以在 Codex 中打开仓库内的 `STDD-SDD` 目录，请 `$init-stdd` 在仓库外的临时目录生成 `demo` 配置、四角色入口和 `002-free-shipping-threshold` 模板。然后进入练习副本验证并提交本地 `main` 基线。实际项目已有技术栈时，通常用 `--profile team` 带入协作文件、技能和脚本。

## 第二步 四个角色对齐规格

在 Codex 中打开练习副本，用 `$stdd-start` 从本地 `main` 建分支，再复用生成的变更目录。

```text
用 $stdd-start 开始 002-free-shipping-threshold，从本地 main 创建 feat/002-free-shipping-threshold。
目标是满 129 元免运费，低于门槛收 8 元，继续使用整数分并拒绝无效输入。
进入开发分支后，完善已有的规格、验收场景和实施方案。
```

打开练习副本的 `docs/stdd/project.md`，沿链接进入 `changes/002-free-shipping-threshold/`。下面是本次已经填写好的例子。

| 角色 | 打开什么 | 本次要完成什么 |
| --- | --- | --- |
| 产品 | [变更](changes/archive/002-free-shipping-threshold/change.md)和[规格](changes/archive/002-free-shipping-threshold/spec.md) | 确定门槛、刚好达到时的结果及要保留的行为 |
| 设计 | [体验设计](changes/archive/002-free-shipping-threshold/ux-design.md) | 写下不同报价对应的展示与失败状态。这个演练用函数验收报价 |
| 研发 | [任务](changes/archive/002-free-shipping-threshold/tasks.md)和[技术设计示例](changes/archive/002-free-shipping-threshold/design.md) | 在练习副本的 `tasks.md` 写明修改位置、关键取舍和验收方式。复杂变更可另写技术设计 |
| 测试 | [验收计划](changes/archive/002-free-shipping-threshold/test-plan.md)和[证据](changes/archive/002-free-shipping-threshold/verification.md) | 验证门槛前后、恰好达到门槛和无效输入，记录实际结果 |

在真实项目里，先确认规则和简短实施方案，再开始测试和实现。这个演练的修改点是 `shipping/quote.py`，沿用整数分和 `>=`，用门槛前、中、后三个输入验收 `REQ-SHIP-001`，并复测 `REQ-SHIP-002` 的输入校验。

## 第三步 先让新测试失败

更新 `tests/acceptance/test_shipping_quote.py`。应收费的用例放入 `0`、`9900` 和 `12899`，刚好达到和超过门槛的用例分别使用 `12900` 和 `12901`，保留无效输入用例。也可以在选定的开发工作区直接复制本项目的测试文件。`stdd_demo_source` 指向原仓库的 `stdd-use-demo` 目录。

```sh
cp "$stdd_demo_source/tests/acceptance/test_shipping_quote.py" tests/acceptance/test_shipping_quote.py
make test-acceptance
```

此时两个子用例应出现 `AssertionError: 0 != 800`。这说明旧实现还按 99 元免邮，测试捕捉到了规格要求改变的行为。

## 第四步 修改实现并复跑

在 `shipping/quote.py` 中把 `subtotal_fen >= 9900` 改为 `subtotal_fen >= 12900`。随后运行 `make test-acceptance`，四个测试方法应通过。

同步 `specs/shipping/spec.md` 的门槛和场景输入，保留需求与场景 ID。可以从本项目的[现行规格](specs/shipping/spec.md)对照修改，最后运行 `make check`。

## 第五步 留下证据和交接入口

在练习副本的 `verification.md` 记录旧实现为什么失败、新实现跑了什么、看到什么结果。勾选已完成的任务，再将变更移入 `changes/archive/` 并更新项目入口链接。团队项目可在 PR 中链接规格差异、用例与实际受测提交。

本演练的 `change.md` 还链接了金额单位的讨论和 ADR。打开其中任意一份记录，都可以反查已归档的变更。 [讨论与 ADR 示例](changes/archive/002-free-shipping-threshold/change.md#关联讨论与-adr)

下次用 `$stdd-start` 续接同一功能时，复用原分支或其 worktree。开下一项新功能时，从指定或默认主干另建分支。当前工作区有其他任务的改动时，在独立 worktree 继续。方案确认后用 `$stdd-delivery` 实现，再用 `$stdd-test-report` 补齐验收证据。 [项目与四角色入口](docs/stdd/project.md) · [研发技能与脚本](docs/stdd/workflows.md)

在有远端的团队项目里，准备提交或 PR 时用 `$stdd-wrap` 刷新真实合入目标，按策略快进或 rebase，处理冲突后同步变化的依赖并复跑检查，记录目标 SHA 与实际受测内容。这个教学演练也可以仅在本地重跑，此时注明本地验收状态即可。 [收尾同步与冲突处理](docs/stdd/git-workflow.md#收尾同步)
