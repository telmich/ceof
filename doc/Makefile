SDOC=thesis.tex
#USDOC=userstories.tex
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

#$(SDOC): $(USDOC) $(USLDOC) $(MDOC)

clean:
	rm -f *.aux *.toc *.log $(USDOC) $(USLDOC) $(MDOC)
