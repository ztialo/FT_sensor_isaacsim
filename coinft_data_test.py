"""Launch Isaac Sim Simulator first."""

import argparse

from isaaclab.app import AppLauncher

# add argparse arguments
parser = argparse.ArgumentParser(
    description="Piper arms using the differential IK controller."
)
# append AppLauncher cli args
AppLauncher.add_app_launcher_args(parser)
# parse the arguments
args_cli = parser.parse_args()
args_cli.num_envs = 1

# launch omniverse app
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

"""Rest everything follows."""
import torch

import isaaclab.sim as sim_utils
from isaaclab.utils import configclass
from isaaclab.scene import InteractiveScene, InteractiveSceneCfg
from isaaclab.assets import AssetBaseCfg, RigidObjectCfg
import isaacsim.core.utils.stage as stage_utils
from isaacsim.core.api.robots import RobotView
from coinft_cfg import COINFT_CFG

@configclass
class SceneCfg(InteractiveSceneCfg):
    """Configuration for a workstation scene with a table and piper robot arms."""

    # Ground-plane
    ground = AssetBaseCfg(
        prim_path="/World/defaultGroundPlane",
        spawn=sim_utils.GroundPlaneCfg(
            color=(0.40, 0.26, 0.13),
        ),
        init_state=AssetBaseCfg.InitialStateCfg(pos=(0.0, 0.0, -0.795)),
    )

    # Lights
    dome_light = AssetBaseCfg(
        prim_path="/World/Light",
        spawn=sim_utils.DomeLightCfg(intensity=3000.0, color=(0.75, 0.75, 0.75)),
    )

    # sensor
    coinft = COINFT_CFG.replace(prim_path="/World/tactile_sensor")

    # sphere
    sphere = RigidObjectCfg(
        prim_path="/World/sphere",
        spawn=sim_utils.SphereCfg(
            radius=0.15,
            rigid_props=sim_utils.RigidBodyPropertiesCfg(),
            mass_props=sim_utils.MassPropertiesCfg(mass=10.0),
            collision_props=sim_utils.CollisionPropertiesCfg(),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(1.0, 0.0, 0.0)),
        ),
        init_state=RigidObjectCfg.InitialStateCfg(pos=(0.0, 0.0, 1)),
    )


def run_simulator(sim: sim_utils.SimulationContext, scene: InteractiveScene):
    """Run the simulation loop."""
    sensor = scene["coinft"]
    sphere = scene["sphere"]
    
    stage = stage_utils.get_current_stage()
    robot_object = RobotView(prim_paths_expr="/World/tactile_sensor")
    joint_name = "FixedJoint"

    robot_object.initialize()

    # Define simulation stepping
    sim_dt = sim.get_physics_dt()
    count = 0

    while sim.app.is_running():
        if count % 400 == 0:
            print("Resetting scene...")
            # reset scnene
            sphere_root_state = sphere.data.default_root_state.clone()
            sphere.write_root_pose_to_sim(sphere_root_state[:, :7])
            sphere.write_root_velocity_to_sim(torch.tensor([[0.0, 0.0, 0.0, 1.0, -2.0, 3.0]]))
            sphere.reset()
            # reset counter
            count = 0
        elif count % 5 == 0:
            val = robot_object.get_measured_joint_forces(joint_names=[joint_name])
            print(val)

        # Update counter
        count += 1
        # Step the simulation
        sim.step()
        # Update the scene
        scene.update(sim_dt)


def main():
    """Main function"""
    sim_cfg = sim_utils.SimulationCfg(dt=0.01, device=args_cli.device)
    sim = sim_utils.SimulationContext(sim_cfg)
    # Set main camera
    sim.set_camera_view([0.5, 0.5, 0.5], [0.0, 0.0, 0.0])
    # Desine scene
    scene_cfg = SceneCfg(num_envs=args_cli.num_envs, env_spacing=2.5)
    scene = InteractiveScene(scene_cfg)
    # Play the simulator
    sim.reset()
    # Now we are ready!
    print("[INFO]: Setup complete...")
    # Run the simulator
    run_simulator(sim, scene)


if __name__ == "__main__":
    # run the main function
    main()
    # close the app
    simulation_app.close()
