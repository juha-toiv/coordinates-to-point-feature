# Copyright (c) 2022 Juha Toivola
# Licensed under the terms of the MIT License
import arcpy
from datetime import datetime
import re
class CoordinatesToPointException(Exception):
    error_msg = ""
    def __init__(self, error_msg, *args):
        super().__init__(args)
        self.error_msg = error_msg
    def __str__(self):
        return 'Exception: ' + self.error_msg
# This is used to execute code if the file was run but not imported
if __name__ == '__main__':
    # Tool parameter accessed with GetParameter or GetParameterAsText
    y = arcpy.GetParameterAsText(0)
    x = arcpy.GetParameterAsText(1)
    x = x.strip()
    y = y.strip()
    if "°" in x:
        x = x.replace(" ","").replace("°"," ").replace("\'"," ").replace("\""," ")
    if "°" in y:
        y = y.replace(" ","").replace("°"," ").replace("\'"," ").replace("\""," ")
    now = datetime.now()
    now_str = now.strftime("%Y%b%d_%H%M%S")
    tmp_tbl = "tbl_" + now_str
    arcpy.management.CreateTable("memory", tmp_tbl)
    arcpy.management.AddField("memory/" + tmp_tbl, "longitude", "TEXT")
    arcpy.management.AddField("memory/" + tmp_tbl, "latitude", "TEXT")
    with arcpy.da.InsertCursor("memory/" + tmp_tbl, ["longitude", "latitude"]) as cursor:
        cursor.insertRow([x,y])
    output_fc = "pnt_" + x.replace(" ","_").replace(".","") + "_" + y.replace(" ","_").replace(".","") + "_" + now_str
    output_fc_path = "memory/" + output_fc
    try:
        aprx = arcpy.mp.ArcGISProject('CURRENT')
        active_map = aprx.activeMap.name
        aprx_map = aprx.listMaps(active_map)[0]
        map_sr = aprx_map.spatialReference.name
        arcpy.management.ConvertCoordinateNotation("memory/" + tmp_tbl, output_fc_path, "longitude", "latitude", "DMS_2", "DMS_2", spatial_reference=map_sr)
        make_feature_lyr_output = arcpy.MakeFeatureLayer_management(output_fc_path, output_fc)
        mem_lyr = make_feature_lyr_output.getOutput(0)
        aprx_map.addLayer(mem_lyr)
    except Exception as e:
        raise CoordinatesToPointException("Error adding output feature layer to map - no active map; " + str(e))
