

__init__.py: *.png __init__.py.gotmpl
	# http://github.com/NateScarlet/gotmpl
	ls *.png | jq -nR 'reduce inputs as $$item ([]; . + [$$item]) | { Files: . }' | gotmpl -o $@ __init__.py.gotmpl
	py -3.8 -m black -t py38 $@
