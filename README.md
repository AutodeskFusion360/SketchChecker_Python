# SketchChecker_Python
Checks the currently open sketch for curves which are not part of a closed loop. 
The Add-In's idea comes from this idea station post: [Identify Open Loops in Sketch Environment - Fusion 360](http://forums.autodesk.com/t5/fusion-360-ideastation-request-a/identify-open-loops-in-sketch-environment-fusion-360/idi-p/5492164)

Though Fusion does not require the sketch curves to go from end point to end point in order to form a profile that can be used e.g. for extrusion, it could be considered a good practice to follow that. If you do not, then this utility will highlight all those sketch points that are not connected to other entities (image on the left). If you do follow this practice then a closed loop will show no issues by this tool (image on the right)
![Sketch curves with open ends]
(./resources/readme/SketchChecker2.png)

Sometimes non-connected curves can be difficult to find and this tool can help with that
![Sketch curves with open ends]
(./resources/readme/SketchChecker1.png)

## Usage
The Add-In provides a single commands that is added to the "Model" workspace's "Inspect" panel:
- "Check Sketch": checks the currently open sketch for curves which are not part of a closed loop and will highlight their open endpoints in the UI by adding them to the current selection.
 
## License
Samples are licensed under the terms of the [MIT License](http://opensource.org/licenses/MIT). Please see the [LICENSE](LICENSE) file for full details.

## Written by 
Written by [Adam Nagy](http://adndevblog.typepad.com/manufacturing/adam-nagy.html)  <br />
(Autodesk Developer Network)
