import requests
import yfinance as yf
import pandas as pd
import time
import os
import json
from datetime import datetime
import pytz
from flask import Flask
import threading

# --- RENDER WEB SUNUCU KABUĞU ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Fibonacci + TD + MFI Botu Aktif!", 200

# --- AYARLAR VE SABİTLER ---
MEMORY_FILE = "hafiza_fib_td_mfi.json"
COOLDOWN_SECONDS = 1800  # Aynı hisse için 30 dakika bekleme süresi
TZ_TR = pytz.timezone("Europe/Istanbul")

# Ntfy Kanalın (Ekrandaki borsa_senet kanalına uyarlandı)
NTFY_URL = "https://ntfy.sh/borsa_senet"

# BIST Tüm Hisseler Listesi
STOCKS = [
    "AAVST.IS", "ACSEL.IS", "ADEL.IS", "ADESE.IS", "ADGYO.IS", "AEFES.IS", "AFYON.IS", "AGESA.IS", "AGHOL.IS", "AGROT.IS",
    "AKBNK.IS", "AKENR.IS", "AKFGY.IS", "AKFYE.IS", "AKGRT.IS", "AKMGY.IS", "AKSA.IS", "AKSEN.IS", "AKSGY.IS", "ALARK.IS",
    "ALBRK.IS", "ALCAR.IS", "ALCTL.IS", "ALFAS.IS", "ALKA.IS", "ALKIM.IS", "ALKLC.IS", "ALMAT.IS", "ANELE.IS", "ANGEN.IS",
    "ANHYT.IS", "ANSGR.IS", "ARASE.IS", "ARCLK.IS", "ARDYZ.IS", "ARENA.IS", "ARSAN.IS", "ARTMS.IS", "ARZUM.IS", "ASELS.IS",
    "ASTOR.IS", "ASUZU.IS", "ATAKP.IS", "ATATP.IS", "ATEKS.IS", "ATLAS.IS", "AVGYO.IS", "AVOD.IS", "AVPGY.IS", "AYCES.IS",
    "AYDEM.IS", "AYEN.IS", "AYES.IS", "AYGAZ.IS", "AZTEK.IS", "BAGFS.IS", "BAKAB.IS", "BALAT.IS", "BANVT.IS", "BARMA.IS",
    "BASCM.IS", "BASGZ.IS", "BAYRK.IS", "BEGYO.IS", "BERA.IS", "BEYAZ.IS", "BIENY.IS", "BIGCH.IS", "BIMAS.IS", "BINHO.IS",
    "BIOEN.IS", "BIZIM.IS", "BJKAS.IS", "BLCYT.IS", "BMSCH.IS", "BMSTL.IS", "BNTAS.IS", "BOBET.IS", "BORLS.IS", "BOSSA.IS",
    "BRISA.IS", "BRKO.IS", "BRKSN.IS", "BRLSM.IS", "BRMEN.IS", "BRYAT.IS", "BSOKE.IS", "BTCIM.IS", "BUCIM.IS", "BURCE.IS",
    "BURVA.IS", "BVSAN.IS", "BYDNR.IS", "CANTE.IS", "CASFY.IS", "CCOLA.IS", "CELHA.IS", "CEMAS.IS", "CEMTS.IS", "CEOEM.IS",
    "CGCAM.IS", "CIMSA.IS", "CLEBI.IS", "CMBTN.IS", "CMENT.IS", "CONSE.IS", "COSMO.IS", "CRDFA.IS", "CRFSA.IS", "CUSAN.IS",
    "CVKMD.IS", "CWENE.IS", "DAGI.IS", "DAPGM.IS", "DARDL.IS", "DENGE.IS", "DERHL.IS", "DERIM.IS", "DESA.IS",
    "DESPC.IS", "DEVA.IS", "DIRIT.IS", "DITAS.IS", "DMRGD.IS", "DMSAS.IS", "DNISI.IS", "DOAS.IS", "DOBUR.IS", "DOCO.IS",
    "DOGUB.IS", "DOHOL.IS", "DSTAN.IS", "DUNYA.IS", "DURDO.IS", "DYOBY.IS", "DZGYO.IS", "EBEBK.IS", "ECILC.IS", "ECZYT.IS",
    "EDIP.IS", "EGEEN.IS", "EGEPO.IS", "EGGUB.IS", "EGPRO.IS", "EGSER.IS", "EKGYO.IS", "EKOS.IS", "EKSUN.IS", "ELITE.IS",
    "EMKEL.IS", "ENERY.IS", "ENKAI.IS", "ENJSA.IS", "EPLAS.IS", "ERBOS.IS", "EREGL.IS", "ERSU.IS", "ESCAR.IS", "ESCOM.IS",
    "ESEN.IS", "ETILR.IS", "EUHOL.IS", "EUKYO.IS", "EUPWR.IS", "EUREN.IS", "EUYO.IS", "EYGYO.IS", "FADE.IS", "FENER.IS",
    "FLAP.IS", "FMIZP.IS", "FONET.IS", "FORMT.IS", "FRIGO.IS", "FROTO.IS", "GARAN.IS", "GARFA.IS", "GEDIK.IS", "GEDZA.IS",
    "GENIL.IS", "GENTS.IS", "GEREL.IS", "GESAN.IS", "GLBMD.IS", "GLCVY.IS", "GLRYH.IS", "GLYHO.IS", "GMTAS.IS", "GOKNR.IS",
    "GOLTS.IS", "GOODY.IS", "GOZDE.IS", "GRNYO.IS", "GRSEL.IS", "GTRGY.IS", "GUBRF.IS", "GWIND.IS", "GZNMI.IS", "HALKB.IS",
    "HATEK.IS", "HATSN.IS", "HEDEF.IS", "HEKTS.IS", "HKTM.IS", "HLGYO.IS", "HTTBT.IS", "HUBVC.IS", "HURGZ.IS", "ICBCT.IS",
    "IDEAS.IS", "IDGYO.IS", "IENTS.IS", "IHEVA.IS", "IHGZT.IS", "IHLAS.IS", "IHLGM.IS", "IMASM.IS", "INDES.IS", "INFO.IS",
    "INGRM.IS", "INTEM.IS", "INVEO.IS", "INVES.IS", "IPEKE.IS", "ISATR.IS", "ISBIR.IS", "ISBTR.IS", "ISCEN.IS", "ISCTR.IS",
    "ISFIN.IS", "ISGSY.IS", "ISGYO.IS", "ISKPL.IS", "ISKUR.IS", "ISMEN.IS", "ISSEN.IS", "IZENR.IS", "IZFAS.IS", "IZINV.IS",
    "JANTS.IS", "KAPLM.IS", "KAREL.IS", "KARSN.IS", "KARTN.IS", "KARYE.IS", "KATMR.IS", "KAYSE.IS", "KBORU.IS", "KCAER.IS",
    "KCHOL.IS", "KENT.IS", "KERVT.IS", "KFEIN.IS", "KGYO.IS", "KIMMR.IS", "KLGYO.IS", "KLKIM.IS", "KLRHO.IS", "KLMSN.IS",
    "KLSER.IS", "KLSYN.IS", "KMPUR.IS", "KNFRT.IS", "KONTR.IS", "KONYA.IS", "KOPOL.IS", "KORDS.IS", "KOTON.IS", "KOZAA.IS",
    "KOZAL.IS", "KRDMD.IS", "KRGYO.IS", "KRONT.IS", "KRPLS.IS", "KRSTL.IS", "KRTEK.IS", "KZBGY.IS", "KZYGZ.IS", "LIDER.IS",
    "LIDFA.IS", "LKMNH.IS", "LMKDC.IS", "LOGO.IS", "LUKSK.IS", "MAALT.IS", "MAKIM.IS", "MAKTK.IS", "MANAS.IS", "MARKA.IS",
    "MARTI.IS", "MAVI.IS", "MEDTR.IS", "MEGAP.IS", "MEKAG.IS", "MEPET.IS", "MERCN.IS", "MERKO.IS", "METUR.IS", "MGROS.IS",
    "MIATK.IS", "MMCAS.IS", "MNDRS.IS", "MNDTR.IS", "MOBTL.IS", "MPARK.IS", "MRGYO.IS", "MTRKS.IS", "MTRYO.IS", "MZHLD.IS",
    "NATEN.IS", "NETAS.IS", "NIBAS.IS", "NTHOL.IS", "NUGYO.IS", "NUHCM.IS", "OBAMS.IS", "OBASE.IS", "ODAS.IS", "OFSYM.IS",
    "ONCSM.IS", "ORCAY.IS", "OYYAT.IS", "OZAKD.IS", "OZGYO.IS", "OZKGY.IS", "OZLTM.IS", "OZRDN.IS", "PAKRD.IS", "PAMEL.IS",
    "PAPIL.IS", "PARSN.IS", "PASEU.IS", "PCILT.IS", "PEKGY.IS", "PENGD.IS", "PENTA.IS", "PETKM.IS", "PETUN.IS", "PGSUS.IS",
    "PINSU.IS", "PKART.IS", "PKENT.IS", "PNSUT.IS", "POLHO.IS", "POLTK.IS", "PRDGS.IS", "PRKME.IS", "PRKAB.IS", "PSGYO.IS",
    "QNBFB.IS", "QNBFL.IS", "QUAGR.IS", "RALYH.IS", "REEDR.IS", "RNPOL.IS", "RODRG.IS", "ROYAL.IS", "RTALB.IS", "RUBNS.IS",
    "RYGYO.IS", "RYSAS.IS", "SAFKR.IS", "SAHOL.IS", "SASA.IS", "SAYAS.IS", "SDTTR.IS", "SEGFO.IS", "SEGYO.IS",
    "SEKFK.IS", "SEKUR.IS", "SELEC.IS", "SELVA.IS", "SEYKM.IS", "SILVR.IS", "SISE.IS", "SKBNK.IS", "SKTAS.IS", "SMART.IS",
    "SMRTG.IS", "SNGYO.IS", "SNICA.IS", "SNPAM.IS", "SODSN.IS", "SOKM.IS", "SONME.IS", "SRVGY.IS", "SUMAS.IS", "SUNTK.IS",
    "SUWEN.IS", "TABGD.IS", "TARKM.IS", "TATEN.IS", "TATGD.IS", "TAVHL.IS", "TBORG.IS", "TCELL.IS", "TCKRC.IS",
    "TDGYO.IS", "TEKTU.IS", "TETMT.IS", "TEZOL.IS", "TGSAS.IS", "THYAO.IS", "TKFEN.IS", "TKNSA.IS", "TMPOL.IS", "TMSN.IS",
    "TOASO.IS", "TRCAS.IS", "TRGYO.IS", "TRMET.IS", "TSKB.IS", "TSPOR.IS", "TTKOM.IS", "TTRAK.IS", "TUCLK.IS",
    "TUPRS.IS", "TURSG.IS", "UFUK.IS", "ULAS.IS", "ULUFA.IS", "ULKER.IS", "ULUUN.IS", "VAKBN.IS",
    "VAKFN.IS", "VAKGY.IS", "VBTYZ.IS", "VERTU.IS", "VERUS.IS", "VESBE.IS", "VESTL.IS", "VKFYO.IS", "VKGYO.IS",
    "VKING.IS", "YAPRK.IS", "YATAS.IS", "YAYLA.IS", "YBTAS.IS", "YEOTK.IS", "YESIL.IS", "YGGYO.IS", "YIGIT.IS",
    "YKBNK.IS", "YKSL.IS", "YUNSA.IS", "YYAPI.IS", "ZEDUR.IS", "ZOREN.IS", "ZRGYO.IS"
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
    if simdi.weekday() >= 5:
        return False
    baslangic = simdi.replace(hour=9, minute=30, second=0, microsecond=0)
    bitis = simdi.replace(hour=18, minute=10, second=0, microsecond=0)
    return baslangic <= simdi <= bitis

def send_ntfy(message):
    try:
        headers = {"Title": "Fibonacci + TD + MFI Sinyali", "Priority": "high"}
        requests.post(NTFY_URL, data=message.encode('utf-8'), headers=headers, timeout=10)
    except Exception as e:
        print(f"Bildirim Hatası: {e}")

def run_scanner():
    hafiza = hafiza_yukle()
    simdi_epoch = time.time()
    
    print(f"[{datetime.now(TZ_TR).strftime('%Y-%m-%d %H:%M:%S')}] Fib + TD + MFI Tarama Başladı...")

    for ticker in STOCKS:
        clean_ticker = ticker.strip()
        try:
            df = yf.download(clean_ticker, period="60d", interval="15m", progress=False)
            if df.empty or len(df) < 40:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            high = df['High']
            low = df['Low']
            close = df['Close']
            volume = df['Volume']

            roll_high = high.rolling(50).max()
            roll_low = low.rolling(50).min()
            fib_channel_upper = roll_low + (roll_high - roll_low) * 1.0

            pivots = (close < close.shift(4)).astype(int)
            setup_count = pivots.groupby((~pivots.astype(bool)).cumsum()).cumsum()

            typical_price = (high + low + close) / 3
            money_flow = typical_price * volume
            pos_flow = money_flow.where(typical_price > typical_price.shift(1), 0).rolling(14).sum()
            neg_flow = money_flow.where(typical_price < typical_price.shift(1), 0).rolling(14).sum()
            mfi = 100 - (100 / (1 + (pos_flow / (neg_flow + 1e-10))))

            recent_setups = setup_count.tail(15)
            if 9 in recent_setups.values:
                idx_9 = recent_setups[recent_setups == 9].index[-1]
                loc_9 = df.index.get_loc(idx_9)
                start_loc = max(0, loc_9 - 8)
                setup_high = high.iloc[start_loc:loc_9+1].max()

                curr_close = close.iloc[-1]
                curr_fib_upper = fib_channel_upper.iloc[-1]
                curr_mfi = mfi.iloc[-1]

                if (curr_close > setup_high or curr_close > curr_fib_upper) and (curr_mfi > 55):
                    son_gonderim = hafiza.get(clean_ticker, 0)
                    if simdi_epoch - son_gonderim > COOLDOWN_SECONDS:
                        temiz_isim = clean_ticker.replace(".IS", "")
                        zaman_str = datetime.now(TZ_TR).strftime('%H:%M')
                        
                        mesaj = f"🎯 *Fib + TD + MFI* ({zaman_str})\n• Hisse: *{temiz_isim}* | Fiyat: {curr_close:.2f}\n• MFI: {curr_mfi:.1f} | Kanal Üst: {curr_fib_upper:.2f}"
                        send_ntfy(mesaj)
                        
                        hafiza[clean_ticker] = simdi_epoch
                        hafiza_kaydet(hafiza)

        except Exception as e:
            continue

def background_loop():
    while True:
        if piyasa_zaman_kontrolu():
            try:
                run_scanner()
            except Exception as e:
                print(f"Hata: {e}")
            time.sleep(900)
        else:
            time.sleep(300)

thread = threading.Thread(target=background_loop, daemon=True)
thread.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
