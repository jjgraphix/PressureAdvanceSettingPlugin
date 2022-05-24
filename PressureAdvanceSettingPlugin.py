# PressureAdvanceSettingPlugin v1.4.0
# For Personal Use - Copyright (c) 2022 JJFX Design
# Project based on LinearAdvanceSettingPlugin (Copyright (c) 2020 Aldo Hoeben / fieldOfView)
# The PressureAdvanceSettingPlugin is released under the terms of the AGPLv3 or higher.
#
# ** Compatible ONLY with Klipper Firmware **
# ** Tested up to Cura version 5.0

from UM.Extension import Extension
from cura.CuraApplication import CuraApplication
from UM.Logger import Logger
from UM.Version import Version
from UM.Settings.SettingDefinition import SettingDefinition
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.ContainerRegistry import ContainerRegistry

from UM.Scene.Iterator.DepthFirstIterator import DepthFirstIterator

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("PressureAdvanceSettingPlugin")

import collections
import json
import os.path

from typing import List, Optional, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from UM.OutputDevice.OutputDevice import OutputDevice

class PressureAdvanceSettingPlugin(Extension):
    def __init__(self) -> None:
        super().__init__()

        self._application = CuraApplication.getInstance()

        self._i18n_catalog = None  # type: Optional[i18nCatalog]

        self._settings_dict = {}  # type: Dict[str, Any]
        self._expanded_categories = []  # type: List[str]  # temporary list used while creating nested settings

        try:
            api_version = self._application.getAPIVersion()
        except AttributeError:
            # UM.Application.getAPIVersion was added for API > 6 (Cura 4)
            # Since this plugin version is only compatible with Cura 3.5 and newer, and no version-granularity
            # is required before Cura 4.7, it is safe to assume API 5
            api_version = Version(5)

        if api_version < Version("7.3.0"):
            settings_definition_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pressure_advance35.def.json")
        else:
            settings_definition_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pressure_advance47.def.json")
        try:
            with open(settings_definition_path, "r", encoding = "utf-8") as f:
                self._settings_dict = json.load(f, object_pairs_hook = collections.OrderedDict)
        except:
            Logger.logException("e", "Could not load pressure advance settings definition")
            return

        ContainerRegistry.getInstance().containerLoadComplete.connect(self._onContainerLoadComplete)
        self._application.getOutputDeviceManager().writeStarted.connect(self._filterGcode)

    def _onContainerLoadComplete(self, container_id: str) -> None:
        if not ContainerRegistry.getInstance().isLoaded(container_id):
            # skip containers that could not be loaded, or subsequent findContainers() will cause an infinite loop
            return

        try:
            container = ContainerRegistry.getInstance().findContainers(id = container_id)[0]
        except IndexError:
            # the container no longer exists
            return
            
        if not isinstance(container, DefinitionContainer):
            # skip containers that are not definitions
            return
        if container.getMetaDataEntry("type") == "extruder":
            # skip extruder definitions
            return

        try:
            material_category = container.findDefinitions(key="material")[0]
        except IndexError:
            Logger.log("e", "Could not find parent category setting to add settings to")
            return

        for setting_key in self._settings_dict.keys():
            setting_definition = SettingDefinition(setting_key, container, material_category, self._i18n_catalog)
            setting_definition.deserialize(self._settings_dict[setting_key])

            # add the setting to already existing material setting definition
            # private member access is naughty, but the alternative is to serialise, nix and deserialise the whole thing,
            # which breaks stuff
            material_category._children.append(setting_definition)
            container._definition_cache[setting_key] = setting_definition

            self._expanded_categories = self._application.expandedCategories.copy()
            self._updateAddedChildren(container, setting_definition)
            self._application.setExpandedCategories(self._expanded_categories)
            self._expanded_categories = []  # type: List[str]
            container._updateRelations(setting_definition)

    def _updateAddedChildren(self, container: DefinitionContainer, setting_definition: SettingDefinition) -> None:
        children = setting_definition.children
        if not children or not setting_definition.parent:
            return
        # make sure this setting is expanded so its children show up in setting views
        if setting_definition.parent.key in self._expanded_categories:
            self._expanded_categories.append(setting_definition.key)

        for child in children:
            container._definition_cache[child.key] = child
            self._updateAddedChildren(container, child)

    def _filterGcode(self, output_device: "OutputDevice") -> None:
        scene = self._application.getController().getScene()
        global_container_stack = self._application.getGlobalContainerStack()
        extruder_manager = self._application.getExtruderManager()
        used_extruder_stacks = self._application.getExtruderManager().getUsedExtruderStacks()
        
        if not global_container_stack or not used_extruder_stacks:
            return

        # Retrieve state of pressure advance control setting (Bool)
        pressure_advance_control = global_container_stack.getProperty("material_pressure_advance_enable", "value")
        if not pressure_advance_control:
            Logger.log("i", "Pressure Advance Control is Disabled - Gcode Not Processed")
            return # Do not process gcode if Disabled

        gcode_dict = getattr(scene, "gcode_dict", {})
        if not gcode_dict: # this also checks for an empty dict
            Logger.log("w", "Scene has no gcode to process")
            return

        # Pressure advance Klipper command template
        gcode_cmd_pattern = "SET_PRESSURE_ADVANCE ADVANCE=%f EXTRUDER=%s"
        gcode_cmd_pattern += " ;PressureAdvanceSettingPlugin"

        dict_changed = False

        for plate_id in gcode_dict:
            gcode_list = gcode_dict[plate_id]
            if len(gcode_list) < 2:
                Logger.log("w", "Plate %s does not contain any layers", plate_id)
                continue
            if ";PRESSUREADVANCEPROCESSED\n" in gcode_list[0]:
                Logger.log("d", "Plate %s has already been processed", plate_id)
                continue

            setting_key = "material_pressure_advance_factor"
            active_extruder_list = list(range(len([extruder for extruder in used_extruder_stacks if extruder.isEnabled])))
            non_mesh_features = list(self.__gcode_type_to_setting_key)[8:] # SUPPORT, SKIRT, etc.

            # Extruder Dictionaries
            apply_factor_per_feature = {}  # type: Dict[int, bool]
            current_advance_factors = {}  # type: Dict[int, float]
            per_extruder_settings = {} # type: Dict[(int,str), float]
            # Mesh Object Dictionaries
            apply_factor_per_mesh = {}  # type: Dict[str, bool]
            per_mesh_settings = {} # type: Dict[(str,str), float]
            per_mesh_extruders = {} # type: Dict[str, int]

            # GET SETTINGS FOR ALL EXTRUDERS
            for extruder_stack in used_extruder_stacks:
                extruder_nr = int(extruder_stack.getProperty("extruder_nr", "value"))
                # Convert extruder number to str for Klipper
                extruder_klip = "extruder" + str(extruder_nr) if extruder_nr > 0 else "extruder"
                
                pressure_advance_factor = extruder_stack.getProperty(setting_key, "value")
                current_advance_factors[extruder_nr] = pressure_advance_factor
                try:
                    gcode_list[1] = gcode_list[1] + gcode_cmd_pattern % (pressure_advance_factor, extruder_klip) + "\n"
                except TypeError:
                    Logger.log("e", "Invalid pressure advance value: '%s'", pressure_advance_factor)
                    return

                dict_changed = True # Primary values for each extruder added to start of gcode

                # Get all feature settings for each extruder
                for feature_type_key,feature_setting_key in self.__gcode_type_to_setting_key.items():
                    per_extruder_settings[(extruder_nr,feature_type_key)] = extruder_stack.getProperty(feature_setting_key, "value")
                    # Check for unique feature settings
                    if (not apply_factor_per_feature.get(extruder_nr, False)
                        and per_extruder_settings[(extruder_nr,feature_type_key)] != pressure_advance_factor):

                        apply_factor_per_feature[extruder_nr] = True # Start gcode processing loop


            # GET SETTINGS FOR ALL PRINTABLE MESH OBJECTS THAT ARE NOT SUPPORT
            nodes = [node for node in DepthFirstIterator(scene.getRoot())
                    if node.isSelectable()and not node.callDecoration("isNonThumbnailVisibleMesh")]
            if not nodes:
                Logger.log("w", "No valid objects in scene to process")
                return

            for node in nodes:
                node_settings = node.callDecoration("getStack").getTop()
                mesh_name = node.getName() # Filename of mesh with extension

                active_extruder_nr = int(node.callDecoration("getActiveExtruderPosition"))
                per_mesh_extruders[mesh_name] = active_extruder_nr # Active extruder number of each mesh
                
                # Get all feature settings for each mesh object
                for feature_type_key,feature_setting_key in self.__gcode_type_to_setting_key.items():
                    # Use extruder value if no per object setting is defined
                    if node_settings.getInstance(feature_setting_key) is not None:
                        mesh_setting_value = node_settings.getInstance(feature_setting_key).value
                    else:
                        if (mesh_name,feature_type_key) not in per_mesh_settings:
                            per_mesh_settings[(mesh_name,feature_type_key)] = per_extruder_settings[(active_extruder_nr,feature_type_key)]
                        continue

                    # Save the children!
                    for feature in (
                        list(self.__gcode_type_to_setting_key)[4:8] if feature_type_key == "_FACTORS"
                            else ["WALL-OUTER","WALL-INNER"] if feature_type_key == "_WALLS"
                            else ["SUPPORT","SUPPORT-INTERFACE"] if feature_type_key == "_SUPPORTS"
                            else [feature_type_key]):

                        if mesh_setting_value != per_extruder_settings[(active_extruder_nr,feature)]:
                            if mesh_setting_value != per_mesh_settings.get((mesh_name,feature)):
                                apply_factor_per_mesh[(mesh_name,feature)] = True
                                per_mesh_settings[(mesh_name,feature)] = mesh_setting_value

                                if not apply_factor_per_feature.get(active_extruder_nr, False):
                                    apply_factor_per_feature[active_extruder_nr] = True # Start gcode processing loop


            # POST-PROCESS GCODE LOOP
            if any(apply_factor_per_feature.values()):
                current_layer_nr = -1
                current_mesh = None
                feature_type_error = False
                extruder_nr = 0 # Start with first extruder

                for layer_nr, layer in enumerate(gcode_list):
                    lines = layer.split("\n")
                    lines_changed = False
                    for line_nr, line in enumerate(lines):
                        if line.startswith(";LAYER:"):
                            try:
                                current_layer_nr = int(line[7:]) # Get gcode layer number
                            except ValueError:
                                Logger.log("w", "Could not parse layer number: ", line)

                            new_layer = True # Set for error checking

                        if len(active_extruder_list) > 1:
                            # Check for toolhead change gcode command (T0,T1...)
                            if line in ["T" + str(i) for i in active_extruder_list]:
                                try:
                                    extruder_nr = int(line[1:]) # Get active extruder number from gcode
                                except ValueError:
                                    Logger.log("w", "Could not parse extruder number: ", line)

                        if line.startswith(";MESH:") and line[6:] in list(per_mesh_extruders):
                            current_mesh = line[6:] # Set gcode mesh name

                            # Fix for when Cura rudely declares TYPE before MESH in new layer
                            if feature_type_error:
                                last_advance_factor = current_advance_factors[extruder_nr]
                                feature_type = "LAYER_0" if current_layer_nr <= 0 else feature_type

                                current_advance_factors[extruder_nr] = per_mesh_settings[(current_mesh,feature_type)]

                                if current_advance_factors[extruder_nr] != last_advance_factor:
                                    extruder_klip = "extruder" + str(extruder_nr) if extruder_nr > 0 else "extruder"
                                    lines.insert(line_nr, gcode_cmd_pattern % (current_advance_factors[extruder_nr], extruder_klip))
                                    lines_changed = True # Corrected command inserted into gcode
                                feature_type_error = new_layer = False
                                continue

                        if line.startswith(";TYPE:"):
                            feature_type = line[6:] # Get gcode feature type
                            
                            # Check for unknown mesh feature in a new layer 
                            if new_layer and feature_type not in non_mesh_features:
                                feature_type_error = True
                                continue # Error corrected at next MESH line

                            if current_layer_nr <= 0 and feature_type != "SKIRT":
                                feature_type = "LAYER_0"

                            if apply_factor_per_mesh.get((current_mesh,feature_type), False):
                                pressure_advance_factor = per_mesh_settings[(current_mesh,feature_type)]
                            else:
                                pressure_advance_factor = per_extruder_settings[(extruder_nr,feature_type)]

                            # Convert extruder number to str for Klipper
                            extruder_klip = "extruder" + str(extruder_nr) if extruder_nr > 0 else "extruder"
                            new_layer = False # Reset layer check

                            # Check if value for current extruder has changed
                            if pressure_advance_factor != current_advance_factors.get(extruder_nr, None):
                                current_advance_factors[extruder_nr] = pressure_advance_factor
                                lines.insert(line_nr + 1, gcode_cmd_pattern % (pressure_advance_factor, extruder_klip))
                                lines_changed = True # New command inserted into gcode

                    if lines_changed:
                        gcode_list[layer_nr] = "\n".join(lines)
                        dict_changed = True

            gcode_list[0] += ";PRESSUREADVANCEPROCESSED\n"
            gcode_dict[plate_id] = gcode_list

        if dict_changed:
            setattr(scene, "gcode_dict", gcode_dict)

    # Dict order must be preserved!
    __gcode_type_to_setting_key = {
        "_FACTORS": "material_pressure_advance_factor", # [0-3] Non-feature parent settings
        "_WALLS": "material_pressure_advance_factor_wall",
        "_SUPPORTS": "material_pressure_advance_factor_support",
        "LAYER_0": "material_pressure_advance_factor_layer_0",
        "WALL-OUTER": "material_pressure_advance_factor_wall_0", # [4-7] Gcode mesh features
        "WALL-INNER": "material_pressure_advance_factor_wall_x",
        "SKIN": "material_pressure_advance_factor_topbottom",
        "FILL": "material_pressure_advance_factor_infill",
        "SUPPORT": "material_pressure_advance_factor_support_infill", # [8-11] Gcode non-mesh features
        "SUPPORT-INTERFACE": "material_pressure_advance_factor_support_interface",
        "PRIME-TOWER": "material_pressure_advance_factor_prime_tower",
        "SKIRT": "material_pressure_advance_factor_skirt_brim"
    }