(defvar *settings* '(
  (about "help" "
cutr: to understand 'it',  cut 'it' up, then seek patterns in 
the pieces. E.g. here we use cuts for multi- objective, 
semi- supervised, rule-based explanation.  
(c) Tim Menzies <timm@ieee.org>, BSD-2 license")
  (bins      "initial number of bins"     16)
  (bootstrap "bootstraps"                 256)
  (cohen     "parametric small delta"    .35)
  (cliffs    "nonparametric small delta" .147)
  (file      "read data file"            "../data/auto93.csv")
  (go        "start up action"           'help)
  (seed      "random number seed"        1234567891)
  (min       "min size"                  .5)
  (rest      "exapansion best to rest"   3)
  (top       "top items to explore"      10)
  (want      "optimization goal"         'plan)))

(defmacro ? (x) 
  "alist accessor, defaults to searching `*settings*`"
  `(second (cdr (assoc *settings*  ,lst :test #'equalp))))

(defmacro o (s x &rest xs)
  "nested slot accessor"
  (if xs `(o (slot-value ,s ',x) ,@xs) `(slot-value ,s ',x)))

(defun thing (s &aux (s1 (trim s)))
  "coerce `s` into a number or string or t or nil or #\?"
  (cond ((equal s1 "?") #\?)
        ((equal s1 "t") t)
        ((equal s1 "nil") nil)
        (t (let ((n (read-from-string s1 nil nil))) 
             (if (numberp n) n s1)))))

(defun cli (&aux it)
  (loop for (flag _ slot) in  *settings* do
        (when (setf it (member (format nil  "--~(~a~)" flag) (args) :test #'equal))
          (setf (? slot) (cond ((eql b4 t) nil)
                               ((eql b4 nil) t)
                               (t (thing (second it)))))))
  (if (? help)
    (format t "~a~%~%" (? about))
    (loop for (flag str slot) in  *settings* do
        (format t " --~(~a~) ~a~%" flag str)))

