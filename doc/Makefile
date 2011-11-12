SDOC=thesis.tex
PARTS=conclusions.tex sources.tex
#USLDOC=userstories-loesungen.tex
#MDOC=manpage.tex

thesis.pdf: $(SDOC) $(PARTS)
	pdflatex $<
	pdflatex $<
	pdflatex $<

praesi: praesi.tex
	pdflatex $<
	pdflatex $<
	pdflatex $<

spellcheck:
	aspell -c doc/ebs_v3 -d en_GB


clean:
	rm -f *.aux *.toc *.log $(USDOC) $(USLDOC) $(MDOC)
