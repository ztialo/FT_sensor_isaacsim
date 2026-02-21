import isaacsim.core.utils.stage as stage_utils
from isaacsim.core.api.robots import RobotView


stage = stage_utils.get_current_stage()
robot_object = RobotView(prim_paths_expr="/World/Robot")
joint_name = "FixedJoint1"

robot_object.initialize()

vals = robot_object.get_measured_joint_forces()

print("All values")
print(vals)

val = robot_object.get_measured_joint_forces(joint_names=[joint_name])

print("Measured joint force by name")
print(val)

joint_index = robot_object._metadata.joint_indices[joint_name] + 1
val = robot_object.get_measured_joint_forces(joint_indices=[joint_index])

print("Measured joint force by index (as in doc)")
print(val)