# PressureAdvanceSettingPlugin

Unofficial Cura plugin which adds the feature option "Enable Pressure Advance Control". When enabled, a number of feature-specific "Pressure Advance"subsettings are added to the Material category in the Custom print setup of Cura.

*Compatibility tested up to Cura version 5.0.0 (SDK 8.0.0)*

This is a work in progress that has improved significantly since initial release. It is based on the LinearAdvanceSettingPlugin by Cura guru fieldOfView which had compatibility issues with Klipper firmware. Features have since expanded well beyond the scope of that plugin but it is still the backbone that makes this possible.

Designed to work natively on any printer running Klipper with Pressure Advance enabled and should be fully compatible with multiple extruders. Does not currently support changing pressure advance smooth time but if anyone would like to see this option implemented, let me know.

*The plugin inserts the following command into Cura gcode as needed:*
```
SET_PRESSURE_ADVANCE ADVANCE=<val> EXTRUDER=extruder<num>
```

### Current Release Notes (v.1.4.0):
- Now compatibile up to Cura version 5.
- Pressure advance control is now easily enabled or disabled with a single check box.
- Added feature setting support for individual mesh objects.
- Fixed reliability issues when using multiple extruders.
- Support infill and interface settings now grouped under a single support option.
- Minor updates to setting definitions.

#### Multiple Extruders:
To improve reliability, active toolhead numbers are now set by detecting Tool Select commands in gcode (T0, T1, T2...). This is then translated into Klipper's standard naming convention of 'extruder', 'extruder1' and so on. I could not get this technique to fail in testing but other plugins/scripts that modify tool change behavior may not be compatible.

#### Feedback:
Due to all the potential variables it's difficult to fully test so please report any issues you run into. This was a curiosity project that turned into an excuse to better understand Python so I'd appreciate any input from those making use of it.
<br/><br/>
## Installation
*Not currently available in the Cura marketplace. I am working on creating a .curapackage for streamlined installation but this is currently beyond my knowledge. If anyone would like to assist me with it, please let me know.*
<br/><br/>
### If Plugin Already Installed:  
Simply replace the old files with those from the latest release. *Make sure all files in the folder are replaced*. If you experience issues, remove the entire folder and install again.
<br/>
### Install from Source Files:  
Uninstall **LinearAdvanceSettingPlugin**, if already added to Cura.

Download PressureAdvanceSettingPlugin source [.zip file](https://github.com/jjgraphix/PressureAdvanceSettingPlugin/archive/main.zip) from Github.

Open Cura, click *'Help'*, *'Show Configuration Folder'*, then navigate to the "plugins" subfolder and unpack .zip file there. Rename folder to **"PressureAdvanceSettingPlugin"**, removing suffix added by Github (e.g "-master"). 

*Repeat process for subfolder of the same name.*
<br/><br/>
## More Info

For more information on Pressure Advance and how to tune it, see the [Klipper documentation](https://www.klipper3d.org/Pressure_Advance.html).

*Please contact jjfx.contact@gmail.com to report issues or suggest changes.*
