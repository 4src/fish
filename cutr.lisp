(defvar *settings* 
  '((about "cutr"
           ("cutr: to understand 'it',  cut 'it' up, then seek patterns in" 
            "the pieces. E.g. here we use cuts for multi- objective,"
            "semi- supervised, rule-based explanation."  
            "(c) Tim Menzies <timm@ieee.org>, BSD-2 license"
            ""))
    (bins      "initial number of bins"     16)
    (bootstrap "bootstraps"                 256)
    (cliffs    "nonparametric small delta"  .147)
    (cohen     "parametric small delta"     .35)
    (file      "read data file"             "../data/auto93.csv")
    (go        "start up action"            help)
    (help      "show help"                  nil)
    (seed      "random number seed"         1234567891)
    (min       "min size"                   .5)
    (rest      "exapansion best to rest"    3)
    (top       "top items to explore"       10)
    (want      "optimization goal"          plan)))

(defmacro ? (x &optional (lst *settings*)) 
  "alist accessor, defaults to searching `*settings*`"
  `(second (cdr (assoc ',x ,lst :test #'equalp))))

(defmacro o (s x &rest xs)
  "nested slot accessor"
  (if xs `(o (slot-value ,s ',x) ,@xs) `(slot-value ,s ',x)))

;;;; ----------------------------------------------------------
(defun trim (s) 
  "kill whitespace at start, at end"
  (string-trim '(#\Space #\Tab #\Newline) s))

(defun string2thing (s &aux (s1 (trim s)))
  "coerce `s` into a number or string or t or nil or #\?"
  (cond ((equal s1 "?") #\?)
        ((equal s1 "t") t)
        ((equal s1 "nil") nil)
        (t (let ((n (read-from-string s1 nil nil))) 
             (if (numberp n) n s1)))))

(defun cli (flag-help-values)
  (loop for (flag help value) in flag-help-values collect
        (labels ((_args ()     #+clisp ext:*args*  #+sbcl sb-ext:*posix-argv*)
                 (_update (arg) (cond ((eql value t) nil)
                                      ((eql value nil) t)
                                      (t (string2thing arg)))))
          (list flag help 
                (let ((it (member (format nil "--~(~a~)" flag) (_args) :test #'equal)))
                  (if it (_update (second it)) value))))))

(defun about (flag-help-values)
  (format t "~%~{~a~%~}OPTIONS:~%" (? about flag-help-values))
  (dolist (x (cdr flag-help-values)) 
    (format t "  ~10a ~a~%" (format nil "--~(~a~)" (first x)) (second x))))
;;;; ----------------------------------------------------------
(setf *settings* (cli *settings*))
(if (? help) (about *settings*))
(print (? bins))
