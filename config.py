# config.py
import json
import os

# Константы по умолчанию
DEFAULT_PLANNED_WORK = [
    ("Замена масла в двигателе", 15000),
    ("Замена масляного фильтра", 15000),
    ("Замена тормозных дисков", 100000),
    ("Замена топливного фильтра", 80000),
    ("Замена воздушного фильтра для двигателя", 40000),
    ("Замена воздушного фильтра для салона", 20000),
    ("Замена свечей зажигания", 100000),
    ("Замена тормозной жидкости", 40000),
    ("Замена масла в раздаточной коробке", 100000),
    ("Замена масла в механизме заднего дифференциала", 100000),  
    ('Замена охлаждающей жидкости двигателя', 80000),
    ("Замена масла в АКПП", 100000),
]

# ИЗМЕНЕНО: допуск теперь 10% (в процентах)
DEFAULT_ALLOWANCE = 10

# Глобальные переменные
PLANNED_WORK = []
ALLOWANCE = DEFAULT_ALLOWANCE

CONFIG_FILE = 'car_config.json'

def save_config(planned_work=None, allowance=None):
    """Сохраняет конфигурацию в JSON файл"""
    global PLANNED_WORK, ALLOWANCE
    
    # Используем переданные значения или текущие
    work_to_save = planned_work if planned_work is not None else PLANNED_WORK
    allowance_to_save = allowance if allowance is not None else ALLOWANCE
    
    config = {
        'PLANNED_WORK': work_to_save,
        'ALLOWANCE': allowance_to_save
    }
    
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        # Обновляем глобальные переменные
        PLANNED_WORK[:] = work_to_save
        ALLOWANCE = allowance_to_save
        
        return True
    except Exception as e:
        print(f"Ошибка сохранения конфигурации: {e}")
        return False

def load_config():
    """Загружает конфигурацию из JSON файла"""
    global PLANNED_WORK, ALLOWANCE
    
    if not os.path.exists(CONFIG_FILE):
        # Если файла нет, сохраняем настройки по умолчанию
        PLANNED_WORK[:] = DEFAULT_PLANNED_WORK[:]
        ALLOWANCE = DEFAULT_ALLOWANCE
        save_config()
        return True
    
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        PLANNED_WORK[:] = config.get('PLANNED_WORK', DEFAULT_PLANNED_WORK)
        ALLOWANCE = config.get('ALLOWANCE', DEFAULT_ALLOWANCE)
        return True
    except Exception as e:
        print(f"Ошибка загрузки конфигурации: {e}")
        # Используем значения по умолчанию при ошибке
        PLANNED_WORK[:] = DEFAULT_PLANNED_WORK[:]
        ALLOWANCE = DEFAULT_ALLOWANCE
        return False

# При импорте загружаем конфигурацию
load_config()