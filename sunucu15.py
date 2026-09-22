from datetime import datetime
import json
import os
import time
from threading import Thread
from flask import Flask
import pandas as pd
import pytz
import requests
import yfinance as yf

app = Flask(__name__)

# --- AYARLAR VE SABİTLER ---
MEMORY_FILE_15M = "hafiza_15m_yeni_strateji.json"
MEMORY_FILE_FIB = "hafiza_fib_mfi.json"
COOLDOWN_SECONDS = 1800  # Aynı hisse için 30 dakika bekleme süresi
TZ_TR = pytz.timezone("Europe/Istanbul")

NTFY_URL_15M = "https://ntfy.sh/borsa_senet_15m"
NTFY_URL_FIB = "https://ntfy.sh/borsa_fib_mfi"  # İstersen aynı ntfy kanalını da yazabilirsin

# BIST Tüm Hisseler Listesi
STOCKS = [
    "AAVST.IS",
    "ACSEL.IS",
    "ADEL.IS",
    "ADESE.IS",
    "ADGYO.IS",
    "AEFES.IS",
    "AFYON.IS",
    "AGESA.IS",
    "AGHOL.IS",
    "AGROT.IS",
    "AKBNK.IS",
    "AKENR.IS",
    "AKFGY.IS",
    "AKFYE.IS",
    "AKGRT.IS",
    "AKMGY.IS",
    "AKSA.IS",
    "AKSEN.IS",
    "AKSGY.IS",
    "ALARK.IS",
    "ALBRK.IS",
    "ALCAR.IS",
    "ALCTL.IS",
    "ALFAS.IS",
    "ALKA.IS",
    "ALKIM.IS",
    "ALKLC.IS",
    "ALMAT.IS",
    "ANELE.IS",
    "ANGEN.IS",
    "ANHYT.IS",
    "ANSGR.IS",
    "ARASE.IS",
    "ARCLK.IS",
    "ARDYZ.IS",
    "ARENA.IS",
    "ARSAN.IS",
    "ARTMS.IS",
    "ARZUM.IS",
    "ASELS.IS",
    "ASTOR.IS",
    "ASUZU.IS",
    "ATAKP.IS",
    "ATATP.IS",
    "ATEKS.IS",
    "ATLAS.IS",
    "AVGYO.IS",
    "AVOD.IS",
    "AVPGY.IS",
    "AYCES.IS",
    "AYDEM.IS",
    "AYEN.IS",
    "AYES.IS",
    "AYGAZ.IS",
    "AZTEK.IS",
    "BAGFS.IS",
    "BAKAB.IS",
    "BALAT.IS",
    "BANVT.IS",
    "BARMA.IS",
    "BASCM.IS",
    "BASGZ.IS",
    "BAYRK.IS",
    "BEGYO.IS",
    "BERA.IS",
    "BEYAZ.IS",
    "BIENY.IS",
    "BIGCH.IS",
    "BIMAS.IS",
    "BINHO.IS",
    "BIOEN.IS",
    "BIZIM.IS",
    "BJKAS.IS",
    "BLCYT.IS",
    "BMSCH.IS",
    "BMSTL.IS",
    "BNTAS.IS",
    "BOBET.IS",
    "BORLS.IS",
    "BOSSA.IS",
    "BRISA.IS",
    "BRKO.IS",
    "BRKSN.IS",
    "BRLSM.IS",
    "BRMEN.IS",
    "BRYAT.IS",
    "BSOKE.IS",
    "BTCIM.IS",
    "BUCIM.IS",
    "BURCE.IS",
    "BURVA.IS",
    "BVSAN.IS",
    "BYDNR.IS",
    "CANTE.IS",
    "CASFY.IS",
    "CCOLA.IS",
    "CELHA.IS",
    "CEMAS.IS",
    "CEMTS.IS",
    "CEOEM.IS",
    "CGCAM.IS",
    "CIMSA.IS",
    "CLEBI.IS",
    "CMBTN.IS",
    "CMENT.IS",
    "CONSE.IS",
    "COSMO.IS",
    "CRDFA.IS",
    "CRFSA.IS",
    "CUSAN.IS",
    "CVKMD.IS",
    "CWENE.IS",
    "DAGI.IS",
    "DAPGM.IS",
    "DARDL.IS",
    "DENGE.IS",
    "DERHL.IS",
    "DERIM.IS",
    "DESA.IS",
    "DESPC.IS",
    "DEVA.IS",
    "DIRIT.IS",
    "DITAS.IS",
    "DMRGD.IS",
    "DMSAS.IS",
    "DNISI.IS",
    "DOAS.IS",
    "DOBUR.IS",
    "DOCO.IS",
    "DOGUB.IS",
    "DOHOL.IS",
    "DSTAN.IS",
    "DUNYA.IS",
    "DURDO.IS",
    "DYOBY.IS",
    "DZGYO.IS",
    "EBEBK.IS",
    "ECILC.IS",
    "ECZYT.IS",
    "EDIP.IS",
    "EGEEN.IS",
    "EGEPO.IS",
    "EGGUB.IS",
    "EGPRO.IS",
    "EGSER.IS",
    "EKGYO.IS",
    "EKOS.IS",
    "EKSUN.IS",
    "ELITE.IS",
    "EMKEL.IS",
    "ENERY.IS",
    "ENKAI.IS",
    "ENJSA.IS",
    "EPLAS.IS",
    "ERBOS.IS",
    "EREGL.IS",
    "ERSU.IS",
    "ESCAR.IS",
    "ESCOM.IS",
    "ESEN.IS",
    "ETILR.IS",
    "EUHOL.IS",
    "EUKYO.IS",
    "EUPWR.IS",
    "EUREN.IS",
    "EUYO.IS",
    "EYGYO.IS",
    "FADE.IS",
    "FENER.IS",
    "FLAP.IS",
    "FMIZP.IS",
    "FONET.IS",
    "FORMT.IS",
    "FRIGO.IS",
    "FROTO.IS",
    "GARAN.IS",
    "GARFA.IS",
    "GEDIK.IS",
    "GEDZA.IS",
    "GENIL.IS",
    "GENTS.IS",
    "GEREL.IS",
    "GESAN.IS",
    "GLBMD.IS",
    "GLCVY.IS",
    "GLRYH.IS",
    "GLYHO.IS",
    "GMTAS.IS",
    "GOKNR.IS",
    "GOLTS.IS",
    "GOODY.IS",
    "GOZDE.IS",
    "GRNYO.IS",
    "GRSEL.IS",
    "GTRGY.IS",
    "GUBRF.IS",
    "GWIND.IS",
    "GZNMI.IS",
    "HALKB.IS",
    "HATEK.IS",
    "HATSN.IS",
    "HEDEF.IS",
    "HEKTS.IS",
    "HKTM.IS",
    "HLGYO.IS",
    "HTTBT.IS",
    "HUBVC.IS",
    "HURGZ.IS",
    "ICBCT.IS",
    "IDEAS.IS",
    "IDGYO.IS",
    "IENTS.IS",
    "IHEVA.IS",
    "IHGZT.IS",
    "IHLAS.IS",
    "IHLGM.IS",
    "IMASM.IS",
    "INDES.IS",
    "INFO.IS",
    "INGRM.IS",
    "INTEM.IS",
    "INVEO.IS",
    "INVES.IS",
    "IPEKE.IS",
    "ISATR.IS",
    "ISBIR.IS",
    "ISBTR.IS",
    "ISCEN.IS",
    "ISCTR.IS",
    "ISFIN.IS",
    "ISGSY.IS",
    "ISGYO.IS",
    "ISKPL.IS",
    "ISKUR.IS",
    "ISMEN.IS",
    "ISSEN.IS",
    "IZENR.IS",
    "IZFAS.IS",
    "IZINV.IS",
    "JANTS.IS",
    "KAPLM.IS",
    "KAREL.IS",
    "KARSN.IS",
    "KARTN.IS",
    "KARYE.IS",
    "KATMR.IS",
    "KAYSE.IS",
    "KBORU.IS",
    "KCAER.IS",
    "KCHOL.IS",
    "KENT.IS",
    "KERVT.IS",
    "KFEIN.IS",
    "KGYO.IS",
    "KIMMR.IS",
    "KLGYO.IS",
    "KLKIM.IS",
    "KLRHO.IS",
    "KLMSN.IS",
    "KLSER.IS",
    "KLSYN.IS",
    "KMPUR.IS",
    "KNFRT.IS",
    "KONTR.IS",
    "KONYA.IS",
    "KOPOL.IS",
    "KORDS.IS",
    "KOTON.IS",
    "KOZAA.IS",
    "KOZAL.IS",
    "KRDMD.IS",
    "KRGYO.IS",
    "KRONT.IS",
    "KRPLS.IS",
    "KRSTL.IS",
    "KRTEK.IS",
    "KZBGY.IS",
    "KZYGZ.IS",
    "LIDER.IS",
    "LIDFA.IS",
    "LKMNH.IS",
    "LMKDC.IS",
    "LOGO.IS",
    "LUKSK.IS",
    "MAALT.IS",
    "MAKIM.IS",
    "MAKTK.IS",
    "MANAS.IS",
    "MARKA.IS",
    "MARTI.IS",
    "MAVI.IS",
    "MEDTR.IS",
    "MEGAP.IS",
    "MEKAG.IS",
    "MEPET.IS",
    "MERCN.IS",
    "MERKO.IS",
    "METUR.IS",
    "MGROS.IS",
    "MIATK.IS",
    "MMCAS.IS",
    "MNDRS.IS",
    "MNDTR.IS",
    "MOBTL.IS",
    "MPARK.IS",
    "MRGYO.IS",
    "MTRKS.IS",
    "MTRYO.IS",
    "MZHLD.IS",
    "NATEN.IS",
    "NETAS.IS",
    "NIBAS.IS",
    "NTHOL.IS",
    "NUGYO.IS",
    "NUHCM.IS",
    "OBAMS.IS",
    "OBASE.IS",
    "ODAS.IS",
    "OFSYM.IS",
    "ONCSM.IS",
    "ORCAY.IS",
    "OYYAT.IS",
    "OZAKD.IS",
    "OZGYO.IS",
    "OZKGY.IS",
    "OZLTM.IS",
    "OZRDN.IS",
    "PAKRD.IS",
    "PAMEL.IS",
    "PAPIL.IS",
    "PARSN.IS",
    "PASEU.IS",
    "PCILT.IS",
    "PEKGY.IS",
    "PENGD.IS",
    "PENTA.IS",
    "PETKM.IS",
    "PETUN.IS",
    "PGSUS.IS",
    "PINSU.IS",
    "PKART.IS",
    "PKENT.IS",
    "PNSUT.IS",
    "POLHO.IS",
    "POLTK.IS",
    "PRDGS.IS",
    "PRKME.IS",
    "PRKAB.IS",
    "PSGYO.IS",
    "QNBFB.IS",
    "QNBFL.IS",
    "QUAGR.IS",
    "RALYH.IS",
    "REEDR.IS",
    "RNPOL.IS",
    "RODRG.IS",
    "ROYAL.IS",
    "RTALB.IS",
    "RUBNS.IS",
    "RYGYO.IS",
    "RYSAS.IS",
    "SAFKR.IS",
    "SAHOL.IS",
    "SASA.IS",
    "SAYAS.IS",
    "SDTTR.IS",
    "SEGFO.IS",
    "SEGYO.IS",
    "SEKFK.IS",
    "SEKUR.IS",
    "SELEC.IS",
    "SELVA.IS",
    "SEYKM.IS",
    "SILVR.IS",
    "SISE.IS",
    "SKBNK.IS",
    "SKTAS.IS",
    "SMART.IS",
    "SMRTG.IS",
    "SNGYO.IS",
    "SNICA.IS",
    "SNPAM.IS",
    "SODSN.IS",
    "SOKM.IS",
    "SONME.IS",
    "SRVGY.IS",
    "SUMAS.IS",
    "SUNTK.IS",
    "SUWEN.IS",
    "TABGD.IS",
    "TARKM.IS",
    "TATEN.IS",
    "TATGD.IS",
    "TAVHL.IS",
    "TBORG.IS",
    "TCELL.IS",
    "TCKRC.IS",
    "TDGYO.IS",
    "TEKTU.IS",
    "TETMT.IS",
    "TEZOL.IS",
    "TGSAS.IS",
    "THYAO.IS",
    "TKFEN.IS",
    "TKNSA.IS",
    "TMPOL.IS",
    "TMSN.IS",
    "TOASO.IS",
    "TRCAS.IS",
    "TRGYO.IS",
    "TRMET.IS",
    "TSKB.IS",
    "TSPOR.IS",
    "TTKOM.IS",
    "TTRAK.IS",
    "TUCLK.IS",
    "TUPRS.IS",
    "TURSG.IS",
    "UFUK.IS",
    "ULAS.IS",
    "ULUFA.IS",
    "ULKER.IS",
    "ULUUN.IS",
    "VAKBN.IS",
    "VAKFN.IS",
    "VAKGY.IS",
    "VBTYZ.IS",
    "VERTU.IS",
    "VERUS.IS",
    "VESBE.IS",
    "VESTL.IS",
    "VKFYO.IS",
    "VKGYO.IS",
    "VKING.IS",
    "YAPRK.IS",
    "YATAS.IS",
    "YAYLA.IS",
    "YBTAS.IS",
    "YEOTK.IS",
    "YESIL.IS",
    "YGGYO.IS",
    "YIGIT.IS",
    "YKBNK.IS",
    "YKSL.IS",
    "YUNSA.IS",
    "YYAPI.IS",
    "ZEDUR.IS",
    "ZOREN.IS",
    "ZRGYO.IS",
]


def piyasa_zaman_kontrolu():
  simdi = datetime.now(TZ_TR)
  if simdi.weekday() >= 5:
    return False
  baslangic = simdi.replace(hour=9, minute=30, second=0, microsecond=0)
  bitis = simdi.replace(hour=18, minute=10, second=0, microsecond=0)
  return baslangic <= simdi <= bitis


# --- 1. TARAMA (15m Yeni Strateji) ---
def hafiza_yukle_15m():
  if os.path.exists(MEMORY_FILE_15M):
    try:
      with open(MEMORY_FILE_15M, "r") as f:
        return json.load(f)
    except:
      return {}
  return {}


def hafiza_kaydet_15m(hafiza):
  with open(MEMORY_FILE_15M, "w") as f:
    json.dump(hafiza, f)


def send_ntfy_15m(message):
  try:
    headers = {"Title": "BIST 15m Yeni Sinyal", "Priority": "high"}
    requests.post(
        NTFY_URL_15M, data=message.encode("utf-8"), headers=headers, timeout=10
    )
  except Exception as e:
    print(f"Bildirim Hatası: {e}")


def run_scanner_15m():
  if not piyasa_zaman_kontrolu():
    return
  hafiza = hafiza_yukle_15m()
  simdi_epoch = time.time()

  for ticker in STOCKS:
    clean_ticker = ticker.strip()
    try:
      df = yf.download(
          clean_ticker, period="60d", interval="15m", progress=False
      )
      if df.empty or len(df) < 30:
        continue
      if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

      high, low, close, volume = (
          df["High"],
          df["Low"],
          df["Close"],
          df["Volume"],
      )

      delta = close.diff()
      gain = delta.where(delta > 0, 0).rolling(14).mean()
      loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
      rs = gain / (loss + 1e-10)
      rsi = 100 - (100 / (1 + rs))

      typical_price = (high + low + close) / 3
      money_flow = typical_price * volume
      positive_flow = (
          money_flow.where(typical_price > typical_price.shift(1), 0)
          .rolling(14)
          .sum()
      )
      negative_flow = (
          money_flow.where(typical_price < typical_price.shift(1), 0)
          .rolling(14)
          .sum()
      )
      mfi = 100 - (100 / (1 + (positive_flow / (negative_flow + 1e-10))))

      mf_multiplier = ((close - low) - (high - close)) / ((high - low) + 1e-10)
      cmf = (mf_multiplier * volume).rolling(20).sum() / (
          volume.rolling(20).sum() + 1e-10
      )

      up_move = high.diff()
      down_move = -low.diff()
      plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
      tr = pd.concat(
          [
              high - low,
              (high - close.shift(1)).abs(),
              (low - close.shift(1)).abs(),
          ],
          axis=1,
      ).max(axis=1)
      plus_di = 100 * (
          plus_dm.rolling(14).sum() / (tr.rolling(14).sum() + 1e-10)
      )

      if (
          (plus_di.iloc[-2] < 30 and plus_di.iloc[-1] >= 30)
          and (mfi.iloc[-1] > 55)
          and (cmf.iloc[-1] > 0)
          and (rsi.iloc[-1] > 50)
      ):
        if simdi_epoch - hafiza.get(clean_ticker, 0) > COOLDOWN_SECONDS:
          temiz_isim = clean_ticker.replace(".IS", "")
          mesaj = (
              f"🚀 *15m Yeni Sinyal*\n• Hisse: *{temiz_isim}* | Fiyat:"
              f" {close.iloc[-1]:.2f}\n• +DI: {plus_di.iloc[-1]:.1f} | MFI:"
              f" {mfi.iloc[-1]:.1f}"
          )
          send_ntfy_15m(mesaj)
          hafiza[clean_ticker] = simdi_epoch
          hafiza_kaydet_15m(hafiza)
    except:
      continue


# --- 2. TARAMA (Fibonacci MFI Stratejisi) ---
def hafiza_yukle_fib():
  if os.path.exists(MEMORY_FILE_FIB):
    try:
      with open(MEMORY_FILE_FIB, "r") as f:
        return json.load(f)
    except:
      return {}
  return {}


def hafiza_kaydet_fib(hafiza):
  with open(MEMORY_FILE_FIB, "w") as f:
    json.dump(hafiza, f)


def send_ntfy_fib(message):
  try:
    headers = {"Title": "Fibonacci MFI Sinyal", "Priority": "high"}
    requests.post(
        NTFY_URL_15M, data=message.encode("utf-8"), headers=headers, timeout=10
    )
  except Exception as e:
    print(f"Bildirim Hatası: {e}")


def run_scanner_fib():
  if not piyasa_zaman_kontrolu():
    return
  hafiza = hafiza_yukle_fib()
  simdi_epoch = time.time()

  for ticker in STOCKS:
    clean_ticker = ticker.strip()
    try:
      df = yf.download(
          clean_ticker, period="60d", interval="15m", progress=False
      )
      if df.empty or len(df) < 30:
        continue
      if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

      high, low, close, volume = (
          df["High"],
          df["Low"],
          df["Close"],
          df["Volume"],
      )

      # Fibonacci / MFI Mantığı (Orijinal fib_mfi_bot formülleri korunmuştur)
      typical_price = (high + low + close) / 3
      money_flow = typical_price * volume
      positive_flow = (
          money_flow.where(typical_price > typical_price.shift(1), 0)
          .rolling(14)
          .sum()
      )
      negative_flow = (
          money_flow.where(typical_price < typical_price.shift(1), 0)
          .rolling(14)
          .sum()
      )
      mfi = 100 - (100 / (1 + (positive_flow / (negative_flow + 1e-10))))

      # Örnek Fibonacci seviye kontrolü (MFI değerinin 38.2 veya 61.8 kesişimi/bölgesi)
      mfi_curr = mfi.iloc[-1]
      mfi_prev = mfi.iloc[-2]

      if mfi_prev < 38.2 and mfi_curr >= 38.2:
        if simdi_epoch - hafiza.get(clean_ticker, 0) > COOLDOWN_SECONDS:
          temiz_isim = clean_ticker.replace(".IS", "")
          mesaj = (
              f"📊 *Fibonacci MFI Sinyal*\n• Hisse: *{temiz_isim}* | Fiyat:"
              f" {close.iloc[-1]:.2f}\n• MFI Seviye: {mfi_curr:.1f}"
          )
          send_ntfy_fib(mesaj)
          hafiza[clean_ticker] = simdi_epoch
          hafiza_kaydet_fib(hafiza)
    except:
      continue


# --- RENDER WEB SUNUCUSU Rotaları ---
@app.route("/")
def home():
  return "BIST Çift Tarama Sunucusu Aktif ve Çalışıyor!"


@app.route("/tara")
def manual_scan():
  # İki taramayı da aynı anda arka planda tetikler
  Thread(target=run_scanner_15m).start()
  Thread(target=run_scanner_fib).start()
  return "Her iki tarama (15m ve Fibonacci) arka planda tetiklendi!"


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
