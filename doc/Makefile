SDOC=thesis.tex
PARTS=chatsystems.tex comm-protocols.tex conclusions.tex
PARTS+=implementation-prototype.tex references.tex requirements.tex
PARTS+= introduction.tex othersystems.tex protocol.tex
PARTS+= test-prototype.tex thesis.tex
PARTS+= proto/ui.tex proto/user.tex proto/features.tex proto/noise.tex
PARTS+= proto/onion.tex proto/tp.tex proto/messages.tex
PARTS+= proto/pgp.tex
PARTS+= proto/basic-data.tex proto/simple-data.tex proto/packet-types.tex
PARTS+= nico.bib

thesis.pdf: $(SDOC) $(PARTS)
	pdflatex $<
	bibtex thesis.aux
	pdflatex $<
	pdflatex $<
	#pdflatex EOF.tex
	#pdflatex EOF.tex
	#pdflatex EOF.tex

praesi: initial-meeting.tex
	pdflatex $<
	pdflatex $<
	pdflatex $<

spellcheck:
	aspell -c ebs_v3 -d en_GB


clean:
	rm -f *.aux *.toc *.log *.pdf $(USDOC) $(USLDOC) $(MDOC)
