check: check-python check-javascript

check-python:
	cd python && \
	make lint && \
	make test

check-javascript:
	cd javascript \
	npm run lint && \
	npm run test
