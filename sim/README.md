# guagua-sim

呱呱项目的仿真/训练子目录，由 uv 管理 Python 依赖。

## 缘起

迁移自 `~/openduck-warmup/`（用户 2026-05-02/05-03 在 WSL 内已搭好的 OpenDuck 预热项目）。原项目 git 未提交过，迁移时直接拷贝以下文件：

- `pyproject.toml`（已改名 openduck-warmup → guagua-sim）
- `uv.lock`
- `.python-version` (3.11)
- `.gitignore`
- `hello_wandb.py`（W&B 验证脚本，PRD plan-m0 W1-1 已通过）

不迁移：`.venv/` `wandb/` `main.py`（uv init 模板）`.git/`。`~/openduck-warmup/` 原目录保留作备份。

## 启动

```bash
# WSL Ubuntu 内
cd /mnt/d/CODE/guagua/sim
~/.local/bin/uv sync                    # 重建 .venv 并装依赖
~/.local/bin/uv run python hello_wandb.py  # 跑 W&B hello world
```

## 目录约定

- `scripts/` 一次性验证/调试脚本（M0 阶段：`verify_mujoco.py`）
- 后续 M1+ 加入 `models/`（MuJoCo XML / URDF）、`policies/`（训练代码）、`data/`（实测/仿真数据日志）

## 上游依赖

不通过 git submodule 引入。M0-M2 阶段如需阅读上游源码（apirrone 4 仓库），临时 clone 到 `~/code/upstream-readonly/` 只读用。submodule 引入推迟到 M2 决策门通过后（见 `../rpiv/requirements/prd-stage-a.md` §5.2）。
