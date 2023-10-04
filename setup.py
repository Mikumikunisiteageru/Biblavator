# setup.py

import setuptools

setuptools.setup(
	name = "biblavator",
	version = "0.1.0",
	author = "Yu-Chang YANG",
	author_email = "yang.yc.allium@gmail.com",
	description = "A tool to clean PDFs",
	url = "https://github.com/Mikumikunisiteageru/Biblavator",
	packages = setuptools.find_packages(),
	entry_points = {
		"console_scripts": [
			"biblavator = biblavator:main",
			"biblava = biblavator:main",
		],
	},
	install_requires = ["pikepdf >= 6"],
	classifiers = [
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
)
