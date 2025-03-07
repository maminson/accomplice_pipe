import maya.cmds as cmds
import maya.api.OpenMaya as om

release = cmds.about(version=True)
if 'Preview' in release:
    version = 2023
else:
    version = int(cmds.about(version=True))


def trailingNumbers(list, SLMesh, extraAttribs):
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    trailingNumbers = []
    for obj in list:
        if obj[len(obj)-1] in numbers:
            trailingNumbers.append(obj)
    return trailingNumbers


def duplicatedNames(list, SLMesh, extraAttribs):
    duplicatedNames = []
    print(list)
    objNames = [[i, i.split('|')[-1]] for i in list]
    seen = set()
    return [n[0] for n in objNames if n[1] in seen or seen.add(n[1])]
    # for item in list:
    #     if '|' in item:
    #         duplicatedNames.append(item)
    # return duplicatedNames


def namespaces(list, SLMesh, extraAttribs):
    namespaces = []
    for obj in list:
        if ':' in obj:
            namespaces.append(obj)
    return namespaces


def shapeNames(list, SLMesh, extraAttribs):
    shapeNames = []
    for obj in list:
        new = obj.split('|')
        shape = cmds.listRelatives(obj, shapes=True)
        if shape is not None:
            name = new[-1] + "Shape"
            if not shape[0] == name:
                shapeNames.append(obj)
    return shapeNames

# Topology checks


def triangles(list, SLMesh, extraAttribs):
    triangles = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not faceIt.isDone():
            numOfEdges = faceIt.getEdges()
            if len(numOfEdges) == 3:
                faceIndex = faceIt.index()
                componentName = str(objectName) + '.f[' + str(faceIndex) + ']'
                triangles.append(componentName)
            else:
                pass
            if version < 2020:
                faceIt.next(None)
            else:
                faceIt.next()
        selIt.next()
    return triangles


def ngons(list, SLMesh, extraAttribs):
    ngons = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not faceIt.isDone():
            numOfEdges = faceIt.getEdges()
            if len(numOfEdges) > 4:
                faceIndex = faceIt.index()
                componentName = str(objectName) + '.f[' + str(faceIndex) + ']'
                ngons.append(componentName)
            else:
                pass
            if version < 2020:
                faceIt.next(None)
            else:
                faceIt.next()
        selIt.next()
    return ngons


def hardEdges(list, SLMesh, extraAttribs):
    hardEdges = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not edgeIt.isDone():
            if edgeIt.isSmooth == False and edgeIt.onBoundary() == False:
                edgeIndex = edgeIt.index()
                componentName = str(objectName) + '.e[' + str(edgeIndex) + ']'
                hardEdges.append(componentName)
            else:
                pass
            edgeIt.next()
        selIt.next()
    return hardEdges


def lamina(list, SLMesh, extraAttribs):
    selIt = om.MItSelectionList(SLMesh)
    lamina = []
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not faceIt.isDone():
            laminaFaces = faceIt.isLamina()
            if laminaFaces == True:
                faceIndex = faceIt.index()
                componentName = str(objectName) + '.f[' + str(faceIndex) + ']'
                lamina.append(componentName)
            else:
                pass
            if version < 2020:
                faceIt.next(None)
            else:
                faceIt.next()
        selIt.next()
    return lamina


def zeroAreaFaces(list, SLMesh, extraAttribs):
    zeroAreaFaces = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not faceIt.isDone():
            faceArea = faceIt.getArea()
            if faceArea <= 0.00000001:
                faceIndex = faceIt.index()
                componentName = str(objectName) + '.f[' + str(faceIndex) + ']'
                zeroAreaFaces.append(componentName)
            else:
                pass
            if version < 2020:
                faceIt.next(None)
            else:
                faceIt.next()
        selIt.next()
    return zeroAreaFaces


def zeroLengthEdges(list, SLMesh, extraAttribs):
    zeroLengthEdges = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not edgeIt.isDone():
            if edgeIt.length() <= 0.00000001:
                componentName = str(objectName) + \
                    '.f[' + str(edgeIt.index()) + ']'
                zeroLengthEdges.append(componentName)
            edgeIt.next()
        selIt.next()
    return zeroLengthEdges


def selfPenetratingUVs(list, SLMesh, extraAttribs):
    selfPenetratingUVs = []
    for obj in list:
        shape = cmds.listRelatives(obj, shapes=True, fullPath=True)
        convertToFaces = cmds.ls(
            cmds.polyListComponentConversion(shape, tf=True), fl=True)
        overlapping = (cmds.polyUVOverlap(convertToFaces, oc=True))
        if overlapping is not None:
            for obj in overlapping:
                selfPenetratingUVs.append(obj)
    return selfPenetratingUVs


def noneManifoldEdges(list, SLMesh, extraAttribs):
    noneManifoldEdges = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not edgeIt.isDone():
            if edgeIt.numConnectedFaces() > 2:
                edgeIndex = edgeIt.index()
                componentName = str(objectName) + '.e[' + str(edgeIndex) + ']'
                noneManifoldEdges.append(componentName)
            else:
                pass
            edgeIt.next()
        selIt.next()
    return noneManifoldEdges


def openEdges(list, SLMesh, extraAttribs):
    openEdges = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        edgeIt = om.MItMeshEdge(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not edgeIt.isDone():
            if edgeIt.numConnectedFaces() < 2:
                edgeIndex = edgeIt.index()
                componentName = str(objectName) + '.e[' + str(edgeIndex) + ']'
                openEdges.append(componentName)
            else:
                pass
            edgeIt.next()
        selIt.next()
    return openEdges


def poles(list, SLMesh, extraAttribs):
    poles = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        vertexIt = om.MItMeshVertex(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not vertexIt.isDone():
            if vertexIt.numConnectedEdges() > 5:
                vertexIndex = vertexIt.index()
                componentName = str(objectName) + \
                    '.vtx[' + str(vertexIndex) + ']'
                poles.append(componentName)
            else:
                pass
            vertexIt.next()
        selIt.next()
    return poles


def starlike(list, SLMesh, extraAttribs):
    starlike = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        polyIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not polyIt.isDone():
            if polyIt.isStarlike() == False:
                polygonIndex = polyIt.index()
                componentName = str(objectName) + \
                    '.e[' + str(polygonIndex) + ']'
                starlike.append(componentName)
            else:
                pass
            if version < 2020:
                polyIt.next(None)
            else:
                polyIt.next()
        selIt.next()
    return starlike

# UV checks


def missingUVs(list, SLMesh, extraAttribs):
    missingUVs = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not faceIt.isDone():
            if faceIt.hasUVs() == False:
                componentName = str(objectName) + \
                    '.f[' + str(faceIt.index()) + ']'
                missingUVs.append(componentName)
            if version < 2020:
                faceIt.next(None)
            else:
                faceIt.next()
        selIt.next()
    return missingUVs


def uvRange(list, SLMesh, extraAttribs):
    uvRange = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not faceIt.isDone():
            UVs = faceIt.getUVs()
            for index, eachUVs in enumerate(UVs):
                if index == 0:
                    for eachUV in eachUVs:
                        if eachUV < 0 or eachUV > 10:
                            componentName = str(
                                objectName) + '.f[' + str(faceIt.index()) + ']'
                            uvRange.append(componentName)
                            break
                if index == 1:
                    for eachUV in eachUVs:
                        if eachUV < 0:
                            componentName = str(
                                objectName) + '.f[' + str(faceIt.index()) + ']'
                            uvRange.append(componentName)
                            break
            if version < 2020:
                faceIt.next(None)
            else:
                faceIt.next()
        selIt.next()
    return uvRange


def crossBorder(list, SLMesh, extraAttribs):
    crossBorder = []
    selIt = om.MItSelectionList(SLMesh)
    while not selIt.isDone():
        faceIt = om.MItMeshPolygon(selIt.getDagPath())
        objectName = selIt.getDagPath().getPath()
        while not faceIt.isDone():
            U = None
            V = None
            UVs = faceIt.getUVs()
            for index, eachUVs in enumerate(UVs):
                if index == 0:
                    for eachUV in eachUVs:
                        if U == None:
                            U = int(eachUV)
                        if U != int(eachUV):
                            componentName = str(
                                objectName) + '.f[' + str(faceIt.index()) + ']'
                            crossBorder.append(componentName)
                if index == 1:
                    for eachUV in eachUVs:
                        if V == None:
                            V = int(eachUV)
                        if V != int(eachUV):
                            componentName = str(
                                objectName) + '.f[' + str(faceIt.index()) + ']'
                            crossBorder.append(componentName)
            if version < 2020:
                faceIt.next(None)
            else:
                faceIt.next()
        selIt.next()
    return crossBorder

# General checks


def unfrozenTransforms(list, SLMesh, extraAttribs):
    unfrozenTransforms = []
    for obj in list:
        translation = cmds.xform(
            obj, q=True, worldSpace=True, translation=True)
        rotation = cmds.xform(obj, q=True, worldSpace=True, rotation=True)
        scale = cmds.xform(obj, q=True, worldSpace=True, scale=True)
        if not translation == [0.0, 0.0, 0.0] or not rotation == [0.0, 0.0, 0.0] or not scale == [1.0, 1.0, 1.0]:
            unfrozenTransforms.append(obj)
    return unfrozenTransforms


def layers(list, SLMesh, extraAttribs):
    layers = []
    for obj in list:
        layer = cmds.listConnections(obj, type="displayLayer")
        if layer is not None:
            layers.append(obj)
    return layers


def shaders(list, SLMesh, extraAttribs):
    shaders = []
    matname = ""
    try:
        matname = extraAttribs['matname']
    except:
        return shaders
    if not matname:
        return shaders
    
    for obj in list:
        print("obj:", obj)
        shadingGrps = None
        # only works properly if history is cleared
        shape = cmds.listRelatives(obj, shapes=True, fullPath=True)
        if cmds.nodeType(shape) == 'mesh':
            materials = []
            if shape is not None:
                shadingGrps = cmds.listConnections(shape, type='shadingEngine')
                materials = cmds.ls(cmds.listConnections(shadingGrps), materials=True)
                print("materials: ", materials)
            if not materials[0] == matname:
                shaders.append(f"{obj} should have lambert material named {matname}")
    return shaders


def history(list, SLMesh, extraAttribs):
    history = []
    for obj in list:
        shape = cmds.listRelatives(obj, shapes=True, fullPath=True)
        if shape is not None:
            if cmds.nodeType(shape[0]) == 'mesh':
                historySize = len(cmds.listHistory(shape))
                if historySize > 1:
                    history.append(obj)
    return history


def uncenteredPivots(list, SLMesh, extraAttribs):
    uncenteredPivots = []
    for obj in list:
        if cmds.xform(obj, q=1, ws=1, rp=1) != [0, 0, 0]:
            uncenteredPivots.append(obj)
    return uncenteredPivots


def emptyGroups(list, SLMesh, extraAttribs):
    emptyGroups = []
    for obj in list:
        children = cmds.listRelatives(obj, ad=True)
        if children is None:
            emptyGroups.append(obj)
    return emptyGroups


def parentGeometry(list, SLMesh, extraAttribs):
    parentGeometry = []
    shapeNode = False
    for obj in list:
        shapeNode = False
        parents = cmds.listRelatives(obj, p=True, fullPath=True)
        if parents is not None:
            for i in parents:
                parentsChildren = cmds.listRelatives(i, fullPath=True)
                for l in parentsChildren:
                    if cmds.nodeType(l) == 'mesh':
                        shapeNode = True
        if shapeNode == True:
            parentGeometry.append(obj)
    return parentGeometry
