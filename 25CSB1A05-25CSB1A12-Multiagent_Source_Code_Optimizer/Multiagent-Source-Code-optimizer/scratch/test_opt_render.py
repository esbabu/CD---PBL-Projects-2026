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
    
    # Target transformation list items in the sidebar
    items = driver.find_elements('css selector', 'ul.space-y-1\\.5 > li')
    print('Filtered Optimized items:', len(items))
    for i, it in enumerate(items[:5]):
        print(f'Item {i} text:', it.text[:100].replace('\n', ' -- '))
        im_name = f'scratch/sample_opt_{i}.png'
        it.screenshot(im_name)
        im = Image.open(im_name)
        print(f'Item {i} size:', im.size)
finally:
    driver.quit()
