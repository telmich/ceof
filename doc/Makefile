SDOC=thesis.tex
PARTS=conclusions.tex sources.tex
#USLDOC=userstories-loesungen.tex
#MDOC=manpage.tex

thesis.pdf: $(SDOC)
	pdflatex $<
	pdflatex $<
	pdflatex $<

praesi: praesi.tex
	pdflatex $<
	pdflatex $<
	pdflatex $<

$(SDOC): $(PARTS)

clean:
	rm -f *.aux *.toc *.log $(USDOC) $(USLDOC) $(MDOC)
