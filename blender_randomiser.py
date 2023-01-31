from typing import List
import bpy
import sys
import logging
from mathutils import Vector, Euler
import random
import time
import copy
import colorsys

# create logger with 'spam_application'
logger = logging.getLogger('blender')
logger.setLevel(logging.INFO)
# create file handler which logs even debug messages
# fh = logging.FileHandler('render.log')
# fh.setLevel(logging.INFO)
# logger.addHandler(fh)

def update_camera(camera):

    # x = random.uniform(-0.1, 0.4)
    # y = random.uniform(-0.5, 0.1)
    # z = random.uniform(-0.4, 0.1)
    # vec = Vector((x, y, z))

    rot = Euler()
    rot.x = random.uniform(-0.3, 0.3)
    rot.y = random.uniform(-0.4, 0.4)
    rot.z = random.uniform(-0.4, 0.4)

    # camera.location = camera.location + vec
    camera.rotation_euler.x = camera.rotation_euler.x + rot.x
    camera.rotation_euler.y = camera.rotation_euler.y + rot.y
    camera.rotation_euler.z = camera.rotation_euler.z + rot.z

    bpy.data.cameras["Camera.002"].dof.aperture_fstop = random.uniform(1.0, 3.0)

def reset_camera(camera, initial_position, initial_rotation):
    
    #camera.location = initial_position
    camera.rotation_euler = initial_rotation
    
def update_light(light):
    
    power = random.randint(10, 150)
    light.energy = power
    logger.info(f"Power: {power}")
    

class MaterialRandomiser:
    
    def __init__(self, material_name: str):
        self.material = bpy.data.materials[material_name]

        self.to_randomise = []

    def get_material_node_by_name(self, name: str):

        node = self.material.node_tree.nodes[name]

        if name.startswith("ColorRamp"):
            return node.color_ramp

        else:
            return node

    def set_color_ramp_node(self, color_ramp_name: str):
        self.color_ramp = self.get_material_node_by_name(color_ramp_name)

    def set_bump_node(self, bump_node_name: str):
        self.bump_node = self.get_material_node_by_name(bump_node_name)

    def set_displacement_node(self, displacement_node_name: str):
        self.displacement_node = self.get_material_node_by_name(displacement_node_name)

    def update_color_ramp_color(self, node, element: int, color: List[float]):
        node.elements[element].color = color

    def update_color_ramp_position(self, node, element: int, position: float):
        node.elements[element].position = position

    def update_bump_strength(self, strength: float):
        self.bump_node.inputs[0].default_value = strength

    def update_displacement_scale(self, scale: float):
        self.displacement_node.inputs[2].default_value = scale

    def randomise_parameter(self, name, idx, range):
        val = random.uniform(range[0], range[1])
        self.material.node_tree.nodes[name].inputs[idx].default_value = val
        logger.info(f'{name} {idx} set to {val}')

    def randomise_all(self):
        for param in self.to_randomise:
            self.randomise_parameter(param["name"], param["index"], param["range"])

    def sample_rgb_hsv_values(self, range):
        """ Sample three values from a range, can be for either RGB or HSV"""
        r_sample = random.uniform( range[0][0], range[1][0] )
        g_sample = random.uniform( range[0][1], range[1][1] )
        b_sample = random.uniform( range[0][2], range[1][2] )

        color_ramp_color = [r_sample, g_sample, b_sample, 1]

        return color_ramp_color
    

class LiverRandomiser(MaterialRandomiser):

    def __init__(self, material_name: str):
        super().__init__(material_name)

        self.color_ramp = self.get_material_node_by_name('ColorRamp')
        self.bump_node = self.get_material_node_by_name("Bump.003")

        self.color_rgb_range = [ [0, 0, 0], [1, 0.1, 0.1] ]
        self.color_position_range = [0, 1]
        self.bump_strength_range = [0, 1]

        self.color_ramp_element_index = 1

        self.to_randomise = [
                        {"name": "Bump.003", "index": 0, "range": [0, 1] },
            ]

    def update(self):

        self.randomise_all()

        color_ramp_position = random.uniform(self.color_position_range[0], self.color_position_range[1])
        color_ramp_color = self.sample_rgb_hsv_values(self.color_rgb_range)

        self.update_color_ramp_position(self.color_ramp, self.color_ramp_element_index, color_ramp_position)
        self.update_color_ramp_color(self.color_ramp, self.color_ramp_element_index, color_ramp_color)


class BackgroundRandomiser(MaterialRandomiser):

    def __init__(self, material_name: str):

        super().__init__(material_name)

        self.color_ramp_A = None
        self.color_ramp_B = None

        self.color_rgb_range_B = [ [0, 0, 0], [0.2, 0.2, 0.2] ]
        self.color_rgb_range_A = [ [0, 0, 0], [1, 1, 1] ]

        self.color_position_range = [0, 1]

        self.color_ramp_element_index = 1

        self.to_randomise = [
            {"name": "Wave Texture",     "index": 1, "range": [5, 20]},
            {"name": "Wave Texture.001", "index": 1, "range": [5, 50]},
            {"name": "Wave Texture.002", "index": 1, "range": [5, 20]},
            {"name": "Voronoi Texture.002", "index": 2, "range": [10, 60] },
            {"name": "Displacement", "index" : 2, "range": [0, 0.4] },
            {"name": "Bump", "index": 0, "range": [0, 1] },
            {"name": "Principled BSDF", "index": 5, "range": [0, 1] }, # Specular

        ]

        self.color_ramp_A = self.get_material_node_by_name("ColorRamp")
        self.color_ramp_B = self.get_material_node_by_name("ColorRamp.001")

    
    def update(self):

        self.randomise_all()

        pos_A = random.uniform(self.color_position_range[0], self.color_position_range[1])
        pos_B = random.uniform(self.color_position_range[0], self.color_position_range[1])

        self.update_color_ramp_position(self.color_ramp_A, 1, pos_A)
        self.update_color_ramp_position(self.color_ramp_B, 1, pos_B)

        for i in (0, 1):

            color_A = self.sample_rgb_hsv_values(self.color_rgb_range_A)
            self.update_color_ramp_color(self.color_ramp_A, i, color_A)

            color_B = self.sample_rgb_hsv_values(self.color_rgb_range_B)
            self.update_color_ramp_color(self.color_ramp_B, i, color_B)
        

class FatRandominer(MaterialRandomiser):

    def __init__(self, material_name: str):

        super().__init__(material_name)

        self.color_ramp = self.get_material_node_by_name("ColorRamp.001")
        self.bsdf = self.get_material_node_by_name("Principled BSDF")

        self.bump_node = None

        self.color_rgb_range = [ [0, 0, 0], [1, 1, 0.1] ]
        self.color_position_range = [0, 1]
        self.bump_strength_range = [0, 1]

        self.subsurface_hsv_range = [[0, 0, 1], [1, 0.6, 1]]

        self.color_ramp_element_index = 1

        self.to_randomise = [
            {"name": "Noise Texture", "index": 2, "range": [1, 20] },
            {"name": "Noise Texture", "index": 3, "range": [2, 15] },
            {"name": "Wave Texture",     "index": 1, "range": [5, 20]},
            {"name": "Wave Texture.001", "index": 1, "range": [5, 50]},
            {"name": "Wave Texture.002", "index": 1, "range": [5, 20]},
            {"name": "Voronoi Texture.002", "index": 2, "range": [10, 60] },
            {"name": "Displacement", "index" : 2, "range": [0, 0.1] },
            {"name": "Bump.001", "index": 0, "range": [0, 1] },
            {"name": "Principled BSDF", "index": 5, "range": [0, 1] }, # Specular
            {"name": "Mix Shader", "index": 0, "range": [0.5, 1] },
        ]

    def update_subsurface(self):

        hsv = self.sample_rgb_hsv_values(self.subsurface_hsv_range)
        h, s, v = hsv[:3]
        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        self.bsdf.inputs[3].default_value = [r, g, b, 1]
        logger.info(f"H: {h} S: {s} V: {v}")

    def update(self):

        self.randomise_all()

        color = self.sample_rgb_hsv_values(self.color_rgb_range)
        self.update_color_ramp_color(self.color_ramp, self.color_ramp_element_index, color)
        self.update_subsurface()

class LigamentRandomiser(MaterialRandomiser):

    def __init__(self, material_name: str):

        super().__init__(material_name)

        self.to_randomise = [
            {"name": "Principled BSDF", "index": 1, "range": [0.05, 1] }, # Subsurface
            {"name": "Principled BSDF", "index": 5, "range": [0, 1] }, # Specular
        ]

    def update(self):

        self.randomise_all()

class GeometryNodeRandomiser():
    def __init__(self, node_name: str):
        self.node = bpy.data.node_groups[node_name]

        self.to_randomise = [
            {"name": "Value.001", "index": 0, "range": [0.0, 1.0]}, # Geo node noise scale
            {"name": "Proximity Value", "index": 0, "range": [0.15, 0.28]}, # proximity for extrude
            {"name": "Stalk Seed", "index": 0, "range": [0, 10000]}, # Seed for stalk distribution
            {"name": "Sessile Seed", "index": 0, "range": [0, 10000]}, # Seed for sessile distribution
            {"name": "Sessile Seed", "index": 0, "range": [0, 10000]}, # Seed for sessile distribution
            {"name": "Resample Count", "index": 0, "range": [1500, 3000]},
            {"name": "Sessile Distance", "index": 0, "range": [1.0, 3.0]},
            {"name": "Stalk Distance", "index": 0, "range": [2.0, 3.0]}, 
                    ]

    def set_noise_scale_node(self, name: str):
        self.noise_scale_node = self.nodes[name]

    def update(self):
        self.randomise_all()

    def randomise_all(self):
        for param in self.to_randomise:

            if isinstance(param["range"][0], float):
                self.randomise_float(param["name"], param["index"], param["range"])

            elif isinstance(param["range"][0], int):
                self.randomise_int(param["name"], param["index"], param["range"])

    def randomise_float(self, name, idx, range):
        val = random.uniform(range[0], range[1])
        self.node.nodes[name].outputs[idx].default_value = val
        logger.info(f'{name} {idx} set to {val}')

    def randomise_int(self, name, idx, range):
        val = random.randint(range[0], range[1])
        self.node.nodes[name].outputs[idx].default_value = val
        logger.info(f'{name} {idx} set to {val}')

def set_material_or_label(label: bool, geo_node_name: str):

    geo_node = bpy.data.node_groups[geo_node_name]

    sessile_node = geo_node.nodes["Set Material.002"]
    stalk_node = geo_node.nodes["Set Material.001"]
    colon_node = geo_node.nodes["Set Material"]

    if label == False:
        STALK_MATERIAL = "Fat.001"
        SESSILE_MATERIAL = "Fat.001"
        COLON_MATERIAL = "Fat.001"
        bpy.data.scenes[SCENE_NAME].render.engine = "CYCLES"


    else:
        STALK_MATERIAL = "Red"
        SESSILE_MATERIAL = "Red"
        COLON_MATERIAL = "Black"
        bpy.data.scenes[SCENE_NAME].render.engine = "BLENDER_EEVEE"

    sessile_node.inputs[2].default_value =  bpy.data.materials[SESSILE_MATERIAL]
    stalk_node.inputs[2].default_value =    bpy.data.materials[STALK_MATERIAL]
    colon_node.inputs[2].default_value =    bpy.data.materials[COLON_MATERIAL]

# Blender ignores anything after " -- " in arguments, the rest can be parsed here
argv = sys.argv
argv = argv[argv.index("--") + 1:]

NUM_ITER = int(argv[0])
SEED = int(argv[1])
SCENE_NAME = "Colon"

random.seed(SEED)

logger.info(f"Seed is {SEED}")
logger.info(f"Rendering {NUM_ITER} frames")

scene = bpy.context.scene
end_frame = 18000
frame_step = 477
current_frame = 50
scene.frame_set(current_frame)

cam = bpy.data.objects['Camera']
spot  = bpy.data.lights['Spot']

initial_position = copy.deepcopy(cam.location)
initial_rotation = copy.deepcopy(cam.rotation_euler)

# liver_randomiser = LiverRandomiser('Liver.001')
# background_randomiser = BackgroundRandomiser("Background_Torso")
fat_randomiser = FatRandominer("Fat.001")
geo_node_randomiser = GeometryNodeRandomiser("Colon Geo Node")
# ligament_randomiser = LigamentRandomiser("Ligament")
# ball_randomiser = BackgroundRandomiser("Ball Object")

render = True

for i in range(NUM_ITER):


    logger.info("Iteration: " + str(i))

    for r in [fat_randomiser, geo_node_randomiser]:
        r.update()

    update_camera(cam)
    update_light(spot)

    if render:
        # Render image
        bpy.data.scenes[SCENE_NAME].render.filepath = f"//images/seed_{SEED}_render{i}"
        set_material_or_label(False, "Colon Geo Node")
        bpy.ops.render.render(write_still=True)

        # Render label
        bpy.data.scenes[SCENE_NAME].render.filepath = f"//labels/seed_{SEED}_render{i}"
        set_material_or_label(True, "Colon Geo Node")
        bpy.ops.render.render(write_still=True)


    # else:
    #     time.sleep(1)
    
    # bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

    reset_camera(cam, initial_position, initial_rotation)

    current_frame = ( current_frame + frame_step ) % end_frame
    scene.frame_set(current_frame)
    logger.info(f"Frame set to {current_frame}")

set_material_or_label(False, "Colon Geo Node")
bpy.data.scenes[SCENE_NAME].render.engine = "CYCLES"

reset_camera(cam, initial_position, initial_rotation)




###############################################################################
# Color ramp position between 0 and 1
# Color ramp color between R: 0-1, G: 0-0.1 B: 0-0.2 (provisional)

# bump strength between 0 and 1cd