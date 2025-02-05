import pytest
from app import app, db
from models import Contact

@pytest.fixture
def client():
    # Configure app for testing
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing

    # Create test client
    with app.test_client() as client:
        with app.app_context():
            # Create all tables in the test database
            db.create_all()
            yield client
            # Clean up after tests
            db.session.remove()
            db.drop_all()

@pytest.fixture
def sample_contact():
    contact = Contact(
        name='John Doe',
        phone='1234567890',
        email='john@example.com',
        type='Personal'
    )
    db.session.add(contact)
    db.session.commit()
    return contact

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_add_contact(client):
    data = {
        'name': 'Jane Doe',
        'phone': '9876543210',
        'email': 'jane@example.com',
        'type': 'Personal'
    }
    response = client.post('/add', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b'Jane Doe' in response.data

def test_update_contact(client, sample_contact):
    data = {
        'name': 'John Smith',
        'phone': sample_contact.phone,
        'email': sample_contact.email,
        'type': sample_contact.type,
        'submit': 'Update'
    }
    response = client.post(
        f'/update/{sample_contact.id}',
        data=data,
        follow_redirects=True
    )
    assert response.status_code == 200
    updated_contact = db.session.get(Contact, sample_contact.id)
    assert updated_contact.name == 'John Smith'

def test_delete_contact(client, sample_contact):
    # Make a GET request to the delete route
    response = client.get(f'/delete/{sample_contact.id}', follow_redirects=True)
    
    # Check if the response status is 200 (OK)
    assert response.status_code == 200
    
    # Verify that the contact is no longer in the database
    deleted_contact = db.session.get(Contact, sample_contact.id)
    assert deleted_contact is None
def test_update_contact_details(client, sample_contact):
    # Data to update the contact
    data = {
        'name': 'John Updated',  # Changing the name
        'phone': '9876543210',   # New phone number
        'email': 'johnupdated@example.com',  # New email
        'type': 'Personal'
    }
    
    # Send a POST request to update the contact details
    response = client.post(f'/update/{sample_contact.id}', data=data, follow_redirects=True)
    
    # Verify the response status code is 200 (OK)
    assert response.status_code == 200
    
    # Query the database to check if the contact's details were updated
    updated_contact = db.session.get(Contact, sample_contact.id)
    
    # Verify the contact's details have been updated
    assert updated_contact.name == 'John Updated'
    assert updated_contact.phone == '9876543210'
    assert updated_contact.email == 'johnupdated@example.com'
def test_get_contacts_api(client, sample_contact):
    response = client.get('/api/contacts')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['name'] == 'John Doe'

def test_get_single_contact_api(client, sample_contact):
    response = client.get(f'/api/contacts/{sample_contact.id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'John Doe'

def test_create_contact_api(client):
    data = {
        'name': 'API User',
        'phone': '5555555555',
        'email': 'api@example.com',
        'type': 'work'
    }
    response = client.post('/api/contacts', json=data)
    assert response.status_code == 201
    assert response.get_json()['name'] == 'API User'

def test_update_contact_api(client, sample_contact):
    data = {
        'name': 'John Updated',
        'phone': '9876543210',
        'email': 'johnupdated@example.com',
        'type': 'Personal'
    }
    # Send a PUT request to update the contact
    response = client.put(f'/api/contacts/{sample_contact.id}', json=data)
    
    # Verify the response status code is 200 (OK)
    assert response.status_code == 200
    
    # Check if the updated contact data is correct
    updated_contact = response.get_json()
    assert updated_contact['name'] == 'John Updated'
    assert updated_contact['phone'] == '9876543210'
    assert updated_contact['email'] == 'johnupdated@example.com'

def test_delete_contact_api(client, sample_contact):
    # Send a DELETE request to delete the contact
    response = client.delete(f'/api/contacts/{sample_contact.id}')
    
    # Verify the response status code is either 200 or 204 (OK or No Content)
    assert response.status_code in [200, 204]
    
    # Check if the contact is no longer in the database
    deleted_contact = db.session.get(Contact, sample_contact.id)
    assert deleted_contact is None



def test_list_contact_api(client, sample_contact):
    # Send a GET request to list all contacts
    response = client.get('/api/contacts')
    
    # Verify the response status code is 200 (OK)
    assert response.status_code == 200
    
    # Get the JSON data from the response
    data = response.get_json()
    
    # Verify that at least one contact is returned
    assert len(data) > 0
    assert data[0]['name'] == sample_contact.name
    assert data[0]['phone'] == sample_contact.phone
    assert data[0]['email'] == sample_contact.email

# Test error cases
def test_invalid_contact_creation(client):
    data = {
        'name': 'Invalid User',
        # Missing required fields
    }
    response = client.post('/api/contacts', json=data)
    assert response.status_code == 400

def test_get_nonexistent_contact(client):
    response = client.get('/api/contacts/999')
    assert response.status_code == 404  