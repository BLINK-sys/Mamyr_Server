"""Seed the database with initial data."""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import text
from app.database import SessionLocal, engine, Base
from app.models import Location, Category, Dish, DishAddon, DishLocation, Banner, Staff, FooterSettings, FooterContact, FooterSchedule
from app.auth import hash_password

def seed():
    # Drop ALL tables (including old ones from previous Flask backend) with CASCADE
    print("Dropping all tables with CASCADE...")
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    # Locations
    loc1 = Location(name="Mamyr Центр", address="ул. Абая 150, Алматы")
    loc2 = Location(name="Mamyr Юг", address="мкр. Мамыр-4, д.12")
    db.add_all([loc1, loc2])
    db.flush()

    # Categories
    cats = [
        Category(title="Супы", order=1, active=True),
        Category(title="Горячие блюда", order=2, active=True),
        Category(title="Шашлык и гриль", order=3, active=True),
        Category(title="Выпечка", order=4, active=True),
        Category(title="Салаты", order=5, active=True),
        Category(title="Напитки", order=6, active=True),
    ]
    db.add_all(cats)
    db.flush()

    # Staff
    staff_data = [
        ("Алмат", "almat@mamyr.kz", "owner123", "owner", loc1.id),
        ("Динара", "dinara@mamyr.kz", "admin123", "admin", loc1.id),
        ("Бауыржан", "baurzhan@mamyr.kz", "cook123", "cook", loc1.id),
        ("Айгуль", "aigul@mamyr.kz", "cook123", "cook", loc2.id),
        ("Марат", "marat@mamyr.kz", "rec123", "reception", loc1.id),
        ("Жанна", "zhanna@mamyr.kz", "rec123", "reception", loc2.id),
    ]
    for name, email, pwd, role, lid in staff_data:
        db.add(Staff(name=name, email=email, password_hash=hash_password(pwd), role=role, location_id=lid))
    db.flush()

    # Dishes
    dishes_data = [
        ("Шорпа", "Наваристый бульон с бараниной и овощами", "Баранина, картофель, морковь, лук, зелень", 990, "400 г", cats[0].id, [loc1.id, loc2.id], [("Лепёшка", 150), ("Сметана", 100)]),
        ("Лагман", "Густой суп с домашней лапшой и говядиной", "Говядина, лапша, перец, помидоры, лук", 1100, "450 г", cats[0].id, [loc1.id, loc2.id], [("Острый соус", 50)]),
        ("Борщ", "Классический с говядиной и сметаной", "Говядина, свёкла, капуста, картофель, сметана", 850, "400 г", cats[0].id, [loc1.id], [("Сметана доп.", 100), ("Чеснок", 50)]),
        ("Плов", "Узбекский плов с бараниной и зирой", "Рис, баранина, морковь, лук, зира, барбарис", 1500, "400 г", cats[1].id, [loc1.id, loc2.id], [("Салат к плову", 200)]),
        ("Манты", "Домашние с сочной начинкой из баранины", "Тесто, баранина, лук, специи", 1300, "350 г", cats[1].id, [loc1.id, loc2.id], [("Сметана", 100), ("Острый соус", 50)]),
        ("Пельмени", "По-домашнему с маслом и зеленью", "Тесто, говядина, свинина, лук", 1200, "300 г", cats[1].id, [loc1.id], []),
        ("Котлеты", "Куриные с картофельным пюре", "Курица, хлеб, лук, картофель, молоко", 1100, "350 г", cats[1].id, [loc1.id, loc2.id], []),
        ("Шашлык из баранины", "На углях с луком и зеленью", "Баранина, лук, зелень, специи", 1650, "300 г", cats[2].id, [loc1.id, loc2.id], [("Лаваш", 100), ("Соус ткемали", 150)]),
        ("Люля-кебаб", "Из рубленой баранины на шампурах", "Баранина, курдюк, лук, специи", 1200, "250 г", cats[2].id, [loc1.id], [("Лаваш", 100)]),
        ("Самса с мясом", "Слоёная с сочной начинкой", "Слоёное тесто, баранина, лук", 650, "200 г", cats[3].id, [loc1.id, loc2.id], []),
        ("Блины", "Золотистые со сметаной", "Мука, молоко, яйца, сметана", 500, "250 г", cats[3].id, [loc1.id, loc2.id], [("Мёд", 100), ("Сгущёнка", 100)]),
        ("Салат свежий", "Помидоры, огурцы, лук, зелень", "Помидоры, огурцы, лук, зелень, масло", 600, "250 г", cats[4].id, [loc1.id, loc2.id], []),
        ("Чай зелёный", "Чайник ароматного зелёного чая", "Зелёный чай", 400, "500 мл", cats[5].id, [loc1.id, loc2.id], [("Лимон", 50)]),
        ("Айран", "Домашний кисломолочный напиток", "Кисломолочная основа, соль", 350, "300 мл", cats[5].id, [loc1.id, loc2.id], []),
        ("Компот", "Из свежих ягод и фруктов", "Ягоды, фрукты, сахар", 300, "300 мл", cats[5].id, [loc1.id, loc2.id], []),
    ]
    for name, desc, ingredients, price, weight, cat_id, loc_ids, addons in dishes_data:
        dish = Dish(name=name, desc=desc, ingredients=ingredients, price=price, weight=weight, category_id=cat_id)
        db.add(dish)
        db.flush()
        for lid in loc_ids:
            db.add(DishLocation(dish_id=dish.id, location_id=lid))
        for aname, aprice in addons:
            db.add(DishAddon(dish_id=dish.id, name=aname, price=aprice))

    # Banners
    db.add(Banner(title="Mamyr КАФЕ", subtitle="Настоящая восточная кухня с душой", order=1))
    db.add(Banner(title="Свежие блюда", subtitle="Готовим из свежих продуктов каждый день", order=2))

    # Footer
    db.add(FooterSettings(description="Настоящая восточная кухня с душой. Готовим по традиционным рецептам из свежих продуктов каждый день."))
    db.add(FooterContact(icon="Phone", text="+7 (777) 123-45-67", order=1))
    db.add(FooterContact(icon="Mail", text="info@mamyr-cafe.kz", order=2))
    db.add(FooterContact(icon="MapPin", text="Доставка по всему городу", order=3))
    db.add(FooterSchedule(text="Пн–Вс: 10:00 – 22:00", order=1))
    db.add(FooterSchedule(text="Доставка бесплатно от 5000 тг", order=2, text_color="hsl(42, 70%, 55%)"))

    db.commit()
    db.close()
    print("Database seeded successfully!")


if __name__ == "__main__":
    seed()
