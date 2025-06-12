import streamlit as st
import re
from collections import Counter
import pymorphy3

def analyze_texts(text1: str, text2: str) -> str:
    """
    Анализирует два текста, находит уникальные леммы из второго текста,
    отсутствующие в первом, и возвращает отсортированный список в формате Markdown.
    """
    try:
        morph = pymorphy3.MorphAnalyzer()
    except Exception as e:
        st.error(f"Ошибка при инициализации морфологического анализатора: {e}")
        return "Не удалось выполнить анализ."

    # --- ШАГ ОЧИСТКИ ТЕКСТА ---
    # 1. Заменяем все пробельные символы на обычный пробел
    text1_cleaned = re.sub(r'\s+', ' ', text1)
    text2_cleaned = re.sub(r'\s+', ' ', text2)
    # 2. Можно добавить и другие правила очистки при необходимости

    def get_lemmas(text: str) -> list:
        # Используем очищенный текст
        words = re.findall(r'\b[а-яА-ЯёЁ-]+\b', text.lower())
        lemmas = [morph.parse(word)[0].normal_form for word in words]
        return lemmas

    lemmas1_set = set(get_lemmas(text1_cleaned))
    all_lemmas_from_text2 = get_lemmas(text2_cleaned)
    
    # Основная логика: оставляем только те леммы из текста 2, которых нет в тексте 1
    unique_lemmas = [lemma for lemma in all_lemmas_from_text2 if lemma not in lemmas1_set]

    if not unique_lemmas:
        return "Во втором тексте не найдено уникальных слов, отсутствующих в первом."

    # Считаем частоту и сортируем
    frequency_counter = Counter(unique_lemmas)
    sorted_lemmas = sorted(frequency_counter.items(), key=lambda x: (-x[1], x[0]))
    
    result_markdown = [f"- **{word}** — {count} раз(а)" for word, count in sorted_lemmas[:300]]

    return "\n".join(result_markdown)

# --- Интерфейс приложения Streamlit ---
st.set_page_config(page_title="Анализатор уникальных слов", layout="wide")
st.title("📊 Анализатор уникальных слов в тексте")
st.info(
    "Этот инструмент находит слова, которые есть во втором тексте, но отсутствуют в первом. "
    "Анализ учитывает разные формы слов (падежи, числа), приводя их к начальной форме (лемме)."
)

# Инициализация состояния для текстовых полей
if 'text1' not in st.session_state:
    st.session_state.text1 = ""
if 'text2' not in st.session_state:
    st.session_state.text2 = ""

# Функции для очистки текстовых полей
def clear_text1():
    st.session_state.text1 = ""

def clear_text2():
    st.session_state.text2 = ""

col1, col2 = st.columns(2)

with col1:
    st.header("Текст №1 (Основной)")
    st.session_state.text1 = st.text_area(
        label="Слова из этого текста будут исключены из анализа:",
        value=st.session_state.text1,
        height=300,
        placeholder="Вставьте сюда основной текст...",
        key="text_area1"
    )
    st.button("Очистить", on_click=clear_text1, key="clear_text1")

with col2:
    st.header("Текст №2 (Сравниваемый)")
    st.session_state.text2 = st.text_area(
        label="Здесь будут искаться уникальные слова:",
        value=st.session_state.text2,
        height=300,
        placeholder="Вставьте сюда текст для сравнения...",
        key="text_area2"
    )
    st.button("Очистить", on_click=clear_text2, key="clear_text2")

if st.button("🚀 Начать анализ", use_container_width=True):
    if st.session_state.text1 and st.session_state.text2:
        with st.spinner("Пожалуйста, подождите, идёт обработка текстов..."):
            analysis_result = analyze_texts(st.session_state.text1, st.session_state.text2)
        
        st.header("Результат анализа")
        st.markdown("---")
        st.markdown(analysis_result)
    else:
        st.error("❗ Пожалуйста, введите тексты в оба поля для анализа.")

# Добавление кнопки "Наверх" с помощью HTML и JavaScript
st.markdown(
    """
    <style>
    .scroll-to-top {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
    }
    </style>
    <button class="scroll-to-top" onclick="window.scrollTo({top: 0, behavior: 'smooth'})">↑ Наверх</button>
    """,
    unsafe_allow_html=True
)