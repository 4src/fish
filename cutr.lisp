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

(defmacro ? (x) 
  "alist accessor, defaults to searching `*settings*`"
  `(second (cdr (assoc ',x *settings* :test #'equalp))))

(defmacro o (s x &rest xs)
  "nested slot accessor"
  (if xs `(o (slot-value ,s ',x) ,@xs) `(slot-value ,s ',x)))

;;;; ----------------------------------------------------------
(defun trim (s) 
  "kill whitespace at start, at end"
  (string-trim '(#\Space #\Tab #\Newline) s))

(defun thing (s &aux (s1 (trim s)))
  "coerce `s` into a number or string or t or nil or #\?"
  (cond ((equal s1 "?") #\?)
        ((equal s1 "t") t)
        ((equal s1 "nil") nil)
        (t (let ((n (read-from-string s1 nil nil))) 
             (if (numberp n) n s1)))))

(defun args () 
  "accessing command-line flats"
  #+clisp ext:*args*  
  #+sbcl sb-ext:*posix-argv*)

(defun cli ()
  (labels ((_flag (flag) (format nil "--~(~a~)" flag))
           (_update (it val) 
                    (cond ((eql val t) nil)
                          ((eql val nil) t)
                          (t (thing (second it)))))
           (_cli (flag val &aux it) 
                 (if (setf it (member (_flag flag) (args) :test #'equal))
                   (_update it val)
                   val)))
    (setf *settings* (loop for (flag  h x) in *settings* 
                           collect (list flag h (_cli flag x))))
    (when (? help)
      (format t "~%~{~a~%~}OPTIONS:~%" (? about))
      (loop for (flag h _) in  *settings* do 
            (format t "  ~10a ~a~%" (_flag flag) h)))))
;;;; ----------------------------------------------------------
(cli)
(print (? bins))
