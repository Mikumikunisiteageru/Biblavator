# biblavator/__init__.py

import argparse
import base64
import io
import os
import pikepdf
import zipfile

def dewatermark(pdf):
	for page in pdf.pages:
		try:
			del page.Resources.XObject.fzImg0
		except:
			pass

def pdflava(spath, tpath, password=""):
	with pikepdf.open(spath, password=password, 
			allow_overwriting_input=True) as pdf:
		dewatermark(pdf)
		pdf.save(tpath)

def ziplava(spath, tpath):
	with pikepdf.new() as pdf:
		fzip = zipfile.ZipFile(spath)
		for fname in sorted(fzip.namelist()):
			htmlbytes = fzip.read(fname)
			x = htmlbytes.find(b"var content_data =")
			i = htmlbytes.find(b"\"", x)
			j = htmlbytes.find(b"\"", i + 1)
			pdfbytes = base64.b64decode(htmlbytes[i+1:j])
			with pikepdf.open(io.BytesIO(pdfbytes)) as subpdf:
				pdf.pages.extend(subpdf.pages)
		dewatermark(pdf)
		pdf.save(tpath)

def main():
	parser = argparse.ArgumentParser(
		description = "Clean PDF files off watermarks or access restriction.")
	parser.add_argument("filename", nargs="+", metavar="FILENAME", type=str, 
        help = "name of a dirty PDF/ZIP file, maybe with parts of a new name")
	parser.add_argument("-p", "--password", type=str, default="", 
		help = "password protecting the PDF file")
	parser.add_argument("-k", "--keep", action="store_true", 
		help = "keep the original file after cleaning up")
	args = parser.parse_args()
	spath = args.filename[0]
	sdir, sname = os.path.split(spath)
	score, sext = os.path.splitext(sname)
	if sext == "":
		sext = ".pdf"
		spath += ".pdf"
	if len(args.filename) == 1:
		tpath = os.path.join(sdir, score + "_lavatus" + ".pdf")
	else:
		tdir, args.filename[1] = os.path.split(args.filename[1])
		if tdir == "":
			tdir = sdir
		if not args.filename[-1].endswith(".pdf"):
			args.filename[-1] += ".pdf"
		tpath = os.path.join(tdir, ' '.join(args.filename[1:]))
	if sext == ".pdf":
		pdflava(spath, tpath, password=args.password)
	elif sext == ".zip":
		ziplava(spath, tpath)
	else:
		raise ValueError("File format unrecognized!")
	if not args.keep:
		os.remove(spath)
