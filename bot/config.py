# from bot import project_configuration
from database.config import Constants as db_const
from database.config import Constants
from global_var import TOKEN
from database.models import Users


class Constants(Constants):
    class Telegram:
        TOKEN = TOKEN
        TIMEOUT_BEFORE_OUTPUT_MODERATE_POSTS = .3
        STATUSES_PICTURES = {status: pic for status, pic in zip(db_const.STATUSES,
                                                                ('👨‍💼',
                                                                 '🤵',
                                                                 '🧟',
                                                                 '🦸‍♂️',
                                                                 '🦹‍♀️',
                                                                 '🧖‍♂️'))}
        STATUSES_TITLES = {status: pic for status, pic in zip(db_const.STATUSES,
                                                              ('👨‍💼 Обычный',
                                                               '🤵 Вип',
                                                               '🧟 Заблокированный',
                                                               '🦸‍♂️Модератор',
                                                               '🦹‍♀️Администратор',
                                                               '🧖‍♂️ Главный администратор'))}

    class Paths:
        TEMP_PHOTOS = 'temp_photos/'


class Commands:
    """
        Все доступные боту команды
    """
    START = ['start']
    ADD_POST = ['add', 'add_post']
    MY_POST = ['my', 'my_post']
    MY_BALANCE = ['my_balance']
    ADD_BALANCE = ['add_balance']
    WITHDRAW_BALANCE = ['withdraw_balance']
    PARTNER = ['partner']
    MODERATE = ['moderate']
    POSTED = ['posted']
    DELETED = ['deleted']
    SEARCH = ['search']
    HELP = ['help']
    PRIVATE_OFFICE = ['account']
    LANGUAGE = ['language']


COMMAND_DESCRIPTIONS = {Commands.HELP[0]: 'Меню помощи',
                        Commands.PRIVATE_OFFICE[0]: 'Личный кабинет',
                        Commands.START[0]: 'Стартовое меню бота',
                        Commands.SEARCH[0]: 'Поиск объявления',
                        Commands.ADD_POST[0]: 'Добавить новое объявление',
                        Commands.MY_POST[0]: 'Мои объявления',
                        Commands.MY_BALANCE[0]: 'Баланс',
                        Commands.ADD_BALANCE[0]: 'Поплнить баланс',
                        Commands.WITHDRAW_BALANCE[0]: 'Вывести деньги',
                        Commands.PARTNER[0]: 'Партнёрам',
                        Commands.MODERATE[0]: 'Модерированные объявления',
                        Commands.POSTED[0]: 'Активные объявления',
                        Commands.DELETED[0]: 'Удалённые объявления',
                        Commands.LANGUAGE[0]: 'Сменить язык',
                        }

COMMAND_DESCRIPTIONS_ON_UZB = {Commands.HELP[0]: 'Ёрдам менюси',
                               Commands.PRIVATE_OFFICE[0]: 'Шахсий Кабинет',
                               Commands.START[0]: 'Ботнинг бошлангич менюси',
                               Commands.SEARCH[0]: 'Элонларни кидирув булим',
                               Commands.ADD_POST[0]: 'Янги элон кушиш',
                               Commands.WITHDRAW_BALANCE[0]: 'Пул ечиб олиш',
                               Commands.MY_POST[0]: 'Менинг элонларим',
                               Commands.PARTNER[0]: 'Хамкорларга',
                               Commands.MY_POST[0]: 'Менинг элонларим',
                               Commands.MY_BALANCE[0]: 'Баланс',
                               Commands.MODERATE[0]: 'Куриб чикиш холатидаги элонлар',
                               Commands.POSTED[0]: 'Чоп этилган элонлар',
                               Commands.DELETED[0]: 'Учирилган элонлар',
                               }


class Callbacks:
    CATEGORY = 'category_{}'                       # категория айди или направление влево или вправо + отступ
    USERS_CHANGER = 'users_{}'          # статус пользователя который просматривает + айди, или влево и вправо + оффсет
    POSTS_CHANGER = 'posts_{}'                     # тест
    OWN_POSTS_CHANGER = 'own_posts_{}'             # тест
    USER_EDIT = 'useredit_{}'                      # что сделать + айди человека
    POST_DELETE = 'postedit_{}'                    # тест
    OWN_POST_DELETE = 'postedit_{}'                # тест
    SEARCH_POSTS = 'searchpost_{}'                 # айди категории для поиска объявлений
    CHANGE_CATEGORIES = 'changecat_{}'             # изменение категории
    BALANCE = 'balance_{}'                         # Баланс (тест)
    ADD_BALANCE = 'add_balance_{}'                 # Пополнить баланс
    WITHDRAW_BALANCE = 'withdraw_balance_{}'       # Вывести деньги
    PARTNER = 'partner_{}'                         # Партнёрам
    CHOOSE_CHANNEL_FOR_POST = 'choose_channel_{}'  # Выбор каналов
    SETTINGS = 'setting_{}'
    RegistrationCity = 'city_{}'
    ChangeCity = 'chcity_{}'
    SEARCH_CITY = 'searchcity_{}'
    MODERATE_POST = 'moderatepost_{}'
    GetGeo = 'getgeo_{}'
    ChangeText = 'oldtextid_{}'

    class Direction:
        LEFT = 'left'
        RIGHT = 'right'

    PatternSearchPost = 'patternsearch_{}'
    Pattern = 'pattern_{}'
    AdminPattern = 'apattern_{}'

    PatternAdd = 'patternadd'
    PatternChange = 'patternchange'
    PatternRemove = 'patternremove'
    PatternEditCategories = 'pateditcat_{}'
    PatternEditAnswer = 'pateditansw_{}'

    BackToStart = 'to_start'

    QuestionToEdit = 'questtoedit_{}'

    Continue = 'continue'


class Keyboards:
    """
        Клавиатуры используемые в боте, в формате список в списке, где:
            внешний список - вся клавиатуры;
            внутренний - один ряд;
    """
    PREVIEW = [['Buttons.Menu.Preview.RESET', 'Buttons.Menu.Preview.LIKE']]
    YES_OR_NOT = [['Buttons.NO', 'Buttons.YES']]
    SearchTypes = [['Buttons.SearchByCategories', 'Buttons.SearchByKeyWords']]
    SetStatus = [['Button.NoStatus', 'Button.SetStatus']]
    GetStatus = [['Button.Old', 'Button.New']]
    Currencies = [['dollar', 'summ']]
    ReEditPost = [['create_post_again', 'post_it']]
    BuyStatus = [['Buy', 'Sell']]

    class Menu:
        POSTS = [['Buttons.Menu.Post.ADD'],
                 ['Buttons.Menu.Post.MODERATE', 'Buttons.Menu.Post.POSTED'],
                 ['Buttons.Menu.Post.DELETE', 'Buttons.Menu.Post.DELETED'],
                 ['Buttons.MAIN_MENU']]

        BALANCE = [['Buttons.Account.Card'],
                  ['Buttons.Menu.Balance.Add', 'Buttons.Menu.Balance.Withdraw'],
                  ['Buttons.Account.TransactionHistory'],
                   ['Buttons.ACCOUNT', 'Buttons.MAIN_MENU']]

        MY_CARD = [['Buttons.Account.AddCard'],
                   ['Buttons.Account.DeleteCard'],
                   ['Buttons.ACCOUNT']]

        ADD_CARD = [['Buttons.Direction.BACK']]

        PAYMENT = [['Buttons.Pay'],
                   ['Buttons.Account.BALANCE']]

        ADD_BALANCE = [['Buttons.Menu.Click'],
                       ['Buttons.Menu.Payme'],
                       ['Buttons.MAIN_MENU']]

        ADD_SUM = [['Buttons.Direction.BACK']]

        WITHDRAW_BALANCE = [['Buttons.Direction.BACK']]

        CARD_CONFIRMATION = [['Buttons.YES', 'Buttons.NO']]

        PARTNERS = [['Buttons.Menu.Partner.BecomePartner'],
                    ['Buttons.MAIN_MENU']]

        EDIT_POST = [['Buttons.Menu.PostEdit.EDIT_AND_POST', 'Buttons.Menu.PostEdit.POST'],
                     ['Buttons.Menu.PostEdit.DELETE']]

        EDIT_POST_PART = [['Buttons.Menu.PostEdit.TITLE', 'Buttons.Menu.PostEdit.DESCRIPTION',
                           'Buttons.Menu.PostEdit.PRICE']]

        OWN_POST_DELETE = [['Buttons.PostEdit.DELETE_POST']]

        CHANGE_LIST_OF_USERS = [['Buttons.Direction.LEFT', 'Buttons.Direction.BACK', 'Buttons.Direction.RIGHT']]

        REMOVE_POST = [['Buttons.Menu.PostEdit.DELETE']]

        SEARCH_PRODUCT_STATUS = [['Buttons.ProductStatus.ALL'],
                                 ['Buttons.ProductStatus.OLD', 'Buttons.ProductStatus.NEW']]

        SEARCH_POSTS = [['Buttons.Direction.LEFT_POST', 'Buttons.Direction.RIGHT_POST']]

        ACCOUNT = [['Buttons.Account.MY_POSTS', 'Buttons.Account.BALANCE'],
                   ['Buttons.Account.CHANGE_CITY', 'Buttons.Account.ChangeLanguage'],
                   ['Buttons.Account.PARTNER'],
                   ['Buttons.MAIN_MENU']]

        Language = [['Button.Language.Russia', 'Button.Language.Uzb']]

        class AddPost:
            PRODUCT_STATUS = [['Buttons.ProductStatus.OLD', 'Buttons.ProductStatus.NEW']]

        class Moderator:
            USER_EDIT = [['Buttons.UserEdit.BLOCK_USER', 'Buttons.UserEdit.PROVIDE_VIP'],
                         ['Buttons.UserEdit.UNBLOCK_USER'], ['Buttons.UserEdit.REMOVE_VIP']]
            POST_DELETE = [['Buttons.PostEdit.DELETE_POST']]

        class Admin:
            USER_EDIT = [['Buttons.UserEdit.BLOCK_USER', 'Buttons.UserEdit.PROVIDE_VIP'],
                         ['Buttons.UserEdit.UNBLOCK_USER'], ['Buttons.UserEdit.REMOVE_VIP'],
                         ['Buttons.UserEdit.PROVIDE_MODERATION']]
            CATEGORIES_EDIT = [['Buttons.Menu.CategoriesEdit.REMOVE', 'Buttons.Menu.CategoriesEdit.CHANGE',
                                'Buttons.Menu.CategoriesEdit.ADD']]
            POST_DELETE = [['Buttons.PostEdit.DELETE_POST']]

        class MainAdmin:
            USER_EDIT = [['Buttons.UserEdit.BLOCK_USER', 'Buttons.UserEdit.PROVIDE_VIP'],
                         ['Buttons.UserEdit.UNBLOCK_USER'], ['Buttons.UserEdit.REMOVE_VIP'],
                         ['Buttons.UserEdit.PROVIDE_MODERATION', 'Buttons.UserEdit.PROVIDE_ADMIN']]
            POST_DELETE = [['Buttons.PostEdit.DELETE_POST']]

        class Main:
            USUAL = [['Buttons.Menu.Post.ADD'],
                     ['Buttons.WATCH_POSTS', 'Buttons.ACCOUNT']]
            BLOCKED = [['Buttons.WATCH_POSTS']]
            MODERATOR = [['Buttons.Menu.Moderator.NEW', 'Buttons.Menu.Moderator.WORK_WITH_USERS'],
                         ['Buttons.WATCH_POSTS', 'Buttons.ACCOUNT'], ]
            ADMIN = [['Buttons.Menu.Moderator.NEW', 'Buttons.Menu.Moderator.WORK_WITH_POSTS',
                      'Buttons.Menu.Moderator.WORK_WITH_USERS'],
                     ['Buttons.Menu.Admin.CATEGORY', 'Button.Patterns', 'Buttons.ACCOUNT'],
                     ['Buttons.WATCH_POSTS', 'Buttons.Menu.Admin.SETTINGS'],
                     ['Buttons.Menu.Activity', 'Buttons.Menu.Post.ADD'],
                     ['Buttons.ChangeQuestionResponse']
                     # ['Buttons.ChangeIcon']
                     ]

        class Search:
            GET_GEO = [['Buttons.GetGeo']]
            GetCurrentGeo = [['Buttons.GetCurrentGeo']]


class BotMessages:
    """
        Все сообщения бота, поделенные на роли
    """

    class Help:
        START = '👋 <b>Добрый день!</b>\n\n🆘 <b>Вы</b> читаете сообщение об использовании бота!)\n☝️ ' \
                'Если вы никогда не пользовался ботами в Telegram,\nя вам расскажу как я устроен;\n\n1️⃣' \
                ' <b>Навигация:</b>\nДля взаимодействия с ботом вам всегда будут предлагать нажать на какую-либо ' \
                'кнопку, она может быть как в самом чате прикреплена к сообщению, так и внизу возле поля ввода.\n' \
                'Зачастую разработчик продумывает все сценарии работы с ботом, и моментов когда кнопки не работают' \
                'ли что-то пошло не так бывают не часто, однако бывают. Для выхода из подобной ситуации пропишите ' \
                'команду <code>/start</code>, которая перенаправит вас на основное меню и всё снова заработает.\n\n' \
                'Далее пункты описывающие поведения бота пойдут персонально для каждого.\n\n2️⃣ <b>Поиск ' \
                'объявлений:</b>\nДля поиска необходимого продукта в боте, в стартовом меню (<code>/start</code>) ' \
                'нажмите кнопку <b>"{Buttons.WATCH_POSTS}"</b>, или пропишите команду <code>/{Commands.SEARCH[0]}' \
                '</code>.\n' \
                'Вам будет предоставлен список <b>🗂 категорий</b> продуктов которые имеются в боте, вам нужно будет ' \
                'выбрать интересующую вас категорию или нажать кнопку <b>"{Buttons.Direction.BACK}"</b> для выхода в ' \
                'главное меню.\nТак как категорий много не всегда в списке могут поместиться сразу все, обычно на ' \
                'одной страницы в категориях помещаются {db_const.LIMIT_CATEGORIES} категорий, поэтому есть под ними ' \
                'сразу 2 кнопки (<b>"{Buttons.Direction.LEFT}"</b>, <b>"{Buttons.Direction.RIGHT}"</b>) для навигации ' \
                'по страницам. После выбора необходимой категории вам будет предоставлен выбор из возможных ' \
                'подкатегорий, если таковые имеются, и после, вам будет предоставлен список объявлений по нужной вам' \
                ' категории.\nОна будет иметь подобный функционал с навигацией как и категории, с помощью кнопок' \
                ' <b>"{Buttons.Direction.LEFT}"</b> и <b>"{Buttons.Direction.RIGHT}"</b> вы сможете листать список ' \
                'доступных объявлений.\nВсе объявления отсортированы по дате создания (вначале самые новые).\n\n'

        # нужно доделать...
        # HELP = {db_const.STATUSES[0]: START + '3️⃣ <b>Д</b>'}
