import subprocess
from black import main
import requests
import os
from pyppeteer import launch
import asyncio
from pyppeteer.network_manager import Request
import threading
 

async def intercept_network_request(request: Request, page):
    if request.url.endswith('index.m3u8') and request.method == 'GET':
        url = request.url[:request.url.find('/index.m3u8')]
        res = await page.evaluate("document.querySelector('#top_audio_player > div > div').textContent")
        print(res)
        my_thread = threading.Thread(target=save_music, args=(res, url,))
        my_thread.start()
    await request.continue_()


def save_music(res, url):
    os.mkdir(f'tmp/{res}')
    a=requests.get(f'{url}/index.m3u8')
    with open(f'tmp/{res}/mus.m3u8', 'wb') as file:
        file.write(a.content)
    p = str(a.content)
    zc=p.count('seg')
    for i in range (1, 1+zc):
        a=requests.get(f'{url}/seg-{i}-a1.ts')
        # print(a.status_code)
        with open(f'tmp/{res}/seg-{i}-a1.ts', 'wb') as file:
            file.write(a.content)

    with open(os.devnull, 'wb') as devnull:
        subprocess.check_call(['ffmpeg', '-protocol_whitelist', 'file,http,https,tcp,tls,crypto', '-i', f'tmp/{res}/mus.m3u8', f'{res}.mp3', '-y'], stdout=devnull, stderr=subprocess.STDOUT)
    # os.system(f"ffmpeg -protocol_whitelist file,http,https,tcp,tls,crypto -i   -y >> zzz")

    os.remove(f'tmp/{res}/mus.m3u8')
    for i in range (1, 1+zc):
        os.remove(f'tmp/{res}/seg-{i}-a1.ts')
    os.rmdir(f'tmp/{res}')

        


async def browser():
    # Создать очередь, которую мы будем использовать для хранения нашей "рабочей нагрузки".
    # queue = asyncio.Queue()

    brow = await launch({'headless': False, 'ignoreHTTPSErrors': True, 'autoClose':False, 'defaultViewport': {'width': 1720, 'height': 980}})
    page = (await brow.pages())[0]
    await page.goto('https://vk.com')
    await page.setRequestInterception(True)

    page.on(event='request', f=lambda req: asyncio.ensure_future(intercept_network_request(req, page)))
    

loop = asyncio.get_event_loop()
loop.create_task(browser())
loop.run_forever()

