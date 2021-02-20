# Personal Use Only - JJFX 2020
# PressureAdvanceSettingPlugin Based on LinearAdvanceSettingPlugin (Copyright (c) 2020 Aldo Hoeben / fieldOfView)

from . import PressureAdvanceSettingPlugin


def getMetaData():
    return {}

def register(app):
    return {"extension": PressureAdvanceSettingPlugin.PressureAdvanceSettingPlugin()}
