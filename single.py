from playwright.sync_api import sync_playwright, Page, BrowserContext, TimeoutError, expect
from datetime import datetime as dt
from playwright_stealth import stealth_sync
from pathlib import Path
import logging
import os
import yagmail
from datetime import datetime as dt

logging.basicConfig(filename='yoda-lair/logs/applogs.log', level=logging.INFO, 
format='%(asctime)s - %(levelname)s - %(name)s --- %(message)s', 
datefmt='%a %b %d %Y %H:%M:%S %z GMT')
appdata = os.getenv('appdata')

URL = 'https://freebitco.in/?op=home'

def roll(page: Page, profile:str):
    def check_final_balance():
        try:
            expect(page.locator('#balance_small')).not_to_have_text(init_bal, timeout=7000)
        except AssertionError:
            logging.critical('ROLL FAILED: Current balance equal to previous')
            return
            
        after_bal = page.locator('#balance_small').text_content()
        print(f'BALANCE AFTER: {after_bal}\n')
        logging.info('BALANCE AFTER: '+after_bal)

    try:
        init_bal = page.locator('#balance_small').text_content()
        print(f'BALANCE BEFORE: {init_bal} ', end='')
        logging.info('BALANCE BEFORE: '+init_bal)
        page.wait_for_timeout(1000)
        roll_btn = page.locator('#free_play_form_button')
        roll_btn.scroll_into_view_if_needed()
        iframe = page.frame_locator('iframe').first
        page.wait_for_timeout(5000)
        # while True:
        page.mouse.click(564, 480, delay=1, click_count=3)
        page.wait_for_timeout(5000)
        print('waiting')
        # if iframe.locator('#success').is_visible():
        #     break

        with open('yoda-lair/shot.png', 'wb') as f:
            f.write(page.screenshot())
        # roll_btn.click(timeout=10000)
        # if dt.now().hour == 23 or dt.now().hour == 11 or dt.now().hour == 17:
        yag = yagmail.SMTP('hannahkamau1964@gmail.com', 'oxbgivizmibwwnqx')
        yag.send(to='joninduati31@gmail.com', subject=f"{profile.title()} captcha", attachments=['./yoda-lair/shot.png'], contents=f"balance: {page.locator('#balance_small').text_content()}")
        # check_final_balance()

    except TimeoutError as e:
        if '<iframe' in e.message:
            logging.warning('Captcha challenge popup')
            init_bal = page.locator('#balance_small').text_content()
            # print(f'\nBALANCE BEFORE: {init_bal} ', end='')
            page.mouse.click(15, 200)
            page.locator('#play_without_captchas_button').click(timeout=5000)
            cost = page.locator('#play_without_captcha_desc').locator('span').text_content()
            
            if int(cost) <= 1:
                page.locator('#free_play_form_button').click(timeout=5000)
            
            check_final_balance()
        else:
            print("In Roll: "+e.message+"\n\n")
            logging.exception(e.stack)
        raise
    
def open_profile(profile: str) -> None:
    try:
        with sync_playwright() as pl:
            context = pl.firefox.launch_persistent_context \
            (
                # Path(__file__).resolve().parent / f'{profile}-moz-profile', 
                profile,
		        headless=True, 
                # color_scheme='dark',
                # args=['--no-default-browser-check'], # chromium
                # args=['-override', 'override.ini'],
                slow_mo=100,
            
            )
            print('browser launched')
            page = context.pages[0]
            # page = context.new_page()
            stealth_sync(page)
            response = page.goto(URL)
            print(f'Response: {response.status} {response.status_text}')
            logging.info(f'Response: {response.status} {response.status_text}')
            roll(page, profile)
            context.close()
    except Exception as e:
        logging.exception(e)
        raise

import sys
open_profile(sys.argv[1])
