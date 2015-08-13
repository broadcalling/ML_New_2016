"""
Student progress page
"""
from bok_choy.page_object import PageObject
from .course_page import CoursePage


class ProgressPage(CoursePage):
    """
    Student progress page.
    """

    url_path = "progress"

    def is_browser_on_page(self):
        is_present = (
            self.q(css='div.course-info').present and
            self.q(css='div#grade-detail-graph').present
        )
        return is_present

    @property
    def grading_formats(self):
        return [label.replace(' Scores:', '') for label in self.q(css="div.scores h4").text]

    @property
    def has_passing_information_table(self):
        """
        Indicates whether progress page has a PassingInformationTable.
        """
        return PassingInformationTable.is_present(self)

    @property
    def passing_information_table(self):
        """
        Returns PassingInformationTable instance.
        """
        return PassingInformationTable(self.browser)

    def scores(self, chapter, section):
        """
        Return a list of (points, max_points) tuples representing the scores
        for the section.

        Example:
            scores('Week 1', 'Lesson 1') --> [(2, 4), (0, 1)]

        Returns `None` if no such chapter and section can be found.
        """

        # Find the index of the section in the chapter
        chapter_index = self._chapter_index(chapter)
        if chapter_index is None:
            return None

        section_index = self._section_index(chapter_index, section)
        if section_index is None:
            return None

        # Retrieve the scores for the section
        return self._section_scores(chapter_index, section_index)

    def _chapter_index(self, title):
        """
        Return the CSS index of the chapter with `title`.
        Returns `None` if it cannot find such a chapter.
        """
        chapter_css = 'div.chapters section h2'
        chapter_titles = self.q(css=chapter_css).map(lambda el: el.text.lower().strip()).results

        try:
            # CSS indices are 1-indexed, so add one to the list index
            return chapter_titles.index(title.lower()) + 1
        except ValueError:
            self.warning("Could not find chapter '{0}'".format(title))
            return None

    def _section_index(self, chapter_index, title):
        """
        Return the CSS index of the section with `title` in the chapter at `chapter_index`.
        Returns `None` if it can't find such a section.
        """

        # This is a hideous CSS selector that means:
        # Get the links containing the section titles in `chapter_index`.
        # The link text is the section title.
        section_css = 'div.chapters>section:nth-of-type({0}) div.sections div h3 a'.format(chapter_index)
        section_titles = self.q(css=section_css).map(lambda el: el.text.lower().strip()).results

        # The section titles also contain "n of m possible points" on the second line
        # We have to remove this to find the right title
        section_titles = [t.split('\n')[0] for t in section_titles]

        # Some links are blank, so remove them
        section_titles = [t for t in section_titles if t]

        try:
            # CSS indices are 1-indexed, so add one to the list index
            return section_titles.index(title.lower()) + 1
        except ValueError:
            self.warning("Could not find section '{0}'".format(title))
            return None

    def _section_scores(self, chapter_index, section_index):
        """
        Return a list of `(points, max_points)` tuples representing
        the scores in the specified chapter and section.

        `chapter_index` and `section_index` start at 1.
        """
        # This is CSS selector means:
        # Get the scores for the chapter at `chapter_index` and the section at `section_index`
        # Example text of the retrieved elements: "0/1"
        score_css = "div.chapters>section:nth-of-type({0}) div.sections>div:nth-of-type({1}) div.scores>ol>li".format(
            chapter_index, section_index
        )

        text_scores = self.q(css=score_css).text

        # Convert text scores to tuples of (points, max_points)
        return [tuple(map(int, score.split('/'))) for score in text_scores]


class PassingInformationTable(PageObject):
    """
    PassingInformationTable page object wrapper
    """
    url = None
    TABLE_SELECTOR = '.grade-category-detail-table'

    def __init__(self, browser):
        super(PassingInformationTable, self).__init__(browser)

    def find_css(self, selector):
        """
        Returns a query corresponding to the given CSS selector within the scope
        of this discussion page
        """
        return self.q(css=self.TABLE_SELECTOR + " " + selector)

    def is_browser_on_page(self):
        """
        Verify that the browser is on the page and it is not still loading.
        """
        return PassingInformationTable.is_present(self)

    @classmethod
    def is_present(cls, page):
        """
        Indicates whether progress page has a PassingInformationTable.
        """
        return page.q(css=cls.TABLE_SELECTOR).present

    @property
    def status(self):
        """
        Returns a list of tuples with information about the categories:
        [('Homework', '50', '25', 'Not pass'), ('Lab', '50', '75', 'Pass')]
        """
        rows = self.find_css('tbody tr')
        # Unfortunetly rows.text returns us information in appropriate fromat.
        # That's why we need to get the text of each nested <td> manualy.
        assignments_info = rows.map(lambda el: [x.text for x in el.find_elements_by_css_selector('td')])
        return [tuple(info) for info in assignments_info]
