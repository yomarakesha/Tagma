"""
seed.py — скрипт для наполнения базы тестовыми данными.
Запуск: python seed.py
"""
from app import create_app, db
from app.models.banner import Banner
from app.models.category import Category
from app.models.client import Client
from app.models.partner import Partner
from app.models.project import Project
from app.models.blog import Blog
from app.models.service import Service
from app.models.review import Review
from app.models.contact import Contact
from app.models.about import About, AboutItem
from app.models.portfolio_pdf import PortfolioPDF
from datetime import date, datetime

app = create_app()

with app.app_context():
    # Синхронизируем схему (добавляем недостающие колонки в существующих таблицах)
    from sqlalchemy import inspect, text
    inspector = inspect(db.engine)

    existing_cols = [c['name'] for c in inspector.get_columns('portfolio_pdf')]
    if 'created_at' not in existing_cols:
        db.session.execute(text("ALTER TABLE portfolio_pdf ADD COLUMN created_at DATETIME"))
        db.session.commit()
        print("Добавлена колонка created_at в portfolio_pdf")

    # ─── Очистка старых данных ──────────────────────────────────────────
    print("Очищаем базу данных...")
    db.session.query(Review).delete()
    db.session.query(PortfolioPDF).delete()
    db.session.query(AboutItem).delete()
    db.session.query(About).delete()
    db.session.query(Contact).delete()
    db.session.query(Blog).delete()
    db.session.query(Service).delete()
    db.session.query(Project).delete()
    db.session.query(Partner).delete()
    db.session.query(Client).delete()
    db.session.query(Category).delete()
    db.session.query(Banner).delete()
    db.session.commit()

    # ─── Категории ──────────────────────────────────────────────────────
    print("Создаём категории...")
    cat_branding = Category(
        title_ru="Брендинг",
        title_en="Branding",
        slug="branding",
        link="/works/branding",
        bg_color="#1a1a1a",
        description_ru="Разработка фирменного стиля и визуальной идентификации",
        description_en="Brand identity and visual style development",
    )
    cat_web = Category(
        title_ru="Веб-дизайн",
        title_en="Web Design",
        slug="web-design",
        link="/works/web",
        bg_color="#2d2d2d",
        description_ru="Проектирование интерфейсов и UX/UI дизайн",
        description_en="Interface design and UX/UI",
    )
    cat_motion = Category(
        title_ru="Моушн",
        title_en="Motion",
        slug="motion",
        link="/works/motion",
        bg_color="#3a3a3a",
        description_ru="Анимация и моушн-дизайн для брендов",
        description_en="Animation and motion design for brands",
    )
    db.session.add_all([cat_branding, cat_web, cat_motion])
    db.session.commit()

    # ─── Баннеры ────────────────────────────────────────────────────────
    print("Создаём баннеры...")
    banners = [
        Banner(
            title_ru="Мы создаём бренды которые запоминаются",
            title_en="We create brands that are remembered",
            subtitle_ru="Дизайн-студия полного цикла",
            subtitle_en="Full-cycle design studio",
            image_url="https://placehold.co/1920x1080/1a1a1a/ffffff?text=Banner+1",
            logo_url="https://placehold.co/200x60/ffffff/1a1a1a?text=TAGMA",
            button_text_ru="Смотреть работы",
            button_text_en="View works",
            button_link="/works",
        ),
        Banner(
            title_ru="Брендинг, который работает на вас",
            title_en="Branding that works for you",
            subtitle_ru="От идеи до готового продукта",
            subtitle_en="From idea to final product",
            image_url="https://placehold.co/1920x1080/2d2d2d/ffffff?text=Banner+2",
            logo_url="https://placehold.co/200x60/ffffff/2d2d2d?text=TAGMA",
            button_text_ru="Связаться с нами",
            button_text_en="Contact us",
            button_link="/contact",
        ),
    ]
    db.session.add_all(banners)
    db.session.commit()

    # ─── Клиенты ────────────────────────────────────────────────────────
    print("Создаём клиентов...")
    clients = [
        Client(
            logo_url="https://placehold.co/160x60/ffffff/333333?text=Client+1",
            default_logo="https://placehold.co/160x60/cccccc/333333?text=Client+1",
        ),
        Client(
            logo_url="https://placehold.co/160x60/ffffff/333333?text=Client+2",
            default_logo="https://placehold.co/160x60/cccccc/333333?text=Client+2",
        ),
        Client(
            logo_url="https://placehold.co/160x60/ffffff/333333?text=Client+3",
            default_logo="https://placehold.co/160x60/cccccc/333333?text=Client+3",
        ),
        Client(
            logo_url="https://placehold.co/160x60/ffffff/333333?text=Client+4",
            default_logo="https://placehold.co/160x60/cccccc/333333?text=Client+4",
        ),
    ]
    db.session.add_all(clients)
    db.session.commit()

    # ─── Партнёры ───────────────────────────────────────────────────────
    print("Создаём партнёров...")
    partners = [
        Partner(
            name_ru="Арт Студия",
            name_en="Art Studio",
            logo_url="https://placehold.co/160x60/ffffff/333333?text=ArtStudio",
            description_ru="Партнёр по производству печатной продукции",
            description_en="Print production partner",
        ),
        Partner(
            name_ru="Медиа Групп",
            name_en="Media Group",
            logo_url="https://placehold.co/160x60/ffffff/333333?text=MediaGroup",
            description_ru="Медиа-партнёр и дистрибьютор контента",
            description_en="Media partner and content distributor",
        ),
    ]
    db.session.add_all(partners)
    db.session.commit()

    # ─── Проекты ────────────────────────────────────────────────────────
    print("Создаём проекты...")
    project1 = Project(
        title_ru="Ребрендинг кофейни «Зерно»",
        title_en="Rebranding of 'Zerno' coffee shop",
        description_ru="Полный ребрендинг локальной кофейни: логотип, фирменный стиль, упаковка",
        description_en="Full rebranding of a local coffee shop: logo, brand identity, packaging",
        content_ru="<p>Проект включал разработку нового логотипа, фирменного стиля и упаковки для кофейни «Зерно». Мы создали тёплый и уютный визуальный образ, отражающий атмосферу заведения.</p>",
        content_en="<p>The project included developing a new logo, brand identity, and packaging for the Zerno coffee shop. We created a warm and cozy visual image that reflects the atmosphere of the establishment.</p>",
        tags_ru=["Брендинг", "Логотип", "Упаковка"],
        tags_en=["Branding", "Logo", "Packaging"],
        main_image="https://placehold.co/800x600/c8a882/ffffff?text=Zerno+Coffee",
        images=[
            "https://placehold.co/800x600/c8a882/ffffff?text=Zerno+1",
            "https://placehold.co/800x600/c8a882/ffffff?text=Zerno+2",
        ],
        bg_color="#c8a882",
        type="branding",
    )
    project1.categories = [cat_branding]

    project2 = Project(
        title_ru="Сайт для IT-компании Nexus",
        title_en="Website for Nexus IT company",
        description_ru="Разработка дизайна корпоративного сайта с современным UI/UX",
        description_en="Corporate website design with modern UI/UX",
        content_ru="<p>Мы разработали современный корпоративный сайт для IT-компании Nexus. Акцент сделан на читаемость, скорость и профессиональный имидж.</p>",
        content_en="<p>We designed a modern corporate website for Nexus IT company. The focus was on readability, speed, and a professional image.</p>",
        tags_ru=["Веб-дизайн", "UI/UX", "Корпоративный"],
        tags_en=["Web Design", "UI/UX", "Corporate"],
        main_image="https://placehold.co/800x600/1e3a5f/ffffff?text=Nexus+Web",
        images=[
            "https://placehold.co/800x600/1e3a5f/ffffff?text=Nexus+1",
            "https://placehold.co/800x600/1e3a5f/ffffff?text=Nexus+2",
        ],
        bg_color="#1e3a5f",
        type="others",
    )
    project2.categories = [cat_web]

    project3 = Project(
        title_ru="Идентификация бренда «Nomad»",
        title_en="Brand identity for 'Nomad'",
        description_ru="Создание визуальной идентичности для fashion-бренда Nomad",
        description_en="Visual identity creation for the Nomad fashion brand",
        content_ru="<p>Для fashion-бренда Nomad мы разработали полную визуальную идентификацию: от логотипа до коммуникационных материалов.</p>",
        content_en="<p>For the Nomad fashion brand, we developed a complete visual identity: from the logo to communication materials.</p>",
        tags_ru=["Брендинг", "Fashion", "Идентификация"],
        tags_en=["Branding", "Fashion", "Identity"],
        main_image="https://placehold.co/800x600/2c2c2c/f0e6d3?text=Nomad",
        images=[
            "https://placehold.co/800x600/2c2c2c/f0e6d3?text=Nomad+1",
        ],
        bg_color="#2c2c2c",
        type="branding",
    )
    project3.categories = [cat_branding, cat_motion]

    db.session.add_all([project1, project2, project3])
    db.session.commit()

    # ─── Отзывы ─────────────────────────────────────────────────────────
    print("Создаём отзывы...")
    reviews = [
        Review(
            content_ru="Tagma полностью преобразила облик нашей кофейни. Клиенты замечают изменения и оставляют много положительных отзывов!",
            content_en="Tagma completely transformed the look of our coffee shop. Customers notice the changes and leave many positive reviews!",
            content_tk="Tagma biziň kofe dükanymyzyň keşbini doly üýtgetdi.",
            author_ru="Анна Петрова, владелец «Зерно»",
            author_en="Anna Petrova, owner of 'Zerno'",
            author_tk="Anna Petrova, 'Zerno' eýesi",
            project_id=project1.id,
        ),
        Review(
            content_ru="Профессиональный подход и отличный результат. Наш сайт теперь выглядит на уровне международных компаний.",
            content_en="Professional approach and excellent result. Our website now looks like an international company.",
            content_tk="Hünärmen çemeleşme we ajaýyp netije.",
            author_ru="Дмитрий Соколов, CEO Nexus",
            author_en="Dmitry Sokolov, CEO Nexus",
            author_tk="Dmitry Sokolov, Nexus baş direktory",
            project_id=project2.id,
        ),
    ]
    db.session.add_all(reviews)
    db.session.commit()

    # ─── Блоги ──────────────────────────────────────────────────────────
    print("Создаём блоги...")
    blogs = [
        Blog(
            title_ru="Почему брендинг важен для малого бизнеса",
            title_en="Why branding matters for small business",
            description_ru="Разбираем, как правильный визуальный стиль помогает малому бизнесу конкурировать с крупными игроками рынка.",
            description_en="We analyze how a proper visual style helps small businesses compete with major market players.",
            image_url="https://placehold.co/800x450/f5f0eb/333333?text=Blog+1",
            date=date(2024, 11, 15),
            read_time="5 min read",
            slug="why-branding-matters",
            tags=["branding", "small business", "design"],
        ),
        Blog(
            title_ru="Тренды веб-дизайна 2025",
            title_en="Web design trends 2025",
            description_ru="Обзор главных тенденций в веб-дизайне: минимализм, AI-генерация и интерактивность.",
            description_en="Overview of the main trends in web design: minimalism, AI generation, and interactivity.",
            image_url="https://placehold.co/800x450/e8f0fe/333333?text=Blog+2",
            date=date(2025, 1, 10),
            read_time="7 min read",
            slug="web-design-trends-2025",
            tags=["web design", "trends", "2025"],
        ),
        Blog(
            title_ru="Цвет в брендинге: психология и практика",
            title_en="Color in branding: psychology and practice",
            description_ru="Как правильно выбрать цветовую палитру бренда и избежать типичных ошибок.",
            description_en="How to choose the right brand color palette and avoid common mistakes.",
            image_url="https://placehold.co/800x450/fde8e8/333333?text=Blog+3",
            date=date(2025, 2, 20),
            read_time="6 min read",
            slug="color-in-branding",
            tags=["color", "branding", "psychology"],
        ),
    ]
    db.session.add_all(blogs)
    db.session.commit()

    # ─── Услуги ─────────────────────────────────────────────────────────
    print("Создаём услуги...")
    services = [
        Service(
            content_ru="<h3>Брендинг</h3><p>Создаём уникальный визуальный образ вашего бренда: логотип, фирменный стиль, брендбук и все коммуникационные материалы.</p>",
            content_en="<h3>Branding</h3><p>We create a unique visual image for your brand: logo, brand identity, brand book, and all communication materials.</p>",
            category_id=cat_branding.id,
        ),
        Service(
            content_ru="<h3>Веб-дизайн</h3><p>Проектируем интерфейсы сайтов и приложений с фокусом на пользовательский опыт и конверсию.</p>",
            content_en="<h3>Web Design</h3><p>We design website and application interfaces with a focus on user experience and conversion.</p>",
            category_id=cat_web.id,
        ),
        Service(
            content_ru="<h3>Моушн-дизайн</h3><p>Создаём анимированные ролики, интро для брендов, анимацию логотипов и рекламные материалы.</p>",
            content_en="<h3>Motion Design</h3><p>We create animated videos, brand intros, logo animations, and advertising materials.</p>",
            category_id=cat_motion.id,
        ),
    ]
    db.session.add_all(services)
    db.session.commit()

    # ─── Контакты ───────────────────────────────────────────────────────
    print("Создаём контакты...")
    contact = Contact(
        phone="+7 (999) 123-45-67",
        email="hello@tagma.studio",
        address_ru="г. Ашхабад, ул. Горгуд, 12",
        address_tk="Aşgabat şäheri, Gorkut köç., 12",
        address_en="Ashgabat, Gorkut St., 12",
        social_media='{"instagram": "https://instagram.com/tagma.studio", "telegram": "https://t.me/tagma_studio"}',
    )
    db.session.add(contact)
    db.session.commit()

    # ─── О компании ─────────────────────────────────────────────────────
    print("Создаём раздел 'О нас'...")
    about = About(
        title_ru="Мы — Tagma",
        title_en="We are Tagma",
        description_ru="Дизайн-студия полного цикла, специализирующаяся на брендинге, веб-дизайне и моушн-дизайне. Мы создаём визуальные истории, которые работают.",
        description_en="A full-cycle design studio specializing in branding, web design, and motion design. We create visual stories that work.",
    )
    db.session.add(about)
    db.session.commit()

    about_items = [
        AboutItem(
            about_id=about.id,
            title_ru="Наш подход",
            title_en="Our approach",
            description_ru="Мы начинаем каждый проект с глубокого погружения в бизнес клиента. Только понимая цели и аудиторию, мы приступаем к созданию визуала.",
            description_en="We start each project with a deep dive into the client's business. Only by understanding the goals and audience do we begin creating visuals.",
            background_image_url="https://placehold.co/1200x800/1a1a1a/ffffff?text=Our+Approach",
            button_text_ru="Узнать больше",
            button_text_en="Learn more",
            button_link="/about",
            color="#1a1a1a",
            type="approach",
            categories=[cat_branding, cat_web],
        ),
        AboutItem(
            about_id=about.id,
            title_ru="Наши ценности",
            title_en="Our values",
            description_ru="Честность, качество и партнёрство — три кита, на которых строится наша работа с каждым клиентом.",
            description_en="Honesty, quality, and partnership — three pillars on which we build our work with every client.",
            background_image_url="https://placehold.co/1200x800/2d2d2d/ffffff?text=Our+Values",
            button_text_ru="О студии",
            button_text_en="About studio",
            button_link="/about",
            color="#2d2d2d",
            type="values",
        ),
    ]
    db.session.add_all(about_items)
    db.session.commit()

    # ─── Portfolio PDF ───────────────────────────────────────────────────
    print("Создаём portfolio PDF...")
    pdf = PortfolioPDF(pdf_file="portfolio/tagma_portfolio_2025.pdf")
    db.session.add(pdf)
    db.session.commit()

    # ─── Итог ───────────────────────────────────────────────────────────
    print("\nОК: База данных успешно заполнена!")
    print(f"   Баннеры:    {Banner.query.count()}")
    print(f"   Категории:  {Category.query.count()}")
    print(f"   Клиенты:    {Client.query.count()}")
    print(f"   Партнёры:   {Partner.query.count()}")
    print(f"   Проекты:    {Project.query.count()}")
    print(f"   Блоги:      {Blog.query.count()}")
    print(f"   Услуги:     {Service.query.count()}")
    print(f"   Отзывы:     {Review.query.count()}")
    print(f"   Контакт:    {Contact.query.count()}")
    print(f"   О нас:      {About.query.count()}")
    print(f"   PDF:        {PortfolioPDF.query.count()}")
    print("\nЗапусти бэкенд и проверь эндпоинты:")
    print("  http://localhost:5000/api/banners")
    print("  http://localhost:5000/api/categories")
    print("  http://localhost:5000/api/clients")
    print("  http://localhost:5000/api/partners")
    print("  http://localhost:5000/api/projects")
    print("  http://localhost:5000/api/blog/")
    print("  http://localhost:5000/api/services")
    print("  http://localhost:5000/api/reviews")
    print("  http://localhost:5000/api/contact")
    print("  http://localhost:5000/api/about")
    print("  http://localhost:5000/api/portfolio_pdf")
    print("\nДля проверки языков добавь ?lang=ru или ?lang=en")
