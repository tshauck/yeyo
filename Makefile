# (c) Copyright 2018 Trent Hauck
# All Rights Reserved

.PHONY: test
test:
	yeyo test

.PHONY: build
build:
	poetry build

.PHONY: publish
publish:
	poetry publish
