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

    for _ in range(40):
        time.sleep(0.5)
        st = driver.execute_script('return window.__COMPILER_AI__.getState()')
        if st and st.get('status') == 'completed':
            break

    # Security Tab
    driver.execute_script('window.__COMPILER_AI__.setActiveTab("security")')
    time.sleep(1)
    sec_cards = driver.find_elements('css selector', 'div.rounded-xl.border')
    print('CPP Security cards count:', len(sec_cards))
    if sec_cards:
        print('First CPP sec card:', sec_cards[0].text[:80].replace('\n', ' -- '))
        print('Last CPP sec card:', sec_cards[-1].text[:80].replace('\n', ' -- '))

    # Optimized Tab
    driver.execute_script('window.__COMPILER_AI__.setActiveTab("optimized_code")')
    time.sleep(1)
    opt_cards = driver.find_elements('css selector', 'li.rounded-lg.border')
    print('CPP Optimized cards count:', len(opt_cards))
    if opt_cards:
        print('First CPP opt card:', opt_cards[0].text[:80].replace('\n', ' -- '))
        print('Last CPP opt card:', opt_cards[-1].text[:80].replace('\n', ' -- '))

    # Now test Python
    with open('scratch/vulnerable_samples.py', 'r', encoding='utf-8') as f:
        py_code = f.read()

    driver.execute_script('window.__COMPILER_AI__.setLanguage("python")')
    driver.execute_script('window.__COMPILER_AI__.setSourceCode(arguments[0])', py_code)
    time.sleep(0.5)
    driver.execute_script('window.__COMPILER_AI__.startRun()')

    for _ in range(40):
        time.sleep(0.5)
        st = driver.execute_script('return window.__COMPILER_AI__.getState()')
        if st and st.get('status') == 'completed':
            break

    # Python Security Tab
    driver.execute_script('window.__COMPILER_AI__.setActiveTab("security")')
    time.sleep(1)
    py_sec_cards = driver.find_elements('css selector', 'div.rounded-xl.border')
    print('PY Security cards count:', len(py_sec_cards))
    if py_sec_cards:
        print('First PY sec card:', py_sec_cards[0].text[:80].replace('\n', ' -- '))
        print('Last PY sec card:', py_sec_cards[-1].text[:80].replace('\n', ' -- '))

    # Python Optimized Tab
    driver.execute_script('window.__COMPILER_AI__.setActiveTab("optimized_code")')
    time.sleep(1)
    py_opt_cards = driver.find_elements('css selector', 'li.rounded-lg.border')
    print('PY Optimized cards count:', len(py_opt_cards))
    if py_opt_cards:
        print('First PY opt card:', py_opt_cards[0].text[:80].replace('\n', ' -- '))
        print('Last PY opt card:', py_opt_cards[-1].text[:80].replace('\n', ' -- '))

finally:
    driver.quit()
