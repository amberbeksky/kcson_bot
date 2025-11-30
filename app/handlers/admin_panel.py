from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from sqlalchemy import select
from app.database import SessionLocal
from app.models import Employee, Announcement, Order, Document, Event, AccessCode

from app.google_drive.uploader import upload_file_to_drive

import aiofiles
import os
from datetime import datetime

router = Router()


# ==============================
# FSM классы для разных действий
# ==============================

class AddAnnouncementFSM(StatesGroup):
    waiting_title = State()
    waiting_text = State()
    waiting_file = State()
    confirm = State()


class AddOrderFSM(StatesGroup):
    waiting_category = State()
    waiting_title = State()
    waiting_file = State()


class AddDocumentFSM(StatesGroup):
    waiting_category = State()
    waiting_title = State()
    waiting_file = State()


class AddEventFSM(StatesGroup):
    waiting_title = State()
    waiting_date = State()
    waiting_description = State()


class UrgentMsgFSM(StatesGroup):
    waiting_text = State()
    waiting_file = State()


class CreateAccessCodeFSM(StatesGroup):
    waiting_role = State()


# =====================
# Открытие панели админа
# =====================

@router.message(F.text == "🔧 Панель администратора")
async def admin_panel(message: types.Message):
    kb = InlineKeyboardBuilder()

    kb.button(text="➕ Объявление", callback_data="admin_add_announcement")
    kb.button(text="📄 Приказ", callback_data="admin_add_order")
    kb.button(text="📚 Документ", callback_data="admin_add_document")
    kb.button(text="📅 Событие", callback_data="admin_add_event")
    kb.button(text="🆘 Срочное сообщение", callback_data="admin_urgent")
    kb.button(text="👥 Список сотрудников", callback_data="admin_list_staff")
    kb.button(text="🔑 Создать код доступа", callback_data="admin_create_code")

    kb.adjust(2)

    await message.answer("🔧 <b>Панель администратора</b>", reply_markup=kb.as_markup(), parse_mode="HTML")


# =========================
# Добавление объявлений (FSM)
# =========================

@router.callback_query(F.data == "admin_add_announcement")
async def add_announcement_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("📝 Введите <b>заголовок</b> объявления:", parse_mode="HTML")
    await state.set_state(AddAnnouncementFSM.waiting_title)


@router.message(AddAnnouncementFSM.waiting_title)
async def announcement_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите <b>текст</b> объявления (или напишите 'нет'):", parse_mode="HTML")
    await state.set_state(AddAnnouncementFSM.waiting_text)


@router.message(AddAnnouncementFSM.waiting_text)
async def announcement_text(message: types.Message, state: FSMContext):
    text = None if message.text.lower() == "нет" else message.text
    await state.update_data(text=text)
    await message.answer("Прикрепите файл (или напишите 'нет'):")
    await state.set_state(AddAnnouncementFSM.waiting_file)


@router.message(AddAnnouncementFSM.waiting_file)
async def announcement_file(message: types.Message, state: FSMContext):
    data = await state.get_data()
    file_url = None

    # Если файл есть — сохраняем во временный каталог и загружаем в Drive
    if message.document:
        file_name = message.document.file_name
        file_path = f"/tmp/{file_name}"

        file = await message.bot.get_file(message.document.file_id)
        await message.bot.download_file(file.file_path, destination=file_path)

        file_url = await upload_file_to_drive(file_path, file_name)

        os.remove(file_path)

    async with SessionLocal() as session:
        new_announcement = Announcement(
            title=data["title"],
            text=data.get("text"),
            file_url=file_url,
            created_by=None
        )
        session.add(new_announcement)
        await session.commit()

    await message.answer("✅ Объявление добавлено и сохранено.")
    await state.clear()


# =========================
# Добавление приказа
# =========================

@router.callback_query(F.data == "admin_add_order")
async def add_order_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите категорию приказа:")
    await state.set_state(AddOrderFSM.waiting_category)


@router.message(AddOrderFSM.waiting_category)
async def order_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Введите заголовок приказа:")
    await state.set_state(AddOrderFSM.waiting_title)


@router.message(AddOrderFSM.waiting_title)
async def order_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Прикрепите PDF приказа:")
    await state.set_state(AddOrderFSM.waiting_file)


@router.message(AddOrderFSM.waiting_file)
async def order_file(message: types.Message, state: FSMContext):
    if not message.document:
        await message.answer("❗ Прикрепите именно файл.")
        return

    file_name = message.document.file_name
    file_path = f"/tmp/{file_name}"

    file = await message.bot.get_file(message.document.file_id)
    await message.bot.download_file(file.file_path, destination=file_path)

    url = await upload_file_to_drive(file_path, file_name)
    os.remove(file_path)

    data = await state.get_data()

    async with SessionLocal() as session:
        new_order = Order(
            category=data["category"],
            title=data["title"],
            file_url=url,
            created_by=None
        )
        session.add(new_order)
        await session.commit()

    await message.answer("✅ Приказ добавлен.")
    await state.clear()


# =========================
# Добавление документа
# =========================

@router.callback_query(F.data == "admin_add_document")
async def add_document_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите категорию документа:")
    await state.set_state(AddDocumentFSM.waiting_category)


@router.message(AddDocumentFSM.waiting_category)
async def document_category(message: types.Message, state: FSMContext):
    await state.update_data(category=message.text)
    await message.answer("Введите заголовок документа:")
    await state.set_state(AddDocumentFSM.waiting_title)


@router.message(AddDocumentFSM.waiting_title)
async def document_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Прикрепите документ (PDF/Word):")
    await state.set_state(AddDocumentFSM.waiting_file)


@router.message(AddDocumentFSM.waiting_file)
async def document_file(message: types.Message, state: FSMContext):
    if not message.document:
        await message.answer("❗ Прикрепите файл.")
        return

    file_name = message.document.file_name
    file_path = f"/tmp/{file_name}"

    file = await message.bot.get_file(message.document.file_id)
    await message.bot.download_file(file.file_path, destination=file_path)

    url = await upload_file_to_drive(file_path, file_name)
    os.remove(file_path)

    data = await state.get_data()

    async with SessionLocal() as session:
        new_doc = Document(
            category=data["category"],
            title=data["title"],
            file_url=url,
            created_by=None
        )
        session.add(new_doc)
        await session.commit()

    await message.answer("✅ Документ добавлен.")
    await state.clear()


# =========================
# Добавление события
# =========================

@router.callback_query(F.data == "admin_add_event")
async def add_event_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название события:")
    await state.set_state(AddEventFSM.waiting_title)


@router.message(AddEventFSM.waiting_title)
async def event_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите дату события формата YYYY-MM-DD:")
    await state.set_state(AddEventFSM.waiting_date)


@router.message(AddEventFSM.waiting_date)
async def event_date(message: types.Message, state: FSMContext):
    try:
        dt = datetime.strptime(message.text, "%Y-%m-%d")
    except:
        await message.answer("❗ Формат неправильный. Введите дату YYYY-MM-DD.")
        return

    await state.update_data(date=dt)
    await message.answer("Введите описание события (или 'нет'):")
    await state.set_state(AddEventFSM.waiting_description)


@router.message(AddEventFSM.waiting_description)
async def event_description(message: types.Message, state: FSMContext):
    desc = None if message.text.lower() == "нет" else message.text
    data = await state.get_data()

    async with SessionLocal() as session:
        new_event = Event(
            title=data["title"],
            date=data["date"],
            description=desc,
            created_by=None
        )
        session.add(new_event)
        await session.commit()

    await message.answer("✅ Событие добавлено.")
    await state.clear()


# =========================
# Срочное сообщение
# =========================

@router.callback_query(F.data == "admin_urgent")
async def urgent_start(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите текст срочного сообщения:")
    await state.set_state(UrgentMsgFSM.waiting_text)


@router.message(UrgentMsgFSM.waiting_text)
async def urgent_text(message: types.Message, state: FSMContext):
    await state.update_data(text=message.text)
    await message.answer("Прикрепите файл (или 'нет'):")
    await state.set_state(UrgentMsgFSM.waiting_file)


@router.message(UrgentMsgFSM.waiting_file)
async def urgent_file(message: types.Message, state: FSMContext):
    data = await state.get_data()

    url = None

    if message.document:
        file_name = message.document.file_name
        file_path = f"/tmp/{file_name}"

        file = await message.bot.get_file(message.document.file_id)
        await message.bot.download_file(file.file_path, destination=file_path)

        url = await upload_file_to_drive(file_path, file_name)
        os.remove(file_path)

    # Рассылка всем сотрудникам
    async with SessionLocal() as session:
        result = await session.execute(select(Employee).where(Employee.is_active == True))
        employees = result.scalars().all()

    for emp in employees:
        try:
            if url:
                await message.bot.send_message(emp.tg_id, f"🆘 Срочное сообщение:\n\n{data['text']}")
                await message.bot.send_message(emp.tg_id, url)
            else:
                await message.bot.send_message(emp.tg_id, f"🆘 Срочное сообщение:\n\n{data['text']}")
        except:
            pass

    await message.answer("✅ Срочное сообщение отправлено.")
    await state.clear()


# =========================
# Список сотрудников
# =========================

@router.callback_query(F.data == "admin_list_staff")
async def list_staff(callback: types.CallbackQuery):
    async with SessionLocal() as session:
        result = await session.execute(select(Employee))
        employees = result.scalars().all()

    text = "👥 <b>Сотрудники:</b>\n\n"
    for e in employees:
        text += f"• {e.fio} — {e.role} — {'активен' if e.is_active else 'неактивен'}\n"

    await callback.message.answer(text, parse_mode="HTML")


# =========================
# Создание кода доступа
# =========================

@router.callback_query(F.data == "admin_create_code")
async def create_code_start(callback: types.CallbackQuery, state: FSMContext):
    kb = InlineKeyboardBuilder()
    kb.button(text="Администратор", callback_data="gen_role_admin")
    kb.button(text="Сотрудник", callback_data="gen_role_staff")
    kb.adjust(2)

    await callback.message.answer("Выберите роль:", reply_markup=kb.as_markup())
    await state.set_state(CreateAccessCodeFSM.waiting_role)


@router.callback_query(CreateAccessCodeFSM.waiting_role, F.data.startswith("gen_role_"))
async def generate_code(callback: types.CallbackQuery, state: FSMContext):
    role = callback.data.replace("gen_role_", "")

    import random
    import string

    new_code = "KCS-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

    async with SessionLocal() as session:
        code = AccessCode(code=new_code, role=role)
        session.add(code)
        await session.commit()

    await state.clear()

    await callback.message.answer(
        f"🔑 Новый код доступа создан:\n\n"
        f"<code>{new_code}</code>\n\n"
        f"Роль: <b>{role}</b>",
        parse_mode="HTML"
    )
