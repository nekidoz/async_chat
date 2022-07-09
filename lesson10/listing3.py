# --------------------- Дескрипторы атрибутов -------------------------------
#
print(' ====== Способы хранения значений при работе с дескрипторами =======')
print(' ========== 1. Хранение в атрибуте дескриптора ==============')
# Первый способ сохранить данные - просто в атрибуте объекта дескриптора.
class Grade:
    def __init__(self):
        self._value = 0

    def __get__(self, instance, instance_type):
        return self._value

    def __set__(self, instance, value):
        if not (1 <= value <= 5):
            raise ValueError("Оценка должна быть от 1 до 5")
        self._value = value

class Exam:
    """ Класс Экзамен.
    Для простоты хранит только оценку за экзамен. """
    grade = Grade()

# Но не стоит забывать, что при таком подходе
# данные будут сохранены на уровне атрибута класса Экзамен!!!
# Т.е. будут общими для всех экземпляров класса Экзамен.

# Для демонстрации создадим два Экзамена:
math_exam = Exam()
math_exam.grade = 3
language_exam = Exam()
language_exam.grade = 5

print(" Проверим результаты: ")
print("Первый экзамен ", math_exam.grade, " - верно?")
print("Второй экзамен ", language_exam.grade, " - верно?")

print('Потому что... ')
print('math_exam.grade is language_exam.grade =', math_exam.grade is language_exam.grade)
print()

#=============================================================================
print()
print(' ====== 2. Хранение данных в отдельном словаре дескриптора =======')
print('* Внимание! Хранение данных в обычном dict будет приводить к утечкам памяти! *')
class Grade:
    def __init__(self):
        self._values = {}

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return self._values.get(instance, 0)

    def __set__(self, instance, value):
        if not (1 <= value <= 5):
            raise ValueError("Оценка должна быть от 1 до 5")
        self._values[instance] = value


# Хотя данное решение достаточно простое и полноценно работает,
# оно будет приводить к утечкам памяти!
# Словарь _values будет хранить ссылку на каждый внешний экземпляр класса,
# который когда-либо передавался в метод __set__.
# Это приведет к тому, что счётчик ссылок у внешних экземпляров никогда не будет равен нулю,
# и сборщик мусора никогда не выполнит свою работу.
print()
print(' Вместо обычного dict нужно использовать класс weakref.WeakKeyDictionary')

from weakref import WeakKeyDictionary

# ----------------------------------------------------------
# Модуль weakref обеспечивает поддержку слабых ссылок.
# В обычном случае сохранение ссылки на объект приводит к увеличению счетчика ссылок,
# что препятствует уничтожению объекта, пока значение счетчика не достигнет
# нуля.
# Слабая ссылка позволяет обращаться к объекту, не увеличивая его счетчик
# ссылок.
#
# ------------------------------------------------------------------------------
# --------------------
# Класс WeakKeyDictionary([dict]) cоздает словарь, в котором ключи
# представлены слабыми ссылками.
# Когда количество обычных ссылок на объект ключа становится равным нулю,
# соответствующий элемент словаря автоматически удаляется.
# В необязательном аргументе dict передается словарь, элементы которого
# добавляются
# в возвращаемый объект типа WeakKeyDictionary.
# Cлабые ссылки могут создаваться только для объектов определенных типов,
# поэтому
# существует большое число ограничений на допустимые типы объектов ключей.
# В частности, встроенные строки НЕ МОГУТ использоваться в качестве ключей со
# слабыми ссылками.
# Однако экземпляры пользовательских классов, объявляющих метод __hash__(),
# могут играть роль ключей.
# Экземпляры класса WeakKeyDictionary имеют два дополнительных метода,
# iterkeyrefs() и keyrefs(),
# которые возвращают слабые ссылки на ключи.

class Grade:
    def __init__(self):
        self._values = WeakKeyDictionary()

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return self._values.get(instance, 0)

    def __set__(self, instance, value):
        if not (1 <= value <= 5):
            raise ValueError("Оценка должна быть от 1 до 5")
        self._values[instance] = value


class Exam():
    """ Класс Экзамен.
        Для простоты хранит только оценку за экзамен
    """
    grade = Grade()


# Для демонстрации создадим два Экзамена:
math_exam = Exam()
math_exam.grade = 3

language_exam = Exam()
language_exam.grade = 5

print(" Проверим результаты: ")
print("Первый экзамен ", math_exam.grade, " - верно?")
print("Второй экзамен ", language_exam.grade, " - верно?")
print()

# Недостаток конкретно данного решения - в одном классе нельзя сохранять
# данные дескрипторов одного типа.
# Т.е., например, сделать экзамен с несколькими оценками.


print(' ====== Хранение в __dict__ экземпляра внешнего класса =======')

# Такой подход, помимо прочего, позволяет в одном внешнем классе
# создавать несколько объектов-дескрипторов одного класса.

class Grade:
    def __init__(self, name):
        # Для данного подхода необходимо сформировать отдельное имя атрибута,
        # иначе при совпадении имени name и имени дескриптора
        # создаваемый атрибут перезапишет объект дескриптора в данном экземпляре
        self.name = '_' + name

    def __get__(self, instance, instance_type):
        if instance is None:
            return self
        return "*{}*".format(getattr(instance, self.name))

    def __set__(self, instance, value):
        if not (1 <= value <= 100):
            raise ValueError("Балл ЕГЭ должен быть от 1 до 100")
        setattr(instance, self.name, value)


class ExamEGE():
    """ Комплексный экзамен, на котором оцениваются разные критерии.
    """
    # Для обновлённого Grade нужно обновить и создание атрибутов, добавив строковые имена.
    # Строковые имена могут не совпадать с именами атрибутов.
    math_grade = Grade('math_grade')
    writing_grade = Grade('writing_grade')
    science_grade = Grade('science')


# Проверим обновлённый дескриптор Оценку и объекты Экзамены.
first_exam = ExamEGE()
first_exam.writing_grade = 3
first_exam.math_grade = 4

print("Содержимое first_exam.__dict__:")
print(' ', first_exam.__dict__)

second_exam = ExamEGE()
second_exam.writing_grade = 2
second_exam.science_grade = 5

print()
print(" Проверим результаты: ")
print("Первый экзамен ", first_exam.writing_grade, first_exam.math_grade, " - верно?")
print("Второй экзамен ", second_exam.writing_grade, second_exam.science_grade, " - верно?")