;; data.csv structure:
; 00 - Launch_Tag
; 01 - Launch_JD
; 02 - Launch_Date
; 03 - LV_Type
; 04 - Variant
; 05 - Flight_ID
; 06 - Mission
; 07 - Platform
; 08 - Launch_Site
; 09 - Agency
; 10 - Launch_Code
; 11 - Category
; 12 - Country
; 13 - Outcome

(defvar gcatdata "data.csv")

(setq csv-separators '(";"))

(defvar country-code-mappings
  '(("CN" . "China")
    ("US" . "Statele Unite")
    ("RU" . "Rusia")
    ("EU" . "Europa")
    ("JP" . "Japonia")
    ("IN" . "India")
    ("IR" . "Iran")
    ("IL" . "Israel")
    ("KP" . "Coreea de Nord")
    ("KR" . "Coreea de Sud")
    ("BR" . "Brazilia")
    ;; Add more mappings as needed
    )
  "Alist mapping country codes to their respective full names.")

;; Helper function
(defun simple-csv-parse-line (&optional separator)
  "Simple CSV parser that splits the line at commas.
It doesn't handle quoted fields with commas inside them."
  (split-string (buffer-substring-no-properties (line-beginning-position) 
                                               (line-end-position))
                (or separator ";")))

;; Get a table with the last 10 launches
(defun get-last-10 (filename &rest columns)
  "Load a CSV from FILENAME in another buffer, then insert the last 10 lines, and specific COLUMNS as an org-table with renamed headers."
  (let ((csv-buffer (find-file-noselect filename))
        data headers selected-data count
        ;; Here's the mapping from original headers to new headers
        (header-rename-alist '(("Launch_Tag" . "ID")
                               ("Launch_Date" . "Dată (UTC)")
                               ("LV_Type" . "Lansator")
                               ("Mission" . "Misiune")
                               ("Flight" . "Satelit")
                               ("Mission" . "Misiune")
                               ("Flight_ID" . "Serie")
                               ("Country" . "TR")
                               ("Outcome" . "R")
                               ("Launch_Site" . "Centru")
                               ;; Add more mappings as needed
                               )))
    (with-current-buffer csv-buffer
      (csv-mode)  ; Make sure csv-mode is active for the buffer
      ;; Extract headers
      (goto-char (point-min))
      (setq headers (mapcar (lambda (col) 
                              (let ((original (nth col (simple-csv-parse-line))))
                                (or (cdr (assoc original header-rename-alist)) 
                                    original)))
                            columns))
      ;; Collect last 10 lines
      (goto-char (point-max))
      (setq count 0)
      (while (and (> (point) (point-min)) (< count 10))
        (let ((parsed-line (simple-csv-parse-line)))
          (when (and parsed-line (> (length parsed-line) 0) 
                     (not (string-empty-p (car parsed-line))))  ; Check if parsed line is not empty and first column is not empty
            (push parsed-line data)
            (setq count (1+ count))))
        (forward-line -1))
      ;; Extract specific columns from the data
      (setq selected-data
            (mapcar (lambda (row)
                      (mapcar (lambda (col) (nth col row)) columns))
                    (nreverse data)))
      ;; Kill the csv buffer since we are done with it
      (kill-buffer csv-buffer))
    ;; Return data formatted as an org table with headers
    (concat "| " (mapconcat 'identity headers " | ") " |\n|-\n"
            (mapconcat (lambda (row)
                         (concat "| " (mapconcat 'identity row " | ") " |"))
                       selected-data "\n")
            "\n|-\n")))
;; Example: 
; (get-last-10 gcatdata 0 2 3 6 7)

;; Get a table with a specific rocket launches
(defun get-rocket (column-index search-string &rest display-columns)
  "Filter the CSV from FILENAME, keeping only rows where COLUMN-INDEX contains SEARCH-STRING. 
Returns the filtered data from DISPLAY-COLUMNS as an org table."
  (let ((csv-buffer (find-file-noselect gcatdata))
        all-data headers filtered-data selected-data)
    (with-current-buffer csv-buffer
      (csv-mode)  ; Make sure csv-mode is active for the buffer
      ;; Extract headers
      (goto-char (point-min))
      (setq headers (mapcar (lambda (col) (nth col (simple-csv-parse-line))) display-columns))
      ;; Collect all data
      (while (not (eobp))
        (push (simple-csv-parse-line) all-data)
        (forward-line 1))
      ;; Filter data
      (setq filtered-data
            (cl-remove-if-not 
             (lambda (row) 
               (string-match-p (regexp-quote search-string) 
                               (nth column-index row)))
             all-data))
      ;; Extract specific columns from the filtered data
      (setq selected-data
            (mapcar (lambda (row)
                      (mapcar (lambda (col) (nth col row)) display-columns))
                    filtered-data))
      ;; Kill the csv buffer since we are done with it
      (kill-buffer csv-buffer))
    ;; Return data formatted as an org table with headers
    (concat "| " (mapconcat 'identity headers " | ") " |\n|-\n"
            (mapconcat (lambda (row)
                         (concat "| " (mapconcat 'identity row " | ") " |"))
                       selected-data "\n")
            "\n|-\n")))
;; Example: 
;; (get-rocket 3 "Astra" 0 2 3 6 7)

(defun counts-for-rocket (search-string)
  "Return the total, 'F', and 'S' counts for a specific rocket based on the SEARCH-STRING."
  (let ((csv-buffer (find-file-noselect gcatdata))
        all-data total F-count S-count)
    (with-current-buffer csv-buffer
      (csv-mode)  ; Make sure csv-mode is active for the buffer
      ;; Collect all data
      (while (not (eobp))
        (push (simple-csv-parse-line) all-data)
        (forward-line 1))
      ;; Initialize counts
      (setq total 0 F-count 0 S-count 0)
      (dolist (row all-data)
        (when (string-match-p (regexp-quote search-string) (nth 3 row))  ; Assuming column index 3 for rocket names
          (setq total (1+ total))
          (cond
           ((string= "F" (nth 13 row)) (setq F-count (1+ F-count)))
           ((string= "S" (nth 13 row)) (setq S-count (1+ S-count))))))
      ;; Kill the csv buffer since we are done with it
      (kill-buffer csv-buffer))
    (list total F-count S-count)))
;; Example:
; #+BEGIN_SRC emacs-lisp :results silent
; (rocket-stats-update 3 "Falcon")
; #+END_SRC
; There were a total of src_emacs-lisp[:results value raw]{(nth 0 (counts-for-rocket "Falcon 9"))} Falcon 9 launches. 
; From these, src_emacs-lisp[:results value raw]{(nth 1 (counts-for-rocket "Falcon 9"))} had an "F" value and 
; src_emacs-lisp[:results value raw]{(nth 2 (counts-for-rocket "Falcon 9"))} had an "S" value.

(defun gregorian-to-julian (year month day)
  "Convert a Gregorian date to Julian Date."
  (let* ((a (floor (/ (- month 14) 12)))
         (y (+ year 4800 a))
         (m (+ month (* 12 a) -3)))
    (+ day
       (floor (/ (+ (* 153 m) 2) 5))
       (* 365 y)
       (floor (/ y 4))
       (- (floor (/ y 100)))
       (floor (/ y 400))
       -32045)))

(defun table-launches-year (year)
  "Return an org-mode table summarizing the total, successful, and failed launches for each country in a given year, in descending order of launches."
  (let ((csv-buffer (find-file-noselect gcatdata))
        country-stats)
    (with-current-buffer csv-buffer
      ;; Collect all data
      (goto-char (point-min))
      (while (not (eobp))
        (let* ((line (buffer-substring-no-properties (line-beginning-position) (line-end-position)))
               (n (length line))
               (country-code (concat (substring line (- n 4) (- n 3)) (substring line (- n 3) (- n 2))))
               (country (or (cdr (assoc country-code country-code-mappings)) country-code)) ; If no mapping is found, use the code
               (status (substring line (- n 1) n))  ; Get the last character for launch status
               (launch-date (substring line 0 4)))
          ;; Check if the launch date matches the specified year
          (when (string= launch-date year)
            (unless (assoc country country-stats)
              (push (list country 0 0 0) country-stats))  ; Initialize stats for the country if not already present
            (let ((stats (assoc country country-stats)))
              (cl-incf (nth 1 stats))  ; Increment total launches
              (cond ((string= status "S") (cl-incf (nth 2 stats)))  ; Increment successful launches
                    ((string= status "F") (cl-incf (nth 3 stats))))))  ; Increment failed launches
          (forward-line 1)))
      (kill-buffer csv-buffer))
    ;; Sort country-stats in descending order based on total launches
    (setq country-stats (sort country-stats (lambda (a b) (> (cadr a) (cadr b)))))
    ;; Format as an org-mode table
    (let ((headers '("Țară" "Tentative" "Reușite" "Eșecuri")))
      (concat "| " (mapconcat 'identity headers " | ") " |\n"
              "|-" (mapconcat (lambda (_) "+-") headers "-") "-|\n"
              (mapconcat (lambda (row)
                           (concat "| " (mapconcat (lambda (item) (format "%s" item)) row " | ") " |"))
                         country-stats "\n")
              "\n"))))

(defun launches-totals-for-year (year)
  "Return the total, successful, and failed number of launches for a specified year."
  (let ((csv-buffer (find-file-noselect gcatdata))
        (total-launches 0)
        (total-successes 0)
        (total-failures 0))
    (with-current-buffer csv-buffer
      (csv-mode)  ; Make sure csv-mode is active for the buffer
      (goto-char (point-min))
      (while (not (eobp))
        (let* ((row (simple-csv-parse-line))
               (launch-date (nth 2 row))
               (status (nth 13 row)))
          ;; If the launch-date starts with the specified year, process the row
          (when (and (stringp launch-date) (string-match (format "^%s-" year) launch-date))
            (setq total-launches (1+ total-launches))
            (cond 
             ((string= status "S") (setq total-successes (1+ total-successes)))
             ((string= status "F") (setq total-failures (1+ total-failures))))))
        (forward-line 1))
      (kill-buffer csv-buffer))
    (list total-launches total-successes total-failures)))
;; Usage
;(let ((results (launches-totals-for-year "2023")))
;  (setq 2023-total (nth 0 results)
;        2023-successes (nth 1 results)
;        2023-failures (nth 2 results)))

(defun launches-totals ()
  "Return the total, successful, and failed number of launches for all years."
  (let ((csv-buffer (find-file-noselect gcatdata))
        (total-launches 0)
        (total-successes 0)
        (total-failures 0))
    (with-current-buffer csv-buffer
      (csv-mode)  ; Make sure csv-mode is active for the buffer
      (goto-char (point-min))
      (while (not (eobp))
        (let* ((row (simple-csv-parse-line))
               (status (nth 13 row)))
          (cond 
           ((string= status "S") 
            (setq total-successes (1+ total-successes))
            (setq total-launches (1+ total-launches)))
           ((string= status "F") 
            (setq total-failures (1+ total-failures))
            (setq total-launches (1+ total-launches))))
          (forward-line 1)))
      (kill-buffer csv-buffer))
    (list total-launches total-successes total-failures)))
;; Usage
;(let ((results (launches-totals)))
;  (setq grand-total (nth 0 results)
;        grand-successes (nth 1 results)
;        grand-failures (nth 2 results)))


(defun table-launches-grand-total ()
  "Return an org-mode table summarizing the total, successful, and failed launches for each country across all years."
  (let ((csv-buffer (find-file-noselect gcatdata))
        country-stats)
    (with-current-buffer csv-buffer
      ;; Collect all data
      (goto-char (point-min))
      (while (not (eobp))
        (let* ((line (buffer-substring-no-properties (line-beginning-position) (line-end-position)))
               (country (substring line (- (length line) 4) (- (length line) 2)))
               (status (if (string= (substring line -1) "S") "S" (if (string= (substring line -1) "F") "F" nil)))
               (stats (assoc country country-stats)))
          (if stats
              (progn
                ;; Increment total launches
                (cl-incf (nth 1 stats))
                ;; Increment successful or failed launches based on status
                (when status
                  (cond 
                   ((string= status "S") (cl-incf (nth 2 stats)))
                   ((string= status "F") (cl-incf (nth 3 stats))))))
            ;; If country is not yet in country-stats, initialize its stats
            (when (and (= (length country) 2) status)
              (push (list country 1 (if (string= status "S") 1 0) (if (string= status "F") 1 0)) country-stats))))
        (forward-line 1))
      (kill-buffer csv-buffer))
    ;; Sort country-stats in descending order based on total launches
    (setq country-stats (sort country-stats (lambda (a b) (> (nth 1 a) (nth 1 b)))))
    ;; Format as an org-mode table
    (let ((headers '("Country" "Total" "Success" "Failed")))
      (concat "| " (mapconcat 'identity headers " | ") " |\n"
              "|-" (mapconcat (lambda (_) "+-") headers "-") "-|\n"
              (mapconcat (lambda (row)
                           (concat "| " (mapconcat (lambda (item) (format "%s" item)) row " | ") " |"))
                         country-stats "\n")
              "\n"))))

(defun table-launches-by-year-and-country ()
  "Return an org-mode table summarizing the total launches for each country across all years, organized by year."
  (let ((csv-buffer (find-file-noselect gcatdata))
        data year-country-stats all-years all-countries)
    (with-current-buffer csv-buffer
      ;; Collect all data
      (goto-char (point-min))
      (while (not (eobp))
        (let* ((line (buffer-substring-no-properties (line-beginning-position) (line-end-position)))
               (year (substring (nth 2 (split-string line ";")) 0 4))
               (country (substring line (- (length line) 4) (- (length line) 2)))
               (key (concat year "-" country))
               (count (or (assoc key year-country-stats) (list key 0))))

          (when (and (= (length country) 2) (string-match-p "^[0-9]\\{4\\}$" year))
            (unless (member year all-years)
              (push year all-years))
            (unless (member country all-countries)
              (push country all-countries))

            ;; Increment total launches
            (cl-incf (cadr count))
            (unless (assoc key year-country-stats)
              (push count year-country-stats))))
        (forward-line 1))
      (kill-buffer csv-buffer))

    ;; Sort years in descending order and countries in ascending order
    (setq all-years (sort all-years (lambda (a b) (string> a b))))
    (setq all-countries (sort all-countries 'string<))

    ;; Format as an org-mode table
    (let ((headers (append (list "Year") all-countries (list "Total"))))
      (concat "| " (mapconcat 'identity headers " | ") " |\n"
              "|-" (mapconcat (lambda (_) "+-") headers "-") "-|\n"
              (mapconcat 
               (lambda (year)
                 (let (row)
                   (push year row)
                   (let ((year-total 0)) ; Initialize year-total
                     (dolist (country all-countries)
                       (let* ((key (concat year "-" country))
                              (count (cadr (or (assoc key year-country-stats) (list key 0)))))
                         (setq year-total (+ year-total count))
                         (push (number-to-string count) row)))
                     (push (number-to-string year-total) row)) ; Add yearly total
                   (concat "| " (mapconcat 'identity (reverse row) " | ") " |")))
               all-years "\n")
              "\n"))))

(defun list-launches-for-year (year &rest args)
  "Return an org-mode table listing all launches for the specified YEAR.
The table will only include the COLUMNS specified by their indices.
Optionally, you can provide custom HEADERS for those columns."
  (let ((csv-buffer (find-file-noselect gcatdata))
        launches
        columns
        custom-headers)
    ;; Check if last argument is a list (for custom headers)
    (if (listp (car (last args)))
        (progn
          (setq custom-headers (car (last args)))
          (setq columns (butlast args))
          (unless (= (length columns) (length custom-headers))
            (error "Number of columns does not match number of custom headers.")))
      (setq columns args))

    (with-current-buffer csv-buffer
      ;; Collect data for the specified year
      (goto-char (point-min))
      (while (not (eobp))
        (let* ((line (buffer-substring-no-properties (line-beginning-position) (line-end-position)))
               (row (split-string line ";"))
               (launch-year (substring (nth 2 row) 0 4)))
          (when (string= launch-year year)
            (let ((selected-data (mapcar (lambda (idx) (nth idx row)) columns)))
              (push selected-data launches))))
        (forward-line 1))
      (kill-buffer csv-buffer))

    ;; Format as an org-mode table
    (let ((headers (if custom-headers
                       custom-headers
                     (mapcar (lambda (idx) (concat "Col " (number-to-string idx))) columns))))
      (concat "| " (mapconcat 'identity headers " | ") " |\n"
              "|-" (mapconcat (lambda (_) "+-") headers "-") "-|\n"
              (mapconcat 
               (lambda (row)
                 (concat "| " (mapconcat 'identity row " | ") " |"))
               (nreverse launches) "\n")
              "\n"))))
;; Example
; (list-launches-for-year "2023" 0 1 2 13 '("Launch ID" "Name" "Date" "Country"))

(defun set-yearly-totals ()
  "Set the global variables for launches totals for all years from the current year to 1956."
  (let* ((current-year (string-to-number (format-time-string "%Y")))
         (year current-year))
    (while (>= year 1956)
      (let* ((results (launches-totals-for-year (number-to-string year)))
             (total-var (intern (format "%d-total" year)))
             (successes-var (intern (format "%d-successes" year)))
             (failures-var (intern (format "%d-failures" year))))
        (set total-var (nth 0 results))
        (set successes-var (nth 1 results))
        (set failures-var (nth 2 results)))
      (setq year (1- year)))))

(let ((results (launches-totals)))
  (setq grand-total (nth 0 results)
        grand-successes (nth 1 results)
        grand-failures (nth 2 results)))








