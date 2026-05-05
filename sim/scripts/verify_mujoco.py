"""W1-5 验收脚本：验证 MuJoCo 装好可用。

用法（WSL Ubuntu 内）：
    cd /mnt/d/CODE/guagua/sim
    uv run python scripts/verify_mujoco.py
"""

import mujoco

print(f"MuJoCo version: {mujoco.__version__}")

import mujoco.viewer  # noqa: F401  仅验证 viewer 模块可 import（不启动 GUI）

print("mujoco.viewer module: importable")

xml = """
<mujoco>
  <worldbody>
    <body pos="0 0 1">
      <freejoint/>
      <geom type="sphere" size="0.1"/>
    </body>
  </worldbody>
</mujoco>
"""
m = mujoco.MjModel.from_xml_string(xml)
d = mujoco.MjData(m)
mujoco.mj_step(m, d)

print(f"sphere model: nq={m.nq} nv={m.nv} nbody={m.nbody}")
print(f"after 1 step, qpos={d.qpos}")
print("=== ALL OK ===")
