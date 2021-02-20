# PressureAdvanceSettingPlugin v1.1.0
# Personal Use Only - JJFX 2020
# PressureAdvanceSettingPlugin based on LinearAdvanceSettingPlugin (Copyright (c) 2020 Aldo Hoeben / fieldOfView)
#
# ** Compatible ONLY with Klipper Firmware Running Pressure Advance **

from UM.Extension import Extension
from cura.CuraApplication import CuraApplication
from UM.Logger import Logger
from UM.Version import Version
from UM.Settings.SettingDefinition import SettingDefinition
from UM.Settings.DefinitionContainer import DefinitionContainer
from UM.Settings.ContainerRegistry import ContainerRegistry

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

        # make sure this setting is expanded so its children show up  in setting views
        if setting_definition.parent.key in self._expanded_categories:
            self._expanded_categories.append(setting_definition.key)

        for child in children:
            container._definition_cache[child.key] = child
            self._updateAddedChildren(container, child)

    def _filterGcode(self, output_device: "OutputDevice") -> None:
        scene = self._application.getController().getScene()

        global_container_stack = self._application.getGlobalContainerStack()
        used_extruder_stacks = self._application.getExtruderManager().getUsedExtruderStacks()
        if not global_container_stack or not used_extruder_stacks:
            return

        gcode_dict = getattr(scene, "gcode_dict", {})
        if not gcode_dict: # this also checks for an empty dict
            Logger.log("w", "Scene has no gcode to process")
            return

        gcode_flavor = global_container_stack.getProperty("machine_gcode_flavor", "value")

        # Pressure Advance Command Insert (Compatible with multiple extruders)
        # Klipper Firmware Only - Pattern Applied to Any Cura Gcode Flavor
        gcode_command_pattern = "SET_PRESSURE_ADVANCE ADVANCE=%f EXTRUDER=%s"
        gcode_command_pattern += " ;PressureAdvanceSettingPlugin"

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

            current_pressure_advance_factors = {}  # type: Dict[int, float]
            apply_factor_per_feature = {}  # type: Dict[int, bool]

            for extruder_stack in used_extruder_stacks:
                extruder_nr = int(extruder_stack.getProperty("extruder_nr", "value"))
                pressure_advance_factor = extruder_stack.getProperty(setting_key, "value")
                # Convert extruder value to str for Klipper compatibility
                if extruder_nr == 0:
                    extruder_klip = "extruder"
                else:
                    extruder_klip = "extruder" + str(extruder_nr)

                gcode_list[1] = gcode_list[1] + gcode_command_pattern % (pressure_advance_factor, extruder_klip) + "\n"

                dict_changed = True

                current_pressure_advance_factors[extruder_nr] = pressure_advance_factor

                for feature_setting_key in self.__gcode_type_to_setting_key.values():
                    if extruder_stack.getProperty(feature_setting_key, "value") != pressure_advance_factor:
                        apply_factor_per_feature[extruder_nr] = True
                        break

            if any(apply_factor_per_feature.values()):
                current_layer_nr = -1
                for layer_nr, layer in enumerate(gcode_list):
                    lines = layer.split("\n")
                    lines_changed = False
                    for line_nr, line in enumerate(lines):

                        if line.startswith(";LAYER:"):
                            try:
                                current_layer_nr = int(line[7:])
                            except ValueError:
                                Logger.log("w", "Could not parse layer number: ", line)
                        if line.startswith(";TYPE:"):
                            # Changed line type
                            feature_type = line[6:] # remove ";TYPE:"
                            try:
                                feature_setting_key = self.__gcode_type_to_setting_key[feature_type]
                            except KeyError:
                                Logger.log("w", "Unknown feature type in gcode: ", feature_type)
                                feature_setting_key = ""

                            if current_layer_nr <= 0 and feature_type != "SKIRT":
                                feature_setting_key = "material_pressure_advance_factor_layer_0"

                            for extruder_stack in used_extruder_stacks:
                                extruder_nr = extruder_stack.getProperty("extruder_nr", "value")
                                # Convert extruder value to str for Klipper
                                if extruder_nr == 0:
                                    extruder_klip = "extruder"
                                else:
                                    extruder_klip = "extruder" + str(extruder_nr)

                                if not apply_factor_per_feature[extruder_nr]:
                                    continue

                                if feature_setting_key:
                                    pressure_advance_factor = extruder_stack.getProperty(feature_setting_key, "value")
                                else: # unknown feature type
                                    pressure_advance_factor = 0 # Pressure Advance Disabled

                                if pressure_advance_factor != current_pressure_advance_factors.get(extruder_nr, None):
                                    current_pressure_advance_factors[extruder_nr] = pressure_advance_factor

                                    lines.insert(line_nr + 1, gcode_command_pattern % (pressure_advance_factor, extruder_klip))

                                    lines_changed = True

                    if lines_changed:
                        gcode_list[layer_nr] = "\n".join(lines)
                        dict_changed = True

            gcode_list[0] += ";PRESSUREADVANCEPROCESSED\n"
            gcode_dict[plate_id] = gcode_list

        if dict_changed:
            setattr(scene, "gcode_dict", gcode_dict)

    __gcode_type_to_setting_key = {
        "WALL-OUTER": "material_pressure_advance_factor_wall_0",
        "WALL-INNER": "material_pressure_advance_factor_wall_x",
        "SKIN": "material_pressure_advance_factor_topbottom",
        "SUPPORT": "material_pressure_advance_factor_support",
        "SUPPORT-INTERFACE": "material_pressure_advance_factor_support_interface",
        "SKIRT": "material_pressure_advance_factor_skirt_brim",
        "FILL": "material_pressure_advance_factor_infill",
        "PRIME-TOWER": "material_pressure_advance_factor_prime_tower"
    }
