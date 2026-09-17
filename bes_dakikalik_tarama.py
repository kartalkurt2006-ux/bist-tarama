import time
from datetime import datetime
import json
import os
import pandas as pd
import numpy as np
import yfinance as yf
import requests
import pytz
import urllib.parse

# --- AYARLAR VE SABİTLER ---
MEMORY_FILE = "hafiza_5dk.json"
COOLDOWN_SECONDS = 3600  # Aynı hisse için 1 saat bekleme süresi
TZ_TR = pytz.timezone("Europe/Istanbul")

# WhatsApp (CallMeBot) Bilgileri
WHATSAPP_PHONE = "905462848792"
WHATSAPP_APIKEY = "3477940"

# BIST Hisselerinin Genişletilmiş Listesi
BIST_HISSELERI = [
    "ACSEL.IS", "ADEL.IS", "ADESE.IS", "AEFES.IS", "AFYON.IS", "AGESA.IS", "AGHOL.IS", "AGROT.IS", "AKBNK.IS", "AKCNS.IS",
    "AKENR.IS", "AKFGY.IS", "AKFYE.IS", "AKGRT.IS", "AKMGY.IS", "AKSA.IS", "AKSEN.IS", "AKSGY.IS", "ALARK.IS", "ALBRK.IS",
    "ALCAR.IS", "ALCTL.IS", "ALFAS.IS", "ALGYO.IS", "ALKA.IS", "ALKIM.IS", "ALKLC.IS", "ANELE.IS", "ANGEN.IS", "ANHYT.IS",
    "ANSGR.IS", "ARASE.IS", "ARCLK.IS", "ARDYZ.IS", "ARENA.IS", "ARSAN.IS", "ARFYO.IS", "ASELS.IS", "ASTOR.IS", "ASUZU.IS",
    "ATAKP.IS", "ATATE.IS", "ATEKS.IS", "ATSYH.IS", "AVGYO.IS", "AVTUR.IS", "AYCES.IS", "AYDEM.IS", "AYEN.IS", "AYES.IS",
    "AYGAZ.IS", "AZTEK.IS", "BAGFS.IS", "BAKAB.IS", "BALAT.IS", "BANVT.IS", "BARMA.IS", "BASGZ.IS", "BASCM.IS", "BAYRK.IS",
    "BEGYO.IS", "BERA.IS", "BEYAZ.IS", "BIENY.IS", "BIGCH.IS", "BIMAS.IS", "BINHO.IS", "BIOEN.IS", "BIZIM.IS", "BJKAS.IS",
    "BLCYT.IS", "BMSCH.IS", "BMVFK.IS", "BNTAS.IS", "BOBET.IS", "BORLS.IS", "BOSSA.IS", "BRISA.IS", "BRKO.IS", "BRKSN.IS",
    "BRYAT.IS", "BUCIM.IS", "BURCE.IS", "BURVA.IS", "BVSAN.IS", "CANTE.IS", "CASFY.IS", "CCOLA.IS", "CELHA.IS", "CEMAS.IS",
    "CEMTS.IS", "CEOEM.IS", "CGCME.IS", "CIMSA.IS", "CLEBI.IS", "CMBTN.IS", "CMENT.IS", "CONSE.IS", "COSMO.IS", "CRDFA.IS",
    "CRFSA.IS", "CUSAN.IS", "CVKMD.IS", "CWENE.IS", "DAGI.IS", "DAPGM.IS", "DARDL.IS", "DENGE.IS", "DERHL.IS", "DERIM.IS",
    "DESA.IS", "DESPC.IS", "DEVA.IS", "DIRIT.IS", "DITAS.IS", "DMRGD.IS", "DMSAS.IS", "DNISI.IS", "DOAS.IS", "DOBUR.IS",
    "DOFER.IS", "DOGUB.IS", "DOHOL.IS", "EBEBK.IS", "ECILC.IS", "ECZYT.IS", "EDATA.IS", "EDIP.IS", "EGEEN.IS", "EGEPO.IS",
    "EGGUB.IS", "EGPRO.IS", "EGSER.IS", "EKGYO.IS", "EKOS.IS", "EKSUN.IS", "ELITE.IS", "EMKEL.IS", "ENERY.IS", "ENJSA.IS",
    "ENKAI.IS", "ENSRI.IS", "EPLAS.IS", "ERBOS.IS", "EREGL.IS", "ERSU.IS", "ESCAR.IS", "ESEN.IS", "ETILR.IS", "EUPWR.IS",
    "EUREK.IS", "EVYOT.IS", "EYGYO.IS", "FADE.IS", "FENER.IS", "FLAP.IS", "FMIZP.IS", "FONET.IS", "FORMT.IS", "FORTE.IS",
    "FRIGO.IS", "FROTO.IS", "GARAN.IS", "GARFA.IS", "GEDIK.IS", "GEDAN.IS", "GENIL.IS", "GENTS.IS", "GEREL.IS", "GESAN.IS",
    "GLCVY.IS", "GLYHO.IS", "GMTAS.IS", "GOKNR.IS", "GOLTS.IS", "GOODY.IS", "GOZDE.IS", "GRNYO.IS", "GRSAN.IS", "GSDDE.IS",
    "GSDHO.IS", "GSRAY.IS", "GUBRF.IS", "GWIND.IS", "GZNMI.IS", "HALKB.IS", "HATEK.IS", "HATSN.IS", "HEDEF.IS", "HEKTS.IS",
    "HKTM.IS", "HLGYO.IS", "HURGZ.IS", "ICBCT.IS", "IDEAS.IS", "IDGYO.IS", "IHEVA.IS", "IHGZT.IS", "IHLAS.IS", "IHLGM.IS",
    "IHYVA.IS", "IMASM.IS", "INDES.IS", "INFO.IS", "INGRM.IS", "INTEM.IS", "INVEO.IS", "IPEKE.IS", "ISATR.IS", "ISBTR.IS",
    "ISCTR.IS", "ISDMR.IS", "ISFIN.IS", "ISGSY.IS", "ISGYO.IS", "ISKPL.IS", "ISKUR.IS", "ISMEN.IS", "ISSEN.IS", "IZFAS.IS",
    "IZINV.IS", "IZMDC.IS", "JANTS.IS", "KAPLM.IS", "KAREL.IS", "KARSN.IS", "KARTN.IS", "KARYS.IS", "KASTB.IS", "KATMR.IS",
    "KAYSE.IS", "KCAER.IS", "KCHOL.IS", "KENT.IS", "KERVT.IS", "KFEIN.IS", "KGYO.IS", "KIMMR.IS", "KLGYO.IS", "KLKIM.IS",
    "KLSYN.IS", "KMPUR.IS", "KNFRT.IS", "KONTR.IS", "KONYA.IS", "KOPOL.IS", "KORDS.IS", "KOTON.IS", "KOZAA.IS", "KOZAL.IS",
    "KRDMD.IS", "KRGYO.IS", "KRONT.IS", "KRPLS.IS", "KRSTL.IS", "KRTEK.IS", "KUTPO.IS", "KUVVA.IS", "KUYAS.IS", "LIDER.IS",
    "LIDFA.IS", "LINK.IS", "LKMNH.IS", "LOGO.IS", "LUKSK.IS", "MAALT.IS", "MAKTK.IS", "MANAS.IS", "MARKA.IS", "MARTI.IS",
    "MAVI.IS", "MEDTR.IS", "MEGAP.IS", "MEKAG.IS", "MENPA.IS", "MERCN.IS", "MERKO.IS", "METUR.IS", "MGROS.IS", "MIATK.IS",
    "MMCAS.IS", "MNDRS.IS", "MNDTR.IS", "MOBTL.IS", "MPARK.IS", "MRSHL.IS", "MSGYO.IS", "MTRKS.IS", "MZHLD.IS",
    "NATEN.IS", "NETAS.IS", "NIBAS.IS", "NTGAZ.IS", "NUGYO.IS", "NUHCM.IS", "OBASE.IS", "ODAS.IS", "OFSYM.IS", "ONCSM.IS",
    "ORCAY.IS", "OYAKC.IS", "OYLUM.IS", "OYYAT.IS", "OZATD.IS", "OZGYO.IS", "OZKGY.IS", "OZLMR.IS", "OZRDN.IS",
    "PAGYO.IS", "PAMEL.IS", "PAPIL.IS", "PARSN.IS", "PENGD.IS", "PENTA.IS", "PETKM.IS", "PETUN.IS", "PGSUS.IS", "PINSU.IS",
    "PKART.IS", "PKENR.IS", "PNSUT.IS", "POLHO.IS", "POLTK.IS", "PRDGS.IS", "PRKME.IS", "PRKAB.IS", "PSGYO.IS", "QUAGR.IS",
    "RALYH.IS", "RAYSG.IS", "REEDR.IS", "RNPOL.IS", "RODRG.IS", "ROYAL.IS", "RTALB.IS", "RUBNS.IS", "RYGYO.IS", "RYSAS.IS",
    "SAFKR.IS", "SAHOL.IS", "SARKY.IS", "SASA.IS", "SAYAS.IS", "SDTTR.IS", "SEGMN.IS", "SEGYO.IS", "SEKFK.IS", "SEKUR.IS",
    "SELEC.IS", "SELGD.IS", "SELVA.IS", "SEYKM.IS", "SILVR.IS", "SISE.IS", "SKBNK.IS", "SKTAS.IS", "SMART.IS", "SMRTG.IS",
    "SNGYO.IS", "SNICA.IS", "SNPAM.IS", "SODSN.IS", "SOKE.IS", "SOKM.IS", "SONME.IS", "SRVGY.IS", "SUMAS.IS", "SUNTK.IS",
    "SUWEN.IS", "TABGD.IS", "TARKM.IS", "TATEN.IS", "TATGD.IS", "TAVHL.IS", "TBORG.IS", "TCELL.IS", "TDGYO.IS", "TEKTN.IS",
    "TEHOL.IS", "TERA.IS", "TETMT.IS", "TFVGY.IS", "THYAO.IS", "TKFEN.IS", "TKNSA.IS", "TMPOL.IS", "TMSN.IS", "TOASO.IS",
    "TRGYO.IS", "TRILC.IS", "TSKB.IS", "TSPOR.IS", "TTKOM.IS", "TTRAK.IS", "TUKAS.IS", "TUPRS.IS", "TURSG.IS", "UFUK.IS",
    "ULAS.IS", "ULKER.IS", "ULUUN.IS", "UNLU.IS", "USAK.IS", "VAKBN.IS", "VAKFN.IS", "VAKGY.IS", "VBTYZ.IS", "VERTU.IS",
    "VERUS.IS", "VESBE.IS", "VESTL.IS", "VKGYO.IS", "VKING.IS", "YAPRK.IS", "YATAS.IS", "YAYLA.IS", "YKBNK.IS", "YKSLN.IS",
    "YUNSA.IS", "YYAPI.IS", "ZEDUR.IS", "ZOREN.IS", "ZRGYO.IS"
]

def hafiza_yukle():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def hafiza_kaydet(hafiza):
    with open(MEMORY_FILE, "w") as f:
        json.dump(hafiza, f)

def piyasa_zaman_kontrolu():
    simdi = datetime.now(TZ_TR)
    if simdi.weekday() >= 5:  # Hafta sonu (Cumartesi, Pazar)
        return False
        
    # Borsa İstanbul seans saatleri kontrolü (09:30 - 18:10 arası)
    baslangic = simdi.replace(hour=9, minute=30, second=0, microsecond=0)
    bitis = simdi.replace(hour=18, minute=10, second=0, microsecond=0)
    
    if baslangic <= simdi <= bitis:
        return True
    return False

def calculate_hma(series, period=20):
    def wma(s, p):
        return s.rolling(window=p).apply(lambda x: np.dot(x, np.arange(1, p + 1)) / np.sum(np.arange(1, p + 1)), raw=True)
    
    half_period = period // 2
    sqrt_period = int(np.sqrt(period))
    
    wma_half = wma(series, half_period)
    wma_full = wma(series, period)
    
    raw_hma = 2 * wma_half - wma_full
    hma = wma(raw_hma, sqrt_period)
    return hma

def mfi_hesapla(df, period=14):
    delta = df['Close'].diff()
    typical_price = (df['High'] + df['Low'] + df['Close']) / 3
    raw_money_flow = typical_price * df['Volume']
    
    positive_flow = raw_money_flow.where(delta > 0, 0).rolling(window=period).sum()
    negative_flow = raw_money_flow.where(delta < 0, 0).rolling(window=period).sum()
    
    mfi = 100 - (100 / (1 + positive_flow / (negative_flow + 1e-10)))
    return mfi

def cmf_hesapla(df, period=20):
    mf_multiplier = ((df['Close'] - df['Low']) - (df['High'] - df['Close'])) / ((df['High'] - df['Low']) + 1e-10)
    mf_volume = mf_multiplier * df['Volume']
    cmf = mf_volume.rolling(window=period).sum() / (df['Volume'].rolling(window=period).sum() + 1e-10)
    return cmf

def dmi_hesapla(df, period=14):
    high = df['High']
    low = df['Low']
    close = df['Close']
    
    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0.0)
    
    tr1 = high - low
    tr2 = abs(high - close.shift(1))
    tr3 = abs(low - close.shift(1))
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    atr = tr.rolling(window=period).mean()
    plus_di = 100 * (pd.Series(plus_dm).rolling(window=period).mean() / (atr + 1e-10))
    return plus_di

def whatsapp_mesaj_gonder(mesaj):
    try:
        url = f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_PHONE}&text={urllib.parse.quote(mesaj)}&apikey={WHATSAPP_APIKEY}"
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            print("[WHATSAPP ANLIK MESAJ GÖNDERİLDİ]")
        else:
            print(f"[WHATSAPP HATA]: Kod {response.status_code}")
    except Exception as e:
        print(f"[WHATSAPP BAĞLANTI HATASI]: {e}")

def tarama_calistir():
    if not piyasa_zaman_kontrolu():
        print("Borsa seans saatleri dışındayız veya hafta sonu. Tarama atlanıyor.")
        return

    hafiza = hafiza_yukle()
    simdi_epoch = time.time()
    
    print(f"[{datetime.now(TZ_TR).strftime('%Y-%m-%d %H:%M:%S')}] 5 Dakikalık Anlık Tarama Başlatıldı...")

    for hisse in BIST_HISSELERI:
        try:
            df = yf.download(hisse, period="5d", interval="5m", progress=False)
            if df.empty or len(df) < 30:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            # İndikatörler
            df['EMA5'] = df['Close'].ewm(span=5, adjust=False).mean()
            df['EMA9'] = df['Close'].ewm(span=9, adjust=False).mean()
            df['HMA20'] = calculate_hma(df['Close'], period=20)
            df['MFI'] = mfi_hesapla(df)
            df['CMF'] = cmf_hesapla(df)
            df['+DI'] = dmi_hesapla(df)

            i = -1
            c_close = df['Close'].iloc[i]
            c_ema5 = df['EMA5'].iloc[i]
            c_ema9 = df['EMA9'].iloc[i]
            p_ema5 = df['EMA5'].iloc[i-1]
            p_ema9 = df['EMA9'].iloc[i-1]
            
            c_mfi = df['MFI'].iloc[i]
            c_cmf = df['CMF'].iloc[i]
            c_plus_di = df['+DI'].iloc[i]
            c_hma20 = df['HMA20'].iloc[i]

            # 5 KRİTER
            kosul_hma20 = c_close > c_hma20                              # 1. Hull 20 fiyatın aşağısında
            kosul_ema_kesisim = (p_ema5 <= p_ema9) and (c_ema5 > c_ema9)  # 2. EMA 5, EMA 9'u yukarı kessin
            kosul_plus_di = c_plus_di > 25                              # 3. +DI > 25
            kosul_mfi = c_mfi > 55                                      # 4. MFI > 55
            kosul_cmf = c_cmf > 0                                       # 5. CMF > 0

            if kosul_hma20 and kosul_ema_kesisim and kosul_plus_di and kosul_mfi and kosul_cmf:
                son_gonderim = hafiza.get(hisse, 0)
                if simdi_epoch - son_gonderim > COOLDOWN_SECONDS:
                    # Anlık olarak mesajı hemen gönder
                    zaman_str = datetime.now(TZ_TR).strftime('%H:%M')
                    temiz_isim = hisse.replace('.IS', '')
                    mesaj = f"🚀 *BIST Sinyal* ({zaman_str})\n• **5 DK** | *{temiz_isim}* | Fiyat: {c_close:.2f} | MFI: {c_mfi:.1f} | CMF: {c_cmf:.2f}"
                    
                    whatsapp_mesaj_gonder(mesaj)
                    
                    # Hafızayı hemen güncelle ve kaydet
                    hafiza[hisse] = simdi_epoch
                    hafiza_kaydet(hafiza)
                else:
                    print(f"{hisse} için 1 saatlik cooldown aktif.")

        except Exception as e:
            print(f"{hisse} taranırken hata: {e}")

    print("Tarama turu tamamlandı.")

if __name__ == "__main__":
    tarama_calistir()
