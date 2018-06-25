# Author - Adam Nagy
# Description - Tests the currently selected sketch for open ended skecth curves

import adsk.core, adsk.fusion, traceback

# Adds the items of coll2 to coll1
def addCollections(coll1, coll2):
    for item in coll2:
        if not coll1.contains(item):
            coll1.add(item)

# Go through each curve's endpoints and check if they are connected to another 
# curve's endpoint. If not then we'll make a note of it. Once we found two of those
# we return
def getLoopEndPoints(loop):
    # Collect all sketch points that is used just once
    one = adsk.core.ObjectCollection.create() 
    more = adsk.core.ObjectCollection.create()
    for curve in loop:
        # skipping construction entities
        if curve.isConstruction:
            continue        

        # If it has issues, e.g. circles and ellipses don't
        # have sketch end points then we get an expection that 
        # we can ignore since those entities are closed anyway
        try:
            if one.contains(curve.startSketchPoint):
                more.add(curve.startSketchPoint)
                one.removeByItem(curve.startSketchPoint)
            elif not more.contains(curve.startSketchPoint):
                one.add(curve.startSketchPoint)
        
            if one.contains(curve.endSketchPoint):
                more.add(curve.endSketchPoint)
                one.removeByItem(curve.endSketchPoint)
            elif not more.contains(curve.endSketchPoint):
                one.add(curve.endSketchPoint) 
                
        except:
            None 
                
    # look for values '1' because those are 
    # not connecting curves, i.e. they are open
    return one

# By default we'll get the sketch points in context of the 
# component that the sketch resides in. In order to select them in the UI
# we'll need the get their proxy in the root context through the 
# active component occurrence  
def selectInRootContext(pts):
    app = adsk.core.Application.get()
    design = app.activeProduct
    root = design.rootComponent
    comp = design.activeComponent
    ui  = app.userInterface
    actSel = ui.activeSelections
    
    # If the root component is active we have nothing to do
    # than select them
    #if comp == root:
    for pt in pts:
        actSel.add(pt)

    return None

    # Unfortunately component does not have an activeOccurrence property :(
    # that's why we have to do the following workaround:
    # we have to check all instances of the component to see 
    # in whose context we can get the selection to work
    occs = root.allOccurrencesByComponent(comp)
    for occ in occs:
        try:
            # If we get an exception when trying to select
            # the sketch point in context of the given 
            # occurrence then we are using the wrong
            # occurrence so we just move on to the next one
            for pt in pts:
                proxy = pt.createForAssemblyContext(occ)
                actSel.add(proxy)
            
            # We're done
            return None
        except:
            # Nothing to do apart from moving on 
            # to the next possible occurrence
            None
            
    show(ui, "Could not select sketch points")            

def show(ui, msg):
   ui.messageBox(msg, "Sketch Tester") 
 
# Global set of event handlers to keep them referenced for the duration of the command
handlers = []
isSavingSnapshot = True
commandId = 'SketchCheckerCmd'
workspaceToUse = 'FusionSolidEnvironment'
panelToUse = 'InspectPanel'

# Some utility functions
def commandDefinitionById(id):
    app = adsk.core.Application.get()
    ui = app.userInterface
    if not id:
        ui.messageBox('commandDefinition id is not specified')
        return None
    commandDefinitions_ = ui.commandDefinitions
    commandDefinition_ = commandDefinitions_.itemById(id)
    return commandDefinition_

def commandControlByIdForPanel(id):
    global workspaceToUse
    global panelToUse
    app = adsk.core.Application.get()
    ui = app.userInterface
    if not id:
        ui.messageBox('commandControl id is not specified')
        return None
    workspaces_ = ui.workspaces
    modelingWorkspace_ = workspaces_.itemById(workspaceToUse)
    toolbarPanels_ = modelingWorkspace_.toolbarPanels
    toolbarPanel_ = toolbarPanels_.itemById(panelToUse)
    toolbarControls_ = toolbarPanel_.controls
    toolbarControl_ = toolbarControls_.itemById(id)
    return toolbarControl_

def destroyObject(uiObj, objToDelete):
    if uiObj and objToDelete:
        if objToDelete.isValid:
            objToDelete.deleteMe()
        else:
            uiObj.messageBox('objToDelete is not a valid object')   

def addCommandToPanel(panel, commandId, commandName, commandDescription, commandResources, onCommandCreated):
    app = adsk.core.Application.get()
    ui = app.userInterface    
    commandDefinitions_ = ui.commandDefinitions
    
    toolbarControlsPanel_ = panel.controls
    toolbarControlPanel_ = toolbarControlsPanel_.itemById(commandId)
    if not toolbarControlPanel_:
        commandDefinitionPanel_ = commandDefinitions_.itemById(commandId)
        if not commandDefinitionPanel_:
            commandDefinitionPanel_ = commandDefinitions_.addButtonDefinition(commandId, commandName, commandDescription, commandResources)
        
        commandDefinitionPanel_.commandCreated.add(onCommandCreated)
        
        # Keep the handler referenced beyond this function
        handlers.append(onCommandCreated)
        toolbarControlPanel_ = toolbarControlsPanel_.addCommand(commandDefinitionPanel_, '')
        toolbarControlPanel_.isVisible = True  

def getControlAndDefinition(commandId, objects):
    commandControl_ = commandControlByIdForPanel(commandId)
    if commandControl_:
        objects.append(commandControl_)

    commandDefinition_ = commandDefinitionById(commandId)
    if commandDefinition_:
        objects.append(commandDefinition_)

def checkSketch():
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface    

        # Collect sketch entities which are 
        # already found as part of a loop
        processed = adsk.core.ObjectCollection.create() 
        
        # No problems found so far
        problemFound = False
        
        # Sketch that the user is currently editing
        sketch = app.activeEditObject
        if not type(sketch) is adsk.fusion.Sketch:
            show(ui, "A sketch needs to be active to run this command")
            return None
        
        for curve in sketch.sketchCurves:
            # If we did not check this curve yet
            if not processed.contains(curve):
                # Check if other curves are connected to it
                #curves = sketch.findConnectedCurves(curve)
                curves = sketch.sketchCurves
                
                pts = getLoopEndPoints(curves)
                
                # If there are open end points
                if pts:
                    # Highlight the open end sketch points
                    #pts = getLoopEndPoints(curves)  
                    selectInRootContext(pts)
                    
                    # We're done
                    problemFound = True
                    break
                
                # If the loop is closed                           
                else:
                    addCollections(processed, curves)
        
        if not problemFound:            
            show(ui, "No open loops found in sketch")
    except:
        if ui:
            show(ui, 'Failed:\n{}'.format(traceback.format_exc()))

# the main function that is called when our addin is loaded
def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        # command properties
        commandName = 'Check Sketch'
        commandDescription = 'Checks the curves in the currently active sketch for ' \
        'any open ends which do not connect to other curves and highlights those\n'
        commandResources = './resources/command'

        # our command
        class CommandExecuteHandler(adsk.core.CommandEventHandler):
            def __init__(self):
                super().__init__()
            def notify(self, args):
                try:
                    checkSketch()
                except:
                    if ui:
                        ui.messageBox('command executed failed:\n{}'.format(traceback.format_exc()))

        class CommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
            def __init__(self):
                super().__init__() 
            def notify(self, args):
                try:
                    cmd = args.command
                    onExecute = CommandExecuteHandler()
                    cmd.execute.add(onExecute)

                    # keep the handler referenced beyond this function
                    handlers.append(onExecute)
                except:
                    if ui:
                        ui.messageBox('Panel command created failed:\n{}'.format(traceback.format_exc()))                
        
        # add our command on "Inspect" panel in "Modeling" workspace
        global workspaceToUse
        global panelToUse
        workspaces_ = ui.workspaces
        modelingWorkspace_ = workspaces_.itemById(workspaceToUse)
        toolbarPanels_ = modelingWorkspace_.toolbarPanels
        # add the new command under the fifth panel / "Inspect"
        toolbarPanel_ = toolbarPanels_.itemById(panelToUse) 
        addCommandToPanel(toolbarPanel_, commandId, commandName, commandDescription, commandResources, CommandCreatedEventHandler())
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
        objArray = []
        
        getControlAndDefinition(commandId, objArray)
            
        for obj in objArray:
            destroyObject(ui, obj)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
