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

_t = bpy.types
map_ui_type_to_header = {
    "CLIP_EDITOR":_t.CLIP_HT_header,
    "CONSOLE":_t.CONSOLE_HT_header,
    "CompositorNodeTree":_t.NODE_HT_header,
    "DOPESHEET":_t.DOPESHEET_HT_header,
    "DRIVERS":_t.GRAPH_HT_header,
    "FCURVES":_t.GRAPH_HT_header,
    "FILE_BROWSER":_t.FILEBROWSER_HT_header,
    "IMAGE_EDITOR":_t.IMAGE_HT_header,
    "INFO":_t.INFO_HT_header,
    "NLA_EDITOR":_t.NLA_HT_header,
    "OUTLINER":_t.OUTLINER_HT_header,
    "PROPERTIES":_t.PROPERTIES_HT_header,
    "SEQUENCE_EDITOR":_t.SEQUENCER_HT_header,
    "ShaderNodeTree":_t.NODE_HT_header,
    "TEXT_EDITOR":_t.TEXT_HT_header,
    "TIMELINE":_t.DOPESHEET_HT_header,
    "TextureNodeTree":_t.NODE_HT_header,
    "UV":_t.IMAGE_HT_header,
    "VIEW_3D":_t.VIEW3D_HT_header
}
ui_type_enums = [
    "CLIP_EDITOR",
    "CONSOLE",
    "CompositorNodeTree",
    "DOPESHEET",
    "DRIVERS",
    "FCURVES",
    "FILE_BROWSER",
    "IMAGE_EDITOR",
    "INFO",
    "INFO",
    "NLA_EDITOR",
    "OUTLINER",
    "PREFERENCES"
    "PROPERTIES",
    "SEQUENCE_EDITOR",
    "ShaderNodeTree",
    "TEXT_EDITOR",
    "TIMELINE",
    "TextureNodeTree",
    "UV",
    "VIEW_3D",
]

class AREATYPE_OT_split(bpy.types.Operator):
    bl_idname = "areatype.splitview"
    bl_label = "areatype.splitview"
    splittype: bpy.props.EnumProperty(
        items=[(_,_,_) for _ in ui_type_enums],
        default="IMAGE_EDITOR")
    direction: bpy.props.EnumProperty(
        items=[(_,_,_) for _ in ("HORIZONTAL","VERTICAL")],
        default="VERTICAL")
    def invoke(self,context,event):
        self.direction = ["VERTICAL","HORIZONTAL"][event.shift]
        return self.execute(context)
    def execute(self,context):
        area1 = context.area
        sortx = lambda _:_.x
        sorty = lambda _:_.x
        above_on_x_same_on_y = lambda _:_.x > area1.x and _.y == area1.y
        above_on_y_same_on_x = lambda _:_.y > area1.y and _.x == area1.x
        if self.direction == "VERTICAL":
            key = sortx
            filt = above_on_x_same_on_y
        else:
            key = sorty
            filt = above_on_y_same_on_x
        sibs_ds = list(sorted(filter(filt,context.screen.areas),key=key))
        _type = area1.ui_type
        if not sibs_ds:
            area1.ui_type = self.splittype
            bpy.ops.screen.area_split(direction=self.direction)
            area2 = context.screen.areas[-1]
            area2.ui_type = _type
        else:
            area2 = sibs_ds[0]
            area2.ui_type = _type
            if self.direction == "VERTICAL":
                c = (area2.x,area1.height)
            else:
                c = (area2.y,area1.width)
            fake1 = dict(area=area1)
            fake2 = dict(area=area2)
            bpy.ops.screen.area_join(fake1,cursor=c)
            bpy.ops.screen.screen_full_area(fake2)
            bpy.ops.screen.screen_full_area()
        return {"FINISHED"}
class AreaTypeSplitPrefs(bpy.types.AddonPreferences):
    bl_idname = __package__
    config_string: bpy.props.StringProperty(
        description="comma-separated list of pipe-separated area-uitype pairs",
        default=("VIEW_3D|IMAGE_EDITOR,"
                 "IMAGE_EDITOR|UV,"
                 "ShaderNodeTree|UV,"
                 "PROPERTIES|OUTLINER,"
                 "TIMELINE|DOPESHEET,"
                 "FCURVES|DRIVERS,"
                 "CONSOLE|TEXT_EDITOR,"
                 "INFO|CONSOLE,"
                 "SEQUENCE_EDITOR|SEQUENCE_EDITOR"))
    @property
    def config_pairs(self):
        yield from [p.split("|") for p in self.config_string.split(",")]
    def draw(self,context):
        self.layout.prop(self,"config_string")
        for a,b in self.config_pairs:
            row = self.layout.row()
            row.label(text=a)
            row.label(text=b,icon="TRIA_RIGHT")

headerdrawfuncs = []
def register():
    headerdrawfuncs.clear()
    bpy.utils.register_class(AREATYPE_OT_split)
    bpy.utils.register_class(AreaTypeSplitPrefs)
    prefs = bpy.context.preferences.addons[__package__].preferences
    P = list(prefs.config_pairs)

    for fromarea,toarea in P:
        ht = map_ui_type_to_header.get(fromarea,None)
        if ht:
            def f(self,context,toarea=toarea):
                op = self.layout.operator("areatype.splitview",text="",icon="BLANK1")
                op.splittype = toarea
            ht.prepend(f)
            headerdrawfuncs.append((ht,f))


def unregister():
    for header,func in headerdrawfuncs:
        header.remove(func)

    bpy.utils.unregister_class(AREATYPE_OT_split)
    bpy.utils.unregister_class(AreaTypeSplitPrefs)

