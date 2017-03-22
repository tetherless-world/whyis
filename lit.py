import config
def getfullname(name):
	for key in config.namespaces.keys():
		if key in name:
			i = name.find(key)
			new_url = name[i:]
			return new_url.replace(key, config.namespaces[key]["source"])
