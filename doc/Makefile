SDOC=thesis.tex
PARTS=chatsystems.tex comm-protocols.tex conclusions.tex
PARTS+=implementation.tex references.tex requirements.tex
PARTS+= introduction.tex othersystems.tex protocol.tex
PARTS+= proto/ui.tex proto/user.tex proto/features.tex proto/noise.tex
PARTS+= proto/onion.tex proto/tp.tex proto/messages.tex
PARTS+= proto/pgp.tex
PARTS+= proto/basic-data.tex proto/simple-data.tex proto/packet-types.tex
PARTS+= nico.bib

all: zhaw-kurzfassung.pdf thesis.pdf

zhaw-kurzfassung.pdf: zhaw-kurzfassung.tex
	pdflatex $<
	pdflatex $<
	pdflatex $<

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
	rm -f *.aux *.toc *.log *.pdf *.idx $(USDOC) $(USLDOC) $(MDOC)
	rm -f proto/*.aux proto/*.toc proto/*.log proto/*.pdf

tar: thesis.pdf
	cd /home/users/nico/.bachelorarbeit && tar cfvJ thesis.tar.xz doc src/ README

iso: thesis.pdf
	cd /home/users/nico/.bachelorarbeit && mkisofs -graft-points -J -R -file-mode 0755 -dir-mode 0755 doc/=doc src/=src README > thesis.iso
