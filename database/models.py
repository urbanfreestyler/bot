import datetime
from playhouse.migrate import *
from playhouse.shortcuts import ReconnectMixin
from database.config import *
import peewee
from playhouse.mysql_ext import JSONField


class ReconnectMySQLDatabase(ReconnectMixin, peewee.MySQLDatabase):
    """
        Класс для переподключения к бд если подключение упало
    """
    pass


db = ReconnectMySQLDatabase(**Constants.DB_CONNECTION_PARAMS)
migrator = MySQLMigrator(db)


class BaseModel(peewee.Model):
    """
        Базовая модель с нужным наследником и коннекшином
    """

    class Meta:
        database = db


class Languages(BaseModel):
    """
        Таблица доступных языков
        (на данный момент 1 - русский 2 - узбекский)
    """
    title = peewee.CharField(max_length=16,
                             help_text='язык текста')


class BotMessages(BaseModel):
    """
        Таблица с текстом бота,
        language -  код языка
        text id -   код фразы
        text -      фраза
    """
    language = peewee.ForeignKeyField(Languages,
                                      on_delete='CASCADE')
    text_id = peewee.CharField(max_length=128,
                               help_text='айди текста')
    text = peewee.CharField(max_length=2048,
                            help_text='сам текст')


class Cities(BaseModel):
    """
        Доступные города в боте
    """
    title = peewee.CharField(max_length=48,
                             help_text='Название города')


class Users(BaseModel):
    """
        Пользователи, их данные
    """

    class Meta:
        primary_key = False

    id = peewee.IntegerField(primary_key=True,
                             help_text='Айди пользователя в системе и в телеграмме')
    session = JSONField(default={},
                        help_text='Временные данные пользователя '
                                  '(чтоб при резете не сбрасывались некоторые формы допустим)')
    username = peewee.CharField(max_length=Constants.Length.Telegram.USERNAME,
                                help_text='Юзернейм пользователя (чтоб была возможность обратится к нему в телеграмме)',
                                null=True)
    first_name = peewee.CharField(max_length=Constants.Length.Telegram.FIRST_NAME,
                                  help_text='Имя пользователя в телеграмме !!!НЕ МОЖЕТ БЫТЬ ПУСТЫМ!!!')
    phone = peewee.CharField(max_length=Constants.Length.Telegram.PHONE,
                             null=True,
                             help_text='Номер телефона пользователя (для бота + для связи)')
    status = peewee.CharField(choices=Constants.STATUSES,
                              help_text='Статус пользователя',
                              default=Constants.STATUSES[0])
    expire_status_date = peewee.DateTimeField(null=True,
                                              help_text='Дата когда статус пропадет')
    available_posts = peewee.IntegerField(help_text='Количество доступных постов на сегодня')
    refresh_date = peewee.DateField(help_text='Дата обновления кол-во постов',
                                    null=True)
    amount_warnings = peewee.IntegerField(help_text='Количество плохих объявлений',
                                          default=0)
    amount_posts = peewee.IntegerField(default=0,
                                       help_text='Количество пройденных модерацию постов у пользователя')
    city = peewee.ForeignKeyField(Cities,
                                  null=True,
                                  on_delete='CASCADE')

    balance = peewee.IntegerField(default=0, help_text="Баланс в сумах")

    card = peewee.CharField(max_length=16, help_text="Номер карты пользователя")


class Patterns(BaseModel):
    """
        Шаблоны для категорий, создано для разделения товаров бота,
        можно создать шаблон: услуги, товары, съемка квартир и так далее
    """
    title = peewee.CharField(max_length=32)


class PatternProps(BaseModel):
    """
        Свойства шаблона, пример:

        шаблон: товар;
        название, цена, описание, фотки;

        шаблон: услуга;
        название, цена за час, мастер;

        и т.д.
    """
    pattern = peewee.ForeignKeyField(Patterns,
                                     on_delete='CASCADE')
    format_ = peewee.CharField(max_length=16)


class Categories(BaseModel):
    """
        Категории в шаблоне,
        parent_id    - родитель категории (если есть)
        title        - название
        item_pattern - шаблон по которому будет производится
                       создание и вывод элементов публикации
    """
    parent_id = peewee.IntegerField(null=True,
                                    help_text='Айди категории (если это подкатегория)')
    pattern_id = peewee.ForeignKeyField(Patterns,
                                        Patterns.id,
                                        # default=Patterns.get_by_id(1),
                                        on_delete='CASCADE')
    status = peewee.BooleanField(default=True)
    buy_status = peewee.BooleanField(default=False)


class Pictures(BaseModel):
    """
        Таблица с картинками
    """
    image = peewee.BlobField(help_text='Поле с картинкой, !!!ОБЯЗАТЕЛЬНО LONG BLOB!!!')


class KeyWord(BaseModel):
    """
        Ключевые слова, для поиска по ним же
    """
    word = peewee.CharField(max_length=32,
                            unique=True)


class Post(BaseModel):
    """
        Посты в боте
    """
    owner = peewee.ForeignKeyField(Users,
                                   on_delete='CASCADE')
    category_id = peewee.ForeignKeyField(Categories,
                                         on_delete='CASCADE',
                                         help_text='Категория продукта')

    pictures = peewee.ManyToManyField(Pictures,
                                      backref='posts',
                                      on_delete='CASCADE')

    moderate = peewee.BooleanField(help_text='Поле показывающее на публикации ли объявление или нет, '
                                             'если модераторство отключену, сразу Истина',
                                   default=True)
    active = peewee.BooleanField(help_text='Активно ли объявления',
                                 default=False)
    deleted = peewee.BooleanField(help_text='Удалено ли объявление',
                                  default=False)
    description_claim = peewee.CharField(null=True,
                                         max_length=255,
                                         help_text='Причина изменения или удаления объявления')
    city = peewee.ForeignKeyField(Cities,
                                  on_delete='CASCADE')
    views = peewee.IntegerField(help_text='количество просмотров поста',
                                default=0)
    keywords = peewee.ManyToManyField(KeyWord,
                                      backref='posts',
                                      on_delete='CASCADE')
    longitude = peewee.FloatField(null=True)
    latitude = peewee.FloatField(null=True)
    status = peewee.BooleanField(default=True)
    currency = peewee.CharField(default='')
    buy_status = peewee.BooleanField(default=False,
                                     help_text='Если 0 - продажа, если 1 - покупка')

    chosen_channels = peewee.CharField(max_length=128, null=True,
                                       help_text="Если польщователь выбирает каналы -"
                                                 "айди каналов записываются через запятую")


class ProductProps(BaseModel):
    """
        Свойства продукта,
        цена - 20000, цвет - зеленый,
        и ссылка на сам продукт
    """
    product = peewee.ForeignKeyField(Post,
                                     on_delete='CASCADE')
    prop = peewee.ForeignKeyField(PatternProps,
                                  on_delete='CASCADE')
    value = peewee.TextField()


# longitude = peewee.FloatField(null=True)
# latitude = peewee.FloatField(null=True)

# currency = peewee.CharField(default='$')
# buy_status = peewee.BooleanField(default=False,
#                                  help_text='Если 0 - продажа, если 1 - покупка')
# migrate(
# migrator.drop_column('itempatterns', 'title'),
# migrator.rename_column('PatternsPropsMultilang', 'item_pattern', 'pattern'),
#     migrator.drop_column('categories', 'quality'),
# migrator.add_column('Post', 'longitude', longitude),
# migrator.add_column('Post', 'buy_status', buy_status),
# )


PostPictures = Post.pictures.get_through_model()
PostKeywords = Post.keywords.get_through_model()


class Settings(BaseModel):
    """
        Настройки бота
    """
    title = peewee.CharField(max_length=Constants.Length.Settings.TITLE,
                             help_text='Название настройки')
    value = peewee.CharField(max_length=Constants.Length.Settings.VALUE,
                             help_text='Значение настройки')
    endings = peewee.CharField(max_length=Constants.Length.Settings.ENDINGS,
                               help_text='Окончание, наприме: 20 *штук*, 20 *часов*, '
                                         'где 20 - value; штук, часов - endings (для красивого вывода)')


class Statistic(BaseModel):
    """
        Статистика по посещаемости бота
    """

    class Meta:
        primary_key = False

    view_date = peewee.DateField(default=datetime.date.today(),
                                 help_text='Дата за которую собрано количество людей',
                                 primary_key=True)
    amount_users = peewee.SmallIntegerField(help_text='Количество пользователей за день')


class CategoriesMultiLang(BaseModel):
    """
        Мультиязычность для категорий
    """
    language = peewee.ForeignKeyField(Languages,
                                      on_delete='CASCADE')
    category = peewee.ForeignKeyField(Categories,
                                      on_delete='CASCADE')
    title = peewee.CharField(max_length=64,
                             help_text='сам текст')


class PatternsMultiLang(BaseModel):
    """
        Мультиязычность для категорий
    """
    language = peewee.ForeignKeyField(Languages,
                                      on_delete='CASCADE')
    pattern = peewee.ForeignKeyField(Patterns,
                                     on_delete='CASCADE')
    title = peewee.CharField(max_length=64,
                             help_text='сам текст')


class PatternsPropsMultilang(BaseModel):
    """
        Мультиязычность для категорий
    """
    language = peewee.ForeignKeyField(Languages,
                                      on_delete='CASCADE')
    patternprop = peewee.ForeignKeyField(PatternProps,
                                         on_delete='CASCADE')
    title = peewee.CharField(max_length=512,
                             help_text='вопрос', )
    title_in_list = peewee.CharField(max_length=64)


class Channel(BaseModel):
    """
        Каналы, в которые будут отправляться объявления
    """

    name = peewee.CharField(max_length=64,
                            help_text="Название канала")

    channel_id = peewee.CharField(max_length=120,
                                  help_text="Айди канала, вводить нужно в кавчках!")

    pattern_id = peewee.ForeignKeyField(PatternsMultiLang,
                                        on_delete='CASCADE')

    channel_owner_id = peewee.CharField(max_length=24,
                                        help_text="Айди владельца канала")

    price_for_post = peewee.IntegerField(help_text="Цена за одно объявление в канале в сумах",
                                         default=0)

    selected = peewee.BooleanField(default=False)


class Transaction(BaseModel):
    user_id = peewee.ForeignKeyField(Users, on_delete='CASCADE',
                                     help_text='ID пользователь, производящий транзакцию')

    trans_sum = peewee.IntegerField(null=False,
                                    help_text='Сумма транзакции')

    trans_type = peewee.BooleanField(default=False,
                                     help_text='0 - Пополнение баланса,'
                                               '1 - вывод денег с баланса')
    trans_date = peewee.DateTimeField(help_text="Дата и время транзакции",
                                      default=datetime.datetime.now())

    def save(self, *args, **kwargs):
        self.trans_date = datetime.datetime.now()
        return super(Transaction, self).save(*args, **kwargs)


class Reaction(BaseModel):
    language = peewee.ForeignKeyField(Languages, on_delete="CASCADE")

    text_id = peewee.CharField(max_length=128)

    text = peewee.CharField(max_length=2048)
