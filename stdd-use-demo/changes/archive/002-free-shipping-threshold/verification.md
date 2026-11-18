# 将免运费门槛调整到 129 元验收记录

## 受测场景

验收依据为[本次变更规格](spec.md)，用例见[运费验收测试](../../../tests/acceptance/test_shipping_quote.py)。

| 场景 | 输入 | 新实现的观察结果 |
| --- | --- | --- |
| [AC-SHIP-001](spec.md#ac-ship-001) | 0、9,900、12,899 分 | 均返回 800 分 |
| [AC-SHIP-002](spec.md#ac-ship-002) | 12,900 分 | 返回 0 分 |
| [AC-SHIP-003](spec.md#ac-ship-003) | 12,901 分 | 返回 0 分 |
| [AC-SHIP-004](spec.md#ac-ship-004) | `-1`、`12900.0`、`"12900"`、`True`、`None` | 均抛出 `ValueError` |

## 本地运行记录

环境为 macOS、Python 3.9.6 和 GNU Make。以下记录对应演练时的本地文件。

1. **基线。** 项目刚生成，实现和原验收都使用 99 元门槛。`make check` 检查两条需求和四个场景，四个测试方法通过。
2. **测试先失败。** 先更新验收测试，保留 99 元实现。运行 `make test-acceptance`，`AC-SHIP-001` 的 9,900 分和 12,899 分两个子用例均出现 `AssertionError: 0 != 800`。
3. **修改实现后通过。** 将门槛改为 12,900 分并同步现行规范。`make test-acceptance` 和 `make check` 各运行四个测试方法，全部通过。直接调用阈值三点的结果为 `800 0 0`，金额单位均为分。
