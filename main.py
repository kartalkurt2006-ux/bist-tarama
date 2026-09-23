from datetime import datetime
import json
import os
import time
import urllib.parse
import urllib.request
import numpy as np
import pandas as pd
import pytz
import requests
import yfinance as yf

# --- AYARLAR VE SABİTLER ---
COOLDOWN_SECONDS = 3600  # Aynı hisse ve aynı periyot için 1 saat bekleme süresi
TZ_TR = pytz.timezone("Europe/Istanbul")

# Ntfy Kanal Ayarı
NTFY_URL = "https://ntfy.sh/borsa_senet"

# Taranacak Periyotlar, Kuralları ve Hafıza Dosyaları (1h odaklı güncellendi)
TIMEFRAMES = [
    {
        "period": "1h",
        "label": "1 Saatlik (Dalga + İndikatör)",
        "memory": "hafiza_1h.json",
        "kural_tipi": "1h_dalga_gorsel",
    },
    {
        "period": "4h",
        "label": "4 Saatlik",
        "memory": "hafiza_4h.json",
        "kural_tipi": "4h",
    },
]

# BIST Tüm Hisseler (Yan Yana Dizilmiş Kompakt Liste)
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


def calculate_hma(series, period=20):
  half_per = period // 2
  sqrt_per = int(np.sqrt(period))

  def wma(s, p):
    weights = np.arange(1, p + 1)
    return s.rolling(p).apply(
        lambda x: np.dot(x, weights) / weights.sum(), raw=True
    )

  wma_half = wma(series, half_per)
  wma_full = wma(series, period)
  raw_hma = 2 * wma_half - wma_full
  hma = wma(raw_hma, sqrt_per)
  return hma


def check_wave_margins(df):
  """İçsel Dalga Değerleri (4, 8, 5, 8, 9) ve Marj Kırılım Kontrolü.

  Fiyatın son dalga boyu içerisindeki sıkışma ve üst marj direnç kırılımını
  test eder.
  """
  try:
    close = df["Close"].values
    high = df["High"].values
    low = df["Low"].values

    if len(close) < 35:
      return False

    # İçsel dalga döngü uzunluğu (4+8+5+8+9 = 34 periyotluk referans pencere)
    wave_sequence = [4, 8, 5, 8, 9]
    total_cycle = sum(wave_sequence)  # 34

    # Son dönemsel dalga marjı (En yüksek ve en düşük bandın tespiti)
    recent_high = np.max(high[-total_cycle:])
    recent_low = np.min(low[-total_cycle:])
    margin_range = recent_high - recent_low

    if margin_range == 0:
      return False

    # Fiyatın dalga içerisindeki konumunu ve üst marja yönelişini / kırılımını kontrol et
    current_price = close[-1]
    prev_price = close[-2]

    # Marjın üst %20'lik direncine yaklaşma veya yukarı yönlü marj delme (Breakout)
    upper_margin_threshold = recent_low + (margin_range * 0.80)

    # Dalga döngüsü içinde sıkışıp yukarı yönlü marj kıran hareket
    is_wave_breakout = (prev_price <= upper_margin_threshold) and (
        current_price > upper_margin_threshold
    )
    return is_wave_breakout
  except Exception:
    return False


def check_supertrend(df, period=10, multiplier=3):
  hl2 = (df["High"] + df["Low"]) / 2
  tr = pd.concat(
      [
          df["High"] - df["Low"],
          (df["High"] - df["Close"].shift()).abs(),
          (df["Low"] - df["Close"].shift()).abs(),
      ],
      axis=1,
  ).max(axis=1)
  atr = tr.rolling(period).mean()

  upper_band = hl2 + (multiplier * atr)
  lower_band = hl2 - (multiplier * atr)

  close = df["Close"].values
  ub = upper_band.values
  lb = lower_band.values

  uptrend = True
  for i in range(period, len(df)):
    if np.isnan(atr.iloc[i]):
      continue
    if close[i] > ub[i]:
      uptrend = True
    elif close[i] < lb[i]:
      uptrend = False
  return uptrend


def hafiza_yukle(dosya_adi):
  if os.path.exists(dosya_adi):
    try:
      with open(dosya_adi, "r") as f:
        return json.load(f)
    except:
      return {}
  return {}


def hafiza_kaydet(dosya_adi, hafiza):
  with open(dosya_adi, "w") as f:
    json.dump(hafiza, f)


def piyasa_zaman_kontrolu():
  simdi = datetime.now(TZ_TR)
  if simdi.weekday() >= 5:  # Hafta sonu
    return False

  baslangic = simdi.replace(hour=9, minute=30, second=0, microsecond=0)
  bitis = simdi.replace(hour=18, minute=10, second=0, microsecond=0)

  if baslangic <= simdi <= bitis:
    return True
  return False


def send_ntfy(message, baslik):
  try:
    headers = {"Title": baslik, "Priority": "high"}
    res = requests.post(
        NTFY_URL, data=message.encode("utf-8"), headers=headers, timeout=10
    )
    print(f"Ntfy Yanıtı ({baslik}): {res.status_code}")
  except Exception as e:
    print(f"Ntfy Mesaj Hatası: {e}")


def run_scanner():
  if not piyasa_zaman_kontrolu():
    print("Borsa seans saatleri dışındayız veya hafta sonu. Tarama atlanıyor.")
    return

  simdi_epoch = time.time()
  print(
      f"[{datetime.now(TZ_TR).strftime('%Y-%m-%d %H:%M:%S')}] 1h (Dalga Entegre)"
      f" ve 4h Periyot Taraması Başlatıldı..."
  )

  for tf in TIMEFRAMES:
    period = tf["period"]
    label = tf["label"]
    mem_file = tf["memory"]
    kural_tipi = tf["kural_tipi"]

    hafiza = hafiza_yukle(mem_file)
    print(
        f"--> {label} ({period}) taraması yapılıyor... Toplam Hisse:"
        f" {len(STOCKS)}"
    )

    for ticker in STOCKS:
      clean_ticker = ticker.strip()
      try:
        df = yf.download(
            clean_ticker, period="1mo", interval=period, progress=False
        )
        if df.empty or len(df) < 40:
          continue

        if isinstance(df.columns, pd.MultiIndex):
          df.columns = df.columns.get_level_values(0)

        close = df["Close"]
        high = df["High"]
        low = df["Low"]
        volume = df["Volume"]

        # Ortak İndikatör Hesaplamaları
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
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
        mfi = 100 - (
            100 / (1 + (positive_flow / (negative_flow + 1e-10)))
        )

        mf_multiplier = ((close - low) - (high - close)) / (
            (high - low) + 1e-10
        )
        mf_volume = mf_multiplier * volume
        cmf = mf_volume.rolling(20).sum() / (volume.rolling(20).sum() + 1e-10)

        up_move = high.diff()
        down_move = -low.diff()
        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)

        tr = pd.concat(
            [
                high - low,
                (high - close.shift(1)).abs(),
                (low - close.shift(1)).abs(),
            ],
            axis=1,
        ).max(axis=1)

        tr_smooth = tr.rolling(14).sum()
        plus_di = 100 * (plus_dm.rolling(14).sum() / (tr_smooth + 1e-10))
        minus_di = 100 * (minus_dm.rolling(14).sum() / (tr_smooth + 1e-10))

        mfi_curr = mfi.iloc[-1]
        rsi_curr = rsi.iloc[-1]
        plus_di_curr = plus_di.iloc[-1]
        minus_di_curr = minus_di.iloc[-1]
        cmf_curr = cmf.iloc[-1]
        close_curr = close.iloc[-1]

        sinyal_var = False

        if kural_tipi == "1h_dalga_gorsel":
          # 1 Saatlik Gelişmiş Kurallar: HMA20, MFI > 55, +DI > 24, DMI Kesişimi, CMF > 0 VE Dalga Marjı Kırılımı (4,8,5,8,9)
          hma20 = calculate_hma(close, 20)
          hma20_curr = hma20.iloc[-1]

          plus_di_prev = plus_di.iloc[-2]
          minus_di_prev = minus_di.iloc[-2]
          di_crossover = (plus_di_prev <= minus_di_prev) and (
              plus_di_curr > minus_di_curr
          )

          # Dalga marjı ve içsel değerlerin doğrulanması
          wave_breakout = check_wave_margins(df)

          if (
              (close_curr > hma20_curr)
              and (mfi_curr > 55)
              and (plus_di_curr > 24)
              and di_crossover
              and (cmf_curr > 0)
              and wave_breakout
          ):
            sinyal_var = True

        elif kural_tipi == "4h":
          # 4 Saatlik Kurallar (Ağır Top)
          hma20 = calculate_hma(close, 20)
          hma20_curr = hma20.iloc[-1]

          supertrend_green = check_supertrend(df)

          mfi_prev = mfi.iloc[-2]
          fibo_mfi_crossover = (mfi_prev < 50) and (mfi_curr >= 50)

          plus_di_prev = plus_di.iloc[-2]
          minus_di_prev = minus_di.iloc[-2]
          di_crossover_4h = (plus_di_prev <= minus_di_prev) and (
              plus_di_curr > minus_di_curr
          )

          if (
              supertrend_green
              and (close_curr > hma20_curr)
              and fibo_mfi_crossover
              and (plus_di_curr > 30)
              and di_crossover_4h
          ):
            sinyal_var = True

        if sinyal_var:
          son_gonderim = hafiza.get(clean_ticker, 0)
          if simdi_epoch - son_gonderim > COOLDOWN_SECONDS:
            temiz_isim = clean_ticker.replace(".IS", "")
            zaman_str = datetime.now(TZ_TR).strftime("%H:%M")

            baslik = f"BIST {label} Sinyal"
            mesaj = (
                f"🚀 *BIST {label} Sinyal* ({zaman_str})\n• Hisse:"
                f" *{temiz_isim}* | Fiyat: {close_curr:.2f} | MFI:"
                f" {mfi_curr:.1f} | +DI: {plus_di_curr:.1f} | Dalga Kırılımı: Aktif"
            )

            send_ntfy(mesaj, baslik)

            hafiza[clean_ticker] = simdi_epoch
            hafiza_kaydet(mem_file, hafiza)

      except Exception as e:
        continue

  print("Tüm Periyotların Tarama Turu Tamamlandı.")


if __name__ == "__main__":
  run_scanner()
