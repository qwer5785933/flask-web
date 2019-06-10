from . import passport_

@passport_.route('/')
def passport():
    return 'success'
