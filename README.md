# STDD 与 SDD 实践

用规格、验收测试和运行证据组织一次可评审的变更。仓库提供项目初始化技能，以及一份从旧规则到新规则的完整运费报价演练。

- [团队快速上手](STDD-SDD/QUICKSTART.md)介绍最新版下载、安装、已有项目升级和初始化后的七技能流程。
- [实践手册](<STDD-SDD/STDD 与 SDD 实践手册.md>)包括使用速查流程图、规范方法与模板入口。
- [init-stdd 使用说明](STDD-SDD/.agents/skills/init-stdd/references/usage.md)适用于新项目和已有仓库。[下载最新版 init-stdd.zip](https://github.com/zhgqwx-del/stdd-sdd/releases/latest/download/init-stdd.zip)后可装到项目技能目录，也可运行初始化脚本。
- [运费报价演练](stdd-use-demo/README.md)展示从 99 元改为 129 元时，怎样先观察验收失败、调整规则并保存通过证据。

从仓库根目录快速验证演练，需要 Python 3.9 或以上及 Make。

```sh
make -C stdd-use-demo check
```
