"""Initial migration with multilingual fields

Revision ID: 9f352ac44db2
Revises: 
Create Date: 2025-06-13 19:34:00
"""

from alembic import op
import sqlalchemy as sa

revision = '9f352ac44db2'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Проверяем наличие таблиц и создаём только отсутствующие
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # Создание таблиц, если они не существуют
    if 'user' not in existing_tables:
        op.create_table('user',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('username', sa.String(length=80), nullable=False),
            sa.Column('email', sa.String(length=120), nullable=False),
            sa.Column('password_hash', sa.String(length=128), nullable=False),
            sa.Column('is_admin', sa.Boolean(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('email'),
            sa.UniqueConstraint('username')
        )

    if 'category' not in existing_tables:
        op.create_table('category',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    if 'client' not in existing_tables:
        op.create_table('client',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('logo_url', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    if 'contact' not in existing_tables:
        op.create_table('contact',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('phone', sa.String(length=255), nullable=True),
            sa.Column('address', sa.String(length=255), nullable=True),
            sa.Column('email', sa.String(length=255), nullable=True),
            sa.Column('social_media', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    if 'banner' not in existing_tables:
        op.create_table('banner',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=True),
            sa.Column('subtitle', sa.String(length=255), nullable=True),
            sa.Column('image_url', sa.String(length=255), nullable=True),
            sa.Column('button_text', sa.String(length=100), nullable=True),
            sa.Column('button_link', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    if 'project' not in existing_tables:
        op.create_table('project',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('background_image_url', sa.String(length=255), nullable=True),
            sa.Column('button_text', sa.String(length=100), nullable=True),
            sa.Column('button_link', sa.String(length=255), nullable=True),
            sa.Column('deliverables', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    if 'blog' not in existing_tables:
        op.create_table('blog',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=True),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('date', sa.DateTime(), nullable=True),
            sa.Column('read_time', sa.String(length=50), nullable=True),
            sa.Column('image_url', sa.String(length=255), nullable=True),
            sa.Column('additional_images', sa.Text(), nullable=True),
            sa.Column('link', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    if 'service' not in existing_tables:
        op.create_table('service',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=255), nullable=True),
            sa.Column('subtitles', sa.Text(), nullable=True),
            sa.Column('button_text', sa.String(length=100), nullable=True),
            sa.Column('button_link', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    if 'about' not in existing_tables:
        op.create_table('about',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('title', sa.String(length=100), nullable=True),
            sa.Column('subtitle', sa.String(length=255), nullable=True),
            sa.Column('description1', sa.Text(), nullable=True),
            sa.Column('description2', sa.Text(), nullable=True),
            sa.Column('image_url', sa.String(length=255), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )

    if 'project_categories' not in existing_tables:
        op.create_table('project_categories',
            sa.Column('project_id', sa.Integer(), nullable=False),
            sa.Column('category_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['category_id'], ['category.id'], ),
            sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
            sa.PrimaryKeyConstraint('project_id', 'category_id')
        )

    if 'review' not in existing_tables:
        op.create_table('review',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('content', sa.Text(), nullable=True),
            sa.Column('author', sa.String(length=255), nullable=True),
            sa.Column('project_id', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

    # Добавление мультиязычных полей и модификация существующих таблиц
    if 'category' in existing_tables:
        with op.batch_alter_table('category', schema=None) as batch_op:
            batch_op.alter_column('name', existing_type=sa.String(length=100), nullable=True)
            if 'name_ru' not in [c['name'] for c in inspector.get_columns('category')]:
                batch_op.add_column(sa.Column('name_ru', sa.String(length=255), nullable=True))
            if 'name_tk' not in [c['name'] for c in inspector.get_columns('category')]:
                batch_op.add_column(sa.Column('name_tk', sa.String(length=255), nullable=True))
            if 'name_en' not in [c['name'] for c in inspector.get_columns('category')]:
                batch_op.add_column(sa.Column('name_en', sa.String(length=255), nullable=True))

    if 'banner' in existing_tables:
        with op.batch_alter_table('banner', schema=None) as batch_op:
            if 'title_ru' not in [c['name'] for c in inspector.get_columns('banner')]:
                batch_op.add_column(sa.Column('title_ru', sa.String(length=255), nullable=True))
            if 'title_tk' not in [c['name'] for c in inspector.get_columns('banner')]:
                batch_op.add_column(sa.Column('title_tk', sa.String(length=255), nullable=True))
            if 'title_en' not in [c['name'] for c in inspector.get_columns('banner')]:
                batch_op.add_column(sa.Column('title_en', sa.String(length=255), nullable=True))
            if 'subtitle_ru' not in [c['name'] for c in inspector.get_columns('banner')]:
                batch_op.add_column(sa.Column('subtitle_ru', sa.String(length=255), nullable=True))
            if 'subtitle_tk' not in [c['name'] for c in inspector.get_columns('banner')]:
                batch_op.add_column(sa.Column('subtitle_tk', sa.String(length=255), nullable=True))
            if 'subtitle_en' not in [c['name'] for c in inspector.get_columns('banner')]:
                batch_op.add_column(sa.Column('subtitle_en', sa.String(length=255), nullable=True))
            if 'button_text_ru' not in [c['name'] for c in inspector.get_columns('banner')]:
                batch_op.add_column(sa.Column('button_text_ru', sa.String(length=100), nullable=True))
            if 'button_text_tk' not in [c['name'] for c in inspector.get_columns('banner')]:
                batch_op.add_column(sa.Column('button_text_tk', sa.String(length=100), nullable=True))
            if 'button_text_en' not in [c['name'] for c in inspector.get_columns('banner')]:
                batch_op.add_column(sa.Column('button_text_en', sa.String(length=100), nullable=True))

    if 'project' in existing_tables:
        with op.batch_alter_table('project', schema=None) as batch_op:
            if 'title_ru' not in [c['name'] for c in inspector.get_columns('project')]:
                batch_op.add_column(sa.Column('title_ru', sa.String(length=255), nullable=True))
            if 'title_tk' not in [c['name'] for c in inspector.get_columns('project')]:
                batch_op.add_column(sa.Column('title_tk', sa.String(length=255), nullable=True))
            if 'title_en' not in [c['name'] for c in inspector.get_columns('project')]:
                batch_op.add_column(sa.Column('title_en', sa.String(length=255), nullable=True))
            if 'description_ru' not in [c['name'] for c in inspector.get_columns('project')]:
                batch_op.add_column(sa.Column('description_ru', sa.Text(), nullable=True))
            if 'description_tk' not in [c['name'] for c in inspector.get_columns('project')]:
                batch_op.add_column(sa.Column('description_tk', sa.Text(), nullable=True))
            if 'description_en' not in [c['name'] for c in inspector.get_columns('project')]:
                batch_op.add_column(sa.Column('description_en', sa.Text(), nullable=True))
            if 'button_text_ru' not in [c['name'] for c in inspector.get_columns('project')]:
                batch_op.add_column(sa.Column('button_text_ru', sa.String(length=100), nullable=True))
            if 'button_text_tk' not in [c['name'] for c in inspector.get_columns('project')]:
                batch_op.add_column(sa.Column('button_text_tk', sa.String(length=100), nullable=True))
            if 'button_text_en' not in [c['name'] for c in inspector.get_columns('project')]:
                batch_op.add_column(sa.Column('button_text_en', sa.String(length=100), nullable=True))
            if 'deliverables_ru' not in [c['name'] for c in inspector.get_columns('project')]:
                batch_op.add_column(sa.Column('deliverables_ru', sa.Text(), nullable=True))
            if 'deliverables_tk' not in [c['name'] for c in inspector.get_columns('project')]:
                batch_op.add_column(sa.Column('deliverables_tk', sa.Text(), nullable=True))
            if 'deliverables_en' not in [c['name'] for c in inspector.get_columns('project')]:
                batch_op.add_column(sa.Column('deliverables_en', sa.Text(), nullable=True))

    if 'blog' in existing_tables:
        with op.batch_alter_table('blog', schema=None) as batch_op:
            if 'title_ru' not in [c['name'] for c in inspector.get_columns('blog')]:
                batch_op.add_column(sa.Column('title_ru', sa.String(length=255), nullable=True))
            if 'title_tk' not in [c['name'] for c in inspector.get_columns('blog')]:
                batch_op.add_column(sa.Column('title_tk', sa.String(length=255), nullable=True))
            if 'title_en' not in [c['name'] for c in inspector.get_columns('blog')]:
                batch_op.add_column(sa.Column('title_en', sa.String(length=255), nullable=True))
            if 'description_ru' not in [c['name'] for c in inspector.get_columns('blog')]:
                batch_op.add_column(sa.Column('description_ru', sa.Text(), nullable=True))
            if 'description_tk' not in [c['name'] for c in inspector.get_columns('blog')]:
                batch_op.add_column(sa.Column('description_tk', sa.Text(), nullable=True))
            if 'description_en' not in [c['name'] for c in inspector.get_columns('blog')]:
                batch_op.add_column(sa.Column('description_en', sa.Text(), nullable=True))

    if 'service' in existing_tables:
        with op.batch_alter_table('service', schema=None) as batch_op:
            if 'title_ru' not in [c['name'] for c in inspector.get_columns('service')]:
                batch_op.add_column(sa.Column('title_ru', sa.String(length=255), nullable=True))
            if 'title_tk' not in [c['name'] for c in inspector.get_columns('service')]:
                batch_op.add_column(sa.Column('title_tk', sa.String(length=255), nullable=True))
            if 'title_en' not in [c['name'] for c in inspector.get_columns('service')]:
                batch_op.add_column(sa.Column('title_en', sa.String(length=255), nullable=True))
            if 'subtitles_ru' not in [c['name'] for c in inspector.get_columns('service')]:
                batch_op.add_column(sa.Column('subtitles_ru', sa.Text(), nullable=True))
            if 'subtitles_tk' not in [c['name'] for c in inspector.get_columns('service')]:
                batch_op.add_column(sa.Column('subtitles_tk', sa.Text(), nullable=True))
            if 'subtitles_en' not in [c['name'] for c in inspector.get_columns('service')]:
                batch_op.add_column(sa.Column('subtitles_en', sa.Text(), nullable=True))
            if 'button_text_ru' not in [c['name'] for c in inspector.get_columns('service')]:
                batch_op.add_column(sa.Column('button_text_ru', sa.String(length=100), nullable=True))
            if 'button_text_tk' not in [c['name'] for c in inspector.get_columns('service')]:
                batch_op.add_column(sa.Column('button_text_tk', sa.String(length=100), nullable=True))
            if 'button_text_en' not in [c['name'] for c in inspector.get_columns('service')]:
                batch_op.add_column(sa.Column('button_text_en', sa.String(length=100), nullable=True))

    if 'review' in existing_tables:
        with op.batch_alter_table('review', schema=None) as batch_op:
            if 'content_ru' not in [c['name'] for c in inspector.get_columns('review')]:
                batch_op.add_column(sa.Column('content_ru', sa.Text(), nullable=True))
            if 'content_tk' not in [c['name'] for c in inspector.get_columns('review')]:
                batch_op.add_column(sa.Column('content_tk', sa.Text(), nullable=True))
            if 'content_en' not in [c['name'] for c in inspector.get_columns('review')]:
                batch_op.add_column(sa.Column('content_en', sa.Text(), nullable=True))
            if 'author_ru' not in [c['name'] for c in inspector.get_columns('review')]:
                batch_op.add_column(sa.Column('author_ru', sa.String(length=255), nullable=True))
            if 'author_tk' not in [c['name'] for c in inspector.get_columns('review')]:
                batch_op.add_column(sa.Column('author_tk', sa.String(length=255), nullable=True))
            if 'author_en' not in [c['name'] for c in inspector.get_columns('review')]:
                batch_op.add_column(sa.Column('author_en', sa.String(length=255), nullable=True))

    if 'contact' in existing_tables:
        with op.batch_alter_table('contact', schema=None) as batch_op:
            if 'address_ru' not in [c['name'] for c in inspector.get_columns('contact')]:
                batch_op.add_column(sa.Column('address_ru', sa.String(length=255), nullable=True))
            if 'address_tk' not in [c['name'] for c in inspector.get_columns('contact')]:
                batch_op.add_column(sa.Column('address_tk', sa.String(length=255), nullable=True))
            if 'address_en' not in [c['name'] for c in inspector.get_columns('contact')]:
                batch_op.add_column(sa.Column('address_en', sa.String(length=255), nullable=True))

    if 'about' in existing_tables:
        with op.batch_alter_table('about', schema=None) as batch_op:
            if 'title_ru' not in [c['name'] for c in inspector.get_columns('about')]:
                batch_op.add_column(sa.Column('title_ru', sa.String(length=255), nullable=True))
            if 'title_tk' not in [c['name'] for c in inspector.get_columns('about')]:
                batch_op.add_column(sa.Column('title_tk', sa.String(length=255), nullable=True))
            if 'title_en' not in [c['name'] for c in inspector.get_columns('about')]:
                batch_op.add_column(sa.Column('title_en', sa.String(length=255), nullable=True))
            if 'subtitle_ru' not in [c['name'] for c in inspector.get_columns('about')]:
                batch_op.add_column(sa.Column('subtitle_ru', sa.String(length=255), nullable=True))
            if 'subtitle_tk' not in [c['name'] for c in inspector.get_columns('about')]:
                batch_op.add_column(sa.Column('subtitle_tk', sa.String(length=255), nullable=True))
            if 'subtitle_en' not in [c['name'] for c in inspector.get_columns('about')]:
                batch_op.add_column(sa.Column('subtitle_en', sa.String(length=255), nullable=True))
            if 'description1_ru' not in [c['name'] for c in inspector.get_columns('about')]:
                batch_op.add_column(sa.Column('description1_ru', sa.Text(), nullable=True))
            if 'description1_tk' not in [c['name'] for c in inspector.get_columns('about')]:
                batch_op.add_column(sa.Column('description1_tk', sa.Text(), nullable=True))
            if 'description1_en' not in [c['name'] for c in inspector.get_columns('about')]:
                batch_op.add_column(sa.Column('description1_en', sa.Text(), nullable=True))
            if 'description2_ru' not in [c['name'] for c in inspector.get_columns('about')]:
                batch_op.add_column(sa.Column('description2_ru', sa.Text(), nullable=True))
            if 'description2_tk' not in [c['name'] for c in inspector.get_columns('about')]:
                batch_op.add_column(sa.Column('description2_tk', sa.Text(), nullable=True))
            if 'description2_en' not in [c['name'] for c in inspector.get_columns('about')]:
                batch_op.add_column(sa.Column('description2_en', sa.Text(), nullable=True))

    # Заполнение мультиязычных полей значениями по умолчанию
    if 'banner' in existing_tables:
        op.execute("UPDATE banner SET title_ru = COALESCE(title, 'Default Title'), title_tk = COALESCE(title, 'Default Title'), title_en = COALESCE(title, 'Default Title'), subtitle_ru = subtitle, subtitle_tk = subtitle, subtitle_en = subtitle, button_text_ru = button_text, button_text_tk = button_text, button_text_en = button_text")
    if 'project' in existing_tables:
        op.execute("UPDATE project SET title_ru = COALESCE(title, 'Default Title'), title_tk = COALESCE(title, 'Default Title'), title_en = COALESCE(title, 'Default Title'), description_ru = description, description_tk = description, description_en = description, button_text_ru = button_text, button_text_tk = button_text, button_text_en = button_text, deliverables_ru = deliverables, deliverables_tk = deliverables, deliverables_en = deliverables")
    if 'blog' in existing_tables:
        op.execute("UPDATE blog SET title_ru = COALESCE(title, 'Default Title'), title_tk = COALESCE(title, 'Default Title'), title_en = COALESCE(title, 'Default Title'), description_ru = description, description_tk = description, description_en = description")
    if 'category' in existing_tables:
        op.execute("UPDATE category SET name_ru = COALESCE(name, 'Default Category'), name_tk = COALESCE(name, 'Default Category'), name_en = COALESCE(name, 'Default Category')")
    if 'service' in existing_tables:
        op.execute("UPDATE service SET title_ru = COALESCE(title, 'Default Title'), title_tk = COALESCE(title, 'Default Title'), title_en = COALESCE(title, 'Default Title'), subtitles_ru = subtitles, subtitles_tk = subtitles, subtitles_en = subtitles")
    if 'review' in existing_tables:
        op.execute("UPDATE review SET content_ru = COALESCE(content, 'Default Content'), content_tk = COALESCE(content, 'Default Content'), content_en = COALESCE(content, 'Default Content'), author_ru = COALESCE(author, 'Author'), author_tk = COALESCE(author, 'Author'), author_en = COALESCE(author, 'Author')")
    if 'contact' in existing_tables:
        op.execute("UPDATE contact SET address_ru = COALESCE(address, 'Default Address'), address_tk = COALESCE(address, 'Default Address'), address_en = COALESCE(address, 'Default Address')")
    if 'about' in existing_tables:
        op.execute("UPDATE about SET title_ru = COALESCE(title, 'Default Title'), title_tk = COALESCE(title, 'Default Title'), title_en = COALESCE(title, 'Default Title'), subtitle_ru = subtitle, subtitle_tk = subtitle, subtitle_en = subtitle, description1_ru = description1, description1_tk = description1, description1_en = description1, description2_ru = description2, description2_tk = description2, description2_en = description2")

    # Установка NOT NULL для обязательных полей
    if 'banner' in existing_tables:
        with op.batch_alter_table('banner', schema=None) as batch_op:
            batch_op.alter_column('title_ru', nullable=False)
            batch_op.alter_column('title_tk', nullable=False)
            batch_op.alter_column('title_en', nullable=False)

    if 'project' in existing_tables:
        with op.batch_alter_table('project', schema=None) as batch_op:
            batch_op.alter_column('title_ru', nullable=False)
            batch_op.alter_column('title_tk', nullable=False)
            batch_op.alter_column('title_en', nullable=False)

    if 'blog' in existing_tables:
        with op.batch_alter_table('blog', schema=None) as batch_op:
            batch_op.alter_column('title_ru', nullable=False)
            batch_op.alter_column('title_tk', nullable=False)
            batch_op.alter_column('title_en', nullable=False)

    if 'category' in existing_tables:
        with op.batch_alter_table('category', schema=None) as batch_op:
            batch_op.alter_column('name_ru', nullable=False)
            batch_op.alter_column('name_tk', nullable=False)
            batch_op.alter_column('name_en', nullable=False)

    if 'service' in existing_tables:
        with op.batch_alter_table('service', schema=None) as batch_op:
            batch_op.alter_column('title_ru', nullable=False)
            batch_op.alter_column('title_tk', nullable=False)
            batch_op.alter_column('title_en', nullable=False)

    if 'review' in existing_tables:
        with op.batch_alter_table('review', schema=None) as batch_op:
            batch_op.alter_column('content_ru', nullable=False)
            batch_op.alter_column('content_tk', nullable=False)
            batch_op.alter_column('content_en', nullable=False)

    if 'about' in existing_tables:
        with op.batch_alter_table('about', schema=None) as batch_op:
            batch_op.alter_column('title_ru', nullable=False)
            batch_op.alter_column('title_tk', nullable=False)
            batch_op.alter_column('title_en', nullable=False)

    # Удаление старых полей
    if 'banner' in existing_tables:
        with op.batch_alter_table('banner', schema=None) as batch_op:
            if 'title' in [c['name'] for c in inspector.get_columns('banner')]:
                batch_op.drop_column('title')
            if 'subtitle' in [c['name'] for c in inspector.get_columns('banner')]:
                batch_op.drop_column('subtitle')
            if 'button_text' in [c['name'] for c in inspector.get_columns('banner')]:
                batch_op.drop_column('button_text')

    if 'project' in existing_tables:
        with op.batch_alter_table('project', schema=None) as batch_op:
            if 'title' in [c['name'] for c in inspector.get_columns('project')]:
                batch_op.drop_column('title')
            if 'description' in [c['name'] for c in inspector.get_columns('project')]:
                batch_op.drop_column('description')
            if 'button_text' in [c['name'] for c in inspector.get_columns('project')]:
                batch_op.drop_column('button_text')
            if 'deliverables' in [c['name'] for c in inspector.get_columns('project')]:
                batch_op.drop_column('deliverables')

    if 'blog' in existing_tables:
        with op.batch_alter_table('blog', schema=None) as batch_op:
            if 'title' in [c['name'] for c in inspector.get_columns('blog')]:
                batch_op.drop_column('title')
            if 'description' in [c['name'] for c in inspector.get_columns('blog')]:
                batch_op.drop_column('description')

    if 'category' in existing_tables:
        with op.batch_alter_table('category', schema=None) as batch_op:
            if 'name' in [c['name'] for c in inspector.get_columns('category')]:
                batch_op.drop_column('name')

    if 'service' in existing_tables:
        with op.batch_alter_table('service', schema=None) as batch_op:
            if 'title' in [c['name'] for c in inspector.get_columns('service')]:
                batch_op.drop_column('title')
            if 'subtitles' in [c['name'] for c in inspector.get_columns('service')]:
                batch_op.drop_column('subtitles')
            if 'button_text' in [c['name'] for c in inspector.get_columns('service')]:
                batch_op.drop_column('button_text')

    if 'review' in existing_tables:
        with op.batch_alter_table('review', schema=None) as batch_op:
            if 'content' in [c['name'] for c in inspector.get_columns('review')]:
                batch_op.drop_column('content')
            if 'author' in [c['name'] for c in inspector.get_columns('review')]:
                batch_op.drop_column('author')

    if 'contact' in existing_tables:
        with op.batch_alter_table('contact', schema=None) as batch_op:
            if 'address' in [c['name'] for c in inspector.get_columns('contact')]:
                batch_op.drop_column('address')

    if 'about' in existing_tables:
        with op.batch_alter_table('about', schema=None) as batch_op:
            if 'title' in [c['name'] for c in inspector.get_columns('about')]:
                batch_op.drop_column('title')
            if 'subtitle' in [c['name'] for c in inspector.get_columns('about')]:
                batch_op.drop_column('subtitle')
            if 'description1' in [c['name'] for c in inspector.get_columns('about')]:
                batch_op.drop_column('description1')
            if 'description2' in [c['name'] for c in inspector.get_columns('about')]:
                batch_op.drop_column('description2')

def downgrade():
    # Восстановление старых полей
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if 'about' in existing_tables:
        with op.batch_alter_table('about', schema=None) as batch_op:
            batch_op.add_column(sa.Column('description2', sa.Text(), nullable=True))
            batch_op.add_column(sa.Column('description1', sa.Text(), nullable=True))
            batch_op.add_column(sa.Column('subtitle', sa.String(length=255), nullable=True))
            batch_op.add_column(sa.Column('title', sa.String(length=100), nullable=True))

    if 'contact' in existing_tables:
        with op.batch_alter_table('contact', schema=None) as batch_op:
            batch_op.add_column(sa.Column('address', sa.String(length=255), nullable=True))

    if 'review' in existing_tables:
        with op.batch_alter_table('review', schema=None) as batch_op:
            batch_op.add_column(sa.Column('author', sa.String(length=255), nullable=True))
            batch_op.add_column(sa.Column('content', sa.Text(), nullable=True))

    if 'service' in existing_tables:
        with op.batch_alter_table('service', schema=None) as batch_op:
            batch_op.add_column(sa.Column('button_text', sa.String(length=100), nullable=True))
            batch_op.add_column(sa.Column('subtitles', sa.Text(), nullable=True))
            batch_op.add_column(sa.Column('title', sa.String(length=255), nullable=True))

    if 'category' in existing_tables:
        with op.batch_alter_table('category', schema=None) as batch_op:
            batch_op.add_column(sa.Column('name', sa.String(length=100), nullable=True))

    if 'blog' in existing_tables:
        with op.batch_alter_table('blog', schema=None) as batch_op:
            batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
            batch_op.add_column(sa.Column('title', sa.String(length=255), nullable=True))

    if 'project' in existing_tables:
        with op.batch_alter_table('project', schema=None) as batch_op:
            batch_op.add_column(sa.Column('deliverables', sa.Text(), nullable=True))
            batch_op.add_column(sa.Column('button_text', sa.String(length=100), nullable=True))
            batch_op.add_column(sa.Column('description', sa.Text(), nullable=True))
            batch_op.add_column(sa.Column('title', sa.String(length=255), nullable=True))

    if 'banner' in existing_tables:
        with op.batch_alter_table('banner', schema=None) as batch_op:
            batch_op.add_column(sa.Column('button_text', sa.String(length=100), nullable=True))
            batch_op.add_column(sa.Column('subtitle', sa.String(length=255), nullable=True))
            batch_op.add_column(sa.Column('title', sa.String(length=255), nullable=True))

    # Заполнение старых полей
    if 'about' in existing_tables:
        op.execute("UPDATE about SET title = title_en, subtitle = subtitle_en, description1 = description1_en, description2 = description2_en")
    if 'contact' in existing_tables:
        op.execute("UPDATE contact SET address = address_en")
    if 'review' in existing_tables:
        op.execute("UPDATE review SET content = content_en, author = author_en")
    if 'service' in existing_tables:
        op.execute("UPDATE service SET title = title_en, subtitles = subtitles_en, button_text = button_text_en")
    if 'category' in existing_tables:
        op.execute("UPDATE category SET name = name_en")
    if 'blog' in existing_tables:
        op.execute("UPDATE blog SET title = title_en, description = description_en")
    if 'project' in existing_tables:
        op.execute("UPDATE project SET title = title_en, description = description_en, button_text = button_text_en, deliverables = deliverables_en")
    if 'banner' in existing_tables:
        op.execute("UPDATE banner SET title = title_en, subtitle = subtitle_en, button_text = button_text_en")

    # Удаление мультиязычных полей
    if 'about' in existing_tables:
        with op.batch_alter_table('about', schema=None) as batch_op:
            batch_op.drop_column('description2_en')
            batch_op.drop_column('description2_tk')
            batch_op.drop_column('description2_ru')
            batch_op.drop_column('description1_en')
            batch_op.drop_column('description1_tk')
            batch_op.drop_column('description1_ru')
            batch_op.drop_column('subtitle_en')
            batch_op.drop_column('subtitle_tk')
            batch_op.drop_column('subtitle_ru')
            batch_op.drop_column('title_en')
            batch_op.drop_column('title_tk')
            batch_op.drop_column('title_ru')

    if 'contact' in existing_tables:
        with op.batch_alter_table('contact', schema=None) as batch_op:
            batch_op.drop_column('address_en')
            batch_op.drop_column('address_tk')
            batch_op.drop_column('address_ru')

    if 'review' in existing_tables:
        with op.batch_alter_table('review', schema=None) as batch_op:
            batch_op.drop_column('author_en')
            batch_op.drop_column('author_tk')
            batch_op.drop_column('author_ru')
            batch_op.drop_column('content_en')
            batch_op.drop_column('content_tk')
            batch_op.drop_column('content_ru')

    if 'service' in existing_tables:
        with op.batch_alter_table('service', schema=None) as batch_op:
            batch_op.drop_column('button_text_en')
            batch_op.drop_column('button_text_tk')
            batch_op.drop_column('button_text_ru')
            batch_op.drop_column('subtitles_en')
            batch_op.drop_column('subtitles_tk')
            batch_op.drop_column('subtitles_ru')
            batch_op.drop_column('title_en')
            batch_op.drop_column('title_tk')
            batch_op.drop_column('title_ru')

    if 'category' in existing_tables:
        with op.batch_alter_table('category', schema=None) as batch_op:
            batch_op.drop_column('name_en')
            batch_op.drop_column('name_tk')
            batch_op.drop_column('name_ru')

    if 'blog' in existing_tables:
        with op.batch_alter_table('blog', schema=None) as batch_op:
            batch_op.drop_column('description_en')
            batch_op.drop_column('description_tk')
            batch_op.drop_column('description_ru')
            batch_op.drop_column('title_en')
            batch_op.drop_column('title_tk')
            batch_op.drop_column('title_ru')

    if 'project' in existing_tables:
        with op.batch_alter_table('project', schema=None) as batch_op:
            batch_op.drop_column('deliverables_en')
            batch_op.drop_column('deliverables_tk')
            batch_op.drop_column('deliverables_ru')
            batch_op.drop_column('button_text_en')
            batch_op.drop_column('button_text_tk')
            batch_op.drop_column('button_text_ru')
            batch_op.drop_column('description_en')
            batch_op.drop_column('description_tk')
            batch_op.drop_column('description_ru')
            batch_op.drop_column('title_en')
            batch_op.drop_column('title_tk')
            batch_op.drop_column('title_ru')

    if 'banner' in existing_tables:
        with op.batch_alter_table('banner', schema=None) as batch_op:
            batch_op.drop_column('button_text_en')
            batch_op.drop_column('button_text_tk')
            batch_op.drop_column('button_text_ru')
            batch_op.drop_column('subtitle_en')
            batch_op.drop_column('subtitle_tk')
            batch_op.drop_column('subtitle_ru')
            batch_op.drop_column('title_en')
            batch_op.drop_column('title_tk')
            batch_op.drop_column('title_ru')

    # Удаление таблиц
    if 'review' in existing_tables:
        op.drop_table('review')
    if 'project_categories' in existing_tables:
        op.drop_table('project_categories')
    if 'about' in existing_tables:
        op.drop_table('about')
    if 'service' in existing_tables:
        op.drop_table('service')
    if 'blog' in existing_tables:
        op.drop_table('blog')
    if 'project' in existing_tables:
        op.drop_table('project')
    if 'banner' in existing_tables:
        op.drop_table('banner')
    if 'contact' in existing_tables:
        op.drop_table('contact')
    if 'client' in existing_tables:
        op.drop_table('client')
    if 'category' in existing_tables:
        op.drop_table('category')
    if 'user' in existing_tables:
        op.drop_table('user')