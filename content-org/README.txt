An attempt to generate parsec.ro content using Emacs and Lisp.

/b/ Buletin Cosmic
/y/ Stastistici anuale
/r/ Informații despre rachete
/m/ materiale diverse

A few examples:

** Testing area

#+BEGIN_SRC emacs-lisp :results raw :exports results
  (get-last-10 gcatdata 0 2 3 6 7)
#+END_SRC

** Specific rocket
#+BEGIN_SRC emacs-lisp :results raw :exports results
(get-rocket 3 "Falcon Heavy" 0 2 3 6 7 14)
#+END_SRC

Just a note:
(filter-and-display-specific-columns gcatdata 3 "Falcon Heavy" 0 2 3 6 7)

#+BEGIN_SRC emacs-lisp :results silent :exports results
(counts-for-rocket "Falcon")
#+END_SRC

** Rocket stats

There were a total of src_emacs-lisp[:results value raw]{(nth 0 (counts-for-rocket "Falcon 9"))} Falcon 9 launches. 
From these, src_emacs-lisp[:results value raw]{(nth 1 (counts-for-rocket "Falcon 9"))} had been a failure and 
src_emacs-lisp[:results value raw]{(nth 2 (counts-for-rocket "Falcon 9"))} had been a success.

** Country statistics

#+BEGIN_SRC emacs-lisp :results raw :exports results
(table-launches-year "2023")
#+END_SRC

#+BEGIN_SRC emacs-lisp :results silent
(let ((results (launches-totals-for-year "2023")))
  (setq 2023-total (nth 0 results)
        2023-successes (nth 1 results)
        2023-failures (nth 2 results)))
#+END_SRC

src_emacs-lisp[:results value raw]{2023-successes}