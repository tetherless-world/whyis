import config
def getfullname(name):
	for key in config.namespaces.keys():
		if key in name:
			return name.replace(key, config.namespaces[key]["source"])
