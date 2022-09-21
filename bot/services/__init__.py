from bot.services import cities, \
    edit_users, \
    moderate_posts, \
    my_account, \
    my_post_work, \
    output_posts, \
    registration, \
    search_post, \
    settings, \
    statistic, \
    change_icon, \
    search_by_keyword, \
    change_questions_response,\
    work_with_channels,\
    my_balance_work,\
    partners,\
    balance
from bot.services.categories import edit_categories
from bot.services.patterns_work import patterns
from bot.services.adding_post import add_post
from bot.services.adding_channel import add_channel
from bot.services.for_partners import add_partner
from project_configuration import logger


logger.info('Import services')
