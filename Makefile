.PHONY: test
test:
	tox
	coverage report

.PHONY: clean
clean:
	rm -rf dist/

.PHONY: deploy
deploy: test clean
	python3 setup.py bdist_wheel sdist
	twine upload dist/*