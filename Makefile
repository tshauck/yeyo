# (c) Copyright 2018 Trent Hauck
# All Rights Reserved

.PHONY: build
build:
	poetry build

.PHONY: publish
publish:
	poetry publish
