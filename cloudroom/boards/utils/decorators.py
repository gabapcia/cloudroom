
def false_on_exception(func):
    def run(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            return False
    return run
