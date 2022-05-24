# For Personal Use - Copyright (c) 2022 JJFX Design
# Project based on LinearAdvanceSettingPlugin (Copyright (c) 2020 Aldo Hoeben / fieldOfView)
# The PressureAdvanceSettingPlugin is released under the terms of the AGPLv3 or higher.

from . import PressureAdvanceSettingPlugin


def getMetaData():
    return {}

def register(app):
    return {"extension": PressureAdvanceSettingPlugin.PressureAdvanceSettingPlugin()}
