#!/usr/local/bin/python3
import sys

sys.path.append("/usr/lib/freecad-python3/lib/")
sys.path.append("/")
try:
    import FreeCAD
    import importDXF
    import Draft
    import Part
    import Mesh
except ValueError:
    print("FreeCAD library not found.")
    exit()

def getFilePath(body, name, build_path, type):
    type_path = (build_path / type)
    if not type_path.exists():
       os.mkdir(type_path)
       
    attachment_path = "" 
    if name == "attachments":
        if not (type_path / "attachments").exists():
            os.mkdir((type_path / "attachments"))
        attachment_path = "attachments"

    label_postfix = ""
    if (body.Label != "Body"):
        label_postfix = "_" + body.Label
        label_postfix = label_postfix.replace("_body", "") # fix for layer bodies
    
    return str((type_path / attachment_path / (str(name) + label_postfix + "." + type)).resolve())
    
    
def exportSTL(body, name, build_path):
    pathOut = getFilePath(body, name, build_path, "stl")

    if hasattr(Mesh, "exportOptions"):
        options = Mesh.exportOptions(pathOut)
        Mesh.export([body], pathOut, options)
    else:
        Mesh.export([body], pathOut)

    
def exportSTEP(body, name, build_path):
    pathOut = getFilePath(body, name, build_path, "step")

    if hasattr(Part, "exportOptions"):
        options = Part.exportOptions(pathOut)
        Part.export([body], pathOut, options)
    else:
        Part.export([body], pathOut)


def exportDXF(body, name, build_path):
    pathOut = getFilePath(body, name, build_path, "dxf")
    
    shape2dview = Draft.make_shape2dview(body, FreeCAD.Vector(0, -1, 0))
    FreeCAD.getDocument(name).recompute()

    if hasattr(importDXF, "exportOptions"):
        options = importDXF.exportOptions(pathOut)
        importDXF.export(shape2dview, pathOut, options)
    else:
        importDXF.export(shape2dview, pathOut) 
    
    
def renderFile(freecadFile):
    doc = FreeCAD.open(str(freecadFile))

    # Use variables from params.csv
    App.getDocument('parameters').getObject('Spreadsheet').importFile(str(dir_path / "scripts/params.csv"))
    doc.recompute()

    # TODO: can we mkae this a bit cleaner? Eg by using something like:
    # root_objects = [obj for obj in doc.Objects if not obj.InList]
    bodies = list()
    for obj in doc.Objects:
        # Fix for motor clamp lock, the chamfer one is the final one
        if obj.isDerivedFrom("PartDesign::Body") or obj.isDerivedFrom("Part::Chamfer"):
           bodies.append(obj)

    for body in bodies:
        build_dir = (freecadFile.parent / "../build").resolve()
        if not build_dir.exists():
           os.mkdir(build_dir)
        exportDXF(body, freecadFile.stem, build_dir)
        exportSTL(body, freecadFile.stem, build_dir)
        exportSTEP(body, freecadFile.stem, build_dir)
    FreeCAD.closeDocument(freecadFile.stem)


import os
import shutil
from pathlib import Path

dir_path =  Path(os.path.dirname(os.path.realpath(__file__))).parent.absolute()
freecad_directory = (dir_path / "freecadFiles").resolve()

# clean build directory
if (dir_path / "build").exists():
    shutil.rmtree(dir_path / "build")

# render all freecad files
for filename in os.listdir(freecad_directory):
    f = freecad_directory / filename
    if f.suffix == ".FCStd" and f.stem != "parameters":
        print(f.stem)
        renderFile(f)