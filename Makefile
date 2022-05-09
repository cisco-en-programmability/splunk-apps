v=$v
default: help
help:
	@echo "Please use \`make <target> <version>' where <target> is one of:"
	@echo "  help     to show this message"
	@echo "  addon    to build the Add on"
	@echo "  app      to build the App"

addon:
	scripts/build.sh -a addon -l -v $(v)

app:
	scripts/build.sh -a app -l -v $(v)
