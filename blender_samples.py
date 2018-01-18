import bpy
from mathutils import Vector

# ------------------------
# camera parameters
cam_x = 6
cam_y = -31
cam_z = 8
cam_alp = 90*(3.141592/180.0)
cam_bet = 0
cam_gam = 0

# lighting parameters - lamp
lamp_x = -0.8
lamp_y = -19.3
lamp_z = 9.5
lamp_en = 1
lamp_dist = 200

# lighting parameters - hemispere
hemi_x = 18.5
hemi_y = -21
hemi_z = 18.8
hemi_en = 0.57
hemi_alp = -225*(3.141592/180.0)
hemi_bet = -118*(3.141592/180.0)
hemi_gam = 2.6*(3.141592/180.0)

width = 3  # half the width of a layer
sub_th = 1  # substrate thickness
buf_th = 1.39  # buffer thickness
layr_th = 0.1  # single DBR layer thickness
QW_th = 0.01  # QW thickness

N_lower = 26*2  # number of layers in lower DBRs
N_middle = 16*2  # number of layers in middle DBRs
N_upper = 22*2  # number of layers in top DBRs

# cut in the lower layers
cut_buffer = False
cut_substrate = True
cut_z1 = 0.5*sub_th  # height of the middle of lower cut
cut_z2 = 0.5*buf_th + sub_th  # height of the middle of the higher cut
cut_th = 0.1  # width of the cut
n_halves = 3  # how many wave maxima in the cut
amplitude = 0.1  # amplitute of the wave in the cut

# render resolution
res_x = 3000
res_y = 2000
render_res = 50  # resolution in %
render_path = './blender_sample.png'
render_to_file = True


# ------------------------
def createMeshFromData(name, origin, verts, faces):
    # Create mesh and object
    me = bpy.data.meshes.new(name+'Mesh')
    ob = bpy.data.objects.new(name, me)
    ob.location = origin
    ob.show_name = True

    # Link object to scene and make active
    scn = bpy.context.scene
    scn.objects.link(ob)
    scn.objects.active = ob
    ob.select = True

    # Create mesh from given verts, faces.
    me.from_pydata(verts, [], faces)
    # Update mesh with new data
    me.update()
    return ob


def makeMaterial(name, diffuse, specular, alpha, emit):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = diffuse
    mat.diffuse_shader = 'LAMBERT'
    mat.diffuse_intensity = 1.0
    mat.specular_color = specular
    mat.specular_shader = 'COOKTORR'
    mat.specular_intensity = 0.5
    mat.alpha = alpha
    mat.ambient = 1
    mat.emit = emit
    return mat


def setMaterial(ob, mat):
    me = ob.data
    me.materials.append(mat)


def run(origo):
    origin = Vector(origo)
    verts = ((1, 1, 0), (1, -1, 0), (-1, -1, 0), (-1, 1, 0),
             (-1, 1, 1), (-1, -1, 1), (1, -1, 1), (1, 1, 1))
    faces = ((0, 1, 2, 3), (0, 7, 4, 3), (0, 1, 6, 7),
             (1, 2, 5, 6), (2, 3, 4, 5), (4, 5, 6, 7))
    createMeshFromData('warstwa', origin, verts, faces)
    return


def make_layer(x0, y0, z0, x, y, z, mat):
    run((x0, y0, z0))
    setMaterial(bpy.context.object, mat)
    bpy.context.object.scale = (x, y, z)
    new_z = z0 + z
    return new_z


def kamera():
    try:
        obj = bpy.data.objects['Camera']  # bpy.types.Camera
        obj.location.x = cam_x
        obj.location.y = cam_y
        obj.location.z = cam_z
        obj.rotation_mode = 'XYZ'
        obj.rotation_euler[0] = cam_alp
        obj.rotation_euler[1] = cam_bet
        obj.rotation_euler[2] = cam_gam
        bpy.data.scene.camera = obj
    except:
        bpy.ops.object.camera_add(view_align=False,
                                  enter_editmode=False,
                                  location=(cam_x, cam_y, cam_z),
                                  rotation=(cam_alp, cam_bet, cam_gam),
                                  layers=(True, False, False, False,
                                          False, False, False, False,
                                          False, False, False, False,
                                          False, False, False, False,
                                          False, False, False, False))
        obj = bpy.data.objects['Camera']  # bpy.types.Camera
        sceneKey = bpy.data.scenes.keys()[0]
        bpy.data.scenes[sceneKey].camera = obj

    bpy.context.scene.render.resolution_x = res_x
    bpy.context.scene.render.resolution_y = res_y
    bpy.context.scene.render.resolution_percentage = render_res

    return None


def lampa():
    # point
    lamp_data = bpy.data.lamps.new(name="Lamp", type='POINT')
    lamp_object = bpy.data.objects.new(name="Lamp",
                                       object_data=lamp_data)
    scene.objects.link(lamp_object)
    lamp_object.location = (lamp_x, lamp_y, lamp_z)
    lamp_object.data.energy = lamp_en
    lamp_object.data.distance = lamp_dist
    lamp_object.select = True
    scene.objects.active = lamp_object
    # hemisphere
    hemi_data = bpy.data.lamps.new(name="Hemi", type='HEMI')
    hemi_object = bpy.data.objects.new(name="Hemi",
                                       object_data=hemi_data)
    scene.objects.link(hemi_object)
    hemi_object.location = (hemi_x, hemi_y, hemi_z)
    hemi_object.rotation_mode = 'XYZ'
    hemi_object.rotation_euler = (hemi_alp, hemi_bet, hemi_gam)
    hemi_object.data.energy = hemi_en
    hemi_object.select = True
    scene.objects.active = hemi_object

    return None


def swiat():
    bpy.context.scene.world.horizon_color = (1, 1, 1)
    bpy.context.scene.world.zenith_color = (1, 1, 1)
    return None


def delete_all():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()


def render():

    for obj in bpy.data.objects:
        # Find cameras that match cameraNames
        if (obj.type == 'Camera'):
            bpy.data.scene.camera = obj

    bpy.context.scene.render.engine = 'BLENDER_RENDER'
    bpy.context.scene.render.filepath = render_path
    bpy.ops.render.render(write_still=True)


def cut(width, cut_z, cut_th, n_halves, cut_ampl):
    # create mesh
    bpy.ops.mesh.primitive_z_function_surface(
            equation="%f*cos(2*3.1415/8*%i*x)" % (cut_ampl, n_halves),
            div_x=200, div_y=3, size_x=2.02*width, size_y=2.02*width)
    bpy.context.object.location[0] = 0
    bpy.context.object.location[1] = 0
    bpy.context.object.location[2] = cut_z - cut_th/2
    # extrude mesh
    bpy.ops.object.editmode_toggle()  # to 'edit mode'
    bpy.ops.mesh.extrude_region_move(
            MESH_OT_extrude_region={"mirror": False},
            TRANSFORM_OT_translate={"value": (0, 0, cut_th),
                                    "constraint_axis": (False, False, True),
                                    "constraint_orientation": 'NORMAL',
                                    "mirror": False,
                                    "proportional": 'DISABLED',
                                    "proportional_edit_falloff": 'SMOOTH',
                                    "proportional_size": 1, "snap": False,
                                    "snap_target": 'CLOSEST',
                                    "snap_point": (0, 0, 0),
                                    "snap_align": False,
                                    "snap_normal": (0, 0, 0),
                                    "gpencil_strokes": False,
                                    "texture_space": False,
                                    "remove_on_cancel": False,
                                    "release_confirm": False})
    bpy.ops.object.editmode_toggle()  # back to 'object mode'

    bpy.ops.object.move_to_layer(layers=(False, True, False, False, False,
                                         False, False, False, False, False,
                                         False, False, False, False, False,
                                         False, False, False, False, False))

if __name__ == "__main__":
    delete_all()
    # make material:   name,   diffuse(rgb), specular(rgb),  alpha , emit
    sub = makeMaterial('sub', (0.84, 0.77, 0.72), (0.84, 0.77, 0.72), 1, 0)
    buf = makeMaterial('buf', (0.77, 0.66, 0.53), (0.77, 0.66, 0.53), 1, 0)
    ZnTe = makeMaterial('ZnTe', (0.94, 0.92, 0.92), (0.94, 0.92, 0.92), 1, 0)
    CdMgSe = makeMaterial('CdMgSe', (212/255, 229/255, 105/255),
                          (212/255, 229/255, 105/255), 1, 0)
    QW_lower = makeMaterial('QW', (0.99, 0.0, 0), (0.91, 0.11, 0), 1, 1)
    QW_upper = makeMaterial('QW', (0.0, 0.0, 0.99), (0.91, 0.11, 0), 1, 1)
    SL = makeMaterial('SL', (0.70, 0.82, 0.91), (0.70, 0.82, 0.91), 1, 0)

    scene = bpy.context.scene
    kamera()
    lampa()
    swiat()

# strukture of the sample
# ---------------------------------------------------------------------------
    #  substrate
    new_z = make_layer(0, 0, 0, width, width, sub_th, sub)
    substrate = bpy.context.active_object
    bpy.ops.object.select_all(action="DESELECT")
    # buffer
    new_z = make_layer(0, 0, new_z, width, width, buf_th, ZnTe)
    buffer = bpy.context.active_object
    bpy.ops.object.select_all(action="DESELECT")
    # lower DBRs
    for index in range(0, N_lower):
        if (index % 2) == 1:
            new_z = make_layer(0, 0, new_z, width, width, layr_th, SL)
        else:
            new_z = make_layer(0, 0, new_z, width, width, layr_th, ZnTe)
    # lower cavity
    new_z = make_layer(0, 0, new_z, width, width, 2*layr_th-0.5*QW_th, ZnTe)
    new_z = make_layer(0, 0, new_z, width, width, QW_th, QW_lower)
    new_z = make_layer(0, 0, new_z, width, width, 2*layr_th-0.5*QW_th, ZnTe)

    # middle DBRs
    for index in range(0, N_middle-1):
        if (index % 2) == 1:
            new_z = make_layer(0, 0, new_z, width, width, layr_th, ZnTe)
        else:
            new_z = make_layer(0, 0, new_z, width, width, layr_th, SL)

    # upper cavity
    new_z = make_layer(0, 0, new_z, width, width, 2*layr_th-0.5*QW_th, ZnTe)
    new_z = make_layer(0, 0, new_z, width, width, QW_th, QW_upper)
    new_z = make_layer(0, 0, new_z, width, width, 2*layr_th-0.5*QW_th, ZnTe)

    # upper DBRs
    for index in range(0, N_upper):
        if (index % 2) == 0:
            new_z = make_layer(0, 0, new_z, width, width, layr_th, SL)
        else:
            new_z = make_layer(0, 0, new_z, width, width, layr_th, ZnTe)
    # wave-like cut
    cut(width, cut_z1, cut_th, n_halves, amplitude)
    cut1 = bpy.context.active_object
    bpy.ops.object.select_all(action="DESELECT")

    cut(width, cut_z2, cut_th, n_halves, amplitude)
    cut2 = bpy.context.active_object
    bpy.ops.object.select_all(action="DESELECT")

    # cutting the substrate
    if cut_substrate:
        bool_one = substrate.modifiers.new(type="BOOLEAN", name="bool 1")
        bool_one.object = cut1
        bool_one.operation = "DIFFERENCE"
        cut1.hide = True

    # cutting the buffer
    if cut_buffer:
        bool_two = buffer.modifiers.new(type="BOOLEAN", name="bool 2")
        bool_two.object = cut2
        bool_two.operation = "DIFFERENCE"
        cut2.hide = True

    # rendering to file
    if render_to_file:
        render()
