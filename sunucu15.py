from datetime import datetime
import json
import math
import os
import threading
import time
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import pytz
import requests
import yfinance as yf

# --- FLASK WEB SUNUCUSU ---
app = Flask(__name__)


@app.route("/")
def index():
  try:
    # Timeout (zaman aşımı) hatasını önlemek için taramayı arka planda (thread) başlatıyoruz
    t = threading.Thread(target=super_15dk_taramasi)
    t.start()
    return (
        "Süper 15 taraması arka planda başarıyla başlatıldı! Hisseler taranıyor"
        " 🚀",
        200,
    )
  except Exception as e:
    return f"Tarama başlatılırken hata oluştu: {e}", 500


# --- AYARLAR VE SABİTLER ---
MEMORY_FILE = "hafiza_sunucu15.json"
COOLDOWN_SECONDS = 3600  # Aynı hisse için 1 saat içinde tekrar bildirim gitmesin
TZ_TR = pytz.timezone("Europe/Istanbul")

# ntfy.sh Bildirim Ayarları (Resimdeki konuya göre güncellendi)
NTFY_TOPIC = "borsa_senet"


# --- BIST TÜM HİSSELER (DÜZENLİ LİSTE) ---
BIST_HISSELERI = [
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


# --- HAFIZA VE SEANS KONTROLÜ ---
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


# --- İNDİKATÖR FONKSİYONLARI ---
def weighted_moving_average(series, period):
  weights = np.arange(1, period + 1)
  return series.rolling(period).apply(
      lambda x: np.dot(x, weights) / weights.sum(), raw=True
  )


def hesapla_hma(df, period=20):
  half_period = int(period / 2)
  sqrt_period = int(math.sqrt(period))
  wma_half = weighted_moving_average(df["Close"], half_period)
  wma_full = weighted_moving_average(df["Close"], period)
  raw_hma = 2 * wma_half - wma_full
  return weighted_moving_average(raw_hma, sqrt_period)


def hesapla_mfi(df, period=14):
  tp = (df["High"] + df["Low"] + df["Close"]) / 3
  rmf = tp * df["Volume"]
  tp_diff = tp.diff()
  pos_flow = np.where(tp_diff > 0, rmf, 0.0)
  neg_flow = np.where(tp_diff < 0, rmf, 0.0)
  pos_flow_s = pd.Series(pos_flow, index=df.index)
  neg_flow_s = pd.Series(neg_flow, index=df.index)
  pos_sma = pos_flow_s.ewm(alpha=1 / period, adjust=False).mean()
  neg_sma = neg_flow_s.ewm(alpha=1 / period, adjust=False).mean()
  money_ratio = pos_sma / neg_sma
  return 100 - (100 / (1 + money_ratio))


def hesapla_rsi(df, period=14):
  delta = df["Close"].diff()
  gain = np.where(delta > 0, delta, 0.0)
  loss = np.where(delta < 0, -delta, 0.0)
  gain_s = pd.Series(gain, index=df.index)
  loss_s = pd.Series(loss, index=df.index)
  avg_gain = gain_s.ewm(alpha=1 / period, adjust=False).mean()
  avg_loss = loss_s.ewm(alpha=1 / period, adjust=False).mean()
  rs = avg_gain / avg_loss
  return 100 - (100 / (1 + rs))


def hesapla_cmf(df, period=20):
  high, low, close, volume = df["High"], df["Low"], df["Close"], df["Volume"]
  mf_multiplier = ((close - low) - (high - close)) / (high - low)
  mf_multiplier = mf_multiplier.fillna(0)
  mf_volume = mf_multiplier * volume
  return mf_volume.rolling(window=period).sum() / volume.rolling(
      window=period
  ).sum()


def hesapla_dmi(df, period=14):
  high, low, close = df["High"], df["Low"], df["Close"]
  high_low = high - low
  high_close = np.abs(high - close.shift(1))
  low_close = np.abs(low - close.shift(1))
  tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)

  plus_dm = high.diff()
  minus_dm = low.shift(1) - low
  plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0.0)
  minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0.0)

  plus_dm_s = pd.Series(plus_dm, index=df.index)
  plus_smoothed = plus_dm_s.ewm(alpha=1 / period, adjust=False).mean()
  tr_smoothed = tr.ewm(alpha=1 / period, adjust=False).mean()

  plus_di = 100 * (plus_smoothed / tr_smoothed)
  return plus_di


# --- NTFY BİLDİRİM GÖNDERME ---
def ntfy_mesaj_gonder(baslik, mesaj):
  try:
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    headers = {
        "Title": baslik.encode("utf-8"),
        "Priority": "default",
        "Tags": "chart_with_upwards_trend,rotating_light",
    }
    response = requests.post(
        url, data=mesaj.encode("utf-8"), headers=headers, timeout=15
    )
    if response.status_code == 200:
      print("[NTFY BİLDİRİMİ GÖNDERİLDİ]")
      time.sleep(2)
    else:
      print(f"[NTFY HATA]: Kod {response.status_code}")
  except Exception as e:
    print(f"[NTFY BAĞLANTI HATASI]: {e}")


# --- ANA TARAMA FONKSİYONU ---
def super_15dk_taramasi():
  print("🚀 Arka plan taraması başlatıldı...")

  hafiza = hafiza_yukle()
  simdi_epoch = time.time()
  print(
      f"[{datetime.now(TZ_TR).strftime('%Y-%m-%d %H:%M:%S')}] Süper 15 dk"
      f" Taraması İşleniyor ({len(BIST_HISSELERI)} Hisse)..."
  )

  for hisse in BIST_HISSELERI:
    try:
      df = yf.download(hisse, period="30d", interval="15m", progress=False)
      if df is None or df.empty or len(df) < 30:
        continue

      if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

      # İndikatör Hesaplamaları
      hma20 = hesapla_hma(df, period=20)
      mfi = hesapla_mfi(df, period=14)
      rsi = hesapla_rsi(df, period=14)
      cmf = hesapla_cmf(df, period=20)
      plus_di = hesapla_dmi(df, period=14)

      c_close = df["Close"].iloc[-1]
      c_hma20 = hma20.iloc[-1]
      c_mfi = mfi.iloc[-1]
      c_rsi = rsi.iloc[-1]
      c_cmf = cmf.iloc[-1]
      c_plus_di = plus_di.iloc[-1]

      # Filtre Koşulları
      kosul_hma = c_close > c_hma20
      kosul_mfi = c_mfi > 70
      kosul_rsi = c_rsi > 50
      kosul_cmf = c_cmf > 0
      kosul_pdi = c_plus_di > 30

      if kosul_hma and kosul_mfi and kosul_rsi and kosul_cmf and kosul_pdi:
        son_gonderim = hafiza.get(hisse, 0)
        if simdi_epoch - son_gonderim > COOLDOWN_SECONDS:
          zaman_str = datetime.now(TZ_TR).strftime("%H:%M")
          temiz_isim = hisse.replace(".IS", "")

          baslik = f"🚀 Süper 15dk Sinyali: {temiz_isim}"
          mesaj = (
              f"Saat: {zaman_str}\nFiyat: {c_close:.2f}\nMFI: {c_mfi:.1f} | RSI:"
              f" {c_rsi:.1f}\nCMF: {c_cmf:.2f} | +DI: {c_plus_di:.1f}"
          )

          ntfy_mesaj_gonder(baslik, mesaj)
          hafiza[hisse] = simdi_epoch
          hafiza_kaydet(hafiza)

      time.sleep(0.2)

    except Exception as e:
      continue

  print("Tarama turu başarıyla tamamlandı.")


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
