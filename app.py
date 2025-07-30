from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_mail import Mail, Message
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
import random

app = Flask(__name__)
app.secret_key = 'سر_سري_قوي_غير_هذا_شي_صعب_التخمين'

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USE_TLS=True,
    MAIL_USERNAME='talfaoory@gmail.com',
    MAIL_PASSWORD='ojcswyluzqogrssq',
    MAIL_DEFAULT_SENDER='your-email@gmail.com',
    RECAPTCHA_PUBLIC_KEY='6LdlPpMrAAAAAMDoU5UqyJh8aCJ-jWVlB8pekRxl',
    RECAPTCHA_PRIVATE_KEY='6LdlPpMrAAAAAH0fmRqi62nBcm64dhMvTZSsxesr',
)

mail = Mail(app)

class EmailForm(FlaskForm):
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    recaptcha = RecaptchaField()
    submit = SubmitField('أرسل رمز التحقق')

def waf_filter(input_str):
    black_list = ['<script', 'union select', '--', ' or 1=1', 'sleep(']
    text = input_str.lower()
    for word in black_list:
        if word in text:
            return False
    return True

@app.route('/', methods=['GET', 'POST'])
def index():
    form = EmailForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        
        if not waf_filter(email):
            flash('تم الكشف عن محتوى مشبوه في البريد الإلكتروني', 'danger')
            return redirect(url_for('index'))

        otp = random.randint(100000, 999999)
        session['otp'] = str(otp)
        session['email'] = email

        try:
            msg = Message('رمز التحقق الخاص بك', recipients=[email])
            msg.body = f'رمز التحقق الخاص بك هو: {otp}'
            mail.send(msg)
            flash('تم إرسال رمز التحقق إلى بريدك الإلكتروني', 'success')
            return redirect(url_for('verify'))
        except Exception as e:
            flash('حدث خطأ في إرسال الإيميل، حاول مرة أخرى', 'danger')
            print(e)
    return render_template('index.html', form=form)

@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'otp' not in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        user_otp = request.form.get('otp')
        if user_otp == session.get('otp'):
            flash('تم التحقق من بريدك بنجاح!', 'success')
            session.pop('otp')
            session.pop('email')
            return redirect(url_for('index'))
        else:
            flash('رمز التحقق غير صحيح', 'danger')
    return render_template('verify.html')
    
if __name__ == '__main__':
    app.run(debug=True)
