import qupath.ext.biop.abba.AtlasTools

// 1. Load ABBA Atlas Annotations
setImageType('FLUORESCENCE')
qupath.ext.biop.abba.AtlasTools.loadWarpedAtlasAnnotations(getCurrentImageData(), "Rat - Waxholm Sprague Dawley V4p2", "abbreviation", true, true)
resolveHierarchy()

// 2. Clear selection and run Cell Detection GLOBALLY (super fast)
getCurrentHierarchy().getSelectionModel().clearSelection()
runPlugin('qupath.imagej.detect.cells.WatershedCellDetection', '{"detectionImage":"Red","requestedPixelSizeMicrons":0.5,"backgroundRadiusMicrons":8.0,"backgroundByReconstruction":true,"medianRadiusMicrons":0.0,"sigmaMicrons":1.5,"minAreaMicrons":10.0,"maxAreaMicrons":400.0,"threshold":25.0,"watershedPostProcess":true,"cellExpansionMicrons":5.0,"includeNuclei":true,"smoothBoundaries":true,"makeMeasurements":true}')

// 3. Grab the generated cells and atlas structures
def cells = getCellObjects()
def annotations = getAnnotationObjects()

// 4. ULTRA-FAST GEOMETRIC MAPPING (Preserves Left/Right designation)
for (annot in annotations) {
    def name = annot.getName()
    
    // Skip the giant global atlas background wrapper named "Root"
    if (name == null || name.equalsIgnoreCase("Root") || name.toLowerCase().contains("background")) {
        continue
    }
    
    def roi = annot.getROI()
    if (roi == null) continue
    
    // Find all cells whose center points physically fall inside this specific brain region
    def cellsInside = cells.findAll { cell ->
        def cellRoi = cell.getROI()
        return cellRoi != null && roi.contains(cellRoi.getCentroidX(), cellRoi.getCentroidY())
    }
    
    // THE FIX: Directly copy ABBA's native PathClass (e.g., "Left: CPu") onto the cells
    if (!cellsInside.isEmpty() && annot.getPathClass() != null) {
        cellsInside.each { it.setPathClass(annot.getPathClass()) }
    }
}

// 5. Save to disk
def entry = getProjectEntry()
if (entry != null) {
    entry.saveImageData(getCurrentImageData())
    print "Successfully classified all cells with their split left/right designations!"
}