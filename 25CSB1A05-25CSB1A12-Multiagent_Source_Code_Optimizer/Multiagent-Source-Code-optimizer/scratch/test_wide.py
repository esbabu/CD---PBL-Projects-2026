from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from PIL import Image

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1600,1000')

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

    driver.execute_script('window.__COMPILER_AI__.setActiveTab("optimized_code")')
    time.sleep(1)
    
    # Expand sidebar width so cards look great
    driver.execute_script("""
        const el = document.querySelector('ul.space-y-1\\\\.5');
        if (el) {
            el.closest('div.shrink-0').style.width = '1200px';
        }
    """)
    time.sleep(0.5)
    
    items = driver.find_elements('css selector', 'ul.space-y-1\\.5 > li')
    if items:
        items[0].screenshot('scratch/test_opt_wide.png')
        im = Image.open('scratch/test_opt_wide.png')
        print('Wide opt item size:', im.size)
        print('Item text:', items[0].text.replace('\n', ' -- '))
finally:
    driver.quit()
