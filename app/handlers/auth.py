from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from sqlalchemy import select, update
from app.database import SessionLocal
from app.models import AccessCode, Employee

router = Router()


# FSM: пользователь вводит код
class AuthFSM(StatesGroup):
    waiting_code = State()


@router.message(commands=["start"])
async def cmd_start(message: types.Message, state: FSMContext):
    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Чтобы получить доступ к сервису, введите *код доступа*.",
        parse_mode="HTML"
    )
    await state.set_state(AuthFSM.waiting_code)


@router.message(AuthFSM.waiting_code)
async def process_code(message: types.Message, state: FSMContext):
    code_input = message.text.strip()

    async with SessionLocal() as session:
        # Ищем код в базе
        result = await session.execute(
            select(AccessCode).where(AccessCode.code == code_input)
        )
        code: AccessCode | None = result.scalar()

        if not code:
            await message.answer("❌ Неверный код доступа. Попробуйте ещё раз.")
            return

        if code.used:
            await message.answer("⚠️ Этот код уже был использован.")
            return

        # Создаём сотрудника
        new_employee = Employee(
            tg_id=message.from_user.id,
            fio="Не указано",
            role=code.role,
            is_active=True
        )
        session.add(new_employee)
        await session.flush()

        # помечаем код использованным
        code.used = True
        code.used_by = new_employee.id

        await session.commit()

    await state.clear()

    # Показываем меню
    if code.role == "admin":
        await message.answer(
            "✅ Авторизация успешна!\n\n"
            "Ваш статус: <b>Администратор</b>\n"
            "Открываю панель управления…",
            parse_mode="HTML"
        )
        await show_admin_menu(message)
    else:
        await message.answer(
            "✅ Авторизация успешна!\n\n"
            "Добро пожаловать!",
            parse_mode="HTML"
        )
        await show_user_menu(message)


# Меню сотрудника
async def show_user_menu(message: types.Message):
    kb = [
        [types.KeyboardButton(text="📢 Объявления")],
        [types.KeyboardButton(text="📄 Приказы")],
        [types.KeyboardButton(text="📚 Документы")],
        [types.KeyboardButton(text="📅 Важные события")],
        [types.KeyboardButton(text="☎️ Контакты руководства")],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Главное меню:", reply_markup=keyboard)


# Меню администратора
async def show_admin_menu(message: types.Message):
    kb = [
        [types.KeyboardButton(text="📢 Объявления")],
        [types.KeyboardButton(text="📄 Приказы")],
        [types.KeyboardButton(text="📚 Документы")],
        [types.KeyboardButton(text="📅 Важные события")],
        [types.KeyboardButton(text="🆘 Срочное сообщение")],
        [types.KeyboardButton(text="🔧 Панель администратора")],
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    await message.answer("Главное меню администратора:", reply_markup=keyboard)
