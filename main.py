import asyncio
import base64
import requests
from playwright.async_api import async_playwright
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import os

import Bot
async def main():

    GEMINI_API_KEY = input("Enter Gemini API Key: ")  
    
 
    solver = Bot.FreeCaptchaSolver(gemini_api_key=GEMINI_API_KEY if GEMINI_API_KEY == "Your Api Key" else None)
    

    SITE_URL = "https://www.ustraveldocs.com/tr/tr/nonimmigrant-visa"
    USERNAME = input("Enter The Name : ")
    PASSWORD = input("Enter The Password: ")
    
    print("🚀 ABOT")
    print("=" * 40)
    print(f"🌐 Site: {SITE_URL}")
    print(f"👤 Kullanıcı: {USERNAME}")
    print(f"🔧 Tesseract: Aktif (Ücretsiz)")
    print(f"🤖 Gemini: {'Aktif' if solver.gemini_api_key else 'Pasif'}")
    print("=" * 40)
    

    try:
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pytesseract.get_tesseract_version()
        print("✅ Tesseract kurulu")
    except:
        print("❌ Tesseract kurulu değil!")
        print("Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("pip install pytesseract pillow")
        return
    
   
    success = await solver.run_bot(SITE_URL, USERNAME, PASSWORD, max_attempts=3)
    
    if success:
        print("\n🎉 BOT BAŞARILI!")
    else:
        print("\n❌ BOT BAŞARISIZ!")

if __name__ == "__main__":
    asyncio.run(main())
