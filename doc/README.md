# Sphinx Documentation svgdigitizer

This documentation is automatically built and uploaded to GitHub Pages.

To build and see the documentation locally, type:

```
cd doc
make html
python -m http.server 8880 -b localhost --directory generated/html &
```

Then open http://localhost:8880/ with your browser.
