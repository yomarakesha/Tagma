from app import create_app, db
from app.models.user import User

def create_admin():
    app = create_app()
    with app.app_context():
        # Проверим, есть ли уже такой пользователь
        existing = User.query.filter_by(username='admin').first()
        if existing:
            print("Пользователь 'admin' уже существует. Обновим пароль...")
            existing.set_password('admin')
        else:
            admin = User(username='admin', is_admin=True)
            admin.set_password('admin')
            db.session.add(admin)
        
        db.session.commit()
        print("✅ Администратор создан или обновлён: admin / admin")

if __name__ == "__main__":
    create_admin()
