import threading
import os
import parsing
import ntpath
import model


def parseModules(context):
	print "go with " + context.getBaseDir()
	# clean context
	context.resetModules()
	# scripts
	for folder in context.settings["script_folders"]:
		parseConfig = parsing.ParseConfig()
		parseConfig.folder = context.getBaseDir() + folder
		parseConfig.ext = ".js"
		parseConfig.type = "script"
		parseForModules(context, parseConfig)
	# texts
	for folder in context.settings["text_folders"]:
		parseConfig = parsing.ParseConfig()
		parseConfig.folder = context.getBaseDir() + folder
		parseConfig.ext = ".html"
		parseConfig.type = "text"
		parseForModules(context, parseConfig)

global _collector_thread
_collector_thread = None


def evalutateFile(file, context, parseConfig):
	fileName, fileExtension = os.path.splitext(file)
	if (fileExtension == parseConfig.getExt()):
		package = file.split(parseConfig.folder)[1][1:].split(ntpath.basename(file))[0]
		module = model.Module(ntpath.basename(file), ntpath.dirname(file), parseConfig.getExt(), parseConfig.getType(), package)
		if module.type == "script":
			context.addScriptModule(module)
		elif module.type == "text":
			context.addTextModule(module)


def parseForModules(context, parseConfig):
	global _collector_thread
	if _collector_thread != None:
		_collector_thread.stop()
	_collector_thread = ParsingThread(context, parseConfig)
	_collector_thread.start()


class ParsingThread(threading.Thread):

	def __init__(self, context, parseConfig):
		self.timeout = 30
		self.parseConfig = parseConfig
		self.context = context
		threading.Thread.__init__(self)

	def parseFolder(self, folder, context, parseConfig):
		for file in os.listdir(folder):
			dirfile = os.path.join(folder, file)
			if os.path.isfile(dirfile):
				evalutateFile(dirfile, context, parseConfig)
			elif os.path.isdir(dirfile):
				self.parseFolder(dirfile, context, parseConfig)

	def run(self):
		self.parseFolder(self.parseConfig.folder, self.context, self.parseConfig)

	def stop(self):
		if self.isAlive():
			self._Thread__stop()


