from datetime import datetime
import json
import os
import time
from threading import Thread
from flask import Flask
import numpy as np
import pandas as pd
import pytz
import requests
import yfinance as yf

app = Flask(__name__)

# --- AYARLAR VE SABİTLER ---
MEMORY_FILE = "hafiza_wave_mfi.json"
COOLDOWN_SECONDS = 1800  # Aynı hisse için 30 dakika bekleme süresi
TZ_TR = pytz.timezone("Europe/Istanbul")
NTFY_URL = "https://ntfy.sh/borsa_senet"

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


def send_ntfy(message):
  try:
    headers = {
        "Title": "15m Hibrit Erken Patlama Sinyali",
        "Priority": "high",
    }
    requests.post(
        NTFY_URL, data=message.encode("utf-8"), headers=headers, timeout=10
    )
  except Exception as e:
    print(f"Bildirim Hatası: {e}")


def calculate_supertrend(df, period=10, multiplier=3):
  hl2 = (df["High"] + df["Low"]) / 2
  tr1 = df["High"] - df["Low"]
  tr2 = (df["High"] - df["Close"].shift(1)).abs()
  tr3 = (df["Low"] - df["Close"].shift(1)).abs()
  tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
  atr = tr.rolling(window=period).mean()

  upper_basic = hl2 + (multiplier * atr)
  lower_basic = hl2 - (multiplier * atr)

  upper_band = upper_basic.copy()
  lower_band = lower_basic.copy()

  direction = pd.Series(1, index=df.index)
  st = pd.Series(index=df.index, dtype="float64")

  for i in range(1, len(df)):
    curr_close = df["Close"].iloc[i]
    if curr_close > upper_band.iloc[i]:
      direction.iloc[i] = 1
    elif curr_close < lower_band.iloc[i]:
      direction.iloc[i] = -1
    else:
      direction.iloc[i] = direction.iloc[i - 1]
      if (
          direction.iloc[i] == 1
          and lower_band.iloc[i] < lower_band.iloc[i - 1]
      ):
        lower_band.iloc[i] = lower_band.iloc[i - 1]
      if (
          direction.iloc[i] == -1
          and upper_band.iloc[i] > upper_band.iloc[i - 1]
      ):
        upper_band.iloc[i] = upper_band.iloc[i - 1]

    st.iloc[i] = (
        lower_band.iloc[i] if direction.iloc[i] == 1 else upper_band.iloc[i]
    )

  return st


def hesapla_fibonacci(df, window=100):
  # Son 'window' mum içindeki en yüksek ve en düşük seviyeyi bul
  recent_df = df.tail(window)
  max_high = recent_df["High"].max()
  min_low = recent_df["Low"].min()
  diff = max_high - min_low

  curr_price = df["Close"].iloc[-1]

  # Standart Fibonacci Seviyeleri
  fib_ratios = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
  # Düşüş veya yükseliş yönüne göre seviye listesi
  levels = [min_low + (diff * r) for r in fib_ratios]
  levels.sort()

  # Fiyatın hemen altındaki ilk destek ve hemen üstündeki ilk direnç
  destekler = [lvl for lvl in levels if lvl < curr_price]
  direncler = [lvl for lvl in levels if lvl > curr_price]

  ilk_destek = destekler[-1] if destekler else min_low
  ilk_direnc = direncler[0] if direncler else max_high

  return ilk_destek, ilk_direnc


def run_scanner():
  if not piyasa_zaman_kontrolu():
    return
  hafiza = hafiza_yukle()
  simdi_epoch = time.time()

  for ticker in STOCKS:
    clean_ticker = ticker.strip()
    try:
      df = yf.download(
          clean_ticker, period="60d", interval="15m", progress=False
      )
      if df.empty or len(df) < 50:
        continue
      if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

      high, low, close, volume = (
          df["High"],
          df["Low"],
          df["Close"],
          df["Volume"],
      )

      # 1. Supertrend Hesaplama ve Yüzdesel Kırılım Kontrolü (* 1.002)
      st = calculate_supertrend(df)
      st_breakout = close.iloc[-1] > (st.iloc[-1] * 1.002)

      # 2. Hacim Kriterleri (Hacim Artışı + Göreceli Hacim RVOL > 0.6)
      vol_ma20 = volume.rolling(window=20).mean()
      rvol = volume.iloc[-1] / (vol_ma20.iloc[-1] + 1e-10)
      volume_growth = volume.iloc[-1] > volume.iloc[-2]
      rvol_check = rvol > 0.6

      # 3. Bollinger Üst Bant Kontrolü (Üst bant kırılımı veya üstünde seyretme)
      sma20 = close.rolling(window=20).mean()
      std20 = close.rolling(window=20).std()
      upper_band = sma20 + (std20 * 2)
      bollinger_check = close.iloc[-1] >= upper_band.iloc[-1]

      # 4. MFI (14 Periyot) > 29
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
      mfi_curr = mfi.iloc[-1]
      mfi_check = mfi_curr > 29

      # 5. +DI (14 Periyot) > 20 (Erken uyanış için esnetildi)
      up_move = high.diff()
      down_move = -low.diff()
      plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
      tr1 = high - low
      tr2 = (high - close.shift(1)).abs()
      tr3 = (low - close.shift(1)).abs()
      tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
      atr = tr.rolling(14).mean()
      plus_di = (
          pd.Series(plus_dm, index=df.index).rolling(14).mean()
          / (atr + 1e-10)
      ) * 100
      plus_di_curr = plus_di.iloc[-1]
      di_check = plus_di_curr > 20

      # 6. RSI (14 Periyot) > 50
      delta = close.diff()
      gain = delta.where(delta > 0, 0).rolling(14).mean()
      loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
      rs = gain / (loss + 1e-10)
      rsi = 100 - (100 / (1 + rs))
      rsi_curr = rsi.iloc[-1]
      rsi_check = rsi_curr > 50

      # Tüm Şartların Birleşimi (Hibrit Erken Patlama + Bollinger Üst Bant)
      if (
          st_breakout
          and volume_growth
          and rvol_check
          and bollinger_check
          and mfi_check
          and di_check
          and rsi_check
      ):
        if simdi_epoch - hafiza.get(clean_ticker, 0) > COOLDOWN_SECONDS:
          temiz_isim = clean_ticker.replace(".IS", "")
          ilk_destek, ilk_direnc = hesapla_fibonacci(df)

          mesaj = (
              f"🚀 *15m Hibrit Erken Patlama Sinyali*\n• Hisse:"
              f" *{temiz_isim}* | Fiyat: {close.iloc[-1]:.2f}\n• 🟢 İlk Destek"
              f" (Fib): {ilk_destek:.2f}\n• 🔴 İlk Direnç (Fib):"
              f" {ilk_direnc:.2f}\n• MFI: {mfi_curr:.1f} | +DI:"
              f" {plus_di_curr:.1f} | RSI: {rsi_curr:.1f} | RVOL: {rvol:.2f}"
          )
          send_ntfy(mesaj)
          hafiza[clean_ticker] = simdi_epoch
          hafiza_kaydet(hafiza)
    except Exception as e:
      continue


@app.route("/")
def home():
  return "15m Hibrit Erken Patlama Tarama Sunucusu Aktif!"


@app.route("/tara")
def manual_scan():
  Thread(target=run_scanner).start()
  return "15m Hibrit Erken Patlama tarama arka planda tetiklendi!"


if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
