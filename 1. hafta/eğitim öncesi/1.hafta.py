class  kahveOtomati:
    def menu(self):
        self.menu = {"americano": 150,"latte":160, "espresso": 150
                     }
    def menugoster(self):
        print("Menü")
        for kahve, fiyat in self.menü.items():
            print(f"{kahve} : {fiyat} tl")

    def sipariş_al(self):
        secim = input("Lütfen bir kahve seçin (Espresso/Latte/Cappuccino): ").lower()
        if secim in self.menü:
            return secim
        else:
            print("Geçersiz seçim!")
            return self.sipariş_al()

    def ücret_hesapla(self, kahve):
        return self.menü[kahve]

    def ödeme_al(self, ücret):
        print(f"Ücret: {ücret} TL")
        try:
            ödeme = int(input("Lütfen ödemenizi yapın (TL): "))
            if ödeme >= ücret:
                para_üstü = ödeme - ücret
                if para_üstü > 0:
                    print(f"{para_üstü} TL para üstünüzü almayı unutmayın.")
                return True
            else:
                print("Yetersiz ödeme. Sipariş iptal edildi.")
                return False
        except ValueError:
            print("Geçersiz giriş! Lütfen sayı girin.")
            return self.ödeme_al(ücret)

    def kahve_hazırla(self, kahve):
        print(f"\n{kahve.title()} hazırlanıyor...")
        import time
        time.sleep(2)
        print(f"{kahve.title()} hazır! Afiyet olsun.")

    def çalıştır(self):
        self.menüyü_göster()
        kahve = self.sipariş_al()
        ücret = self.ücret_hesapla(kahve)
        if self.ödeme_al(ücret):
            self.kahve_hazırla(kahve)

otomatik = kahveOtomati()
otomatik.çalıştır()