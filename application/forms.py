from wtforms import Form, StringField, TextAreaField, validators, PasswordField, DateField

class Form_Login(Form):
    uName = StringField('Username', validators=[validators.DataRequired()])
    pWord = PasswordField('Password', validators=[validators.DataRequired()])


class Form_IP_Add(Form):
    ipAdress = StringField('ipAdress', validators=[validators.DataRequired(),
                                                validators.Length(max=25, message='max 25 characters'),
                                                validators.IPAddress(message='Sorry, not a valid IP4 Address.')])
    
    hostName = StringField('hostName', validators=[validators.DataRequired(message='What is hostname?')])
    
    Owner = StringField('Owner', validators=[validators.DataRequired(message='Who is the owner?')])

    Owner = StringField('Owner', validators=[validators.DataRequired(message='Who is the owner?')])
    
    dateStart = DateField('dateStart', format='%d/%m/%Y')

# class Form_Service_Add(Form):
#     serviceName = StringField('serviceName', validators=[validators.DataRequired(),
#                                              validators.Length(max=25, message='max 25 characters')])
#     ipAddress = StringField('ipAddress', validators=[validators.DataRequired(),
#                                              validators.Length(max=25, message='max 25 characters')])
#     proto = StringField('proto', validators=[validators.DataRequired(),
#                                              validators.Length(max=25, message='max 25 characters')])
#     port = StringField('port', validators=[validators.DataRequired(),
#                                              validators.Length(max=25, message='max 25 characters')])