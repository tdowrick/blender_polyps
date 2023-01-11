from typing import List
import bpy
from mathutils import Vector, Euler
import random
import time
import copy


def update_camera(camera):

    x = random.uniform(-0.1, 0.4)
    y = random.uniform(-0.5, 0.1)
    z = random.uniform(-0.4, 0.1)
    vec = Vector((x, y, z))

    rot = Euler()
    rot.x = random.uniform(0, 0.3)
    rot.y = random.uniform(-0.2, 0.4)
    rot.z = random.uniform(-0.4, 0.2)

    camera.location = camera.location + vec
camera.rotation_euler.x = camera.rotation_euler.x + rot.x
camera.rotation_euler.y = camera.rotation_euler.y + rot.y
camera.rotation_euler.z = camera.rotation_euler.z + rot.z

def reset_camera(camera, initial_position, initial_rotation):
    
    camera.location = initial_position
    camera.rotation_euler = initial_rotation
    
def update_light(light):
    
    power = random.randint(25, 200)
    light.energy = power
    print(f"Power: {power}")
    

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
        self.material.node_tree.nodes[name].inputs[idx].default_value = random.uniform(range[0], range[1])

    def randomise_all(self):
        for param in self.to_randomise:
            self.randomise_parameter(param["name"], param["index"], param["range"])

    def sample_rgb_values(self, range):

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
        color_ramp_color = self.sample_rgb_values(self.color_rgb_range)

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

            color_A = self.sample_rgb_values(self.color_rgb_range_A)
            self.update_color_ramp_color(self.color_ramp_A, i, color_A)

            color_B = self.sample_rgb_values(self.color_rgb_range_B)
            self.update_color_ramp_color(self.color_ramp_B, i, color_B)
        

class FatRandominer(MaterialRandomiser):

    def __init__(self, material_name: str):

        super().__init__(material_name)

        self.color_ramp = self.get_material_node_by_name("ColorRamp.001")

        self.bump_node = None

        self.color_rgb_range = [ [0, 0, 0], [1, 1, 0.1] ]
        self.color_position_range = [0, 1]
        self.bump_strength_range = [0, 1]

        self.color_ramp_element_index = 1

        self.to_randomise = [
            {"name": "Noise Texture", "index": 2, "range": [1, 20] },
            {"name": "Noise Texture", "index": 3, "range": [2, 15] },
            {"name": "Wave Texture",     "index": 1, "range": [5, 20]},
            {"name": "Wave Texture.001", "index": 1, "range": [5, 50]},
            {"name": "Wave Texture.002", "index": 1, "range": [5, 20]},
            {"name": "Voronoi Texture.002", "index": 2, "range": [10, 60] },
            {"name": "Displacement", "index" : 2, "range": [0, 0] },
            {"name": "Bump", "index": 0, "range": [0, 1] },
            {"name": "Principled BSDF", "index": 5, "range": [0, 1] }, # Specular
        ]

    def update(self):

        self.randomise_all()

        color = self.sample_rgb_values(self.color_rgb_range)
        self.update_color_ramp_color(self.color_ramp, self.color_ramp_element_index, color)


class LigamentRandomiser(MaterialRandomiser):

    def __init__(self, material_name: str):

        super().__init__(material_name)

        self.to_randomise = [
            {"name": "Principled BSDF", "index": 1, "range": [0.05, 1] }, # Subsurface
            {"name": "Principled BSDF", "index": 5, "range": [0, 1] }, # Specular
        ]

    def update(self):

        self.randomise_all()

random.seed(10)
cam = bpy.data.objects['Camera']
spot  = bpy.data.lights['Spot']

initial_position = copy.deepcopy(cam.location)
initial_rotation = copy.deepcopy(cam.rotation_euler)

liver_randomiser = LiverRandomiser('Liver.001')
background_randomiser = BackgroundRandomiser("Background_Torso")
fat_randomiser = FatRandominer("Fat")
ligament_randomiser = LigamentRandomiser("Ligament")
ball_randomiser = BackgroundRandomiser("Ball Object")

render = True

num_iter = 1000
for i in range(num_iter):
    print("Iteration: " + str(i))

    bpy.data.scenes["Patient10 Render"].render.filepath = f"//render{i}"
    for r in [ball_randomiser, fat_randomiser, background_randomiser, liver_randomiser, ligament_randomiser]:
        r.update()

    update_camera(cam)
    update_light(spot)

    if render:
        bpy.ops.render.render(write_still=True)
    
    else:
        time.sleep(1)
    
    #bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)

    reset_camera(cam, initial_position, initial_rotation)

reset_camera(cam, initial_position, initial_rotation)




###############################################################################
# Color ramp position between 0 and 1
# Color ramp color between R: 0-1, G: 0-0.1 B: 0-0.2 (provisional)

# bump strength between 0 and 1