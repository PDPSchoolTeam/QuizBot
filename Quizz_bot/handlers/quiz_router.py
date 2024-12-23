from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
from button import get_main_menu_buttons, get_quiz_menu_buttons
from models import User, QuizResult

router = Router()

quiz_categories = {
    "Programming": [
        {
            "question": "Python dasturlash tilida o'zgaruvchi e'lon qilish uchun qaysi kalit so'z ishlatiladi?",
            "options": ["var", "let", "const", "Hech qanday kalit so'z kerak emas"],
            "correct_answer": "Hech qanday kalit so'z kerak emas",
            "explanation": "Python'da o'zgaruvchilarni e'lon qilish uchun maxsus kalit so'z kerak emas. To'g'ridan-to'g'ri qiymat berish kifoya: x = 5"
        },
        {
            "question": "Python'da ro'yxat (list) qaysi qavslar bilan yaratiladi?",
            "options": ["()", "[]", "{}", "<>"],
            "correct_answer": "[]",
            "explanation": "Python'da ro'yxatlar kvadrat qavslar [] bilan yaratiladi. Masalan: my_list = [1, 2, 3]"
        },
        {
            "question": "Python'da izohlar qaysi belgi bilan boshlanadi?",
            "options": ["//", "#", "/*", "--"],
            "correct_answer": "#",
            "explanation": "Python'da bir qatorli izohlar # belgisi bilan boshlanadi"
        },
        {
            "question": "Python'da ko'paytirish amali qanday bajariladi?",
            "options": ["**", "*", "+", "-"],
            "correct_answer": "*",
            "explanation": "Python'da ko'paytirish amali * belgisi yordamida bajariladi"
        },
        {
            "question": "Python'da funksiya qanday e'lon qilinadi?",
            "options": ["function", "func", "def", "lambda"],
            "correct_answer": "def",
            "explanation": "Python'da funksiya def kalit so'zi yordamida e'lon qilinadi. Masalan: def my_function():"
        }
    ],
    "Algebra": [
        {
            "question": "7 + 5 nechiga teng?",
            "options": ["10", "11", "12", "13"],
            "correct_answer": "12",
            "explanation": "7 bilan 5 ni qo'shsak, 12 bo'ladi."
        },
        {
            "question": "15 - 9 = ?",
            "options": ["6", "5", "7", "8"],
            "correct_answer": "6",
            "explanation": "15 - 9 natijasi 6."
        },
        {
            "question": "6 * 4 = ?",
            "options": ["20", "24", "22", "26"],
            "correct_answer": "24",
            "explanation": "6 x 4 = 24."
        },
        {
            "question": "20 / 5 = ?",
            "options": ["2", "3", "4", "5"],
            "correct_answer": "4",
            "explanation": "20 / 5 = 4."
        },
        {
            "question": "12 - 8 = ?",
            "options": ["2", "4", "6", "8"],
            "correct_answer": "4",
            "explanation": "12 - 8 = 4."
        },
    ]
}

@router.message(lambda message: message.text == "↩️ Back")
async def back_to_main_menu(message: types.Message, state: FSMContext):
    await message.answer(
        "Asosiy menyu:",
        reply_markup=get_main_menu_buttons()
    )

class QuizStates(StatesGroup):
    selecting_category = State()
    waiting_for_answer = State()
    waiting_for_next_question = State()




# Start command handler
@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await message.answer(
        "Assalomu alaykum! Quiz botga xush kelibsiz 😊\n"
        "Quizz boshlash uchun '📚 Quizzes' tugmasini bosing 🔘\n"
        "Yordam uchun 'ℹ️ Help' tugmasini bosing ⬅️\n",
        reply_markup=get_main_menu_buttons(

        )
    )
    await state.clear()

# Points command handler
@router.message(Command("points"))
async def points_command(message: types.Message, state: FSMContext):
    user = await User.get_or_none(telegram_id=message.from_user.id)
    if user and user.score > 0:
        await message.answer(f"Sizning ballaringiz: {user.score} ")
    else:
        await message.answer("Siz hali savol yechmadingiz. Viktorinani boshlash uchun '📚 Quizzes' ni tanlang.")

# Main menu button handlers
@router.message(lambda message: message.text == "📚 Quizzes")
async def show_quiz_menu(message: types.Message):
    await message.answer(
        "Quizzes menyusi:",
        reply_markup=get_quiz_menu_buttons()
    )

@router.message(lambda message: message.text == "🏆 Points")
async def show_points(message: types.Message, state: FSMContext):
    user = await User.get_or_none(telegram_id=message.from_user.id)
    if user and user.score > 0:
        await message.answer(f"Sizning ballaringiz: {user.score} 🏆 ")
    else:
        await message.answer("Siz hali savol yechmadingiz. Viktorinani boshlash uchun '📚 Quizzes' ni tanlang.")

@router.message(lambda message: message.text == "ℹ️ Help")
async def show_help(message: types.Message):
    help_text = """
 Quiz Bot yordamchisi:

1.  Viktorinani boshlash uchun "📚 Quizzes" tugmasini bosing
2.  Kategoriyani tanlang ✅
3.  Savollarga javob bering ⬅️
4.  Ballaringizni ko'rish uchun "Points" tugmasini bosing 

Omad! 
    """
    await message.answer(help_text)

@router.message(lambda message: message.text == "🎯 Start Quiz")
async def start_quiz(message: types.Message, state: FSMContext):
    # Merge categories into a single dictionary
    all_categories = {**quiz_categories}

    # Create keyboard with a single menu for all categories
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=cat)] for cat in all_categories.keys()],
        resize_keyboard=True
    )

    await message.answer(
        "Kategoriyani tanlang:",
        reply_markup=keyboard
    )
    await state.set_state(QuizStates.selecting_category)


@router.message(QuizStates.selecting_category)
async def handle_category_selection(message: types.Message, state: FSMContext):
    selected_category = message.text.strip()

    # Merge categories dynamically
    all_categories = {**quiz_categories}

    # Validate the selected category
    if selected_category not in all_categories:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=cat)] for cat in all_categories.keys()],
            resize_keyboard=True
        )
        await message.answer("Iltimos, quyidagi kategoriyalardan birini tanlang:", reply_markup=keyboard)
        return



    # Save selected category and questions
    questions = all_categories[selected_category]

    await state.update_data(category=selected_category, questions=questions, current_question=0, score=0)

    # Get first question
    current_question = questions[0]

    # Create options keyboard
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=option)] for option in current_question["options"]],
        resize_keyboard=True
    )

    # Send the first question
    await message.answer(
        f"Savol: {current_question['question']}",
        reply_markup=keyboard
    )
    await state.set_state(QuizStates.waiting_for_answer)


@router.message(lambda message: message.text == "📊 Leaderboard")
async def show_leaderboard(message: types.Message, state: FSMContext):
    data = await state.get_data()
    current_score = data.get("score", 0)

    leaderboard = [
        ("Bot Master 👑", 100),
        ("Quiz Pro 🤵", 75),
        ("Challenger 🙎‍♂️", 50),
        ("YOU 🤖", current_score)
    ]

    leaderboard_text = "TOP NATIJALAR:\n\n"
    for player, score in leaderboard:
        leaderboard_text += f"{player}: {score} ball\n"

    await message.answer(leaderboard_text)

@router.message(lambda message: message.text == "📝 My Progress")
async def show_progress(message: types.Message, state: FSMContext):
    # Get user from database
    user = await User.get_or_none(telegram_id=message.from_user.id)
    if not user:
        await message.answer("Siz hali hech qanday quiz yechmagansiz.")
        return

    # Get latest quiz result
    latest_result = await QuizResult.filter(user=user).order_by('-completed_at').first()
    if not latest_result:
        await message.answer("Siz hali hech qanday quiz yechmagansiz.")
        return

    progress_text = "SIZNING NATIJALARINGIZ:\n\n"
    progress_text += f"Umumiy ball 📈: {user.score} \n"
    progress_text += f"Yechilgan savollar 🧾: {latest_result.questions_total} \n"
    progress_text += f"To'g'ri javoblar 🗂: {latest_result.questions_correct} \n"

    if latest_result.questions_total > 0:
        accuracy = (latest_result.questions_correct / latest_result.questions_total) * 100
        progress_text += f"Aniqlik darajasi📌: {accuracy:.1f}% "

    await message.answer(progress_text)

@router.message(lambda message: message.text == "↩️ Back")
async def back_to_main_menu(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    data = await state.get_data()
    score = data.get("score", 0)

    if current_state == QuizStates.waiting_for_answer:
        await message.answer(
            "Quiz bekor qilindi. Asosiy menyu:",
            reply_markup=get_main_menu_buttons()
        )
    else:
        await message.answer(
            "Asosiy menyu:",
            reply_markup=get_main_menu_buttons()
        )

    await state.clear()
    if score > 0:
        await state.update_data(score=score)

# Category selection handler
@router.message(QuizStates.selecting_category)
async def handle_category_selection(message: types.Message, state: FSMContext):
    if message.text not in quiz_categories:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=cat)] for cat in quiz_categories],
            resize_keyboard=True
        )
        await message.answer("Iltimos, quyidagi kategoriyalardan birini tanlang:", reply_markup=keyboard)
        return

    # Save selected category
    await state.update_data(category=message.text, current_question=0, score=0)
    data = await state.get_data()

    # Get first question
    questions = quiz_categories[message.text]
    current_question = questions[0]

    # Create options keyboard
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=option)] for option in current_question["options"]],
        resize_keyboard=True
    )

    # Send question
    await message.answer(
        f"Savol: {current_question['question']}",
        reply_markup=keyboard
    )
    await state.set_state(QuizStates.waiting_for_answer)

# Answer checking handler
@router.message(QuizStates.waiting_for_answer)
async def check_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    if not data:
        await message.answer("Xatolik yuz berdi, qayta urinib ko'ring.")
        return

    user_answer = message.text.strip()
    category = data.get("category")
    questions = quiz_categories[category]
    current_question_index = data.get("current_question")
    current_question = questions[current_question_index]
    correct_answer = current_question["correct_answer"]
    score = data.get("score", 0)
    questions_answered = data.get("questions_answered", 0)
    correct_answers = data.get("correct_answers", 0)

    if user_answer in current_question["options"]:
        questions_answered += 1
        if user_answer == correct_answer:
            score += 5
            correct_answers += 1
            await message.answer(f"To'g'ri javob! \nSizning ballaringiz: {score}", reply_markup=types.ReplyKeyboardRemove())
        else:
            await message.answer(f"Noto'g'ri javob! \nTo'g'ri javob: {correct_answer}\nSizning ballaringiz: {score}")

        await state.update_data(
            score=score,
            questions_answered=questions_answered,
            correct_answers=correct_answers
        )

        current_question_index += 1
        if current_question_index < len(questions):
            next_question = questions[current_question_index]
            options = next_question["options"]

            keyboard = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=option)] for option in options],
                resize_keyboard=True
            )

            await message.answer(
                f"Savol: {next_question['question']}",
                reply_markup=keyboard
            )

            await state.update_data(
                current_question=current_question_index
            )
            await state.set_state(QuizStates.waiting_for_answer)
        else:
            await message.answer(f"Viktorina tugadi! \nSizning yakuniy ballaringiz: {score} ")

            # Save results to database
            user, _ = await User.get_or_create(telegram_id=message.from_user.id,
                defaults={
                    'username': message.from_user.username,
                    'first_name': message.from_user.first_name,
                    'last_name': message.from_user.last_name
                })

            # Update user's total score by adding new score
            user.score = user.score + score
            await user.save()

            # Save quiz result
            await QuizResult.create(
                user=user,
                category=category,
                score=score,
                questions_total=questions_answered,
                questions_correct=correct_answers
            )

            await message.answer(
                "Asosiy menyu:",
                reply_markup=get_main_menu_buttons()
            )
            await state.clear()
            await state.update_data(
                score=score,
                questions_answered=questions_answered,
                correct_answers=correct_answers
            )
    else:
        await message.answer("Iltimos, berilgan variantlardan birini tanlang.")
