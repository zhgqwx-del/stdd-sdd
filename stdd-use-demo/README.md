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

在 Codex 中打开仓库内的 `STDD-SDD` 目录，使会话能发现其中的 `$init-stdd`。输入下面这段，请 Agent 先生成项目和规格草稿。

```text
用 $init-stdd 在当前 Git 仓库的根目录下初始化 stdd-use-demo-replay，选择 demo 配置。
项目目标是将免运费门槛从 99 元提高到 129 元，低于门槛收 8 元，继续使用整数分并拒绝无效输入。
变更 ID 用 002-free-shipping-threshold。先生成四角色入口与变更草稿。
```

也可以从终端直接运行脚本。选其中一种方式即可。从仓库根目录运行下面的命令。之后可在 Codex 中让 Agent 结合项目内容起草规格。

```sh
python3 -B STDD-SDD/.agents/skills/init-stdd/scripts/init_stdd.py stdd-use-demo-replay \
  --profile demo \
  --name 'STDD 运费报价演练' \
  --goal '满 129 元免运费，低于门槛收 8 元，继续使用整数分并拒绝无效输入。' \
  --change-id 002-free-shipping-threshold \
  --change-title '将免运费门槛调整到 129 元'
cd stdd-use-demo-replay
make check
```

这时 `make check` 验证的是脚手架自带的 99 元基线。实际项目已有技术栈或准备自己写代码时，通常用 `--profile team` 带入协作文件、技能和脚本。

## 第二步 四个角色对齐规格

打开练习副本的 `docs/stdd/project.md`，沿链接进入 `changes/002-free-shipping-threshold/`。下面是本次已经填写好的例子。

| 角色 | 打开什么 | 本次要完成什么 |
| --- | --- | --- |
| 产品 | [变更](changes/archive/002-free-shipping-threshold/change.md)和[规格](changes/archive/002-free-shipping-threshold/spec.md) | 确定门槛、刚好达到时的结果及要保留的行为 |
| 设计 | [体验设计](changes/archive/002-free-shipping-threshold/ux-design.md) | 写下不同报价对应的展示与失败状态。这个演练用函数验收报价 |
| 研发 | [任务](changes/archive/002-free-shipping-threshold/tasks.md)和[技术设计示例](changes/archive/002-free-shipping-threshold/design.md) | 在练习副本的 `tasks.md` 写明修改位置、关键取舍和验收方式。复杂变更可另写技术设计 |
| 测试 | [验收计划](changes/archive/002-free-shipping-threshold/test-plan.md)和[证据](changes/archive/002-free-shipping-threshold/verification.md) | 验证门槛前后、恰好达到门槛和无效输入，记录实际结果 |

在真实项目里，先确认规则和简短实施方案，再开始测试和实现。这个演练的修改点是 `shipping/quote.py`，沿用整数分和 `>=`，用门槛前、中、后三个输入验收 `REQ-SHIP-001`，并复测 `REQ-SHIP-002` 的输入校验。

## 第三步 先让新测试失败

更新 `tests/acceptance/test_shipping_quote.py`。应收费的用例放入 `0`、`9900` 和 `12899`，刚好达到和超过门槛的用例分别使用 `12900` 和 `12901`，保留无效输入用例。也可以在练习副本根目录直接复制本项目的测试文件。

```sh
cp ../stdd-use-demo/tests/acceptance/test_shipping_quote.py tests/acceptance/test_shipping_quote.py
make test-acceptance
```

此时两个子用例应出现 `AssertionError: 0 != 800`。这说明旧实现还按 99 元免邮，测试捕捉到了规格要求改变的行为。

## 第四步 修改实现并复跑

在 `shipping/quote.py` 中把 `subtotal_fen >= 9900` 改为 `subtotal_fen >= 12900`。随后运行 `make test-acceptance`，四个测试方法应通过。

同步 `specs/shipping/spec.md` 的门槛和场景输入，保留需求与场景 ID。可以从本项目的[现行规格](specs/shipping/spec.md)对照修改，最后运行 `make check`。

## 第五步 留下证据和交接入口

在练习副本的 `verification.md` 记录旧实现为什么失败、新实现跑了什么、看到什么结果。勾选已完成的任务，再将变更移入 `changes/archive/` 并更新项目入口链接。团队项目可在 PR 中链接规格差异、用例与实际受测提交。

以后在项目根目录启动新的 Codex 会话，可以用 `$stdd-start` 建立下一项变更，再用 `$stdd-delivery` 实现，用 `$stdd-test-report` 补齐验收证据。 [项目与四角色入口](docs/stdd/project.md) · [研发技能与脚本](docs/stdd/workflows.md)
