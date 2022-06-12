## PressureAdvanceSettingPlugin

*Compatibility tested up to Cura version 5.0.0 (SDK 8.0.0)* <br><br>

*My new [KlipperSettingsPlugin](https://github.com/jjgraphix/KlipperSettingsPlugin/blob/main/KlipperSettingsPlugin.py)! includes Pressure Advance and a number of other Klipper features. Give it a shot!* 

Unofficial Cura plugin which adds the feature option "Enable Pressure Advance Control". When enabled, a number of feature-specific "Pressure Advance" subsettings are added to the Material category in the Custom print setup of Cura.

Designed to work natively on any printer running Klipper with Pressure Advance enabled. Now fully compatible with multiple extruders and per-object settings. Does not currently support changing pressure advance smooth time but let me know if anyone would like to see it implemented. It is **NOT** compatible with Marlin's Linear Advance. 

This is a work in progress that has improved significantly thanks to user feedback. Due to all of the variables it's difficult to test so I appreciate input from those making use of it. It is based on the LinearAdvanceSettingPlugin by Cura guru fieldOfView which had compatibility issues with Klipper. Features have since expanded beyond the scope of the original plugin but it is still the backbone that makes this possible.

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

<details><summary><strong>Bug Fix (v1.4.1)</strong></summary>
  <p><ul type="disc">
    <li>Disabled per-mesh setting support and "prime tower" option for older Cura versions.</li>
    <li>Fixed error when only extruder used is not number 0.</li>
  </ul></p>
</details>

#### Multiple Extruders
To improve reliability, active tool head numbers are now set by detecting Tool Select commands in gcode (T0, T1, T2...). This is then translated into Klipper's standard naming convention of 'extruder', 'extruder1' and so on. I could not get this technique to fail in testing but custom extruder names or plugins/scripts that modify tool change behavior may not be compatible.<br><br>

### How to Use

The **Enable Pressure Advance** option is added to the *bottom* of the Material category and effectively enables/disables this plugin. When unchecked, no commands will be added to final gcode. This does **NOT** mean pressure advance is disabled. To command Klipper to disable pressure advance, *enable control* and set values to '0'.

*When **Enabled**, most feature-specfic settings can be adjusted:*
  
<details><summary><em>Extruder Settings</em></summary>
  <br><p>Check setting visibility if options are missing.
  
  ![image](https://github.com/jjgraphix/PressureAdvanceSettingPlugin/blob/main/images/PAP-v1.4.0_ExtruderSettings.JPG)
  </p>
</details>

<details><summary><em>Per-Object Settings</em></summary>
  <br><p>Per-object settings available in Cura version 4.7 and newer.
  
  ![image](https://github.com/jjgraphix/PressureAdvanceSettingPlugin/blob/main/images/PAP-v1.4.0_MeshSettings.JPG)
  </p>
</details>

Any defined subsettings will always override the primary factor value. Setting only the primary value in *per-object settings* will override all extruder settings for that mesh but will not affect non-mesh features (first layer, skirt/brim and supports).

If you're wondering who could possibly need to change all of these, you're probably right. Most users should save profiles with the primary value and leave the rest hidden. Advanced users will likely see a benefit from controlling features like walls. Reducing P.A. for infill, skin or support may reduce excessive extruder movement on machines requiring high values, especially at high acceleration. Per-object settings were primarily added for testing to make it easy to quickly print multiple test geometries using different setting combinations. <br><br>

## Installation
**_Not currently available in the Cura marketplace_**. *I am working on creating a .curapackage for streamlined installation but this is currently beyond my knowledge. If anyone would like to assist me with it, please let me know.* <br>

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
