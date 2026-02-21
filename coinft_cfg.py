import os
import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets.articulation import ArticulationCfg
from isaaclab.assets import AssetBaseCfg

script_dir = os.path.dirname(os.path.abspath(__file__))
sensor_usd_path = os.path.join(
    script_dir,
    "asset",
    "coinft_prototype.usd",
)

COINFT_CFG = AssetBaseCfg(
    spawn=sim_utils.UsdFileCfg(
        usd_path=sensor_usd_path,
        scale=[10, 10, 10],
    ),
    init_state=AssetBaseCfg.InitialStateCfg(
        pos=(0.0, -0.25, 0.05),
    ),
)

# COINFT_CFG = ArticulationCfg(
#     spawn=sim_utils.UsdFileCfg(
#         usd_path=sensor_usd_path,
#         scale=[10, 10, 10],
#     ),
#     init_state=ArticulationCfg.InitialStateCfg(
#         pos=(0.0, 0.0, 0.05),
#     ),
#     actuators={},
# )
