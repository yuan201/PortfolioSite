from selenium.webdriver.firefox.webdriver import WebDriver

from django.contrib.staticfiles.testing import StaticLiveServerTestCase


# todo a whole lot to do for functional test
class NewPortfolioTest(StaticLiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(NewPortfolioTest, cls).setUpClass()
        cls.browser = WebDriver()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(NewPortfolioTest, cls).tearDownClass()

    def test_create_new_portfolio(self):
        # Yuan found this new website which can help him manage investment portfolios
        self.browser.get(self.live_server_url)
        # On the front page, he nothing since no portfolios has been created
        # The title of the page is simply called portfolios
        self.assertIn('Portfolio', self.browser.title)

        # Follow the link for creating new portfolios
        link = self.browser.find_element_by_link_text('New Portfolio')
        link.click()

        # Enter portfolios name "Value" and description "Simple value portfolios"
        inputbox = self.browser.find_element_by_id('id_name')
        inputbox.send_keys('Value')

        inputbox = self.browser.find_element_by_id('id_description')
        inputbox.send_keys('Simple value portfolios')

        # Submit the form. This redirect him back to the front page
        inputbox.submit()

        # The front page now has a item 'value 1' which link to the page for the
        # portfolios
        page_text = self.browser.find_element_by_tag_name('body').text
        self.assertIn('Value', page_text)

        # Follow the link on the portfolios name, he finds a page summaries the portfolios
        # link = self.browser.find_element_by_link_text('Value')
        # link.click()





