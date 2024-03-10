#!/usr/local/bin/FreeCADCmd

import sys

sys.path.append("/usr/lib/freecad-python3/lib/")
sys.path.append("/")
try:
    import FreeCAD
    import importDXF
    import Draft
    import Mesh
except ValueError:
    print("FreeCAD library not found.")
    exit()


def renderdxf(path, name):
    filepath = path + name + ".FCStd"
    doc = FreeCAD.open(filepath)
    bodies = list()
    for obj in doc.Objects:
        # Fix for motor clamp lock, the chamfer one is the final one
        if obj.isDerivedFrom("PartDesign::Body") or obj.isDerivedFrom("Part::Chamfer"):
            bodies.append(obj)
    for body in bodies:
        renderbody(path, name, body, doc, filepath)
        renderstl(path, name, body, doc, filepath)
    FreeCAD.closeDocument(name)


def renderbody(path, name, body, doc, filepath):
    sv0 = Draft.make_shape2dview(body, FreeCAD.Vector(0, -1, 0))
    FreeCAD.getDocument(name).recompute()
    pathOut = filepath.replace(".FCStd", f"_{body.Label}.dxf")
    # Code as shown in FreeCAD console when generating dxf file:
    __objs__ = []
    __objs__.append(FreeCAD.getDocument(name).getObject(sv0.Name))

    if hasattr(importDXF, "exportOptions"):
        options = importDXF.exportOptions(pathOut)
        importDXF.export(__objs__, pathOut, options)
    else:
        d = importDXF.export(__objs__, pathOut)

    del __objs__


def renderstl(path, name, body, doc, filepath):
    # Code as shown in FreeCAD console when generating stl file:
    __objs__ = []
    __objs__.append(body)
    pathOut = filepath.replace(".FCStd", f"_{body.Label}.stl")

    if hasattr(Mesh, "exportOptions"):
        options = Mesh.exportOptions(pathOut)
        Mesh.export(__objs__, pathOut, options)
    else:
        Mesh.export(__objs__, pathOut)

    del __objs__


import os

directory = "/tmp/mirte-frame/"
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    if os.path.isfile(f):
        if f.endswith(".FCStd"):
            name = f.split("/")[-1].split(".")[0]
            print(name)
            renderdxf(directory, name)
