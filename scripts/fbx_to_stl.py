# Blender export all .fbx collections inside a .blend file to .stl format. 
#
# https://stackoverflow.com/questions/38096913/blender-convert-stl-to-obj-with-prompt-commande
# https://blender.stackexchange.com/questions/168140/batch-exporting-scene-collections-or-selected-objects-using-gltf-blender-io
#
# Usage:
# $ /Applications/Blender.app/Contents/MacOS/Blender --background --python fbx_to_stl.py -- ~/Desktop/NaomiUniversal3D/assets/CCBYNCSA_NaomiUniversalArcadeCabinets.blend

import bpy
import sys
from pathlib import Path

argv = sys.argv
argv = argv[argv.index("--") + 1:] # get all args after "--"

blend_in = argv[0]
stl_out = "/tmp/"    # You should probably make this somewhere that you care about... 

# Import entire scene
bpy.ops.wm.open_mainfile(filepath=blend_in)

# Export entire scene as .STL
bpy.ops.export_mesh.stl(filepath=stl_out + blend_in.split("/")[-1:][0].split(".")[0] + ".stl")

# export individual objects as STL
context = bpy.context
scene = context.scene
viewlayer = context.view_layer

obs = [o for o in scene.objects if o.type == 'MESH']
bpy.ops.object.select_all(action='DESELECT')    
for ob in obs:
	viewlayer.objects.active = ob
	ob.select_set(True)
	stl_path = stl_out + ob.users_collection[0].name + "_" + ob.name + ".stl"
##### DISABLED ########
#	bpy.ops.export_mesh.stl(
#		filepath=str(stl_path),
#		use_selection=True)
	ob.select_set(False)


# Export each cabinet collection 

col_levels = 1                          # Levels to export
scn_col = bpy.context.scene.collection  # Root collection

def file_name(s):
    '''Return valid file name from string'''
    return "".join(x for x in s if x.isalnum())

def col_hierarchy(root_col, levels=1):
    '''Read hierarchy of the collections in the scene'''
    level_lookup = {}
    def recurse(root_col, parent, depth):
        if depth > levels: 
            return
        if isinstance(parent,  bpy.types.Collection):
            level_lookup.setdefault(parent, []).append(root_col)
        for child in root_col.children:
            recurse(child, root_col,  depth + 1)
    recurse(root_col, root_col.children, 0)
    return level_lookup

lkp_col = col_hierarchy(scn_col, levels=col_levels)
prt_col = {i : k for k, v in lkp_col.items() for i in v}
candidates = [x for v in lkp_col.values() for x in v]

for c in candidates:
    prt_col.get(c).children.unlink(c)

for c in candidates:
    scn_col.children.link(c)
    bpy.ops.export_mesh.stl(
        filepath=stl_out + "CCBYNCSA_" + file_name(c.name) + ".stl"
    )
    scn_col.children.unlink(c)

for c in candidates: prt_col.get(c).children.link(c)

