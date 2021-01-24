# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110 - 1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
        "name": "Areatype Split (3D View/UV Editor)",
        "description":"a button which toggles a split of an area with another.",
        "author":"dustractor@gmail.com",
        "version":(0,2),
        "blender":(2,80,0),
        "location":"Prepended to the header of the viewport.",
        "warning":"",
        "wiki_url":"",
        "category": "System"
        }

import bpy

_area_type_enums = [
    _.identifier for _ in bpy.types.Area.bl_rna.properties["type"].enum_items]

class AREATYPE_OT_split(bpy.types.Operator):
    bl_idname = "areatype.splitview"
    bl_label = "areatype.splitview"
    splittype: bpy.props.EnumProperty(
        items=[(_,_,_) for _ in _area_type_enums],
        default="IMAGE_EDITOR")
    direction: bpy.props.EnumProperty(
        items=[(_,_,_) for _ in ("HORIZONTAL","VERTICAL")],
        default="VERTICAL")
    def execute(self,context):
        A = context.area
        _type = A.type
        rs = [_ for _ in context.screen.areas if _.x > A.x and _.y == A.y]
        if not rs:
            A.type = self.splittype
            bpy.ops.screen.area_split(direction=self.direction)
            B = context.screen.areas[-1]
            B.type = _type
        else:
            B = rs[0]
            c = (A.x+A.width+3,A.x+A.height//2)
            bpy.ops.screen.area_join(cursor=c)
            fakectx = dict()
            B.type = _type
            fakectx["area"] = B
            bpy.ops.screen.screen_full_area(fakectx)
            bpy.ops.screen.screen_full_area()
        return {"FINISHED"}


def viewdraw(self,context):
    layout = self.layout
    op = layout.operator("areatype.splitview",text="",icon="IMAGE")
    op.splittype = "IMAGE_EDITOR"


def register():
    bpy.types.VIEW3D_HT_header.prepend(viewdraw)
    bpy.utils.register_class(AREATYPE_OT_split)


def unregister():
    bpy.types.VIEW3D_HT_header.remove(viewdraw)
    bpy.utils.unregister_class(AREATYPE_OT_split)

