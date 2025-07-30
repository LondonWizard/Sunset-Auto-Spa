from flask import Flask, render_template, request, flash, redirect, url_for
from flask_mail import Mail, Message
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'sunset_auto_spa_secret_key_2025'

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME')

mail = Mail(app)

# Cache busting - add version parameter to static files
@app.template_filter('bust_cache')
def bust_cache_filter(filename):
    """Add a timestamp to static files to bust cache"""
    return f"{filename}?v={int(datetime.now().timestamp())}"

# Add cache control headers to all responses
@app.after_request
def after_request(response):
    """Add cache control headers"""
    # For static files, set no-cache to force revalidation
    if request.endpoint == 'static':
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    # For HTML pages, set short cache with revalidation
    else:
        response.headers['Cache-Control'] = 'no-cache, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
    return response

# Service packages data
SERVICES = {
    'bronze': {
        'name': 'Bronze Package',
        'price': 105,
        'duration': '1 hour',
        'description': 'Essential exterior and interior cleaning',
        'exterior': [
            'Complete exterior wash and rinse',
            'Wheel and tire cleaning',
            'Quick shine and dry finish',
            'Basic tire shine application'
        ],
        'interior': [
            'Full vacuum and surface cleaning',
            'Interior glass cleaning'
        ]
    },
    'silver': {
        'name': 'Silver Package',
        'price': 155,
        'duration': '1.5 hours',
        'description': 'Enhanced detailing with protective treatments',
        'exterior': [
            'Premium two-stage wash process',
            'Detailed wheel and tire scrubbing',
            'Engine bay rinse and cleaning',
            'Protective spray wax application',
            'Graphene tire dressing'
        ],
        'interior': [
            'Deep vacuum and detail cleaning',
            'Leather and surface conditioning',
            'Interior glass glazing'
        ]
    },
    'gold': {
        'name': 'Gold Package',
        'price': 300,
        'duration': '3 hours',
        'description': 'Premium comprehensive detailing experience',
        'exterior': [
            'Professional clay mitt treatment',
            'Graphene shampoo wash system',
            'Complete engine bay detailing',
            'Hand-applied graphene wax',
            'Exterior trim restoration',
            'Premium tire dressing'
        ],
        'interior': [
            'Complete interior detailing',
            'Leather conditioning and protection',
            'Floor mat deep extraction',
            'Fabric and rubber protection',
            'Interior trim restoration',
            'Anti-fog glass treatment'
        ]
    }
}

PREMIUM_SERVICES = [
    {
        'name': 'Paint Correction',
        'description': 'Professional multi-stage paint correction to remove swirl marks, scratches, and restore your paint\'s clarity and depth.',
        'features': ['Swirl mark removal', 'Scratch correction', 'Paint depth restoration', 'High-gloss finish']
    },
    {
        'name': 'Ceramic Coating',
        'description': 'Long-lasting protection with superior gloss and hydrophobic properties that keep your car looking newer for longer.',
        'features': ['Long-term protection', 'Enhanced gloss', 'Hydrophobic properties', 'UV protection']
    }
]

@app.route('/')
def home():
    return render_template('index.html', services=SERVICES, premium_services=PREMIUM_SERVICES)

@app.route('/services')
def services():
    return render_template('services.html', services=SERVICES, premium_services=PREMIUM_SERVICES)

@app.route('/service/<package>')
def service_detail(package):
    if package in SERVICES:
        return render_template('service_detail.html', service=SERVICES[package], package=package)
    return redirect(url_for('services'))

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/book')
def book():
    return render_template('booking.html', services=SERVICES)

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        service = request.form.get('service')
        message = request.form.get('message')
        
        # Create email message
        msg = Message(
            subject=f'New Contact Form Submission - {service if service else "General Inquiry"}',
            recipients=['info@sunsetautospa.com'],  # Change to your business email
            body=f"""
New contact form submission:

Name: {name}
Email: {email}
Phone: {phone}
Service Interest: {service if service else 'Not specified'}

Message:
{message}

Submitted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
        )
        
        mail.send(msg)
        flash('Thank you for your message! We\'ll get back to you soon.', 'success')
        
    except Exception as e:
        flash('Sorry, there was an error sending your message. Please try again or call us directly.', 'error')
        
    return redirect(url_for('contact'))

@app.route('/quote', methods=['POST'])
def get_quote():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        service = request.form.get('service')
        vehicle_info = request.form.get('vehicle_info')
        preferred_date = request.form.get('preferred_date')
        
        # Create quote request email
        msg = Message(
            subject=f'New Quote Request - {service}',
            recipients=['info@sunsetautospa.com'],  # Change to your business email
            body=f"""
New quote request:

Name: {name}
Email: {email}
Phone: {phone}
Service: {service}
Vehicle Information: {vehicle_info}
Preferred Date: {preferred_date}

Submitted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
        )
        
        mail.send(msg)
        flash('Quote request submitted successfully! We\'ll contact you within 24 hours.', 'success')
        
    except Exception as e:
        flash('Sorry, there was an error submitting your quote request. Please try again.', 'error')
        
    return redirect(url_for('book'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False) 