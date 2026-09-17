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
MEMORY_FILE = "hafiza_15dk.json"
COOLDOWN_SECONDS = 3600  # Aynı hisse için 1 saat içinde tekrar sinyal atmasın
TZ_TR = pytz.timezone("Europe/Istanbul")

# WhatsApp (CallMeBot) Bilgileri
WHATSAPP_PHONE = "905462848792"
WHATSAPP_APIKEY = "3477940"

# BIST Hisseler Listesi
STOCKS = [
    "AAVST.IS", "ACSEL.IS", "ADEL.IS", "ADESE.IS", "ADGYO.IS", "AEFES.IS", "AFYON.IS", "AGESA.IS",
    "AKBNK.IS", "AKENR.IS", "AKFGY.IS", "AKFYE.IS", "AKGRT.IS", "AKMGY.IS", "AKSA.IS", "AKSEN.IS",
    "ALBRK.IS", "ALCAR.IS", "ALCTL.IS", "ALFAS.IS", "ALKA.IS", "ALKIM.IS", "ALKLC.IS", "ALMAT.IS",
    "ANHYT.IS", "ANSGR.IS", "ARASE.IS", "ARCLK.IS", "ARDYZ.IS", "ARENA.IS", "ARSAN.IS", "ARTMS.IS",
    "ASTOR.IS", "ASUZU.IS", "ATAKP.IS", "ATATP.IS", "ATEKS.IS", "ATLAS.IS", "AVGYO.IS", "AVOD.IS",
    "AYDEM.IS", "AYEN.IS", "AYES.IS", "AYGAZ.IS", "AZTEK.IS", "BAGFS.IS", "BAKAB.IS", "BALAT.IS",
    "BASCM.IS", "BASGZ.IS", "BAYRK.IS", "BEGYO.IS", "BERA.IS", "BEYAZ.IS", "BIENY.IS", "BIGCH.IS",
    "BIOEN.IS", "BIZIM.IS", "BJKAS.IS", "BLCYT.IS", "BMSCH.IS", "BMSTL.IS", "BNTAS.IS", "BOBET.IS",
    "BRISA.IS", "BRKO.IS", "BRKSN.IS", "BRLSM.IS", "BRMEN.IS", "BRYAT.IS", "BSOKE.IS", "BTCIM.IS",
    "BURVA.IS", "BVSAN.IS", "BYDNR.IS", "CANTE.IS", "CASFY.IS", "CCOLA.IS", "CELHA.IS", "CEMAS.IS",
    "CGCAM.IS", "CIMSA.IS", "CLEBI.IS", "CMBTN.IS", "CEMENT.IS", "CONSE.IS", "COSMO.IS", "CRDFA.IS",
    "CVKMD.IS", "CWENE.IS", "DAGI.IS", "DAPGM.IS", "DARDL.IS", "DENGE.IS", "DERHL.IS",
    "DESPC.IS", "DEVA.IS", "DIRIT.IS", "DITAS.IS", "DMRGD.IS", "DMSAS.IS", "DNISI.IS", "DOAS.IS",
    "DOGUB.IS", "DOHOL.IS", "DSTAN.IS", "DUNYA.IS", "DURDO.IS", "DYOBY.IS", "DZGYO.IS", "EBEBK.IS",
    "EDIP.IS", "EGEEN.IS", "EGEPO.IS", "EGGUB.IS", "EGPRO.IS", "EGSER.IS", "EKGYO.IS", "EKOS.IS",
    "EMKEL.IS", "ENERY.IS", "ENKAI.IS", "ENJSA.IS", "EPLAS.IS", "ERBOS.IS", "EREGL.IS", "ERSU.IS",
    "ESEN.IS", "ETILR.IS", "EUHOL.IS", "EUKYO.IS", "EUPWR.IS", "EUREN.IS", "EUYO.IS", "EYGYO.IS",
    "FLAP.IS", "FMIZP.IS", "FONET.IS", "FORMT.IS", "FRIGO.IS", "FROTO.IS", "GARAN.IS", "GARFA.IS",
    "GENIL.IS", "GENTS.IS", "GEREL.IS", "GESAN.IS", "GLBMD.IS", "GLCVY.IS", "GLRYH.IS", "GLYHO.IS",
    "GOLTS.IS", "GOODY.IS", "GOZDE.IS", "GRNYO.IS", "GRSEL.IS", "GTRGY.IS", "GUBRF.IS", "GWIND.IS",
    "HALKB.IS", "HATEK.IS", "HATSN.IS", "HEDEF.IS", "HEKTS.IS", "HKTM.IS", "HLGYO.IS", "HOROZ.IS",
    "HTTBT.IS", "HZNDR.IS", "IHEVA.IS", "IHGZT.IS", "IHLAS.IS", "IHLGM.IS", "IMASM.IS", "INDES.IS",
    "INFO.IS", "INTEM.IS", "INVEO.IS", "IPEKE.IS", "ISCTR.IS", "ISDMR.IS", "ISFIN.IS", "ISGSY.IS",
    "ISGYO.IS", "ISKPL.IS", "ISMEN.IS", "ISSEN.IS", "IZENR.IS", "IZFAS.IS", "IZINV.IS", "JANTS.IS",
    "KAPLM.IS", "KAREL.IS", "KARSN.IS", "KARTN.IS", "KARYE.IS", "KCAER.IS", "KCHOL.IS", "KENT.IS",
    "KERVT.IS", "KFEIN.IS", "KGYO.IS", "KIMMR.IS", "KLGYO.IS", "KLKIM.IS", "KLSYN.IS", "KMPUR.IS",
    "KNFRT.IS", "KONTR.IS", "KONYA.IS", "KOPOL.IS", "KORDS.IS", "KOTON.IS", "KOZAA.IS", "KOZAL.IS",
    "KRDMD.IS", "KRGYO.IS", "KRONT.IS", "KRPLS.IS", "KRSTL.IS", "KRTEK.IS", "KTLEV.IS", "KTSKR.IS",
    "KUTPO.IS", "KUVVA.IS", "KUYAS.IS", "LIDER.IS", "LKMNH.IS", "LOGO.IS", "LUKSK.IS", "MAALT.IS",
    "MAKIM.IS", "MAKTK.IS", "MANAS.IS", "MARKA.IS", "MARTI.IS", "MAVI.IS", "MEDTR.IS", "MEGAP.IS",
    "MEKAG.IS", "MEMUR.IS", "MERCN.IS", "MERIT.IS", "MERKO.IS", "MGROS.IS", "MIATK.IS", "MIPAZ.IS",
    "MMCAS.IS", "MNDRS.IS", "MNDTR.IS", "MOBTL.IS", "MPARK.IS", "MRSHL.IS", "MSGYO.IS", "MTRKS.IS",
    "MIVEN.IS", "Naten.IS", "NETAS.IS", "NIBAS.IS", "NTGAZ.IS", "NTHOL.IS", "NUGYO.IS", "NUHCM.IS",
    "OBAMS.IS", "OBASE.IS", "ODAS.IS", "OFSYM.IS", "ONCSM.IS", "ORGE.IS", "ORMA.IS", "OSMEN.IS",
    "OSTIM.IS", "OTKAR.IS", "OYAKC.IS", "OYLUM.IS", "OYYAT.IS", "OZATD.IS", "OZGYO.IS", "OZKGY.IS",
    "OZRDN.IS", "PASTR.IS", "PAKDM.IS", "PANRM.IS", "PCILT.IS", "PEKGY.IS", "PENGD.IS", "PENTA.IS",
    "PETKM.IS", "PETUN.IS", "PGSUS.IS", "PINSU.IS", "PKART.IS", "PKENT.IS", "PNSUT.IS", "POLHO.IS",
    "POLTK.IS", "PRDGS.IS", "PRKME.IS", "PRKTS.IS", "PSGYO.IS", "QUAGR.IS", "RALYH.IS", "RAYSG.IS",
    "REYSAS.IS", "RNPOL.IS", "RODRG.IS", "ROYAL.IS", "RTALB.IS", "RUBNS.IS", "RYGYO.IS", "RYSAS.IS",
    "SAFKR.IS", "SAHOL.IS", "SARKY.IS", "SASA.IS", "SAYAS.IS", "SDTTR.IS", "SEGMN.IS", "SEGYO.IS",
    "SEKFK.IS", "SEKUR.IS", "SELEC.IS", "SELGD.IS", "SELVA.IS", "SEYKM.IS", "SILVR.IS", "SISE.IS",
    "SKBNK.IS", "SMRTG.IS", "SNGYO.IS", "SNICA.IS", "SNKRN.IS", "SNPAM.IS", "SODSN.IS", "SOKE.IS",
    "SOKM.IS", "SONME.IS", "SUMAS.IS", "SUNTK.IS", "SUWEN.IS", "TABGD.IS", "TARKM.IS", "TATEN.IS",
    "TATGD.IS", "TAVHL.IS", "TBORG.IS", "TCELL.IS", "TCKRC.IS", "TDGYO.IS", "TEHOL.IS", "TEKFN.IS",
    "TEKTU.IS", "TETMT.IS", "TEZOL.IS", "TGSAS.IS", "THYAO.IS", "TIAFS.IS", "TKFEN.IS", "TKNSA.IS",
    "TMPOL.IS", "TMSN.IS", "TOASO.IS", "TRGYO.IS", "TRILC.IS", "TSKB.IS", "TSPOR.IS", "TTKOM.IS",
    "TTRAK.IS", "TUCLK.IS", "TUPRS.IS", "TUREX.IS", "TURGG.IS", "UFUK.IS", "ULAS.IS", "ULKER.IS",
    "ULUUN.IS", "UMPAS.IS", "UNLU.IS", "USAK.IS", "VAKBN.IS", "VAKFN.IS", "VAKGY.IS", "VANGD.IS",
    "VBTYZ.IS", "VERTU.IS", "VERUS.IS", "VESBE.IS", "VESTL.IS", "VKGYO.IS", "VKING.IS", "YAPRK.IS",
    "YATAS.IS", "YAYLA.IS", "YBTAS.IS", "YEOTK.IS", "YESIL.IS", "YGGYO.IS", "YKBNK.IS", "YKSL.IS",
    "YUNSA.IS", "YYAPI.IS", "ZEDUR.IS", "ZOREN.IS"
]

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_memory(memory):
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f)
    except Exception as e:
        print(f"Hafıza kayıt hatası: {e}")

def send_whatsapp(message):
    encoded_message = urllib.parse.quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={WHATSAPP_PHONE}&text={encoded_message}&apikey={WHATSAPP_APIKEY}"
    try:
        res = requests.get(url, timeout=10)
        print(f"WhatsApp Yanıtı: {res.status_code}")
    except Exception as e:
        print(f"Mesaj Hatası: {e}")

def run_scanner():
    print(f"BIST 15dk Tarama Başlatıldı... Toplam Hisse: {len(STOCKS)}")
    memory = load_memory()
    current_time = time.time()
    matched = []

    for ticker in STOCKS:
        clean_ticker = ticker.strip()
        short_name = clean_ticker.replace(".IS", "")
        
        # Cooldown kontrolü (1 saat içinde tekrar sinyal atmasın)
        if short_name in memory:
            if current_time - memory[short_name] < COOLDOWN_SECONDS:
                continue

        try:
            df = yf.download(clean_ticker, period="5d", interval="15m", progress=False)
            if df.empty or len(df) < 30:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            close = df['Close']
            high = df['High']
            low = df['Low']
            volume = df['Volume']

            # --- ESKİ 15DK ORİJİNAL İNDİKATÖRLERİ ---
            # Hull Moving Average (HMA 14)
            def calculate_hma(series, period=14):
                half_period = int(period / 2)
                sqrt_period = int(np.sqrt(period))
                wma_half = series.rolling(half_period).apply(lambda x: np.dot(x, np.arange(1, len(x) + 1)) / np.sum(np.arange(1, len(x) + 1)), raw=True)
                wma_full = series.rolling(period).apply(lambda x: np.dot(x, np.arange(1, len(x) + 1)) / np.sum(np.arange(1, len(x) + 1)), raw=True)
                diff = 2 * wma_half - wma_full
                return diff.rolling(sqrt_period).apply(lambda x: np.dot(x, np.arange(1, len(x) + 1)) / np.sum(np.arange(1, len(x) + 1)), raw=True)

            hma = calculate_hma(close, 14)

            # MFI (14)
            typical_price = (high + low + close) / 3
            money_flow = typical_price * volume
            positive_flow = money_flow.where(typical_price > typical_price.shift(1), 0).rolling(14).sum()
            negative_flow = money_flow.where(typical_price < typical_price.shift(1), 0).rolling(14).sum()
            mfi = 100 - (100 / (1 + (positive_flow / negative_flow)))

            # CMF (20)
            mf_multiplier = ((close - low) - (high - close)) / (high - low)
            mf_volume = mf_multiplier * volume
            cmf = mf_volume.rolling(20).sum() / volume.rolling(20).sum()

            # +DI (14)
            up_move = high.diff()
            down_move = -low.diff()
            plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
            tr = pd.concat([high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
            plus_di = 100 * (plus_dm.rolling(14).sum() / tr.rolling(14).sum())

            # Relative Volume (RVOL)
            rvol = volume / volume.rolling(20).mean()

            hma_curr = hma.iloc[-1]
            hma_prev = hma.iloc[-2]
            mfi_curr = mfi.iloc[-1]
            plus_di_curr = plus_di.iloc[-1]
            cmf_curr = cmf.iloc[-1]
            rvol_curr = rvol.iloc[-1]
            close_curr = close.iloc[-1]

            # --- ESKİ 15DK ORİJİNAL KOŞULLARI ---
            if (hma_curr > hma_prev) and (close_curr > hma_curr) and (mfi_curr > 50) and (plus_di_curr > 25) and (cmf_curr > 0) and (rvol_curr > 1.2):
                matched.append(short_name)
                memory[short_name] = current_time

        except Exception as e:
            continue

    save_memory(memory)

    if matched:
        rapor_metni = "⚡ BIST 15dk Momentum Sinyali:\n" + "\n".join([f"• {hisse}" for hisse in matched])
        send_whatsapp(rapor_metni)
    else:
        print("Yeni uyan 15dk'lık hisse bulunamadı.")

if __name__ == "__main__":
    run_scanner()
