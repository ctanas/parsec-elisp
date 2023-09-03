# parsec.ro

Files used for [parsec.ro](https://www.parsec.ro) website.

Raw data are parsed from Jonathan McDowell's [GCAT](https://planet4589.org/space/gcat/) using a Python script, into a CSV file, read and processed by Emacs-Lisp in Emacs' org-mode, then exported to Markdown files using [ox-hugo](https://ox-hugo.scripter.co) and finally [Hugo](https://gohugo.io/) to generate the static HTML pages. A slighty modified version of [hugo-alageek-theme](https://github.com/gkmngrgn/hugo-alageek-theme) is used for coating.
