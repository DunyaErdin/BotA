import asyncio
import random
async def insan_tipi_yazma(element, text):
    for karakter in text:
        await element.type(karakter)
        await asyncio.sleep(random.uniform(0.1, 0.25))  # Tuşlar arası rastgele gecikme

async def insan_tipi_fare_hareketi(page, hedef_x, hedef_y):
    # Fareyi küçük adımlarla ilerlet
    mevcut_x, mevcut_y = 0, 0
    adim_sayisi = random.randint(20, 50)
    for i in range(adim_sayisi):
        mevcut_x += (hedef_x - mevcut_x) / (adim_sayisi - i)
        mevcut_y += (hedef_y - mevcut_y) / (adim_sayisi - i)
        await page.mouse.move(mevcut_x, mevcut_y)
        await asyncio.sleep(random.uniform(0.01, 0.05))