all: report.pdf

report.pdf: report.tex bibliography.bib pictures/MainMenu.png pictures/TicTacToe_gameplay.png pictures/Othello_gameplay.png pictures/Connect4_gameplay.png
	pdflatex report
	bibtex report
	pdflatex report
	pdflatex report

.PHONY: clean

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc *.lof *.lot report.pdf
