import pytest

# Список всех полей, которые будем проверять в каждой структуре
FIELDS_TO_CHECK = ["separator", "coordinates", "val_extra_info", "key_extra_info"]  # Добавьте все нужные поля


# Параметризация для тестирования каждого поля во всех структурах
@pytest.mark.parametrize("field", FIELDS_TO_CHECK)
def test_compare_field_across_structures(field):
    # Получаем все структуры, переданные в тестовый контекст
    all_structures = get_all_structures()  # Функция, которая возвращает список всех структур (замените на вашу логику получения структур)

    # Проверяем каждую структуру на наличие и сравнение поля
    for structure in all_structures:
        assert field in structure, f"Field '{field}' is missing in the structure"
        assert structure[field] == REFERENCE_STRUCTURE[field], f"Field '{field}' value mismatch"


def get_all_structures():
    # Здесь должна быть ваша логика получения всех динамических структур
    # Например, из API, базы данных, файла и т.д.
    # Возвращает список структур
    return [
        {
            "separator": ":",
            "coordinates": {"x0": 13.512, "y0": 222.067},
            "val_extra_info": {"font_name": "ArialMT", "font_size": 7.507, "font_color": 0},
            "key_extra_info": {"font_name": "Arial-BoldMT", "font_size": 7.507, "font_color": 0}
        },
        {
            "separator": "-",
            "coordinates": {"x0": 15.0, "y0": 200.0},
            "val_extra_info": {"font_name": "Times New Roman", "font_size": 10.0, "font_color": 0},
            "key_extra_info": {"font_name": "Calibri", "font_size": 8.0, "font_color": 0}
        }
        # Дополнительные структуры, если есть
    ]


# Эталонная структура для сравнения
REFERENCE_STRUCTURE = {
    "separator": ":",
    "coordinates": {"x0": 13.512, "y0": 222.067},
    "val_extra_info": {"font_name": "ArialMT", "font_size": 7.507, "font_color": 0},
    "key_extra_info": {"font_name": "Arial-BoldMT", "font_size": 7.507, "font_color": 0}
}
