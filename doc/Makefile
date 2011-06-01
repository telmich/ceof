SDOC=semesterarbeit.tex
USDOC=userstories.tex
USLDOC=userstories-loesungen.tex
MDOC=manpage.tex

praesi: praesi.tex
	pdflatex $<
	pdflatex $<
	pdflatex $<

doc: $(SDOC)
	pdflatex $<
	pdflatex $<
	pdflatex $<

# FIXME: should depend on files, not directory
$(USDOC): user-stories us-to-latex.sh userstories-header.tex
	./us-to-latex.sh > $@

$(USLDOC): user-stories-loesungen us-loesungen-to-latex.sh umsetzung.tex
	./us-loesungen-to-latex.sh > $@

$(MDOC): ../src/doc/uc.1
	echo "\\subsection{Benutzerhandbuch}" > $@
	echo "Das Benutzerhandbuch wurde im Unix-Manpage-Stil erzeugt:" >> $@
	./verbatim-include.sh $^ >> $@

$(SDOC): $(USDOC) $(USLDOC) $(MDOC)

clean:
	rm -f *.aux *.toc *.log $(USDOC) $(USLDOC) $(MDOC)
