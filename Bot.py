import asyncio
import base64
import requests
from playwright.async_api import async_playwright
import pytesseract
from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import os
import random as rnd



class FreeCaptchaSolver:
    def __init__(self, gemini_api_key=None):
        """
        Ücretsiz CAPTCHA çözücü - Tesseract ve Gemini ile
        """
        self.gemini_api_key = gemini_api_key
        
        # Tesseract path'ini ayarla
        self._setup_tesseract()
        
        # Tesseract ayarları - Bu CAPTCHA tipine özel
        self.tesseract_config = '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
    
    def _setup_tesseract(self):
        """
        Tesseract path'ini otomatik ayarla
        """
        if os.name == 'nt':  # Windows
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Users\{}\AppData\Local\Tesseract-OCR\tesseract.exe'.format(os.getenv('USERNAME')),
                r'C:\tesseract\tesseract.exe'
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    print(f"🔧 Tesseract path ayarlandı: {path}")
                    return
            
            print("⚠️  Tesseract path bulunamadı, varsayılan kullanılacak")
    
    def solve_captcha_with_tesseract(self, image_path):
        """
        Bu özel CAPTCHA tipine optimize edilmiş Tesseract OCR
        Renkli, eğik, farklı fontlu harfler için özel ayarlar
        """
        try:
            print("🎯 Özel CAPTCHA tipi tespit edildi - Optimize ediliyor...")
            
            # Görüntüyü aç
            img = Image.open(image_path)
            original_img = img.copy()
            
            # Bu CAPTCHA tipine özel yöntemler
            methods = [
                self._preprocess_colorful_captcha_v1,
                self._preprocess_colorful_captcha_v2,
                self._preprocess_colorful_captcha_v3,
                self._preprocess_colorful_captcha_v4,
                self._preprocess_colorful_captcha_v5
            ]
            
            # Bu tip CAPTCHA için özel konfigürasyonlar
            configs = [
                '--psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                '--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                '--psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                '--psm 13 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
                '--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            ]
            
            results = []
            
            for i, method in enumerate(methods):
                for j, config in enumerate(configs):
                    try:
                        processed_img = method(original_img.copy())
                        
                        # Debug için kaydet
                        processed_img.save(f"captcha_processed_method{i+1}_config{j+1}.png")
                        
                        # OCR çalıştır
                        text = pytesseract.image_to_string(processed_img, config=config)
                        
                        # Temizle
                        text = ''.join(filter(str.isalpha, text))
                        
                        if text and len(text) >= 4:  # Bu CAPTCHA tipi genelde 4-6 harf
                            results.append(text.lower())  # Küçük harfe çevir
                            print(f"🔍 Yöntem {i+1}-Config {j+1}: {text}")
                    
                    except Exception as e:
                        continue
            
            # En iyi sonucu seç
            if results:
                from collections import Counter
                
                # En sık tekrar edeni bul
                counter = Counter(results)
                most_common = counter.most_common(3)  # En çok tekrar eden 3'ü al
                
                print(f"📊 Sonuç dağılımı: {most_common}")
                
                # En uygun olanı seç
                best_result = most_common[0][0]
                
                # Sonucu formatla (ilk harfi büyük, diğerleri küçük - örneğe uygun)
                formatted_result = self._format_captcha_result(best_result)
                
                print(f"✅ Final sonuç: {formatted_result}")
                return formatted_result
            
            print("❌ Tesseract hiçbir sonuç üretemedi")
            return None
            
        except Exception as e:
            print(f"❌ Tesseract hatası: {str(e)}")
            return None
    
    def _format_captcha_result(self, text):
        """
        CAPTCHA sonucunu görüntüdeki stile uygun formatla
        """
        if not text:
            return text
            
        # Bu örnekteki gibi karma case olabilir
        # Şimdilik düz lowercase döndür, site nasıl istiyorsa ona göre ayarlarız
        return text.lower()
    
    def _preprocess_colorful_captcha_v1(self, img):
        """
        Renkli CAPTCHA için - Renk kanallarını ayrı işle
        """
        import numpy as np
        
        # RGB kanallarını ayrı ayrı işle
        img_array = np.array(img)
        
        # Her renk kanalından en iyi kontrastı bul
        channels = []
        if len(img_array.shape) == 3:
            for i in range(3):  # R, G, B
                channel = img_array[:, :, i]
                # Kontrast artır
                channel = np.clip(channel * 1.5, 0, 255).astype(np.uint8)
                channels.append(channel)
            
            # En yüksek kontrastlı kanalı seç
            best_channel = max(channels, key=lambda x: np.std(x))
            img = Image.fromarray(best_channel)
        
        # Gri tonlama ve kontrast
        img = img.convert('L')
        img = ImageEnhance.Contrast(img).enhance(2.5)
        
        return img
    
    def _preprocess_colorful_captcha_v2(self, img):
        """
        HSV renk uzayı ile preprocessing
        """
        import numpy as np
        
        # HSV'ye çevir
        img_hsv = img.convert('HSV')
        img_array = np.array(img_hsv)
        
        # Value (parlaklık) kanalını al ve işle
        if len(img_array.shape) == 3:
            v_channel = img_array[:, :, 2]
            # Threshold uygula
            v_channel = np.where(v_channel > 128, 255, 0).astype(np.uint8)
            img = Image.fromarray(v_channel)
        else:
            img = img.convert('L')
        
        # Morfolojik işlemler
        img = img.filter(ImageFilter.MedianFilter(3))
        
        return img
    
    def _preprocess_colorful_captcha_v3(self, img):
        """
        Adaptif threshold ile
        """
        img = img.convert('L')
        
        # Otomatik kontrast
        img = ImageOps.autocontrast(img)
        
        # Keskinleştir
        img = img.filter(ImageFilter.SHARPEN)
        img = img.filter(ImageFilter.UnsharpMask())
        
        # Binary threshold
        img = img.point(lambda x: 0 if x < 140 else 255, '1')
        
        return img
    
    def _preprocess_colorful_captcha_v4(self, img):
        """
        Renkli harfler için özel edge detection
        """
        # Gri tonlama
        img = img.convert('L')
        
        # Gaussian blur + sharpen kombinasyonu
        img = img.filter(ImageFilter.GaussianBlur(radius=0.5))
        img = ImageEnhance.Sharpness(img).enhance(3.0)
        
        # Kontrast maksimuma çıkar
        img = ImageEnhance.Contrast(img).enhance(3.0)
        
        # Edge enhancement
        img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
        
        return img
    
    def _preprocess_colorful_captcha_v5(self, img):
        """
        En agresif temizleme yöntemi
        """
        # Boyutu büyüt (daha iyi OCR için)
        original_size = img.size
        img = img.resize((original_size[0] * 3, original_size[1] * 3), Image.LANCZOS)
        
        # Gri tonlama
        img = img.convert('L')
        
        # Çok güçlü kontrast
        img = ImageEnhance.Contrast(img).enhance(4.0)
        
        # Noise reduction
        img = img.filter(ImageFilter.MedianFilter(5))
        
        # Sert threshold
        img = img.point(lambda x: 0 if x < 120 else 255, '1')
        
        return img
    
    def _preprocess_method1(self, img):
        """Basit gri tonlama ve kontrast"""
        img = img.convert('L')  # Gri tonlama
        img = ImageEnhance.Contrast(img).enhance(2.0)  # Kontrast artır
        img = img.filter(ImageFilter.MedianFilter(3))  # Gürültü azalt
        return img
    
    def _preprocess_method2(self, img):
        """Threshold ve morfolojik işlemler"""
        img = img.convert('L')
        img = ImageEnhance.Sharpness(img).enhance(2.0)
        img = ImageOps.autocontrast(img)
        
        # Binary threshold
        threshold = 128
        img = img.point(lambda x: 0 if x < threshold else 255, '1')
        return img
    
    def _preprocess_method3(self, img):
        """Gelişmiş filtreleme"""
        img = img.convert('L')
        img = img.filter(ImageFilter.SMOOTH_MORE)
        img = ImageEnhance.Brightness(img).enhance(1.2)
        img = ImageEnhance.Contrast(img).enhance(1.5)
        return img
    
    def _preprocess_method4(self, img):
        """Adaptif threshold"""
        img = img.convert('L')
        img = ImageOps.equalize(img)  # Histogram eşitleme
        img = img.filter(ImageFilter.UnsharpMask())
        return img
    
    async def solve_captcha_with_gemini(self, image_path):
        """
        Google Gemini Vision API ile CAPTCHA çöz (Ücretsiz)
        """
        if not self.gemini_api_key:
            return None
            
        try:
            print("Gemini API ile görüntü işleniyor...")
            
            # Görüntüyü base64'e çevir
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": "Bu görüntüdeki üstü çizili harfleri ve rakamları oku. Sadece bana görüntüdeki yazıyı dön başka birşey söyleme örnek: ABC12 hepsini büyük yaz lütfen"
                            },
                            {
                                "inline_data": {
                                    "mime_type": "image/png",
                                    "data": base64_image
                                }
                            }
                        ]
                    }
                ]
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                captcha_text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Temizle - sadece alfanumerik karakterler
                captcha_text = ''.join(filter(str.isalnum, captcha_text)).upper()
                
                print(f"Gemini sonucu: {captcha_text}")
                return captcha_text
            else:
                print(f"Gemini API hatası: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Gemini API hatası: {str(e)}")
            return None

    async def solve_captcha(self, image_path):
        """
        CAPTCHA'yı çözmeye çalış - önce Tesseract, sonra Gemini
        """
        # Önce Tesseract dene (tamamen ücretsiz)
    
        
        # Tesseract başarısızsa Gemini dene
        
        print("Tesseract başarısız, Gemini deneniyor...")
        result = await self.solve_captcha_with_gemini(image_path)
        if result:
            return result
        
        print("Her iki yöntem de başarısız!")
        return None

    async def run_bot(self, site_url, username, password, max_attempts=5):
        """
        Ana bot fonksiyonu
        """
        bulundumu = False
        
        async with async_playwright() as p:
            # Tarayıcıyı başlat
          
            browser = await p.chromium.launch(
                headless=False,  # Görünür tarayıcı
                slow_mo=1000
            )
            
            context = await browser.new_context(
                viewport={'width': 1280, 'height': 720}
            )
            page = await context.new_page()
            while True:
                try:
                    print(f"🌐 Siteye gidiliyor: {site_url}")
                    await page.goto(site_url, wait_until='networkidle')

                    await asyncio.sleep(rnd.randint(2,5))
                    await page.click('xpath=/html/body/div/div[1]/div/main/div[4]/div/div[2]/div[4]/div/div')
                    await asyncio.sleep(rnd.randint(2,5))
                    await page.click('xpath=/html/body/div/header/div[3]/nav/div/a[2]')
                    await asyncio.sleep(rnd.randint(2,5))
                    await page.click('xpath=/html/body/div[3]/table/tbody/tr/td[2]/div/div/div[3]/h3[2]/p/a')
                    await asyncio.sleep(rnd.randint(2,5))

                
                
                
                
                
                
                
                    for attempt in range(max_attempts):
                        print(f"\n🔥 Deneme {attempt + 1}/{max_attempts}")
                    
                        try:
                        # Form alanlarını doldur
                            print("📝 Kullanıcı bilgileri giriliyor...")
                        
                        # Sayfanın yüklenmesini bekle
                            await page.wait_for_timeout(2000)
                        
                        # Kullanıcı adı
                        
                        
                            try:
                                await page.fill("xpath=/html/body/div[3]/table/tbody/tr/td[2]/div/div/div[1]/form/div[4]/ul/li[1]/div/input", username)
                                print("✅ Kullanıcı adı girildi:")
                            except:
                                continue
                        
                        # Şifre
                            await asyncio.sleep(rnd.randint(2,5))
                        
                            try:
                            
                                await page.fill("xpath=/html/body/div[3]/table/tbody/tr/td[2]/div/div/div[1]/form/div[4]/ul/li[2]/div[1]/input", password)
                                print("✅ Şifre girildi:")
                            except:
                                continue
                            await asyncio.sleep(rnd.randint(2,5))
                            try:
                                
                                captcha_element = page.locator("xpath=/html/body/div[3]/table/tbody/tr/td[2]/div/div/div[1]/form/div[4]/ul/li[2]/div[2]/div/div[1]/div/img")
                                print("✅ CAPTCHA bulundu")
                            except:
                                continue
                        
                            if not captcha_element:
                                print("❌ CAPTCHA elementi bulunamadı!")
                                continue
                        
                        # CAPTCHA'nın yüklenmesini bekle
                            await page.wait_for_timeout(2000)
                        
                        # Screenshot al
                            captcha_path = f"captcha_attempt_{attempt + 1}.png"
                            await captcha_element.screenshot(path=captcha_path)
                            print(f"📸 CAPTCHA kaydedildi: {captcha_path}")
                        
                        # CAPTCHA'yı çöz
                            print("🔍 CAPTCHA çözülüyor...")
                            captcha_text = await self.solve_captcha(captcha_path)
                        
                            if captcha_text:
                                print(f"✅ CAPTCHA çözüldü: {captcha_text}")
                            
                        
                            
                            
                            try:
                            
                                await page.fill("xpath=/html/body/div[3]/table/tbody/tr/td[2]/div/div/div[1]/form/div[4]/ul/li[3]/div/input", captcha_text)
                                print(f"✅ CAPTCHA girildi")
                            
                            except:
                                continue
                            await asyncio.sleep(rnd.randint(2,5))

                            try:
                            
                                print(f"🚀 Giriş butonu tıklanıyor:")
                                await page.click("xpath=/html/body/div[3]/table/tbody/tr/td[2]/div/div/div[1]/form/div[5]/button[1]")
                            
                            except:
                                continue
                            
                            # Sonucu bekle
                            await asyncio.sleep(rnd.randint(2,5))
                            element = page.locator("#password")
                            if await element.count() == 0 or element == None:
                                print("✅CAPTCHA Başarıyla Çözüldü...")
                                break
                            else:
                                print("❌CAPTCHA Çözümü Başarısız...")
                                await page.click("xpath=/html/body/div[3]/table/tbody/tr/td[2]/div/div/div[1]/form/div[4]/ul/li[2]/div[2]/div/div[2]/span/a[1]/button")
                            
                            
                            # Başarı kontrolü
                        
                            
                        
                        except Exception as e:
                            print(f"❌ Deneme {attempt + 1} hatası: {str(e)}")
                            if attempt < max_attempts - 1:
                                await page.reload(wait_until='networkidle')
                                await page.wait_for_timeout(3000)
                
                
                    await asyncio.sleep(rnd.randint(2,5))            
                    guvenliksorusu1 =  page.locator("xpath=/html/body/div[3]/table/tbody/tr/td[2]/div/div/div/form/div[4]/ul/li[2]/div/p")
                    print("Güvenlik sorusu bulunuyor...")
                    guvenliksorusu1text = await guvenliksorusu1.text_content()
                    guvenlikinput1= page.locator("xpath=/html/body/div[3]/table/tbody/tr/td[2]/div/div/div/form/div[4]/ul/li[3]/div/input")
                    if guvenliksorusu1text == "What was your first car?":
                        await guvenlikinput1.fill("SUZUKI")
                    
                    elif guvenliksorusu1text == "What was the first company that you worked for?":
                        await guvenlikinput1.fill("ERDIN")
                    else:
                        await guvenlikinput1.fill("ISTANBUL")
                    print("✅Güvenlik Sorusu Uygun Şekilde Cevaplandı")
                

                    await asyncio.sleep(rnd.randint(2,5))

                    guvenliksorusu2 =  page.locator("xpath=/html/body/div[3]/table/tbody/tr/td[2]/div/div/div/form/div[4]/ul/li[4]/div/p")
                    guvenliksorusu2text = await guvenliksorusu2.text_content()
                    guvenlikinput2= page.locator("xpath=/html/body/div[3]/table/tbody/tr/td[2]/div/div/div/form/div[4]/ul/li[5]/div/input")
                    if guvenliksorusu2text == "What was your first car?":
                        await guvenlikinput2.fill("SUZUKI")
                    elif guvenliksorusu2text == "What was the first company that you worked for?":
                        await guvenlikinput2.fill("ERDIN")
                    else:
                        await guvenlikinput2.fill("ISTANBUL")
                    await asyncio.sleep(rnd.randint(2,5))
                    await page.click("xpath=/html/body/div[3]/table/tbody/tr/td[2]/div/div/div/form/div[5]/button[1]")

                    await asyncio.sleep(rnd.randint(4,8))
                
                    await page.click("xpath=/html/body/main/div/div/div[1]/div[1]/nav/ul/li[3]/a")

                    await asyncio.sleep(rnd.randint(3,6))
                

                    tablobilgi = page.locator("xpath=/html/body/main/div/div/div/div[1]/div/div")
                    controlh1 = page.locator("xpath=/html/body/div[3]/table/tbody/tr/td[2]/div/div/div[1]/div[1]/h1")
                    if tablobilgi.count()>0 and tablobilgi.text_content() == "Hiçbir Zaman Dilimi Mevcut Değil":
                        await asyncio.sleep(rnd.randint(180,300))
                        await page.reload()
                    elif await controlh1.count()>0 and controlh1.text_content()=="Kullanıcı Detayları":
                        print("Oturum suresi doldu tekrar açılıcak")    
                    else:
                        print("RandevuBulunduuuuuu")
                        bulundumu==True
                        break
                        

                
                    
                    
                
                except Exception as e:
                    print(f"❌ Kritik hata: {str(e)}")
                    break
                    return False
            
            if bulundumu == True:
                return True

# Kullanım
