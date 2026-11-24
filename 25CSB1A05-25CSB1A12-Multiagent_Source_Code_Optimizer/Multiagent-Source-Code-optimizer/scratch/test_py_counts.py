from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1600,1000')

driver = webdriver.Chrome(options=options)
try:
    driver.get('http://localhost:5173')
    time.sleep(2)
    with open('scratch/vulnerable_samples.py', 'r', encoding='utf-8') as f:
        py_code = f.read()

    driver.execute_script('window.__COMPILER_AI__.setMode("pipeline")')
    driver.execute_script('window.__COMPILER_AI__.setLanguage("python")')
    driver.execute_script('window.__COMPILER_AI__.setSourceCode(arguments[0])', py_code)
    time.sleep(0.5)
    driver.execute_script('window.__COMPILER_AI__.startRun()')

    for _ in range(40):
        time.sleep(0.5)
        st = driver.execute_script('return window.__COMPILER_AI__.getState()')
        if st and st.get('status') == 'completed':
            break

    driver.execute_script('window.__COMPILER_AI__.setActiveTab("security")')
    time.sleep(1)
    
    sec_cards = driver.find_elements('css selector', 'div.space-y-3 > div.rounded-xl')
    print('Filtered Python Security cards:', len(sec_cards))
    if sec_cards:
        print('First PY sec card:', sec_cards[0].text[:100].replace('\n', ' -- '))
        print('Last PY sec card:', sec_cards[-1].text[:100].replace('\n', ' -- '))

    driver.execute_script('window.__COMPILER_AI__.setActiveTab("optimized_code")')
    time.sleep(1)
    
    opt_items = driver.find_elements('css selector', 'ul.space-y-1\\.5 > li')
    print('Filtered Python Optimized items:', len(opt_items))
    if opt_items:
        print('First PY opt item:', opt_items[0].text[:100].replace('\n', ' -- '))
        print('Last PY opt item:', opt_items[-1].text[:100].replace('\n', ' -- '))
finally:
    driver.quit()
