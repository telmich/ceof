SDOC=thesis.tex
PARTS=chatsystems.tex comm-protocols.tex conclusions.tex
PARTS+=implementation-prototype.tex references.tex requirements.tex
PARTS+= initial-meeting.tex introduction.tex othersystems.tex protocol.tex
PARTS+= test-prototype.tex thesis.tex

thesis.pdf: $(SDOC) $(PARTS)
	pdflatex $<
	pdflatex $<
	pdflatex $<

praesi: initial-meeting.tex
	pdflatex $<
	pdflatex $<
	pdflatex $<

spellcheck:
	aspell -c ebs_v3 -d en_GB


clean:
	rm -f *.aux *.toc *.log *.pdf $(USDOC) $(USLDOC) $(MDOC)
