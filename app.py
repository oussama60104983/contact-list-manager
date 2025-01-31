import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from models import db, Contact
from forms import ContactForm
from flask_migrate import Migrate
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///contacts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure the uploads directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

# Initialize the database and migration tool
db.init_app(app)
migrate = Migrate(app, db)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update_contact(id):
    contact = Contact.query.get_or_404(id)
    form = ContactForm(obj=contact)

    if form.validate_on_submit():
        contact.name = form.name.data
        contact.phone = form.phone.data
        contact.email = form.email.data
        contact.type = form.custom_type.data if form.type.data == 'Other' else form.type.data

        # Save changes to the database
        try:
            db.session.commit()
            flash('Contact updated successfully!', 'success')
            return redirect(url_for('list_contacts'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating contact. Please try again.', 'error')
    
    return render_template('update_contact.html', form=form, contact=contact)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_contact(id):
    contact = Contact.query.get_or_404(id)
    try:
        db.session.delete(contact)
        db.session.commit()
        flash('Contact deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting contact. Please try again.', 'error')
    return redirect(url_for('list_contacts'))


@app.route('/contacts')
def list_contacts():
    contacts = Contact.query.all()
    return render_template('contacts.html', contacts=contacts)

@app.route('/debug/contacts')
def debug_contacts():
    contacts = Contact.query.all()
    return jsonify([contact.to_dict() for contact in contacts])


@app.route('/add', methods=['GET', 'POST'])
def add_contact():
    form = ContactForm()
    if form.validate_on_submit():
        image_url = None
        if form.image.data:
            filename = secure_filename(form.image.data.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            form.image.data.save(file_path)
            image_url = f'/static/uploads/{filename}'

        # Use the 'custom_type' if the user selected 'Other'
        contact_type = form.custom_type.data if form.type.data == 'Other' else form.type.data

        contact = Contact(
            name=form.name.data,
            phone=form.phone.data,
            email=form.email.data,
            type=contact_type,
            image_url=image_url
        )
        try:
            db.session.add(contact)
            db.session.commit()
            flash('Contact added successfully!', 'success')
            return redirect(url_for('list_contacts'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding contact. Please try again.', 'error')
    return render_template('add_contact.html', form=form)

if __name__ == '__main__':
    # Explicitly enable static file serving
    app.run(debug=True, port=5001)
