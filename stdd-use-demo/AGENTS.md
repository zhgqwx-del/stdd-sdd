# 项目协作说明

- 从 [项目入口](docs/stdd/project.md) 获取目标、角色导航和进行中的变更。阅读 [工程约定](docs/engineering.md) 及受影响的规范和测试。
- 进行中的行为变更以 `changes/<id>/spec.md` 为评审稿，`specs/` 记录已交付的行为。做业务决定时将确认记录写入 `change.md`。
- 确认验收口径和 `tasks.md` 中的实施方案后开始开发。复杂取舍可写进 `design.md`。记录真实合入目标；准备提交或 PR 时默认刷新目标，按分支策略同步并复验。Git 操作沿用[项目约定](docs/stdd/git-workflow.md)。
- 产品、设计、研发和测试用相同的 `REQ-*` 与 `AC-*` 交接。使用仓库现有测试入口，按实际受测版本和结果更新 `verification.md`。
