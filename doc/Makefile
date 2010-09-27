all: $(patsubst %.tex,%.pdf, $(wildcard *.tex))

%.pdf: %.eps
	epstopdf $<

%.pdf: %.tex
	pdflatex $<
	while egrep "^LaTeX Warning:.*Rerun to" \
	    `echo $< | sed -e 's/.*\///' -e 's/.tex$$/.log/'`; do \
	  rm -f $(subst $<,.tex,.log); \
	  pdflatex $<; \
	done

%.dvi: %.tex
	latex $<
	while egrep "^LaTeX Warning:.*Rerun to" \
	    `echo $< | sed -e 's/.*\///' -e 's/.tex$$/.log/'`; do \
	  rm -f $(subst $<,.tex,.log); \
	  latex $<; \
	done


%.rtf: %.tex
	latex2rtf $<

%.html: %.tex
	htlatex $<
