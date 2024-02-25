import re

def validate_form(request):
    if not all(key in request.form for key in ['name', 'password', 'email']):
        return 'Please fill out the form!'
    elif not re.match(r'[^@]+@[^@]+\.[^@]+', request.form['email']):
        return 'Invalid email address!'
    return None

