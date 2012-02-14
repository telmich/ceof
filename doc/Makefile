SDOC=thesis.tex
PARTS=conclusions.tex sources.tex
#USLDOC=userstories-loesungen.tex
#MDOC=manpage.tex

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
	rm -f *.aux *.toc *.log $(USDOC) $(USLDOC) $(MDOC)
