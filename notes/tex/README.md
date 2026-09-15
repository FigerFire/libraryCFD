# Solver Analysis Documentation

Build the Chinese solver analysis with XeLaTeX:

```bash
cd documentation/tex
make LATEXMK=/Library/TeX/texbin/latexmk
```

The build writes:

- `documentation/tex/solver_analysis.pdf`
- `output/pdf/solver_analysis.pdf`

Intermediate LaTeX files stay in `documentation/build/`.
