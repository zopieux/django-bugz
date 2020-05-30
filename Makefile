bugz/static/bugz/bundle.js:
	make -C js
	mkdir -p $(dir $@)
	cp -v js/build/static/js/bundle.js $@

.PHONY: bugz/static/bugz/bundle.js
