# -- Доступ к атрибутам (методы __getattr__, __getattribute__, __setattr__) --
print(' ================= Контроль доступа к атрибутам ======================')
print(' ------------ Порядок обращения к специальным методам ------------')

print(' ----- 1. __getattr__ ')
# Метод __getattr__ вызывается, когда атрибут не найден в __dict__ экземпляра класса


class LazyDB(object):
    def __init__(self):
        self.exists = 5

    def __getattr__(self, name):
        print(' LazyDB.__getattr__(%s)' % name)
        value = 'Super %s' % name
        setattr(self, name, value)
        return value


data = LazyDB()
print('data.__dict__ до обращения к атрибутам:', data.__dict__)
print('Атрибут exists:', data.exists)
print('Атрибут foo: ', data.foo)
print('data.__dict__ после обращения к атрибутам: ', data.__dict__)
print()

print(' ----- 2. __getattribute__ ')
# Метод __getattribute__ вызывается при обращении к атрибуту объекта,
# даже если атрибут не существует в словаре __dict__ экземпляра класса;
# вызывается при обращении к функциям getattr(), hasattr().


class ValidatingDB:
    def __init__(self):
        self.exists = 5

    def __getattribute__(self, name):
        print(' ValidatingDB.__getattribute__(%s)' % name)
        try:
            return super().__getattribute__(name)
        except AttributeError:
            value = 'Puper %s' % name
            setattr(self, name, value)
        return value


data = ValidatingDB()
print('Атрибут exists:', data.exists)
print('Атрибут foo: ', data.foo)
print('Атрибут foo: ', data.foo)
print('Атрибут zero через getattr: ', getattr(data, 'zero'))
print()

print(' ----- 3. __getattr__ + __getattribute__ ')


class ValidatingDB:
    def __init__(self):
        self.exists = 5

    def __getattr__(self, name):
        print(' ValidatingDB.__getattr__(%s)' % name)
        value = 'Super %s' % name
        setattr(self, name, value)
        return value

    def __getattribute__(self, name):
        print(' ValidatingDB.__getattribute__(%s)' % name)
        return super().__getattribute__(name)

data = ValidatingDB()
print('Атрибут exists:', data.exists)
print('Атрибут foo: ', data.foo)
print('Снова атрибут foo: ', data.foo)
print('Есть ли атрибут zoom в объекте:', hasattr(data, 'zoom'))
print('Атрибут face в объекте, доступ через getattr:', getattr(data, 'face'))
print()

print(' ----- 4. __setattr__ ')
# Метод __setattr__ вызывается, когда атрибут назначается экземпляру класса # (в т.ч. при обращении к функции `setattr`).


class SavingDB:
    def __setattr__(self, name, value):
        print(' SavingDB.__setattr__(%s, %r)' % (name, value))
        # Сохранение данных в БД
        # ...
        super().__setattr__(name, value)


data = SavingDB()
print('data.__dict__ до установки атрибута: ', data.__dict__)
data.foo = 5
print('data.__dict__ после установки атрибута: ', data.__dict__)
data.foo = 7
print('data.__dict__ в итоге:', data.__dict__)
print()

print(' -------- Проблема рекурсивного обращения к атрибутам ----------------')
print(' (раскомментируйте строки кода для создания экземпляра)')


class BrokenDictionaryDB:
    def __init__(self, data):
        self._data = {}

    def __getattribute__(self, name):
        print('BrokenDictionaryDB.__getattribute__(%s)' % name)
        return self._data[name]


# Раскомментируйте строки ниже, чтобы увидеть проблему рекурсии:
# data = BrokenDictionaryDB({'foo': 3})
# print(data.foo)
print()

print(' -------- Чтобы избежать рекурсии, используйте объект super -----------')
# Для решения проблемы рекурсивного обращения к атрибутам используйте объект super:

class DictionaryDB:
    def __init__(self, data):
        self._data = data

    def __getattribute__(self, name):
        print('DictionaryDB.__getattribute__(%s)' % name)
        data_dict = super().__getattribute__('_data')
        return data_dict[name]


data = DictionaryDB({'foo': 'This is the right way!'})
print(data.foo)
print()

print(' ---------------- __getattribute__ и дескриптор ---------------- ')
# В дополнение рассмотрим совместное использование
# методов контроля доступа к атрибутам и дескриптора атрибутов


class Grade:
    def __init__(self, name):
        self.name = '_' + name

    def __get__(self, instance, instance_type):
        print(' Grade.__get__')
        if instance is None:
            return self
        return "*{}*".format(getattr(instance, self.name))

    def __set__(self, instance, value):
        print(' Grade.__set__')
        if not (1 <= value <= 100):
            raise ValueError("Балл ЕГЭ должен быть от 1 до 100")
        setattr(instance, self.name, value)


class Exam:
    grade = Grade('grade')

    def __init__(self, title):
        self.title = title

    def __getattribute__(self, name):
        print(' Exam.__getattribute__(%s)' % name)
        return super().__getattribute__(name)


data = Exam('Математика')
print('Задаём количество баллов за экзамен...')
data.grade = 95
print('Выводим это количество баллов...')
print(data.grade)
print('А что такое Exam.grade?')
print(Exam.grade)