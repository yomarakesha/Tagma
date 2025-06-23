from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    
    admin = User.query.filter_by(username='admin').first()
    if admin:
        
        admin.username = 'tagma'  
        admin.set_password('tagma')  
        db.session.commit()
        print("Логин и пароль успешно изменены!")
        print("Новый логин: new_admin")
        print("Новый пароль: new_password123")
    else:
        print("Пользователь 'admin' не найден!")