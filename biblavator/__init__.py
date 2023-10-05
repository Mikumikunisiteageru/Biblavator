# biblavator/__init__.py

import argparse
import base64
import io
import os
import pikepdf
import zipfile

class Path:
	def __init__(self, dir, core, ext):
		self.dir = dir
		self.core = core
		self.ext = ext
	def __eq__(self, another):
		return self.dir == another.dir and \
			self.core == another.core and self.ext == another.ext
	def copy(self):
		return Path(self.dir, self.core, self.ext)
	def isa(self, ext):
		return self.ext == ext
	def join(self):
		return os.path.join(self.dir, self.core + self.ext)
	def inheritdir(self, another):
		if self.dir == "":
			self.dir = another.dir
		return self
	def suffixcore(self, suffix):
		self.core += suffix
		return self
	def supplyext(self, ext):
		if self.ext == "":
			self.ext = ext
		return self
	def forceext(self, ext):
		self.ext = ext
		return self

def splitpath(string):
	dir, filename = os.path.split(string)
	core, ext = os.path.splitext(filename)
	return Path(dir, core, ext)

def dewatermark(pdf):
	for page in pdf.pages:
		try:
			del page.Resources.XObject.fzImg0
		except:
			pass

def pdflava(srcpath, dscpath, password=""):
	with pikepdf.open(srcpath.join(), password=password, 
			allow_overwriting_input=True) as pdf:
		dewatermark(pdf)
		pdf.save(dscpath.join())

def ziplava(srcpath, dscpath):
	with pikepdf.new() as pdf:
		with zipfile.ZipFile(srcpath.join()) as fzip:
			for fname in sorted(fzip.namelist()):
				htmlbytes = fzip.read(fname)
				posref = htmlbytes.find(b"var content_data =")
				poslqt = htmlbytes.find(b"\"", posref)
				posrqt = htmlbytes.find(b"\"", poslqt + 1)
				pdfbytes = base64.b64decode(htmlbytes[poslqt+1:posrqt])
				with pikepdf.open(io.BytesIO(pdfbytes)) as subpdf:
					pdf.pages.extend(subpdf.pages)
		dewatermark(pdf)
		pdf.save(dscpath.join())

def removefile(path):
	os.remove(path.join())

def parseargs():
	parser = argparse.ArgumentParser(
		description = "Clean PDF files off watermarks or access restriction.")
	parser.add_argument("filename", nargs="+", metavar="FILENAME", type=str, 
        help = "name of a dirty PDF/ZIP file, maybe with parts of a new name")
	parser.add_argument("-p", "--password", type=str, default="", 
		help = "password protecting the PDF file")
	parser.add_argument("-k", "--keep", action="store_true", 
		help = "keep the original file after cleaning up")
	return parser.parse_args()

def extractpaths(args):
	srcpath = splitpath(args.filename[0]).supplyext(".pdf")
	if len(args.filename) == 1:
		dstpath = srcpath.copy().suffixcore("_lavatus")
	else:
		dstpath = splitpath(' '.join(args.filename[1:])).inheritdir(srcpath)
	dstpath.forceext(".pdf")
	return srcpath, dstpath

def main():
	args = parseargs()
	srcpath, dstpath = extractpaths(args)
	if srcpath.isa(".pdf"):
		pdflava(srcpath, dstpath, password=args.password)
	elif srcpath.isa(".zip"):
		ziplava(srcpath, dstpath)
	else:
		raise ValueError("File format unrecognized!")
	if srcpath != dstpath and not args.keep:
		removefile(srcpath)
