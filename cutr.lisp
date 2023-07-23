(defmacro settings (&rest lst)
  (let (pairs flags)
    (loop for (key _ value) in lst do
          (push (list key value) pairs)
          (push (list (format nil "-~(~a~)" key) key) flags))
    `(progn (defstruct settings (_flags ',flags) ,@(reverse pairs))
            (defvar *settings* (make-settings)))))

(settings 
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
  (want      "optimization goal"         'plan))

(defmacro ? (s x &rest xs)
  (if xs `(? (slot-value ,s ',x) ,@xs) `(slot-value ,s ',x)))

(defmacro $ (x) `(? *settings* ,x))

(defun thing (s &aux (s1 (trim s)))
  "coerce `s` into a number or string or t or nil or #\?"
  (cond ((equal s1 "?") #\?)
        ((equal s1 "t") t)
        ((equal s1 "nil") nil)
        (t (let ((n (read-from-string s1 nil nil))) 
             (if (numberp n) n s1)))))

(defun cli (&aux it)
  (loop for (flag slot) in (? *settings* _flags) do
        (when (setf it (member flag (args) :test #'equal))
          (setf (? *settings* slot) (cond ((eql b4 t) nil)
                                          ((eql b4 nil) t)
                                          (t (thing (second it))))))))
