SupportedLanguages = {"go",
                        "py",
                        "java",
                        "c",
                        "cpp",
                        "python",
                        "python2",
                        "php",
                        "js" 
                        }

def response(code,msg,data):
    return {"code":code,"msg":msg,"data":data}

def retry(times,function,*args,**kwargs):
    """Assist in retrying function calls that are likely to fail"""
    app_conntext=kwargs.get("app-context")
    while times>0:
        times-=1
        try:
            if app_conntext:
                with app_conntext.app_context() as actx:
                    function(*args)
            else:
                function(*args,**kwargs)
            print(function.__name__,"Ran sucessfully with args ",args," and ",kwargs)
            return True # no exception
        except Exception as e:
            #can be any exception so try again
            print(function.__name__,"exception ",e)
    print(function.__name__,"failed with ",args," and ",kwargs)
    return False
