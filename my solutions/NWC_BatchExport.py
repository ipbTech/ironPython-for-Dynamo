import clr
clr.AddReference('RevitServices')
import RevitServices
from RevitServices.Persistence import DocumentManager as DM
from RevitServices.Transactions import TransactionManager as TM

clr.AddReference('RevitAPI')
import Autodesk.Revit.DB
from Autodesk.Revit.DB import NavisworksExportScope, View3D, FilteredElementCollector, Document, ModelPathUtils, OpenOptions, NavisworksExportOptions, NavisworksCoordinates, DetachFromCentralOption, WorksetConfiguration, WorksetConfigurationOption, WorksharingUtils, WorksetTable


uiapp = DM.Instance.CurrentUIApplication
app = uiapp.Application
doc = DM.Instance.CurrentDBDocument

model_list = IN[0]                       
folder_to_export = IN[1]

def worksets_info(model_path):
	worksets_info = WorksharingUtils.GetUserWorksetInfo(model_path)
	ws_id = []
	ws_names = []
	for ws in worksets_info:
		if "связ" not in ws.Name.ToLower():
			ws_id.append(ws.Id)
			ws_names.append(ws.Name)
	return ws_id
	
def open_options_file(ws_id):
	#ws_open_config = WorksetConfiguration().Open(ws_id)
	ws_open_config = WorksetConfiguration(WorksetConfigurationOption.CloseAllWorksets)
	ws_open_config.Open(ws_id)
	open_options = OpenOptions()
	open_options.DetachFromCentralOption = DetachFromCentralOption.DetachAndPreserveWorksets
	open_options.AllowOpeningLocalByWrongUser = True
	open_options.SetOpenWorksetsConfiguration(ws_open_config)	
	return open_options

def nwc_export_options(nwc_view):
	nwc_export_options = NavisworksExportOptions()
	nwc_export_options.ExportScope = NavisworksExportScope.View
	nwc_export_options.ViewId = nwc_view[0].Id		
	nwc_export_options.ExportRoomGeometry = False
	nwc_export_options.ExportRoomAsAttribute = False		
	nwc_export_options.Coordinates = NavisworksCoordinates.Shared
	nwc_export_options.ExportLinks = False
	nwc_export_options.ExportParts = True
	nwc_export_options.ExportElementIds = True
	nwc_export_options.DivideFileIntoLevels = True
	nwc_export_options.ExportUrls = False
	nwc_export_options.FindMissingMaterials = False
	nwc_export_options.ConvertElementProperties = False
	return nwc_export_options


for model in model_list:

	model_path = ModelPathUtils.ConvertUserVisiblePathToModelPath(model)	
	ws = worksets_info(model_path)
	op_opt = open_options_file(ws)
	doc = app.OpenDocumentFile(model_path,op_opt)
	
	views3d = [v for v in FilteredElementCollector(doc).OfClass(View3D) if not v.IsTemplate]
	nwc_view = [view for view in views3d if "navisworks" in view.Name.ToLower()]
	
	get_nwc = nwc_export_options(nwc_view)
	
	doc.Export(folder_to_export, doc.Title, get_nwc)
	doc.Close(False)
	

OUT = 'success'
