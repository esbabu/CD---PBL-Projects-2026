from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')

driver = webdriver.Chrome(options=options)
try:
    driver.get('http://localhost:5173')
    time.sleep(2)
    with open('scratch/vulnerable_samples.cpp', 'r', encoding='utf-8') as f:
        cpp_code = f.read()

    driver.execute_script('window.__COMPILER_AI__.setMode("pipeline")')
    driver.execute_script('window.__COMPILER_AI__.setLanguage("cpp")')
    driver.execute_script('window.__COMPILER_AI__.setSourceCode(arguments[0])', cpp_code)
    time.sleep(0.5)
    driver.execute_script('window.__COMPILER_AI__.startRun()')

    for _ in range(30):
        time.sleep(0.5)
        st = driver.execute_script('return window.__COMPILER_AI__.getState()')
        if st.get('status') == 'completed':
            break

    driver.execute_script('window.__COMPILER_AI__.setActiveTab("security")')
    driver.execute_script('window.__COMPILER_AI__.setResultsHeight(500)')
    time.sleep(1)

    cards = driver.find_elements('css selector', 'div[class*="border-l-4"]')
    print('Found cards count in Security tab:', len(cards))
    if cards:
        print('First card text snippet:', repr(cards[0].text[:80]))
finally:
    driver.quit()
