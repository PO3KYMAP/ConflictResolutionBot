# main.py
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from collections import defaultdict
from aiohttp import web
from dotenv import load_dotenv
import os

# Загружаем переменные окружения
load_dotenv()

API_TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode='HTML'))
dp = Dispatcher()

# Conflict resolution styles
styles = {
    'A': 'Avoiding',
    'B': 'Accommodating',
    'C': 'Compromising',
    'D': 'Collaborating',
    'E': 'Competing'
}

style_descriptions = {
    'A': '❌ <b>Avoiding</b>: You prefer to sidestep conflict, hoping it resolves itself or disappears.\n<i>Useful when issue is trivial or tensions are high.</i>',
    'B': '🤝 <b>Accommodating</b>: You prioritize relationships, often yielding to others.\n<i>Useful when preserving harmony matters more than winning.</i>',
    'C': '⚖️ <b>Compromising</b>: You seek a quick, fair middle ground.\n<i>Useful when time is limited or both sides hold equal power.</i>',
    'D': '🤔 <b>Collaborating</b>: You aim for a win-win by deeply exploring all needs.\n<i>Useful for complex, long-term solutions.</i>',
    'E': '🏆 <b>Competing</b>: You assert your position to achieve your goal.\n<i>Useful when quick action is critical or principle is at stake.</i>'
}

# Store user states
user_data = defaultdict(lambda: {"current_q": 0, "answers": []})

questions = [
    {
        'text': """<b>Scenario 1 — Team Conflict</b>

You're working on a critical group project where team tensions are rising. Two members frequently argue over technical decisions, slowing progress and frustrating everyone else. The deadline is fast approaching, and morale is dropping.

<b>How do you handle the situation?</b>""",
        'options': ['Avoid involvement', 'Support one person', 'Blend approaches', 'Organize discussion',
                    'Choose best idea yourself'],
        'mapping': ['A', 'B', 'C', 'D', 'E']
    },
    {
        'text': """<b>Scenario 2 — Manager's Disagreement</b>

You and a colleague disagree about how to divide tasks on a complex assignment.  
Your manager is unavailable for guidance, and the project is time-sensitive.

<b>What is your approach?</b>""",
        'options': ['Let them take over', 'Agree to avoid conflict', 'Split tasks equally',
                    'Discuss pros/cons of both ideas', 'Insist on your idea'],
        'mapping': ['A', 'B', 'C', 'D', 'E']
    },
    {
        'text': """<b>Scenario 3 — Disengaged Group Member</b>

In a class project, one teammate consistently misses meetings and fails to deliver their part on time, jeopardizing the group's grade.  
The rest of the team is frustrated, but no one has confronted them directly yet.

<b>What do you do?</b>""",
        'options': ['Ignore their behavior', 'Cover for them', 'Reassign tasks', 'Organize team meeting',
                    'Confront them directly'],
        'mapping': ['A', 'B', 'C', 'D', 'E']
    },
    {
        'text': """<b>Scenario 4 — Public Mistake</b>

During a high-stakes class presentation, you make a factual error that is immediately noticed by a professor. Your group looks concerned, and you feel embarrassed.

<b>How do you react?</b>""",
        'options': ['Step back silently', 'Acknowledge mistake quickly', 'Clarify error is minor',
                    'Correct openly and follow up', 'Defend original statement'],
        'mapping': ['A', 'B', 'C', 'D', 'E']
    },
    {
        'text': """<b>Scenario 5 — Personal Boundary</b>

A classmate often asks to borrow your notes and resources, but rarely reciprocates or helps you in return.  
It's becoming inconvenient, and you feel the relationship is one-sided.

<b>What do you do?</b>""",
        'options': ['Keep sharing', 'Reduce sharing quietly', 'Suggest sharing equally', 'Discuss unfair dynamic',
                    'Refuse to share anymore'],
        'mapping': ['A', 'B', 'C', 'D', 'E']
    },
    {
        'text': """<b>Scenario 6 — Overloaded with Tasks</b>

You're part of a volunteer team organizing a university event. The team leader assigns you multiple time-consuming tasks while others have lighter workloads.  
You're feeling overwhelmed and falling behind in your studies.

<b>How do you handle the situation?</b>""",
        'options': ['Accept all tasks quietly', 'Hint you`re overloaded', 'Ask for redistribution',
                    'Propose transparent discussion', 'Refuse extra tasks'],
        'mapping': ['A', 'B', 'C', 'D', 'E']
    },
    {
        'text': """<b>Scenario 7 — Roommate Conflict</b>

Your roommate frequently hosts loud gatherings late at night, disrupting your sleep and study schedule.  
Although you've hinted at your discomfort, nothing has changed.

<b>How do you act?</b>""",
        'options': ['Ignore noise', 'Use earplugs', 'Propose quiet hours', 'Express clearly how it affects you',
                    'Demand gatherings stop'],
        'mapping': ['A', 'B', 'C', 'D', 'E']
    },
    {
        'text': """<b>Scenario 8 — Unmet Expectations</b>

You agreed to collaborate on a side project with a friend, but they consistently miss deadlines, leaving you to complete most of the work alone.

<b>What is your response?</b>""",
        'options': ['Work alone silently', 'Do it and hope they improve', 'Adjust project scope',
                    'Discuss rebalancing tasks', 'Continue without them'],
        'mapping': ['A', 'B', 'C', 'D', 'E']
    },
    {
        'text': """<b>Scenario 9 — Family Obligation vs Academic Duty</b>

Your family asks you to visit for an important celebration, but it coincides with a critical group project deadline. Your team is relying on you.

<b>What do you do?</b>""",
        'options': ['Skip project work', 'Go home & rush tasks', 'Redistribute tasks',
                    'Discuss balance with both sides', 'Decline family invite'],
        'mapping': ['A', 'B', 'C', 'D', 'E']
    },
    {
        'text': """<b>Scenario 10 — Team Member With Personal Issues</b>

A teammate confides in you that they are going through personal difficulties, which is why their performance has declined.  
The rest of the team is frustrated and unaware of this.

<b>What's your approach?</b>""",
        'options': ['Say nothing', 'Quietly cover for them', 'Ask team to accommodate them', 'Encourage transparency',
                    'Tell leader to redistribute tasks'],
        'mapping': ['A', 'B', 'C', 'D', 'E']
    },
    {
        'text': """<b>Scenario 11 — Supervisor Micromanagement</b>

Your supervisor gives you detailed instructions and constantly checks on your progress, limiting your ability to work independently.

<b>What do you do?</b>""",
        'options': ['Follow exactly', 'Follow but show initiative', 'Suggest periodic check-ins',
                    'Discuss need for autonomy', 'Push back and ask full control'],
        'mapping': ['A', 'B', 'C', 'D', 'E']
    },
    {
        'text': """<b>Scenario 12 — Handling Criticism</b>

During a peer-review session, a fellow student critiques your work very harshly and dismissively, leaving you demotivated.  
The feedback contains both valid and exaggerated points.

<b>How do you respond?</b>""",
        'options': ['Stay silent', 'Thank & avoid them', 'Accept valid points only', 'Engage in dialogue',
                    'Challenge criticism'],
        'mapping': ['A', 'B', 'C', 'D', 'E']
    },
    {
        'text': """<b>Scenario 13 — Conflicting Deadlines</b>

Two professors assign conflicting deadlines for major assignments. Both require a large amount of work in a short timeframe.

<b>How do you handle it?</b>""",
        'options': ['Prioritize one task', 'Focus on easier task first', 'Split effort evenly',
                    'Discuss extensions with both professors', 'Choose most rewarding task'],
        'mapping': ['A', 'B', 'C', 'D', 'E']
    },
    {
        'text': """<b>Scenario 14 — Overheard Gossip</b>

You overhear classmates spreading false rumors about another student, who is unaware of it.  
You dislike gossip but don't know whether to intervene.

<b>What do you do?</b>""",
        'options': ['Ignore it', 'Distance yourself silently', 'Talk privately to gossiper', 'Warn the person targeted',
                    'Confront gossipers directly'],
        'mapping': ['A', 'B', 'C', 'D', 'E']
    },
    {
        'text': """<b>Scenario 15 — Resource Allocation</b>

Your team has limited budget/resources, and two project ideas are competing for them. Both sides are passionate and won't easily compromise.

<b>How do you respond?</b>""",
        'options': ['Avoid the argument', 'Support one project quietly', 'Split budget evenly',
                    'Facilitate group negotiation', 'Push for your preferred project'],
        'mapping': ['A', 'B', 'C', 'D', 'E']
    }
]


def get_question_keyboard(question_index):
    """Generate inline keyboard for a question"""
    question = questions[question_index]
    buttons = []
    for i, option in enumerate(question['options']):
        buttons.append([InlineKeyboardButton(
            text=option,
            callback_data=f"answer:{question['mapping'][i]}"
        )])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_style_summary(scores):
    """Determine user's dominant style"""
    result = max(scores, key=scores.get)
    desc = style_descriptions[result]
    return result, desc


@dp.message(Command("start"))
async def cmd_start(message: Message):
    text = (
        "<b>Welcome to the Conflict Resolution Style Test Bot!</b>\n\n"
        "🛠️ This is a soft skills portfolio project by <b>Bohdan Sharloimov</b>\n"
        "Student ID: <b>104936</b>\n\n"
        "Use /info to get in detail about this project.\n"
        "Use /test to start the assessment!\n"
        "Or /styles to learn about all conflict styles."
    )
    await message.answer(text)


@dp.message(Command("styles"))
async def cmd_styles(message: Message):
    text = "<b>Conflict Resolution Styles Overview:</b>\n\n"
    for desc in style_descriptions.values():
        text += f"{desc}\n\n"
    await message.answer(text)


@dp.message(Command("info"))
async def cmd_info(message: Message):
    text = (
        "<b>ℹ️ About This Bot</b>\n\n"
        "This bot is designed to help users identify their dominant <b>Conflict Resolution Style</b> through an interactive assessment.\n\n"
        "💡 <b>Purpose:</b>\n"
        "• Raise awareness of different conflict-handling strategies.\n"
        "• Provide users with actionable insights on how they approach conflicts.\n"
        "• Offer guidance on how to leverage their preferred style effectively.\n\n"
        "🛠️ <b>Developed by:</b> Bohdan Sharloimov\n"
        "🎓 <b>University Soft Skills Portfolio Project</b>\n"
        "🆔 <b>Student ID:</b> 104936\n\n"
        "<b>Key Features:</b>\n"
        "• 15 scenario-based questions\n"
        "• Clear descriptions of all 5 conflict styles\n"
        "• Tailored recommendations based on results\n"
        "• User-friendly interface with intuitive buttons\n\n"
        "Use /test to start the assessment or /styles to learn about all styles!"
    )
    await message.answer(text)


@dp.message(Command("test"))
async def cmd_test(message: Message):
    user_id = message.from_user.id
    user_data[user_id] = {"current_q": 0, "answers": []}
    await send_question(message.chat.id, user_id)


async def send_question(chat_id, user_id):
    state = user_data[user_id]
    q_index = state['current_q']
    if q_index < len(questions):
        question = questions[q_index]
        await bot.send_message(chat_id, question['text'], reply_markup=get_question_keyboard(q_index))
    else:
        # Test complete — calculate result
        counts = defaultdict(int)
        for answer in state['answers']:
            counts[answer] += 1
        result, desc = get_style_summary(counts)

        text = f"<b>🎉 Your dominant Conflict Resolution Style: {styles[result]}</b>\n\n{desc}\n\n"
        text += "✅ <b>Tips for you:</b>\n"
        text += get_advice(result)

        await bot.send_message(chat_id, text)
        # Clear state after completion
        user_data.pop(user_id)


def get_advice(style_code):
    """Give tailored advice"""
    advice = {
        'A': "• Use avoiding when issues are minor.\n• Don't avoid important conflicts too often.\n• Try expressing concerns earlier.",
        'B': "• Good for relationships, but don't neglect your needs.\n• Assert yourself when it matters.\n• Balance harmony with fairness.",
        'C': "• Works well when time is short.\n• Aim for compromise that feels fair.\n• Use collaboration for complex problems.",
        'D': "• Excellent for strong partnerships.\n• Invest time to understand all perspectives.\n• Watch for over-analysis paralysis.",
        'E': "• Useful when urgent action is key.\n• Ensure not to alienate others.\n• Be open to other views when time permits."
    }
    return advice[style_code]


@dp.callback_query(F.data.startswith("answer:"))
async def answer_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    if user_id not in user_data:
        await callback.answer("Please start a new test with /test.", show_alert=True)
        return
    answer = callback.data.split(":")[1]
    state = user_data[user_id]
    q_index = state['current_q']
    question = questions[q_index]
    state['answers'].append(answer)
    state['current_q'] += 1
    buttons = []
    for i, option in enumerate(question['options']):
        style_code = question['mapping'][i]
        prefix = "✅ " if style_code == answer else ""
        buttons.append([InlineKeyboardButton(
            text=prefix + option,
            callback_data="disabled"  # Disable further clicks
        )])

    feedback_kb = InlineKeyboardMarkup(inline_keyboard=buttons)

    # Edit message with feedback keyboard
    await callback.message.edit_reply_markup(reply_markup=feedback_kb)

    # Pause briefly (optional, to show feedback before next question)
    await asyncio.sleep(1.5)

    # Send next question
    await send_question(callback.message.chat.id, user_id)


async def webhook(request):
    update = await request.json()
    await dp.feed_webhook_update(bot, update)
    return web.Response()


async def main():
    try:
        print("Starting bot...")
        print(f"Bot token: {API_TOKEN[:10]}...")  # Показываем только начало токена

        # Удаляем старый вебхук если он есть
        print("Deleting old webhook...")
        await bot.delete_webhook(drop_pending_updates=True)

        # Получаем URL из переменных окружения
        webhook_url = os.getenv('WEBHOOK_URL', 'https://problemsol.onrender.com/webhook')

        # Устанавливаем новый вебхук
        await bot.set_webhook(url=webhook_url)
        print("Webhook set successfully")

        # Создаем веб-приложение
        app = web.Application()
        app.router.add_post('/webhook', webhook)
        print("Web application created")
        return app
    except Exception as e:
        print(f"Error in main(): {e}")
        raise


if __name__ == "__main__":
    app = asyncio.run(main())
    web.run_app(app, host='0.0.0.0', port=8000)
