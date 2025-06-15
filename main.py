import asyncio
import base64
import requests
from playwright.async_api import async_playwright
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import os

import Bot
async def main():
    # Google Gemini API anahtarı (opsiyonel - ücretsiz)
    # https://makersuite.google.com/app/apikey
    GEMINI_API_KEY = "AIzaSyDZij01DZ5oZnDGnZIVi_fU55oZiEdQ91A"  # Boş bırakabilirsiniz
    
    # Eğer çevre değişkeninden alacaksanız:
    # GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Bot'u başlat
    solver = Bot.FreeCaptchaSolver(gemini_api_key=GEMINI_API_KEY if GEMINI_API_KEY == "AIzaSyDZij01DZ5oZnDGnZIVi_fU55oZiEdQ91A" else None)
    
    # Site bilgileri
    SITE_URL = "https://www.ustraveldocs.com/tr/tr/nonimmigrant-visa"
    USERNAME = "SERKAN SEYHUN"
    PASSWORD = "Serkan@2025"
    
    print("🚀 ÜCRETSİZ CAPTCHA ÇÖZÜCÜ BOT")
    print("=" * 40)
    print(f"🌐 Site: {SITE_URL}")
    print(f"👤 Kullanıcı: {USERNAME}")
    print(f"🔧 Tesseract: Aktif (Ücretsiz)")
    print(f"🤖 Gemini: {'Aktif' if solver.gemini_api_key else 'Pasif'}")
    print("=" * 40)
    
    # Tesseract kurulum kontrolü
    try:
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pytesseract.get_tesseract_version()
        print("✅ Tesseract kurulu")
    except:
        print("❌ Tesseract kurulu değil!")
        print("Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("pip install pytesseract pillow")
        return
    
    # Bot'u çalıştır
    success = await solver.run_bot(SITE_URL, USERNAME, PASSWORD, max_attempts=3)
    
    if success:
        print("\n🎉 BOT BAŞARILI!")
    else:
        print("\n❌ BOT BAŞARISIZ!")

if __name__ == "__main__":
    asyncio.run(main())