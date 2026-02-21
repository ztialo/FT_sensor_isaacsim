from isaacsim import SimulationApp

# Start Isaac Sim (set headless to True if you don't need a window)
simulation_app = SimulationApp({"headless": False})

from omni.isaac.core import World
from omni.isaac.core.objects import DynamicCuboid
from omni.isaac.core.utils.prims import get_prim_at_path
from pxr import Gf, UsdPhysics, PhysxSchema
import omni.usd
import numpy as np

# Initialize world
world = World()

world.scene.add_default_ground_plane()

stage = omni.usd.get_context().get_stage()

articulation_path = "/World/Robot"
articulation_root = UsdPhysics.ArticulationRootAPI.Apply(stage.DefinePrim(articulation_path, "Xform"))


# Fixed joint creation
def create_fixed_joint(stage, path, parent_path, child_path, parent_offset, child_offset):
    joint = UsdPhysics.FixedJoint.Define(stage, path)
    joint.CreateBody0Rel().SetTargets([parent_path])
    joint.CreateBody1Rel().SetTargets([child_path])
    joint.CreateLocalPos0Attr().Set(Gf.Vec3f(*parent_offset))
    joint.CreateLocalPos1Attr().Set(Gf.Vec3f(*child_offset))


# Revolute joint creation
def create_revolute_joint(stage, path, parent_path, child_path, parent_offset, child_offset, axis="Z"):
    joint = UsdPhysics.RevoluteJoint.Define(stage, path)
    joint.CreateBody0Rel().SetTargets([parent_path])
    joint.CreateBody1Rel().SetTargets([child_path])
    joint.CreateLocalPos0Attr().Set(Gf.Vec3f(*parent_offset))
    joint.CreateLocalPos1Attr().Set(Gf.Vec3f(*child_offset))
    joint.CreateAxisAttr().Set(axis.upper())
    PhysxSchema.PhysxJointAPI.Apply(joint.GetPrim())
    
    drive_api = UsdPhysics.DriveAPI.Apply(joint.GetPrim(), "revolute_joint")

    # Enable drive on rotation axis (Z axis, index 0 for RevoluteJoint)
    drive_api.CreateTypeAttr().Set("force")
    drive_api.CreateStiffnessAttr().Set(1000.0)    # stiffness of the drive
    drive_api.CreateDampingAttr().Set(100.0)       # damping of the drive
    drive_api.CreateMaxForceAttr().Set(1000.0)   # max force/torque applied

# Dimensions and placement
cube_size = 0.2
offset = cube_size / 2.0 + 0.01
cube_mass = 1.0

base_position = [0.0, 0.0, offset]
body1_pos = [0.0, 0.0, base_position[2] + cube_size]
body2_pos = [0.0, 0.0, body1_pos[2] + cube_size]

# Create robot parts
base = DynamicCuboid("/World/Robot/Base", position=base_position, size=cube_size, color=np.array([1, 0, 0]), mass=cube_mass)
body1 = DynamicCuboid("/World/Robot/Body1", position=body1_pos, size=cube_size, color=np.array([0, 1, 0]), mass=cube_mass)
body2 = DynamicCuboid("/World/Robot/Body2", position=body2_pos, size=cube_size, color=np.array([0, 0, 1]), mass=cube_mass)

# Add joints
create_fixed_joint(stage, "/World/Robot/FixedJoint1", base.prim_path, body1.prim_path, [0, 0, offset], [0, 0, -offset])
create_revolute_joint(stage, "/World/Robot/RevoluteJoint1", body1.prim_path, body2.prim_path, [0, 0, offset], [0, 0, -offset])

# Reset simulation
world.reset()