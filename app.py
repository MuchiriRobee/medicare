from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask_mail import Mail, Message
import mysql.connector
import secrets
import string
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'clinic_db'
}

# Function to connect to the database
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    # Add buffered=True to prevent unread results issues
    cursor = conn.cursor(dictionary=True, buffered=True)
    return conn

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Services page
@app.route('/services')
def services():
    return render_template('services.html')

# About Us page
@app.route('/about')
def about():
    return render_template('about.html')
# faq page
@app.route('/faq')
def faq():
    return render_template('faq.html')

# Contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/send-message', methods=['POST'])
def send_message():
    try:
        # Get form data
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        # Basic validation
        if not all([name, email, subject, message]):
            return jsonify({'success': False, 'error': 'All fields are required'}), 400

        # Store in database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO contact_messages (name, email, subject, message)
            VALUES (%s, %s, %s, %s)
        ''', (name, email, subject, message))
        conn.commit()
        cursor.close()
        conn.close()

        # Return success response
        return jsonify({
            'success': True,
            'message': 'Thank you! Your message has been sent successfully.'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
# Team Page
@app.route('/team')
def team():
    return render_template('team.html')

# Book Appointment page
@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'GET':
        # Fetch services from the database
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM services')
        services = cursor.fetchall()
        cursor.close()
        conn.close()

        # Get today's date for the minimum date in the form
        min_date = datetime.now().strftime('%Y-%m-%d')
        
        return render_template('book.html', services=services, min_date=min_date)
    
    elif request.method == 'POST':
        # Handle form submission
        full_name = request.form['full_name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        home_address = request.form['home_address']
        appointment_date = request.form['appointment_date']
        service_id = request.form['service_id']
        receive_notifications = 'receive_notifications' in request.form

        # Validate date
        appointment_date_obj = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        if appointment_date_obj < datetime.now().date():
            flash('Please select a date that is not in the past', 'error')
            return redirect(url_for('book'))

        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Insert appointment
            cursor.execute('''
                INSERT INTO appointments (full_name, phone_number, email, home_address, appointment_date, service_id, receive_notifications)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (full_name, phone_number, email, home_address, appointment_date, service_id, receive_notifications))
            
            # Get the inserted appointment ID
            appointment_id = cursor.lastrowid
            
            # Get service name for email
            cursor.execute('SELECT name FROM services WHERE id = %s', (service_id,))
            service = cursor.fetchone()
            service_name = service[0] if service else "Selected Service"
            
            conn.commit()
            
            # Prepare appointment details for email
            appointment_details = {
                'id': appointment_id,
                'full_name': full_name,
                'appointment_date': appointment_date,
                'service_name': service_name
            }
            
            # Send confirmation email
            if email and receive_notifications:
                if not send_confirmation_email(email, appointment_details):
                    flash('Appointment booked successfully, but we couldn\'t send a confirmation email', 'warning')
                else:
                    flash('Appointment booked successfully! A confirmation email has been sent.', 'success')
            else:
                flash('Appointment booked successfully!', 'success')
                
            return redirect(url_for('book'))
            
        except Exception as e:
            conn.rollback()
            flash(f'Error booking appointment: {str(e)}', 'error')
            return redirect(url_for('book'))
            
        finally:
            cursor.close()
            conn.close()
# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Use your email provider's SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'robeemuchiri@gmail.com'  # Your email
app.config['MAIL_PASSWORD'] = 'clxelbzenhovoify'  # Your email password or app-specific password
app.config['MAIL_DEFAULT_SENDER'] = 'noreply@medicareclinic.com'

mail = Mail(app)

def send_confirmation_email(recipient, appointment_details):
    try:
        msg = Message('Appointment Confirmation - Medicare Clinic',
                      recipients=[recipient])
        
        msg.body = f"""
Dear {appointment_details['full_name']},

Thank you for booking an appointment with Medicare Clinic.

Appointment Details:
- Date: {appointment_details['appointment_date']}
- Service: {appointment_details['service_name']}
- Reference ID: {appointment_details['id']}

Please arrive 15 minutes before your scheduled time. If you need to reschedule or cancel, please contact us at appointments@medicareclinic.com or call 254 743371171.

We look forward to seeing you!

Best regards,
Medicare Clinic Team
"""
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False
# Admin login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM staff_users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and user['password'] == password:
            session['username'] = username
            return redirect(url_for('admin_appointments'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

# Admin Page
@app.route('/admin/appointments')
def admin_appointments():
    if 'username' not in session:
        return redirect(url_for('login'))

    sort_type = request.args.get('sort', 'nearest')
    service_filter = request.args.get('service', 'all')

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True, buffered=True)  # Add buffered here too

    try:
        # Get all services first
        cursor.execute('SELECT id, name FROM services')
        services = cursor.fetchall()  # Important: fetch all results immediately

        # Build main query
        base_query = '''
            SELECT a.*, s.name AS service_name
            FROM appointments a
            LEFT JOIN services s ON a.service_id = s.id
        '''
        
        params = []
        where_clause = ''
        if service_filter != 'all':
            where_clause = ' WHERE a.service_id = %s'
            params.append(service_filter)
        
        if sort_type == 'nearest':
            order_by = '''
                ORDER BY 
                    CASE 
                        WHEN a.appointment_date >= CURDATE() THEN 0
                        ELSE 1
                    END,
                    ABS(DATEDIFF(a.appointment_date, CURDATE()))
            '''
        elif sort_type == 'newest':
            order_by = ' ORDER BY a.appointment_date DESC'
        elif sort_type == 'oldest':
            order_by = ' ORDER BY a.appointment_date ASC'
        else:
            order_by = ' ORDER BY a.appointment_date'
        
        # Execute main query
        cursor.execute(base_query + where_clause + order_by, params if params else None)
        appointments = cursor.fetchall()  # Fetch all results immediately

        return render_template('admin/appointments.html', 
                            appointments=appointments,
                            services=services,
                            sort_type=sort_type,
                            current_service=service_filter)
    
    finally:
        cursor.close()
        conn.close()
@app.route('/admin/appointments/<int:appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM appointments WHERE id = %s', (appointment_id,))
        conn.commit()
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/admin/pos', methods=['GET', 'POST'])
def admin_pos():
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM drugs')
    drugs = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/pos.html', drugs=drugs)

@app.route('/admin/reports')
def admin_reports():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Fetch all reports (optional: fetch only recent reports)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM reports')
    reports = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/reports.html', reports=reports)

@app.route('/submit_report', methods=['POST'])
def submit_report():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Get form data
    patient_name = request.form['patient_name']
    appointment_date = request.form['appointment_date']
    service_type = request.form['service_type']
    diagnosis = request.form['diagnosis']
    prescription = request.form['prescription']
    follow_up = request.form['follow_up']

    # Insert report into the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO reports (patient_name, appointment_date, service_type, diagnosis, prescription, follow_up)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (patient_name, appointment_date, service_type, diagnosis, prescription, follow_up))
    conn.commit()
    cursor.close()
    conn.close()

    flash('Report submitted successfully!', 'success')
    return redirect(url_for('admin_reports'))

@app.route('/search_reports')
def search_reports():
    if 'username' not in session:
        return redirect(url_for('login'))

    query = request.args.get('query', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM reports WHERE patient_name LIKE %s', (f'%{query}%',))
    reports = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(reports)

@app.route('/edit_report/<int:report_id>', methods=['GET', 'POST'])
def edit_report(report_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Update the report in the database
        patient_name = request.form['patient_name']
        appointment_date = request.form['appointment_date']
        service_type = request.form['service_type']
        diagnosis = request.form['diagnosis']
        prescription = request.form['prescription']
        follow_up = request.form['follow_up']

        cursor.execute('''
            UPDATE reports
            SET patient_name = %s, appointment_date = %s, service_type = %s, diagnosis = %s, prescription = %s, follow_up = %s
            WHERE id = %s
        ''', (patient_name, appointment_date, service_type, diagnosis, prescription, follow_up, report_id))
        conn.commit()

        flash('Report updated successfully!', 'success')
        return redirect(url_for('admin_reports'))

    # Fetch the report details
    cursor.execute('SELECT * FROM reports WHERE id = %s', (report_id,))
    report = cursor.fetchone()
    cursor.close()
    conn.close()

    if not report:
        flash('Report not found!', 'error')
        return redirect(url_for('admin_reports'))

    return render_template('admin/edit_report.html', report=report)


@app.route('/admin/invoice', methods=['POST'])
def admin_invoice():
    if 'username' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401

    # Get JSON data from the request
    data = request.get_json()
    patient_name = data.get('patient_name')
    items = data.get('items', [])

    if not patient_name or not items:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400

    # Fetch drug details from the database and calculate total price
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    total_price = 0
    invoice_items = []

    try:
        # Insert invoice into the database
        cursor.execute('''
            INSERT INTO invoices (patient_name, total_price, payment_status)
            VALUES (%s, %s, %s)
        ''', (patient_name, 0, 'Pending'))  # Initialize total_price as 0
        invoice_id = cursor.lastrowid

        # Process each item
        for item in items:
            drug_name = item.get('name')
            quantity = int(item.get('quantity'))
            price = float(item.get('price'))

            cursor.execute('SELECT * FROM drugs WHERE name = %s', (drug_name,))
            drug = cursor.fetchone()

            if not drug:
                raise Exception(f'Drug {drug_name} not found!')

            # Validate quantity
            if quantity > drug['quantity']:
                raise Exception(f'Error: The selected quantity for {drug_name} exceeds the available stock.')

            # Update drug quantity in the database
            new_quantity = drug['quantity'] - quantity
            cursor.execute('UPDATE drugs SET quantity = %s WHERE id = %s', (new_quantity, drug['id']))

            # Calculate item total price
            item_total = quantity * price
            total_price += item_total

            # Insert item into the invoice_items table
            cursor.execute('''
                INSERT INTO invoice_items (invoice_id, drug_name, quantity, price, total)
                VALUES (%s, %s, %s, %s, %s)
            ''', (invoice_id, drug_name, quantity, price, item_total))

        # Update the total price in the invoices table
        cursor.execute('UPDATE invoices SET total_price = %s WHERE id = %s', (total_price, invoice_id))

        # Commit the transaction
        conn.commit()

    except Exception as e:
        # Rollback the transaction in case of an error
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400

    finally:
        # Close the database connection
        cursor.close()
        conn.close()

    # Return success response with invoice ID
    return jsonify({'success': True, 'invoice_id': invoice_id})

@app.route('/admin/invoice/<int:invoice_id>', methods=['GET'])
def view_invoice(invoice_id):
    if 'username' not in session:
        return redirect(url_for('login'))

    # Fetch invoice details from the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM invoices WHERE id = %s', (invoice_id,))
    invoice = cursor.fetchone()

    if not invoice:
        flash('Invoice not found!', 'error')
        return redirect(url_for('admin_pos'))

    # Fetch invoice items
    cursor.execute('SELECT * FROM invoice_items WHERE invoice_id = %s', (invoice_id,))
    invoice_items = cursor.fetchall()

    cursor.close()
    conn.close()

    # Render the invoice template
    return render_template('admin/invoice.html', invoice=invoice, items=invoice_items)
@app.route('/admin/billing/<int:invoice_id>')
def admin_billing(invoice_id):
    # Fetch invoice details from the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM invoices WHERE id = %s', (invoice_id,))
    invoice = cursor.fetchone()

    # Fetch invoice items
    cursor.execute('SELECT * FROM invoice_items WHERE invoice_id = %s', (invoice_id,))
    items = cursor.fetchall()

    cursor.close()
    conn.close()

    if not invoice:
        flash('Invoice not found!', 'error')
        return redirect(url_for('admin_pos'))

    return render_template('admin/billing.html', invoice=invoice, items=items)

@app.route('/admin/payment_success')
def admin_payment_success():
    return render_template('admin/payment_success.html')
# Logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index')) 

# Display Messages
@app.route('/admin/contact_messages')
def admin_contact_messages():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Get sorting parameters from request
    name_sort = request.args.get('name_sort', 'asc')  # 'asc' or 'desc'
    date_sort = request.args.get('date_sort', 'desc')  # 'asc' or 'desc'

    # Build SQL query with sorting
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Base query
    query = 'SELECT * FROM contact_messages'
    
    # Add sorting
    order_by = []
    if name_sort:
        order_by.append(f'name {name_sort}')
    if date_sort:
        order_by.append(f'created_at {date_sort}')
    
    if order_by:
        query += ' ORDER BY ' + ', '.join(order_by)
    
    cursor.execute(query)
    messages = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/contact_messages.html', 
                         messages=messages,
                         name_sort=name_sort,
                         date_sort=date_sort)

# search drugs
@app.route('/search_drugs')
def search_drugs():
    query = request.args.get('query', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM drugs WHERE name LIKE %s', (f'%{query}%',))
    drugs = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(drugs)

# Add this route to search for services
@app.route('/search_services')
def search_services():
    query = request.args.get('query', '').strip()

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM services WHERE name LIKE %s', (f'%{query}%',))
    services = cursor.fetchall()
    cursor.close()
    conn.close()

    return jsonify(services)

@app.route('/admin/stock')
def admin_stock():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Fetch all drugs from the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM drugs')
    drugs = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/stock.html', drugs=drugs)

@app.route('/update_stock', methods=['POST'])
def update_stock():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Get form data
    drug_id = request.form['drug_id']
    quantity_to_add = int(request.form['quantity_to_add'])
    new_price = request.form.get('new_price')  # Optional field

    # Fetch the current stock from the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Update stock quantity
        cursor.execute('SELECT quantity FROM drugs WHERE id = %s', (drug_id,))
        drug = cursor.fetchone()

        if not drug:
            flash('Drug not found!', 'error')
            return redirect(url_for('admin_stock'))

        new_quantity = drug['quantity'] + quantity_to_add
        cursor.execute('UPDATE drugs SET quantity = %s WHERE id = %s', 
                      (new_quantity, drug_id))

        # Update price if provided
        if new_price:
            cursor.execute('UPDATE drugs SET price = %s WHERE id = %s', 
                          (float(new_price), drug_id))

        conn.commit()
        flash(f'Stock updated successfully! Added {quantity_to_add} units. New stock: {new_quantity}', 'success')
        
    except Exception as e:
        conn.rollback()
        flash(f'Error updating stock: {str(e)}', 'error')
        
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('admin_stock'))

# Function to delete expired appointments
def delete_expired_appointments():
    conn = get_db_connection()
    cursor = conn.cursor()
    today = datetime.now().date()
    cursor.execute('DELETE FROM appointments WHERE appointment_date < %s', (today,))
    conn.commit()
    cursor.close()
    conn.close()
    print("Expired appointments deleted.")

# Add these new routes to app.py

# Patient registration
@app.route('/patient/register', methods=['GET', 'POST'])
def patient_register():
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        
        # Hash password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO patients (full_name, email, phone, password)
                VALUES (%s, %s, %s, %s)
            ''', (full_name, email, phone, hashed_password))
            conn.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('patient_login'))
        except mysql.connector.IntegrityError:
            flash('Email already exists. Please use a different email.', 'error')
            return redirect(url_for('patient_register'))
        finally:
            cursor.close()
            conn.close()
    
    return render_template('patient/register.html')

# Patient login
@app.route('/patient/login', methods=['GET', 'POST'])
def patient_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM patients WHERE email = %s', (email,))
        patient = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if patient and bcrypt.checkpw(password.encode('utf-8'), patient['password'].encode('utf-8')):
            session['patient_id'] = patient['id']
            session['patient_email'] = patient['email']
            return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid email or password', 'error')
    
    return render_template('patient/login.html')

# Patient dashboard
@app.route('/patient/dashboard')
def patient_dashboard():
    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Get patient info
    cursor.execute('SELECT full_name, email, phone FROM patients WHERE id = %s', (session['patient_id'],))
    patient = cursor.fetchone()
    
    # Get appointments
    cursor.execute('''
        SELECT a.*, s.name as service_name 
        FROM appointments a
        LEFT JOIN services s ON a.service_id = s.id
        WHERE a.email = %s
        ORDER BY a.appointment_date DESC
    ''', (session['patient_email'],))
    appointments = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('patient/dashboard.html', patient=patient, appointments=appointments)

# Cancel appointment
@app.route('/patient/cancel_appointment/<int:appointment_id>', methods=['POST'])
def cancel_appointment(appointment_id):
    if 'patient_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verify the appointment belongs to the patient
        cursor.execute('SELECT email FROM appointments WHERE id = %s', (appointment_id,))
        appointment = cursor.fetchone()
        
        if not appointment or appointment[0] != session['patient_email']:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        # Delete the appointment
        cursor.execute('DELETE FROM appointments WHERE id = %s', (appointment_id,))
        conn.commit()
        
        return jsonify({'success': True})
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Patient logout
@app.route('/patient/logout')
def patient_logout():
    session.pop('patient_id', None)
    session.pop('patient_email', None)
    return redirect(url_for('index'))

# Password reset routes
@app.route('/patient/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Check if email exists
            cursor.execute('SELECT id FROM patients WHERE email = %s', (email,))
            patient = cursor.fetchone()
            
            if patient:
                # Generate token
                token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64))
                expires_at = datetime.now() + timedelta(hours=1)
                
                # Store token in database
                cursor.execute('''
                    INSERT INTO password_reset_tokens (patient_id, token, expires_at)
                    VALUES (%s, %s, %s)
                ''', (patient['id'], token, expires_at))
                conn.commit()
                
                # Send email with reset link
                reset_link = url_for('reset_password', token=token, _external=True)
                send_password_reset_email(email, reset_link)
            
            # Always show success message to prevent email enumeration
            flash('If an account with that email exists, a password reset link has been sent.', 'success')
            return redirect(url_for('patient_login'))
            
        except Exception as e:
            conn.rollback()
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('forgot_password'))
            
        finally:
            cursor.close()
            conn.close()
    
    return render_template('patient/forgot_password.html')

@app.route('/patient/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Validate token
        cursor.execute('''
            SELECT p.id, p.email 
            FROM password_reset_tokens t
            JOIN patients p ON t.patient_id = p.id
            WHERE t.token = %s 
            AND t.expires_at > NOW() 
            AND t.used = FALSE
        ''', (token,))
        token_data = cursor.fetchone()
        
        if not token_data:
            flash('Invalid or expired password reset link.', 'error')
            return redirect(url_for('forgot_password'))
        
        if request.method == 'POST':
            new_password = request.form['password']
            confirm_password = request.form['confirm_password']
            
            if new_password != confirm_password:
                flash('Passwords do not match.', 'error')
                return redirect(request.url)
            
            # Update password
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('UPDATE patients SET password = %s WHERE id = %s', 
                          (hashed_password, token_data['id']))
            
            # Mark token as used
            cursor.execute('UPDATE password_reset_tokens SET used = TRUE WHERE token = %s', (token,))
            
            conn.commit()
            flash('Your password has been updated successfully! Please log in.', 'success')
            return redirect(url_for('patient_login'))
        
        return render_template('patient/reset_password.html', token=token)
        
    except Exception as e:
        conn.rollback()
        flash('An error occurred. Please try again.', 'error')
        return redirect(url_for('forgot_password'))
        
    finally:
        cursor.close()
        conn.close()

# Add this email sending function
def send_password_reset_email(email, reset_link):
    try:
        msg = Message('Password Reset Request - Medicare Clinic',
                      recipients=[email])
        
        msg.body = f"""
You have requested to reset your password for your Medicare Clinic patient account.

Please click the following link to reset your password:
{reset_link}

This link will expire in 1 hour. If you didn't request a password reset, please ignore this email.

Best regards,
Medicare Clinic Team
"""
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending password reset email: {str(e)}")
        return False

# Add this route for changing password while logged in
@app.route('/patient/change-password', methods=['GET', 'POST'])
def change_password():
    if 'patient_id' not in session:
        return redirect(url_for('patient_login'))
    
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        
        if new_password != confirm_password:
            flash('New passwords do not match.', 'error')
            return redirect(url_for('change_password'))
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        try:
            # Verify current password
            cursor.execute('SELECT password FROM patients WHERE id = %s', (session['patient_id'],))
            patient = cursor.fetchone()
            
            if not patient or not bcrypt.checkpw(current_password.encode('utf-8'), patient['password'].encode('utf-8')):
                flash('Current password is incorrect.', 'error')
                return redirect(url_for('change_password'))
            
            # Update password
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cursor.execute('UPDATE patients SET password = %s WHERE id = %s', 
                          (hashed_password, session['patient_id']))
            conn.commit()
            
            flash('Your password has been changed successfully!', 'success')
            return redirect(url_for('patient_dashboard'))
            
        except Exception as e:
            conn.rollback()
            flash('An error occurred. Please try again.', 'error')
            return redirect(url_for('change_password'))
            
        finally:
            cursor.close()
            conn.close()
    
    return render_template('patient/change_password.html')
# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=delete_expired_appointments, trigger='cron', hour=0, minute=0)  # Run daily at midnight
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)

 

