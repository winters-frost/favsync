from selenium import webdriver

driver = None


def __init():
    global driver
    if driver is None:
        options = webdriver.FirefoxOptions()
        options.set_headless(True)
        driver = webdriver.Firefox(options=options)


def get_page_source(url):
    global driver
    # Initialize the driver if not already done
    if driver is None:
        __init()

    driver.get(url)
    return driver.page_source


def cleanup():
    global driver
    if not(driver is None):
        driver.close()
