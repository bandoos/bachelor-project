# * combing context managers




"""
class A():
    def __enter__(self):
        print("enter A")
        return self

    def __exit__(self,*args):
        print("exit A")

class B(A):

    def __call__(self):
        raise Exception('ti')

    def __enter__(self):
        super(B,self).__enter__()
        print("enter B")
        return self

    def __exit__(self,*args):
        print("exit B")
        return super(B,self).__exit__(*args)



b = B()



with b as ctx:
##    ctx()
    print("foo")

"""
