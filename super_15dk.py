from datetime import datetime
import json
import math
import os
import time
import numpy as np
import pandas as pd
import pytz
import requests
import urllib.parse
import yfinance as yf

# --- AYARLAR VE SABİTLER ---
MEMORY_FILE = "hafiza_15dk.json"
COOLDOWN_SECONDS = (
    3600  # Aynı hisse için 1 saat (3600 saniye) boyunca tekrar mesaj engeli
)
TZ_TR = pytz.timezone("Europe/Istanbul")

# WhatsApp (CallMeBot) Gerçek Bilgilerin
WHATSAPP_PHONE = "905462848792"
WHATSAPP_APIKEY = "3477940"

# --- TÜM BİST HİSSELERİNİN KAPSAMLI LİSTESİ ---
BIST_HISSELERI = [
    "ACSEL.IS",
    "ADEL.IS",
    "ADESE.IS",
    "ADGYO.IS",
    "AEFES.IS",
    "AFYON.IS",
    "AGESA.IS",
    "AGHOL.IS",
    "AGROT.IS",
    "AHGAZ.IS",
    "AKBNK.IS",
    "AKCNS.IS",
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
    "ALMAD.IS",
    "ALTNY.IS",
    "ANELE.IS",
    "ANGEN.IS",
    "ANHYT.IS",
    "ANSGR.IS",
    "ARASE.IS",
    "ARCLK.IS",
    "ARDYZ.IS",
    "ARENA.IS",
    "ARSAN.IS",
    "ARZUM.IS",
    "ASELS.IS",
    "ASTOR.IS",
    "ATAGY.IS",
    "ATAKP.IS",
    "ATEKS.IS",
    "AVOD.IS",
    "AVPGY.IS",
    "AYDEM.IS",
    "AYEN.IS",
    "AYES.IS",
    "AYGAZ.IS",
    "AZTEK.IS",
    "BAGFS.IS",
    "BAKAB.IS",
    "BALAT.IS",
    "BANVT.IS",
    "BASCM.IS",
    "BASGZ.IS",
    "BERAS.IS",
    "BFREN.IS",
    "BIENY.IS",
    "BIGCH.IS",
    "BIMAS.IS",
    "BINHO.IS",
    "BIOEN.IS",
    "BOBET.IS",
    "BOSSA.IS",
    "BRISA.IS",
    "BRKVY.IS",
    "BRSAN.IS",
    "BUCIM.IS",
    "BURCE.IS",
    "BURVA.IS",
    "BVSAN.IS",
    "CANTE.IS",
    "CATES.IS",
    "CCOLA.IS",
    "CELHA.IS",
    "CEMAS.IS",
    "CEMTS.IS",
    "CEOEM.IS",
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
    "DERIM.IS",
    "DESA.IS",
    "DESPC.IS",
    "DEVA.IS",
    "DIRIT.IS",
    "DMSAS.IS",
    "DNISI.IS",
    "DOAS.IS",
    "DOBUR.IS",
    "DOCO.IS",
    "DOGUE.IS",
    "DOHOL.IS",
    "EBEBK.IS",
    "ECILC.IS",
    "ECZYT.IS",
    "EDIP.IS",
    "EGEEN.IS",
    "EGEPO.IS",
    "EGGUB.IS",
    "EGPRO.IS",
    "EKGYO.IS",
    "EKOS.IS",
    "EKSUN.IS",
    "ELITE.IS",
    "EMKEL.IS",
    "ENERY.IS",
    "ENJSA.IS",
    "ENKAI.IS",
    "EPLAS.IS",
    "ERCB.IS",
    "EREGL.IS",
    "ERSU.IS",
    "ESCAR.IS",
    "ESCOM.IS",
    "ESEN.IS",
    "EUPWR.IS",
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
    "GENIL.IS",
    "GEREL.IS",
    "GESAN.IS",
    "GLBMD.IS",
    "GLRYH.IS",
    "GMSTR.IS",
    "GOKNR.IS",
    "GOLTS.IS",
    "GOODY.IS",
    "GOZDE.IS",
    "GRNYO.IS",
    "GRSEL.IS",
    "GSDDE.IS",
    "GSDHO.IS",
    "GSRAY.IS",
    "GUBRF.IS",
    "GWIND.IS",
    "GZNMI.IS",
    "HALKB.IS",
    "HATEK.IS",
    "HATSN.IS",
    "HDFGS.IS",
    "HEKTS.IS",
    "HKTM.IS",
    "HLGYO.IS",
    "HTTBT.IS",
    "HUBVC.IS",
    "HUNER.IS",
    "HURGZ.IS",
    "ICBCT.IS",
    "IDEAS.IS",
    "IDGYO.IS",
    "IHEVA.IS",
    "IHGZT.IS",
    "IHLAS.IS",
    "IHLGM.IS",
    "IHYVA.IS",
    "IMASM.IS",
    "INDES.IS",
    "INFO.IS",
    "INGRM.IS",
    "INTEM.IS",
    "INVEO.IS",
    "IPEKE.IS",
    "ISATR.IS",
    "ISBIR.IS",
    "ISBTR.IS",
    "ISCEN.IS",
    "ISCTR.IS",
    "ISDMR.IS",
    "ISFIN.IS",
    "ISGSY.IS",
    "ISGYO.IS",
    "ISKPL.IS",
    "ISKUR.IS",
    "ISMEN.IS",
    "ITTFH.IS",
    "IZFAS.IS",
    "IZINV.IS",
    "IZMDC.IS",
    "JANTS.IS",
    "KAPLM.IS",
    "KAREL.IS",
    "KARSN.IS",
    "KARTN.IS",
    "KAYSE.IS",
    "KCAER.IS",
    "KCHOL.IS",
    "KENT.IS",
    "KERVT.IS",
    "KFEIN.IS",
    "KGYO.IS",
    "KIMMR.IS",
    "KLGYO.IS",
    "KLKIM.IS",
    "KLMSN.IS",
    "KLSYN.IS",
    "KMPUR.IS",
    "KNFRT.IS",
    "KONTR.IS",
    "KONYA.IS",
    "KOPOL.IS",
    "KORDS.IS",
    "KOZAA.IS",
    "KOZAL.IS",
    "KRDMD.IS",
    "KRGYO.IS",
    "KRONT.IS",
    "KRSTL.IS",
    "KRTEK.IS",
    "KZBGY.IS",
    "LIDER.IS",
    "LKMNH.IS",
    "LOGO.IS",
    "LUKSK.IS",
    "MAALT.IS",
    "MAVI.IS",
    "MEDTR.IS",
    "MEGAP.IS",
    "MEKAG.IS",
    "MEPET.IS",
    "MERCN.IS",
    "MERIT.IS",
    "MERKO.IS",
    "MGROS.IS",
    "MIATK.IS",
    "MMCAS.IS",
    "MNDRS.IS",
    "MNDTR.IS",
    "MOBTL.IS",
    "MPARK.IS",
    "MRSHL.IS",
    "MSGYO.IS",
    "MTRKS.IS",
    "MTRYO.IS",
    "MZHLD.IS",
    "NATEN.IS",
    "NETAS.IS",
    "NIBAS.IS",
    "NTHOL.IS",
    "NTGAZ.IS",
    "NUGYO.IS",
    "NUHCM.IS",
    "ODAS.IS",
    "OFSYM.IS",
    "ONCSM.IS",
    "ORMA.IS",
    "OTKAR.IS",
    "OYAKC.IS",
    "OYLUM.IS",
    "OYYAT.IS",
    "OZAKD.IS",
    "OZGYO.IS",
    "OZRDN.IS",
    "PAKDM.IS",
    "PAMEL.IS",
    "PAPIL.IS",
    "PARSN.IS",
    "PENDK.IS",
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
    "PSGYO.IS",
    "QUAGR.IS",
    "RALYH.IS",
    "RAYSG.IS",
    "REEDR.IS",
    "RNPOL.IS",
    "RODRG.IS",
    "ROYAL.IS",
    "RTALB.IS",
    "RUBNS.IS",
    "SAFKR.IS",
    "SAHOL.IS",
    "SAMAT.IS",
    "SANEL.IS",
    "SANFM.IS",
    "SANKO.IS",
    "SARKY.IS",
    "SASA.IS",
    "SAYAS.IS",
    "SDTTR.IS",
    "SEGMN.IS",
    "SEGYO.IS",
    "SEKFK.IS",
    "SEKUR.IS",
    "SELEC.IS",
    "SELGD.IS",
    "SELVA.IS",
    "SEYKM.IS",
    "SILVR.IS",
    "SISE.IS",
    "SKBNK.IS",
    "SKTAS.IS",
    "SMART.IS",
    "SMRTG.IS",
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
    "TDGYO.IS",
    "TEKTU.IS",
    "TEHOL.IS",
    "TGSAS.IS",
    "THYAO.IS",
    "TKFEN.IS",
    "TKNSA.IS",
    "TMPOL.IS",
    "TMSN.IS",
    "TOASO.IS",
    "TRGYO.IS",
    "TRILC.IS",
    "TSKB.IS",
    "TSPOR.IS",
    "TTKOM.IS",
    "TTRAK.IS",
    "TUKAS.IS",
    "TUPRS.IS",
    "TUREX.IS",
    "TURSG.IS",
    "UFUK.IS",
    "ULAS.IS",
    "ULKER.IS",
    "UNLU.IS",
    "USAK.IS",
    "VAKBN.IS",
    "VAKFN.IS",
    "VAKKO.IS",
    "VANGD.IS",
    "VERTU.IS",
    "VERUS.IS",
    "VESBE.IS",
    "VESTL.IS",
    "VKGYO.IS",
    "VKING.IS",
    "APEK.IS",
    "YAPRK.IS",
    "YATAS.IS",
    "YAYLA.IS",
    "YEOTK.IS",
    "YESIL.IS",
    "YGGYO.IS",
    "YGYO.IS",
    "YKBNK.IS",
    "YKSLN.IS",
    "YUNSA.IS",
    "YYAPI.IS",
    "YYLGD.IS",
    "ZEDUR.IS",
    "ZOREN.IS",
    "ZRGYO.IS",
]


# --- HAFIZA VE SEANS KONTROLü ---
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
  if simdi.weekday() >= 5:  # Hafta sonu
    return False
  baslangic = simdi.replace(hour=9, minute=30, second=0, microsecond=0)
  bitis = simdi.replace(hour=18, minute=10, second=0, microsecond=0)
  return baslangic <= simdi <= bitis


# --- TRADINGVIEW UYUMLU ÖZEL İNDİKATÖR FONKSİYONLARI ---
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


# --- WHATSAPP MESAJ GÖNDERME ---
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


# --- ANA TARAMA FONKSİYONU ---
def super_15dk_taramasi():
  # Manuel tetikleme (workflow_dispatch) durumunda seans saatine takılma!
  github_event = os.environ.get("GITHUB_EVENT_NAME", "")

  if github_event != "workflow_dispatch" and not piyasa_zaman_kontrolu():
    print(
        "Borsa seans saatleri dışındayız veya hafta sonu (Otomatik Çalışma)."
        " Tarama atlanıyor."
    )
    return

  if github_event == "workflow_dispatch":
    print(
        "🚀 Manuel tetikleme algılandı: Seans saati kontrolü es geçilerek tarama"
        " başlatılıyor!"
    )

  hafiza = hafiza_yukle()
  simdi_epoch = time.time()
  print(
      f"[{datetime.now(TZ_TR).strftime('%Y-%m-%d %H:%M:%S')}] Süper 15 dk"
      f" Taraması Başlatıldı ({len(BIST_HISSELERI)} Hisse)..."
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

      # Filtre Koşulları: Fiyat > HMA20, MFI > 70, RSI > 50, CMF > 0, +DI > 30
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
          mesaj = (
              f"🚀 *Süper 15 dk Sinyali* ({zaman_str})\n• *{temiz_isim}* | Fiyat:"
              f" {c_close:.2f} | MFI: {c_mfi:.1f} | RSI: {c_rsi:.1f} | CMF:"
              f" {c_cmf:.2f} | +DI: {c_plus_di:.1f}"
          )

          whatsapp_mesaj_gonder(mesaj)

          hafiza[hisse] = simdi_epoch
          hafiza_kaydet(hafiza)
        else:
          print(f"{hisse} için 1 saatlik cooldown aktif, mesaj atılmadı.")

      time.sleep(0.2)

    except Exception as e:
      continue

  print("Tarama turu tamamlandı.")


if __name__ == "__main__":
  super_15dk_taramasi()
