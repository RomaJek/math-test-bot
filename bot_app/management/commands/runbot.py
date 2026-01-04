import asyncio  # Asinxron proceslerdi (bottyń toqtap qalmawın) basqarıw ushın
import logging  # Botta ne bolıp atırǵanin terminalda (log) kórip turıw ushın
import os       # Sistemalıq fayllar hám papkalar menen islesiw ushın
import random   # Sorawlardı tosınnan (random) saylap alıw ushın
import math     # Betler sanın (pagination) dońalaqlap esaplaw ushın

# --- DJANGO IMPORTS ---
from django.core.management.base import BaseCommand  # Djangoda jeke komanda (runbot) jaratıw ushın
from django.conf import settings                    # settings.py daǵı maǵlıwmatlardı (token) alıw ushın
from django.utils import timezone                   # Waqıt zonaları menen islesiw ushın
from asgiref.sync import sync_to_async              # Sinxron ORM-dı asinxron botqa sáykeslestiriw ushın

# --- AIOGRAM IMPORTS (BOT FRAMEWORK) ---
from aiogram import Bot, Dispatcher, types, F       # Bottyń tiykarǵı komponentleri
from aiogram.filters import Command as CommandFilter # /start sıyaqlı buyrıqlarnı tutıw ushın
from aiogram.fsm.state import State, StatesGroup    # Jaǵdaylar (FSM) jaratıw ushın
from aiogram.fsm.context import FSMContext          # Házirgi jaǵdaydı basqarıw ushın
from aiogram.types import FSInputFile, ReplyKeyboardRemove # Súwret jiberiw hám menyunu óshiriw ushın
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder # Túymeler jasaw ushın

# --- PROJECT MODELS & STORAGE ---
from bot_app.models import BotUser, Question, TestAttempt, AttemptDetail # Bazadaǵı kestelerimiz
from bot_app.storage import DjangoORMStorage  # FSM-di PostgreSQL-de saqlawshı "yad" (Biz jazǵan)

# Logging sazlamasy: Terminalda tek INFO dárejesindegi maǵlıwmatlardı kórsetedi
logging.basicConfig(level=logging.INFO)

# --- FSM STATES (Bottyń Logikalıq Yadı) ---
class Registration(StatesGroup):
    """Oqıwshı dizimnen ótip atırǵan waqıt"""
    waiting_for_name = State() # Atı-familiyasın jazıwın kútiw

class TestProcess(StatesGroup):
    """Oqıwshı test sheship atırǵan waqıt"""
    answering = State() # Sorawlarǵa juwap beriw procesi

# --- KEYBOARDS (Bas Menyu) ---
def get_main_menu():
    """Tiykarǵı bas menyu túymelerin jasaydı"""
    builder = ReplyKeyboardBuilder()
    builder.button(text="🎯 Testti baslaw")   # Testti baslaw túymesi
    builder.button(text="📊 Meniń nátiyjelerim") # Statistika túymesi
    builder.adjust(1) # Túymelerdi bir-biriniń astınan diziw
    return builder.as_markup(resize_keyboard=True) # Túymelerdi ekranǵa sáykeslestiriw

# --- DJANGO COMMAND CLASS ---
class Command(BaseCommand):
    """Bul klass 'python manage.py runbot' buyrıǵın iske túsiredi"""
    help = "Telegram botty iske túsiriw hám Django ORM menen biriktiriw"

    def handle(self, *args, **options):
        """Djangonıń sinxron baslaw noqatı"""
        if not settings.BOT_TOKEN: # Eger token settings-te joq bolsa
            self.stdout.write(self.style.ERROR("QÁTE: BOT_TOKEN tabılmadı!"))
            return
        
        self.stdout.write(self.style.SUCCESS("Bot iske túsirilip atır..."))
        asyncio.run(self.main()) # Asinxron main() funksiyasın iske túsiremiz

    async def main(self):
        """Bottyń tiykarǵı asinxron logikasy"""
        bot = Bot(token=settings.BOT_TOKEN) # Botty token menen tanıtamız
        storage = DjangoORMStorage()        # PostgreSQL tiykarındaǵı turaqlı yaddı qosamyz
        dp = Dispatcher(storage=storage)    # Dispatcher-di "aqıllı" storage menen iske túsiremiz

        # --- INTERNAL HELPERS (Kómekshi funksiyalar) ---

        async def send_next_question(message: types.Message, state: FSMContext):
            """Gezektegi sorawdı formatlap oqıwshıǵa jiberiw"""
            data = await state.get_data() # FSM-degi barlıq saqlanǵan maǵlıwmattı alamız
            index = data['current_index'] # Házirgi sorawdıń sanı (0-den baslap)
            q_ids = data['questions_ids'] # Saylap alınǵan 10 sorawdıń ID-leri

            # Bazadan gezektegi sorawdı ID boyınsha tartıp alamız
            current_q_id = q_ids[index]
            question = await sync_to_async(Question.objects.get)(id=current_q_id)

            # Variant túymelerin jasaw
            kb = InlineKeyboardBuilder()
            choices = [
                ('a', question.option_a), ('b', question.option_b),
                ('c', question.option_c), ('d', question.option_d),
            ]
            for char, val in choices: # Túyme tekstin "A) Juvap" túrinde jasaymız
                kb.button(text=f"{char.upper()}) {val}", callback_data=f"ans_{char}")
            kb.adjust(1) # Hár bir variant úlken túyme retinde tómende diziledi

            full_text = f"<b>{index + 1}-soraw:</b>\n\n{question.text}"

            # Súwretli yamasa tekstli sorawdı jiberiw logikasy
            sent_msg = None
            if question.image: # Eger sorawdıń súwreti bolsa
                photo = FSInputFile(question.image.path) # Súwret jolın alamız
                sent_msg = await message.answer_photo(photo=photo, caption=full_text, reply_markup=kb.as_markup(), parse_mode="HTML")
            else: # Eger tek tekst bolsa
                sent_msg = await message.answer(full_text, reply_markup=kb.as_markup(), parse_mode="HTML")

            # Security: Aqırǵı jiberilgen xabar ID-sin saqlaymız (Eski túymelerdi bloklaw ushın)
            await state.update_data(last_msg_id=sent_msg.message_id)
            await state.set_state(TestProcess.answering) # Jaǵdaydı 'answering' dep belgileymiz

        async def finish_test(message: types.Message, state: FSMContext):
            """Testti juvmaqlaw hám nátiyjelerdi bazaga bekitip saqlaw"""
            data = await state.get_data() # Jıynalǵan juvaplar hám ballardı alamız
            user_id = message.chat.id
            score = data['score']
            details = data['details'] 

            # Oqıwshı obyektin bazadan alıw
            user = await sync_to_async(BotUser.objects.get)(telegram_id=user_id)
            
            # TestAttempt (Ulıwma nátiyje) kestesne saqlaymız
            attempt = await sync_to_async(TestAttempt.objects.create)(user=user, score=score, total_questions=10)

            error_report = "" # Qáteler dizimin jıynaw ushın bos tekst
            for idx, item in enumerate(details, 1): # Hár bir juvaptı aylanıp shıǵamız
                q = await sync_to_async(Question.objects.get)(id=item['question_id'])
                
                # AttemptDetail (Hár bir soraw boyınsha detal) kestesne saqlaymız
                await sync_to_async(AttemptDetail.objects.create)(
                    attempt=attempt, question=q, user_answer=item['user_answer'], is_correct=item['is_correct']
                )
                
                # Qáte reportın tayarlaw (idx - qatar sanı)
                if not item['is_correct']:
                    user_ans_text = getattr(q, f"option_{item['user_answer']}") # Oqıwshı belgilegen tekst
                    corr_ans_text = getattr(q, f"option_{q.correct_answer}")     # Durıs juvap teksti
                    error_report += (
                        f"❌ <b>{idx}-Soraw:</b> {q.text[:50]}...\n"
                        f"Siz: {item['user_answer'].upper()}) {user_ans_text}\n"
                        f"Durıs: {q.correct_answer.upper()}) {corr_ans_text}\n\n"
                    )

            # Aqırǵı nátiyje xabarı
            result_text = f"🏁 <b>Test juvmaqlandı!</b>\n\nSiziń nátiyjeńiz: <b>{score} / 10</b>\n"
            if error_report:
                result_text += "\n<b>Qáte jiberilgen sorawlar:</b>\n\n" + error_report
            else:
                result_text += "\nBarékella! Hámme sorawǵa durıs juvap berdińiz! ✨"

            # Oqıwshıǵa esabat jiberiw hám menyunu qaytarıw
            await message.answer(result_text, parse_mode="HTML", reply_markup=get_main_menu())
            await state.clear() # Bazadaǵı oqıwshı state-in taza qılıp óshiremiz

        # --- CORE HANDLERS (LOGİKALIK İZBE-İZLİK) ---

        # 1. /start buyrıǵı hám State Locking (Qulıplaw)
        @dp.message(CommandFilter("start"))
        async def cmd_start(message: types.Message, state: FSMContext):
            current_state = await state.get_state()
            
            # Eger oqıwshı test tapsırıp atırǵanda start bassa, oǵan Reset/Continue usınıs etemiz
            if current_state == TestProcess.answering:
                kb = InlineKeyboardBuilder()
                kb.button(text="🔄 Testti qaytadan baslaw (Reset)", callback_data="force_reset_test")
                kb.button(text="▶️ Testti dawam ettiriw", callback_data="continue_test")
                kb.adjust(1)
                await message.answer("⚠️ <b>Siz házir test procesindesiz!</b>", parse_mode="HTML", reply_markup=kb.as_markup())
                return # Buyrıqtı usı jerde toqtatamız

            # Bazadan oqıwshını izlew
            user = await sync_to_async(BotUser.objects.filter(telegram_id=message.from_user.id).first)()

            if user: # Eger oqıwshı aldın dizimnen ótken bolsa
                await message.answer(f"Qaytaldan xosh keldińiz, {user.full_name}!", reply_markup=get_main_menu())
            else: # Eger taza oqıwshı bolsa
                await message.answer("Assalawma aleykum! Matematika test botına xosh keldińiz.\nTestti baslaw ushın dáslep atı-familiyańizdı kiritiń:")
                await state.set_state(Registration.waiting_for_name) # Atın kútemiz

        # 2. Registratsiya: Atı-familiyanı qabıllaw hám tazalaw
        @dp.message(Registration.waiting_for_name)
        async def process_name(message: types.Message, state: FSMContext):
            full_name = " ".join(message.text.split()) # Sózler arasındaǵı artıqsha boslıqlardı tazalaw
            await sync_to_async(BotUser.objects.create)(
                telegram_id=message.from_user.id, full_name=full_name, username=message.from_user.username
            )
            await message.answer(f"Raxmet, {full_name}! Dizimnen óttińiz.", reply_markup=get_main_menu())
            await state.clear() # Dizimnen ótip boldı, state-ti tazalaymız

        # 3. Testti baslaw (Túyme arqalı)
        @dp.message(lambda m: m.text == "🎯 Testti baslaw")
        async def start_test(message: types.Message, state: FSMContext):
            # Test tapsırıp atırǵanda jańa test baslawdı bloklaw
            if await state.get_state() == TestProcess.answering:
                await message.answer("⚠️ <b>Siz házir test tapsırıp atırsız!</b>", parse_mode="HTML")
                return

            # Bazadan barlıq aktiv sorawlardıń ID dizimin alamız
            all_q = await sync_to_async(list)(Question.objects.filter(is_active=True).values_list('id', flat=True))
            if len(all_q) < 10: # Eger sorawlar 10-nan kem bolsa
                await message.answer(f"Keshiriń, bazada sorawlar jetkiliksiz.")
                return

            # Tákrarlanbaytuǵın 10 random ID saylap alamız
            selected_ids = random.sample(all_q, 10)
            # FSM yadına test maǵlıwmatların jazıp alamız
            await state.update_data(questions_ids=selected_ids, current_index=0, score=0, details=[])
            
            # Menyu túymelerin óshirip (ReplyKeyboardRemove), testti baslaymız
            await message.answer("Test baslandı! Áwmet!", reply_markup=ReplyKeyboardRemove())
            await send_next_question(message, state)

        # 4. Emergency Reset (Avariyalıq jaǵdayda state-ti tazalaw)
        @dp.callback_query(F.data == "force_reset_test")
        async def force_reset(callback: types.CallbackQuery, state: FSMContext):
            await state.clear() # Bazadaǵı state-ti tolıq óshiriw
            await callback.message.edit_text("✅ Test procesi tazalandı. Endi jańadan baslasańız boladı.")
            await callback.message.answer("Bas menyu:", reply_markup=get_main_menu())
            await callback.answer()

        # 5. Continue Test (Qalǵan jerinen dawam ettiriw logikasy)
        @dp.callback_query(F.data == "continue_test")
        async def continue_test(callback: types.CallbackQuery, state: FSMContext):
            await callback.message.delete() # Reset/Continue sorawın óshiriw
            await send_next_question(callback.message, state) # Bazadaǵı index boyınsha sorawdı qayta jiberiw
            await callback.answer()

        # 6. Statistika hám Pagination (Betlerge bóliw)
        @dp.message(lambda m: m.text == "📊 Meniń nátiyjelerim")
        async def my_statistics(message: types.Message, state: FSMContext):
            if await state.get_state() == TestProcess.answering: # Test waqtında statistikanı bloklaw
                await message.answer("⚠️ Test waqtında statistikanı kóre almaysız.")
                return
            
            # Sońǵı 10 test nátiyjesin alıw
            attempts = await sync_to_async(list)(
                TestAttempt.objects.filter(user__telegram_id=message.from_user.id).order_by('-created_at')[:10]
            )
            if not attempts:
                await message.answer("Siz ele test tapsırmapsız.")
                return

            res = "<b>📊 Sońǵı 10 nátiyjeńiz:</b>\n<i>(Asia/Tashkent)</i>\n\n"
            for i, att in enumerate(attempts, 1):
                local_dt = timezone.localtime(att.created_at) # UTC-ni Tashkent waqtına aylandırıw
                res += f"{i}) {local_dt.strftime('%d.%m.%Y %H:%M')} — <b>{att.score}/10</b>\n"

            kb = InlineKeyboardBuilder()
            kb.button(text="📄 Barlıq nátiyjeni kóriw", callback_data="results_page:1")
            await message.answer(res, parse_mode="HTML", reply_markup=kb.as_markup())

        # 7. Pagination Handler (Barlıq nátiyjelerdi betlerge bólip kórsetiw)
        @dp.callback_query(F.data.startswith("results_page:"))
        async def paginate_results(callback: types.CallbackQuery):
            page = int(callback.data.split(":")[1]) # Bet nomerin callback-ten alıw
            page_size = 10 # Bir bette 10 nátiyje
            query = TestAttempt.objects.filter(user__telegram_id=callback.from_user.id).order_by('-created_at')
            total_count = await sync_to_async(query.count)()
            total_pages = math.ceil(total_count / page_size) # Jámi betler sanı
            
            # Bazadan tek kerekli bettiń maǵlıwmatların (Slicing) tartıp alamız
            start, end = (page - 1) * page_size, page * page_size
            attempts = await sync_to_async(list)(query[start:end])

            res = f"<b>📜 Barlıq nátiyjelerińiz ({page}/{total_pages}):</b>\n\n"
            for i, att in enumerate(attempts, start + 1):
                local_dt = timezone.localtime(att.created_at)
                res += f"{i}) {local_dt.strftime('%d.%m.%Y %H:%M')} — <b>{att.score}/10</b>\n"

            kb = InlineKeyboardBuilder()
            if page > 1: kb.button(text="⬅️ Aldınǵı", callback_data=f"results_page:{page-1}")
            if page < total_pages: kb.button(text="Keyingi ➡️", callback_data=f"results_page:{page+1}")
            kb.adjust(2)
            try: await callback.message.edit_text(res, parse_mode="HTML", reply_markup=kb.as_markup())
            except: pass # Eger tekst ózgermese qáte bermew ushın
            await callback.answer()

        # 8. Tiykarǵı Test Juvapların tekseriw (Eń názik handler!)
        @dp.callback_query(TestProcess.answering, F.data.startswith("ans_"))
        async def handle_answer(callback: types.CallbackQuery, state: FSMContext):
            data = await state.get_data()
            
            # Security Check: Oqıwshı basqa (eski) xabardaǵı túymeni bassa bloklaw
            if callback.message.message_id != data.get('last_msg_id'):
                await callback.answer("⚠️ Bul eski soraw! Tek jańa sorawǵa juwap beriń.", show_alert=True)
                return

            # Concurrency Lock: Eki túymeni birden basıwdan qorǵanıw (Race Condition)
            if data.get('is_processing'):
                await callback.answer() # Signaldi ignore qılamız
                return

            await state.update_data(is_processing=True) # Handlerdi qulıplaymız

            try:
                user_ans = callback.data.split("_")[1] # Callback-ten 'a', 'b' háribin alıw
                current_q_id = data['questions_ids'][data['current_index']]
                q = await sync_to_async(Question.objects.get)(id=current_q_id)
                
                # Durıs-qáteligini tekseriw
                is_correct = (user_ans == q.correct_answer)
                
                # Detallardı jańalap, yadda saqlaymız
                data['details'].append({'question_id': q.id, 'user_answer': user_ans, 'is_correct': is_correct})
                await state.update_data(
                    current_index=data['current_index'] + 1, 
                    score=data['score'] + (1 if is_correct else 0), 
                    details=data['details'],
                    is_processing=False # Qulıptı ashamız
                )

                await callback.message.edit_reply_markup(reply_markup=None) # Túymeni óshiriw
                
                # Kelesi sorawǵa ótiw yamasa testti pitkeriw
                if data['current_index'] + 1 < 10:
                    await send_next_question(callback.message, state)
                else:
                    await finish_test(callback.message, state)
                await callback.answer()
            except Exception as e:
                await state.update_data(is_processing=False) # Qáte bolsa da qulıptı ashamız
                await callback.answer("Qáte júz berdi.")

        # 9. Expired Session (Bot restarttan keyingi 'zombi' túymelerden qorǵanıw)
        @dp.callback_query(lambda c: c.data.startswith('ans_'))
        async def expired_session(callback: types.CallbackQuery, state: FSMContext):
            if await state.get_state() is None: # Eger oqıwshınıń state-i None bolsa
                await callback.answer("⚠️ Sessiya waqtı ótti (Bot restart boldı).", show_alert=True)
                await callback.message.edit_reply_markup(reply_markup=None)

        # 10. Test waqtındaǵı kerek-emez tekstlerdi bloklaw (Tazalaw)
        @dp.message(TestProcess.answering)
        async def warning_test(message: types.Message):
            warn = await message.answer("⚠️ <b>Test tapsırıp atırsız!</b> Shalǵıp tekst jazbań.", parse_mode="HTML")
            try:
                await message.delete() # Oqıwshı jibergen tekstti óshiriw
            except: pass

        # 11. Global Catch-all (EŃ AQIRINDA: Hámme nárseni tutıp alıwshı filtr)
        @dp.message()
        async def global_catch_all(message: types.Message):
            warn = await message.answer("⚠️ Iltimas, menyudaǵı túymelerden paydalanıń yamasa /start jazıń.")
            try:
                await message.delete() # Kerek-emez tekst, emoji yamasa medianı óshiriw
            except: pass

        # --- BOT START (POLLING) ---
        self.stdout.write(self.style.SUCCESS("Bot iske tústi!"))
        try:
            # skip_updates=True: Bot óshik waqıtta jiberilgen eski xabarlardı tastap jiberedi
            await dp.start_polling(bot, skip_updates=True)
        finally:
            await bot.session.close() # Bot toqtatılǵanda Telegram baylanısın jabıw