import qupath.lib.gui.tools.MeasurementExporter
import qupath.lib.objects.PathAnnotationObject

// Get the current QuPath project
def project = getProject()
if (project == null) {
    print "No project open!"
    return
}

// Create an 'export' folder inside your QuPath project directory
def exportDir = buildFilePath(PROJECT_BASE_DIR, "export")
mkdirs(exportDir)
// Updated file name and extension to .csv
def exportPath = buildFilePath(exportDir, "All_Annotations_Measurements.csv") 
def outputFile = new File(exportPath)

// Export ALL annotations from ALL images in the project into one CSV file
new MeasurementExporter()
    .imageList(project.getImageList())
    .separator(",") // Changed from tab ("\t") to comma (",")
    .exportType(PathAnnotationObject.class) // Changed export type to Annotations
    .exportMeasurements(outputFile)

print "Success! Your CSV file has been generated here: " + exportPath