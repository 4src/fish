(defmacro def (a) `(progn ,@mapcar (cddr a,) #'(lambda (a) `(deparameter ,(second a), (third a) ,(fourth a)))))

(def (defun reset()
        (setf *bin* 10)
        (setf *some* "asda")))

