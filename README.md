## PressureAdvanceSettingPlugin

*Compatibility tested up to Cura version 5.0.0 (SDK 8.0.0)* <br><br>

Unofficial Cura plugin which adds the feature option "Enable Pressure Advance Control". When enabled, a number of feature-specific "Pressure Advance" subsettings are added to the Material category in the Custom print setup of Cura.

This is a work in progress that has improved significantly since initial release. It is based on the LinearAdvanceSettingPlugin by Cura guru fieldOfView which had compatibility issues with Klipper firmware. Features have since expanded beyond the scope of the original plugin but it is still the backbone that makes this possible.

Designed to work natively on any printer running Klipper with Pressure Advance enabled. It is **NOT** compatible with Marlin's Linear Advance. Now fully compatible with multiple extruders and per-object settings. Does not currently support changing pressure advance smooth time but if anyone would like to see this option implemented, let me know.

*The plugin inserts the following command into Cura gcode as needed:*
```
SET_PRESSURE_ADVANCE ADVANCE=<value> EXTRUDER=extruder<int>
```

### Current Release Notes (v1.4.0)
- Now compatible up to Cura version 5.
- Pressure advance control is now easily enabled or disabled with a single check box.
- Added feature setting support for individual mesh objects.
- Fixed reliability issues when using multiple extruders.
- Support infill and interface settings now grouped under a single support option.
- Minor updates to setting definitions.

<details><summary>Bug Fix - v1.4.1</summary>
  &nbsp;&nbsp;&nbsp;&bull; Disabled per-mesh setting support and "prime tower" option for older Cura versions.<br>
  &nbsp;&nbsp;&nbsp;&bull; Fixed error when only extruder used is not number 0.
</details>

#### Multiple Extruders
To improve reliability, active tool head numbers are now set by detecting Tool Select commands in gcode (T0, T1, T2...). This is then translated into Klipper's standard naming convention of 'extruder', 'extruder1' and so on. I could not get this technique to fail in testing but other plugins/scripts that modify tool change behavior may not be compatible.

#### Feedback
Due to all the potential variables it's difficult to fully test so please report any issues you run into. This was a curiosity project that turned into an excuse to better understand Python so I'd appreciate any input from those making use of it. <br><br>

### How to Use

The **Enable Pressure Advance** option is added to the *bottom* of the Material category and effectively enables/disables this plugin. When unchecked, no commands will be added to final gcode. This does **NOT** mean pressure advance is disabled. To command Klipper to disable pressure advance, *enable control* and set values to '0'. Disabling the control option for individual extruders is not currently supported.

When **Enabled**, most feature-specfic settings can be adjusted:
  
<details><summary>Extruder Settings</summary><br>
  Check setting visibility if options are missing.<br>
  
  ![image](https://github.com/jjgraphix/PressureAdvanceSettingPlugin/blob/main/images/PAP-v1.4.0_ExtruderSettings.JPG)
  
</details>
<details><summary>Per-Object Settings</summary><br>
  Per-object settings only supported for Cura version 4.7 and newer.<br>
  
  ![image](https://github.com/jjgraphix/PressureAdvanceSettingPlugin/blob/main/images/PAP-v1.4.0_MeshSettings.JPG)

</details>

Any defined subsettings will always override the primary factor value. Only setting the primary factor in *per-object settings* will override all extruder settings for that mesh. However, this will not affect non-mesh feature settings (first layer, skirt/brim and supports).

If you're wondering who could possibly need to change all of these, you're probably right. Most users should simply use it for saving profiles with the primary value and leave the rest hidden. Advanced users will likely see a benefit from independently controlling features like walls. For extruders/materials requiring higher values, reducing it during infill, skin or support can help minimize excessive extruder movements, especially at high acceleration. The primary reason I added per-object setting support is for testing. This makes it easy to quickly print multiple test geometries using different values at the same time. <br><br>

## Installation
**_Not currently available in the Cura marketplace_**. *I am working on creating a .curapackage for streamlined installation but this is currently beyond my knowledge. If anyone would like to assist me with it, please let me know.* <br><br>

### If Plugin Already Installed  
Simply replace the old files with those from the latest release. *Make sure all files in the folder are replaced*. Any extra files in your folder are likely temporary and can be left alone or deleted. If you have issues, remove the entire folder and install again as instructed below.

### Install from Source Files  
Uninstall **LinearAdvanceSettingPlugin**, if already added to Cura.

Download PressureAdvanceSettingPlugin source [.zip file](https://github.com/jjgraphix/PressureAdvanceSettingPlugin/archive/main.zip) from Github.

Open Cura, click *'Help'*, *'Show Configuration Folder'*, then navigate to the "plugins" subfolder and unpack .zip file there. Rename folder to **"PressureAdvanceSettingPlugin"**, removing suffix added by Github (e.g "-master"). 

*Repeat process for subfolder of the same name.* <br><br/>

## More Info

For more information on Pressure Advance and how to tune it, see the [Klipper documentation](https://www.klipper3d.org/Pressure_Advance.html).

*For quicker response to questions or feedback, contact me directly at jjfx.contact@gmail.com.*
