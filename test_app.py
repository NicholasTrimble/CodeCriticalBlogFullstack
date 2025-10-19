import pytest
from app import app, db, Post

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # in-memory DB for tests
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_create_post(client):
    response = client.post('/new', data={
        'title': 'Test Post',
        'subtitle': 'Subtitle',
        'author': 'Tester',
        'content': 'Test content'
    }, follow_redirects=True)
    assert response.status_code == 200
    post = Post.query.filter_by(title='Test Post').first()
    assert post is not None
    assert post.author == 'Tester'

def test_read_post(client):
    with app.app_context():  # ensure DB context
        post = Post(title='Read Test', subtitle='Sub', author='Tester', content='Content')
        db.session.add(post)
        db.session.commit()
        post_id = post.id

    response = client.get(f'/post/{post_id}')
    assert response.status_code == 200
    assert b'Read Test' in response.data

def test_edit_post(client):
    with app.app_context():
        post = Post(title='Old Title', subtitle='Sub', author='Tester', content='Content')
        db.session.add(post)
        db.session.commit()
        post_id = post.id

    response = client.post(f'/edit/{post_id}', data={
        'title': 'New Title',
        'subtitle': 'Sub',
        'content': 'Updated content'
    }, follow_redirects=True)

    with app.app_context():
        updated_post = Post.query.get(post_id)
        assert updated_post.title == 'New Title'

def test_delete_post(client):
    with app.app_context():
        post = Post(title='Delete Me', subtitle='Sub', author='Tester', content='Content')
        db.session.add(post)
        db.session.commit()
        post_id = post.id

    response = client.post(f'/delete/{post_id}', follow_redirects=True)

    with app.app_context():
        deleted_post = Post.query.get(post_id)
        assert deleted_post is None