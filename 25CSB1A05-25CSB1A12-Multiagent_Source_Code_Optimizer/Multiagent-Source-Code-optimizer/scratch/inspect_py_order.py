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
    
    cards = driver.find_elements('css selector', 'div.space-y-3 > div.rounded-xl')
    print('Total PY Security Cards:', len(cards))
    for i in range(len(cards)):
        txt = cards[i].text.replace('\n', ' -- ')
        print(f'PY Card {i+1}: {txt[:120]}')

    driver.execute_script('window.__COMPILER_AI__.setActiveTab("optimized_code")')
    time.sleep(1)
    
    items = driver.find_elements('css selector', 'ul.space-y-1\\.5 > li')
    print('\nTotal PY Opt Items:', len(items))
    for i in range(len(items)):
        txt = items[i].text.replace('\n', ' -- ')
        print(f'PY Opt {i+1}: {txt[:120]}')

finally:
    driver.quit()
