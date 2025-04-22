from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import mysql.connector
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'black',
    'database': 'clinic_db'
}

# Function to connect to the database
def get_db_connection():
    return mysql.connector.connect(**db_config)
    

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

# Contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')
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

        return render_template('book.html', services=services)
    elif request.method == 'POST':
        # Handle form submission
        full_name = request.form['full_name']
        phone_number = request.form['phone_number']
        email = request.form['email']
        home_address = request.form['home_address']
        appointment_date = request.form['appointment_date']
        service_id = request.form['service_id']
        receive_notifications = 'receive_notifications' in request.form

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO appointments (full_name, phone_number, email, home_address, appointment_date, service_id, receive_notifications)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (full_name, phone_number, email, home_address, appointment_date, service_id, receive_notifications))
        conn.commit()
        cursor.close()
        conn.close()

        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('book'))
    return render_template('book.html', services=[])

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

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('''
        SELECT appointments.*, services.name AS service_name
        FROM appointments
        LEFT JOIN services ON appointments.service_id = services.id
    ''')
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/appointments.html', appointments=appointments)

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

    # Fetch the current stock from the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT quantity FROM drugs WHERE id = %s', (drug_id,))
    drug = cursor.fetchone()

    if not drug:
        flash('Drug not found!', 'error')
        return redirect(url_for('admin_stock'))

    # Calculate the new stock quantity
    new_quantity = drug['quantity'] + quantity_to_add

    # Update the drug quantity in the database
    cursor.execute('UPDATE drugs SET quantity = %s WHERE id = %s', (new_quantity, drug_id))
    conn.commit()
    cursor.close()
    conn.close()

    flash(f'Stock updated successfully! Added {quantity_to_add} units. New stock: {new_quantity}', 'success')
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

# Initialize the scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(func=delete_expired_appointments, trigger='cron', hour=0, minute=0)  # Run daily at midnight
scheduler.start()

if __name__ == '__main__':
    app.run(debug=True)
    

