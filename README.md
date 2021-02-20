# PressureAdvanceSettingPlugin

Unofficial Cura plugin which adds the setting "Pressure Advance Factor" and a number of feature-specific subsettings to the Material category in the Custom print setup of Cura.

*Tested compatibility up to Cura v.4.8.0 and Klipper v.0.9.1*

This is a work in progress, remixed from the LinearAdvanceSettingPlugin by fieldOfView who did most of the heavy lifting. This plugin can be made to work with Klipper but can conflict with extruder selection and values aren't specific to Pressure Advance.

Should work natively on any printer running Klipper with Pressure Advance enabled. Multiple extruders should be compatible but I have not had a chance to test. This does not currently allow change to pressure advance smooth time setting.

*The plugin inserts the following command into Cura gcode as needed:*
```
SET_PRESSURE_ADVANCE ADVANCE=<val> EXTRUDER=extruder<num>
```

## Install

Uninstall **LinearAdvanceSettingPlugin**, if already added to Cura.

Download PressureAdvanceSettingPlugin source [.zip file](https://github.com/jjgraphix/PressureAdvanceSettingPlugin/archive/main.zip) from Github.

Open Cura, click *'Help'*, *'Show Configuration Folder'*, then navigate to the "plugins" subfolder and unpack .zip file there. Rename folder to **"PressureAdvanceSettingPlugin"**, removing suffix added by Github (e.g "-master"). *Repeat process for subfolder of the same name.*

## More Info

For more information on Pressure Advance and how to tune it, see the [Klipper documentation](https://www.klipper3d.org/Pressure_Advance.html).


*Please contact jjfx.contact@gmail.com to report issues or suggest changes*
