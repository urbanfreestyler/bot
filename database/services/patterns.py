from typing import Union

from database.services.session import SessionWork as session
from database.models import Patterns, PatternsMultiLang, PatternProps, PatternsPropsMultilang, Categories, ProductProps, \
    Post


class PatternsWork:

    @staticmethod
    def get_patterns(chat_id: int) -> tuple:
        return tuple(PatternsMultiLang
                     .select(PatternsMultiLang.pattern,
                             PatternsMultiLang.title)
                     .where(PatternsMultiLang.language == 1).tuples())

    @staticmethod
    def get_title(chat_id: int, pattern_id: Union[str, int]) -> str:
        return PatternsMultiLang.get(language=session.get_lang_code(chat_id=chat_id),
                                     pattern=pattern_id).title

    @staticmethod
    def create(chat_id: int):
        pattern = Patterns()
        pattern.save()
        # pattern_titles = session.pop(chat_id=chat_id, key='pattern')
        pattern_titles = session.get(chat_id=chat_id, key='pattern')

        PatternsMultiLang(language=1,
                          pattern=pattern,
                          title=pattern_titles.pop('rus')).save()

        PatternsMultiLang(language=2,
                          pattern=pattern,
                          title=pattern_titles.pop('uzb')).save()

        # questions = session.pop(chat_id=chat_id,
        #                         key='questions')
        questions = session.get(chat_id=chat_id,
                                key='questions')

        for question in questions:
            props = PatternProps(pattern=pattern,
                                 format_=question.pop('format_'))
            props.save()

            PatternsPropsMultilang(language=1,
                                   patternprop=props,
                                   title=question.pop('rus'),
                                   title_in_list=question.pop('rus_title_in_list')).save()

            PatternsPropsMultilang(language=2,
                                   patternprop=props,
                                   title=question.pop('uzb'),
                                   title_in_list=question.pop('uzb_title_in_list')).save()

    @staticmethod
    def remove(pattern_id: str):
        Patterns.get(Patterns.id == pattern_id).delete_instance()

    @staticmethod
    def change(chat_id: int):
        pattern_id = session.pop(chat_id=chat_id,
                                 key='editable_pattern_id')
        rus, uzb = session.pop(chat_id=chat_id,
                               key='new_pattern_rus_title'), \
                   session.pop(chat_id=chat_id,
                               key='new_pattern_uzb_title')
        rus_pattern: PatternsMultiLang = PatternsMultiLang.get(language=1,
                                                               pattern=pattern_id)
        rus_pattern.title = rus
        rus_pattern.save()

        uzb_pattern: PatternsMultiLang = PatternsMultiLang.get(language=2,
                                                               pattern=pattern_id)
        uzb_pattern.title = uzb
        uzb_pattern.save()


def get_pattern_questions(pattern_id: str, chat_id: int = None) -> list:
    props = PatternProps\
        .select(PatternProps.id)\
        .where(PatternProps.pattern == pattern_id)

    language = PatternsPropsMultilang.language == (session.get_lang_code(chat_id=chat_id) if chat_id else 1)

    return list(PatternsPropsMultilang
                .select(PatternsPropsMultilang.patternprop.id,
                        PatternsPropsMultilang.patternprop.format_,
                        PatternsPropsMultilang.title,
                        PatternsPropsMultilang.title_in_list,)
                .join(PatternProps)
                .where(PatternsPropsMultilang.patternprop.in_(props) &
                       language).tuples())


def get_pattern_props_by_category(category_id: int, chat_id: int):
    return get_pattern_questions(pattern_id=Categories.get_by_id(category_id).pattern_id,
                                 chat_id=chat_id)


def get_product_props_with_names(post: Post):
    # props = ProductProps.select(ProductProps.id).where(ProductProps.product == post)
    language = PatternsPropsMultilang.language == session.get_lang_code(chat_id=post.owner.id)

    return list(PatternsPropsMultilang
                .select(PatternsPropsMultilang.title_in_list,
                        PatternProps.format_,
                        ProductProps.value)
                .join(PatternProps)
                .join(ProductProps)
                .where((ProductProps.product == post) &
                       language).tuples()
                )


def get_question_format(question_id: str) -> str:
    format_: str = PatternProps.get_by_id(question_id).format_
    return format_


def change_prop_format(prop_id: str, new_format: str):
    pattern_prop: PatternProps = PatternProps.get_by_id(prop_id)
    pattern_prop.format_ = new_format
    pattern_prop.save()


if __name__ == '__main__':
    session.set(chat_id=704369002,
                key='pattern',
                value={'rus': '?????????? ??????????????', 'uzb': '?????????? ??????????????_??????'})
    session.set(chat_id=704369002,
                key='questions',
                value=[{'rus': '1_????????????', 'uzb': '1_????????????_??????', 'format_': 'text_10', 'rus_title_in_list': '????????????????_????????????????_??????', 'uzb_title_in_list': '????????????????_????????????????_??????'}, {'rus': '2_????????????', 'uzb': '2_????????????_??????', 'format_': 'text_10', 'rus_title_in_list': '????????????????_????????????????_??????_2', 'uzb_title_in_list': '????????????????_????????????????_??????_2'}])
    PatternsWork.create(chat_id=704369002)
