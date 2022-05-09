# Sphinx Documentation svgdigitizer

This documentation is automatically built and uploaded to GitHub Pages.

To build and see the documentation locally, type:

```
cd doc
make html
python -m http.server 8880 -b 127.0.0.1 --directory generated/html &
```

Then open http://localhost:8880/ with your browser.
