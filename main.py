from datetime import datetime
import json
import os
import time
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

# Tek Merkezi Hafıza Dosyası
MERKEZI_HAFIZA_DOSYASI = "borsa_hafiza.json"

# BIST Tüm Hisseler
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
    "CVKMD.IS", "CWENE.IS", "DAGI.IS", "DAPGM.IS", "DARDL.IS", "DENGE.IS", "DERHL.IS", "DERIM.IS", "DESA.IS", "DESPC.IS",
    "DEVA.IS", "DIRIT.IS", "DITAS.IS", "DMRGD.IS", "DMSAS.IS", "DNISI.IS", "DOAS.IS", "DOBUR.IS", "DOCO.IS", "DOGUB.IS",
    "DOHOL.IS", "DSTAN.IS", "DUNYA.IS", "DURDO.IS", "DYOBY.IS", "DZGYO.IS", "EBEBK.IS", "ECILC.IS", "ECZYT.IS", "EDIP.IS",
    "EGEEN.IS", "EGEPO.IS", "EGGUB.IS", "EGPRO.IS", "EGSER.IS", "EKGYO.IS", "EKOS.IS", "EKSUN.IS", "ELITE.IS", "EMKEL.IS",
    "ENERY.IS", "ENKAI.IS", "ENJSA.IS", "EPLAS.IS", "ERBOS.IS", "EREGL.IS", "ERSU.IS", "ESCAR.IS", "ESCOM.IS", "ESEN.IS",
    "ETILR.IS", "EUHOL.IS", "EUKYO.IS", "EUPWR.IS", "EUREN.IS", "EUYO.IS", "EYGYO.IS", "FADE.IS", "FENER.IS", "FLAP.IS",
    "FMIZP.IS", "FONET.IS", "FORMT.IS", "FRIGO.IS", "FROTO.IS", "GARAN.IS", "GARFA.IS", "GEDIK.IS", "GEDZA.IS", "GENIL.IS",
    "GENTS.IS", "GEREL.IS", "GESAN.IS", "GLBMD.IS", "GLCVY.IS", "GLRYH.IS", "GLYHO.IS", "GMTAS.IS", "GOKNR.IS", "GOLTS.IS",
    "GOODY.IS", "GOZDE.IS", "GRNYO.IS", "GRSEL.IS", "GTRGY.IS", "GUBRF.IS", "GWIND.IS", "GZNMI.IS", "HALKB.IS", "HATEK.IS",
    "HATSN.IS", "HEDEF.IS", "HEKTS.IS", "HKTM.IS", "HLGYO.IS", "HTTBT.IS", "HUBVC.IS", "HURGZ.IS", "ICBCT.IS", "IDEAS.IS",
    "IDGYO.IS", "IENTS.IS", "IHEVA.IS", "IHGZT.IS", "IHLAS.IS", "IHLGM.IS", "IMASM.IS", "INDES.IS", "INFO.IS", "INGRM.IS",
    "INTEM.IS", "INVEO.IS", "INVES.IS", "IPEKE.IS", "ISATR.IS", "ISBIR.IS", "ISBTR.IS", "ISCEN.IS", "ISCTR.IS", "ISFIN.IS",
    "ISGSY.IS", "ISGYO.IS", "ISKPL.IS", "ISKUR.IS", "ISMEN.IS", "ISSEN.IS", "IZENR.IS", "IZFAS.IS", "IZINV.IS", "JANTS.IS",
    "KAPLM.IS", "KAREL.IS", "KARSN.IS", "KARTN.IS", "KARYE.IS", "KATMR.IS", "KAYSE.IS", "KBORU.IS", "KCAER.IS", "KCHOL.IS",
    "KENT.IS", "KERVT.IS", "KFEIN.IS", "KGYO.IS", "KIMMR.IS", "KLGYO.IS", "KLKIM.IS", "KLRHO.IS", "KLMSN.IS", "KLSER.IS",
    "KLSYN.IS", "KMPUR.IS", "KNFRT.IS", "KONTR.IS", "KONYA.IS", "KOPOL.IS", "KORDS.IS", "KOTON.IS", "KOZAA.IS", "KOZAL.IS",
    "KRDMD.IS", "KRGYO.IS", "KRONT.IS", "KRPLS.IS", "KRSTL.IS", "KRTEK.IS", "KZBGY.IS", "KZYGZ.IS", "LIDER.IS", "LIDFA.IS",
    "LKMNH.IS", "LMKDC.IS", "LOGO.IS", "LUKSK.IS", "MAALT.IS", "MAKIM.IS", "MAKTK.IS", "MANAS.IS", "MARKA.IS", "MARTI.IS",
    "MAVI.IS", "MEDTR.IS", "MEGAP.IS", "MEKAG.IS", "MEPET.IS", "MERCN.IS", "MERKO.IS", "METUR.IS", "MGROS.IS", "MIATK.IS",
    "MMCAS.IS", "MNDRS.IS", "MNDTR.IS", "MOBTL.IS", "MPARK.IS", "MRGYO.IS", "MTRKS.IS", "MTRYO.IS", "MZHLD.IS", "NATEN.IS",
    "NETAS.IS", "NIBAS.IS", "NTHOL.IS", "NUGYO.IS", "NUHCM.IS", "OBAMS.IS", "OBASE.IS", "ODAS.IS", "OFSYM.IS", "ONCSM.IS",
    "ORCAY.IS", "OYYAT.IS", "OZAKD.IS", "OZGYO.IS", "OZKGY.IS", "OZLTM.IS", "OZRDN.IS", "PAKRD.IS", "PAMEL.IS", "PAPIL.IS",
    "PARSN.IS", "PASEU.IS", "PCILT.IS", "PEKGY.IS", "PENGD.IS", "PENTA.IS", "PETKM.IS", "PETUN.IS", "PGSUS.IS", "PINSU.IS",
    "PKART.IS", "PKENT.IS", "PNSUT.IS", "POLHO.IS", "POLTK.IS", "PRDGS.IS", "PRKME.IS", "PRKAB.IS", "PSGYO.IS", "QNBFB.IS",
    "QNBFL.IS", "QUAGR.IS", "RALYH.IS", "REEDR.IS", "RNPOL.IS", "RODRG.IS", "ROYAL.IS", "RTALB.IS", "RUBNS.IS", "RYGYO.IS",
    "RYSAS.IS", "SAFKR.IS", "SAHOL.IS", "SASA.IS", "SAYAS.IS", "SDTTR.IS", "SEGFO.IS", "SEGYO.IS", "SEKFK.IS", "SEKUR.IS",
    "SELEC.IS", "SELVA.IS", "SEYKM.IS", "SILVR.IS", "SISE.IS", "SKBNK.IS", "SKTAS.IS", "SMART.IS", "SMRTG.IS", "SNGYO.IS",
    "SNICA.IS", "SNPAM.IS", "SODSN.IS", "SOKM.IS", "SONME.IS", "SRVGY.IS", "SUMAS.IS", "SUNTK.IS", "SUWEN.IS", "TABGD.IS",
    "TARKM.IS", "TATEN.IS", "TATGD.IS", "TAVHL.IS", "TBORG.IS", "TCELL.IS", "TCKRC.IS", "TDGYO.IS", "TEKTU.IS", "TETMT.IS",
    "TEZOL.IS", "TGSAS.IS", "THYAO.IS", "TKFEN.IS", "TKNSA.IS", "TMPOL.IS", "TMSN.IS", "TOASO.IS", "TRCAS.IS", "TRGYO.IS",
    "TRMET.IS", "TSKB.IS", "TSPOR.IS", "TTKOM.IS", "TTRAK.IS", "TUCLK.IS", "TUPRS.IS", "TURSG.IS", "UFUK.IS", "ULAS.IS",
    "ULUFA.IS", "ULKER.IS", "ULUUN.IS", "VAKBN.IS", "VAKFN.IS", "VAKGY.IS", "VBTYZ.IS", "VERTU.IS", "VERUS.IS", "VESBE.IS",
    "VESTL.IS", "VKFYO.IS", "VKGYO.IS", "VKING.IS", "YAPRK.IS", "YATAS.IS", "YAYLA.IS", "YBTAS.IS", "YEOTK.IS", "YESIL.IS",
    "YGGYO.IS", "YIGIT.IS", "YKBNK.IS", "YKSL.IS", "YUNSA.IS", "YYAPI.IS", "ZEDUR.IS", "ZOREN.IS", "ZRGYO.IS",
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


def calculate_strend(df, period=10, multiplier=3):
  hl2 = (df["High"] + df["Low"]) / 2
  tr = pd.concat([
      df["High"] - df["Low"],
      (df["High"] - df["Close"].shift()).abs(),
      (df["Low"] - df["Close"].shift()).abs()
  ], axis=1).max(axis=1)
  atr = tr.rolling(period).mean()
  lowerband = hl2 - (multiplier * atr)
  return lowerband


def calculate_fisher(df, length=9):
  high = df["High"]
  low = df["Low"]
  close = df["Close"]

  min_low = low.rolling(length).min()
  max_high = high.rolling(length).max()

  price_range = max_high - min_low
  price_range = price_range.replace(0, 1e-10)
  
  price_vals = ((2.0 * (close - min_low) / price_range) - 1.0).values
  val_arr = np.zeros_like(price_vals)
  fish_arr = np.zeros_like(price_vals)
  
  for i in range(len(price_vals)):
    if i == 0:
      val_arr[i] = 0.33 * price_vals[i]
      fish_arr[i] = 0.5 * np.log((1.0 + val_arr[i]) / (1.0 - val_arr[i] + 1e-10))
    else:
      clamped_p = np.clip(price_vals[i], -0.999, 0.999)
      val_arr[i] = 0.33 * clamped_p + 0.67 * val_arr[i-1]
      val_arr[i] = np.clip(val_arr[i], -0.999, 0.999)
      
      fish_val = 0.5 * np.log((1.0 + val_arr[i]) / (1.0 - val_arr[i] + 1e-10))
      fish_arr[i] = 0.5 * fish_val + 0.5 * fish_arr[i-1]

  fish = pd.Series(fish_arr, index=close.index)
  trigger = fish.shift(1).fillna(0)
  return fish, trigger


def check_wave_margins(df, lookback=3):
  try:
    close = df["Close"].values
    high = df["High"].values
    low = df["Low"].values

    if len(close) < 35:
      return False

    wave_sequence = [4, 8, 5, 8, 9]
    total_cycle = sum(wave_sequence)

    recent_high = np.max(high[-total_cycle:])
    recent_low = np.min(low[-total_cycle:])
    margin_range = recent_high - recent_low

    if margin_range == 0:
      return False

    upper_margin_threshold = recent_low + (margin_range * 0.80)

    for i in range(-lookback, 0):
      prev_p = close[i - 1]
      curr_p = close[i]
      if prev_p <= upper_margin_threshold and curr_p > upper_margin_threshold:
        return True

    return False
  except Exception:
    return False


def hesapla_fibonacci_destek_direnc(df, window=100):
  try:
    recent_df = df.tail(window)
    max_high = recent_df["High"].max()
    min_low = recent_df["Low"].min()
    diff = max_high - min_low
    curr_price = df["Close"].iloc[-1]

    fib_ratios = [0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0]
    levels = [min_low + (diff * r) for r in fib_ratios]
    levels.sort()

    destekler = [lvl for lvl in levels if lvl < curr_price]
    direncler = [lvl for lvl in levels if lvl > curr_price]

    ilk_destek = destekler[-1] if destekler else min_low
    ilk_direnc = direncler[0] if direncler else max_high
    return float(ilk_destek), float(ilk_direnc)
  except Exception:
    curr_price = df["Close"].iloc[-1]
    return float(curr_price * 0.95), float(curr_price * 1.05)


def hafiza_yukle():
  if os.path.exists(MERKEZI_HAFIZA_DOSYASI):
    try:
      with open(MERKEZI_HAFIZA_DOSYASI, "r") as f:
        return json.load(f)
    except:
      return {}
  return {}


def hafiza_kaydet(hafiza):
  with open(MERKEZI_HAFIZA_DOSYASI, "w") as f:
    json.dump(hafiza, f, indent=4)


def piyasa_zaman_kontrolu():
  if os.environ.get("FORCE_RUN", "true").lower() == "true":
    return True

  simdi = datetime.now(TZ_TR)
  if simdi.weekday() >= 5:
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
      f"[{datetime.now(TZ_TR).strftime('%Y-%m-%d %H:%M:%S')}] Optimizasyonlu"
      " merkezi tarama başlatılıyor..."
  )

  tum_hafiza = hafiza_yukle()

  # Strateji kural tipleri ve etiketleri
  aktif_stratejiler = [
      {"kural_tipi": "15m_klasik", "label": "bomba 15", "period": "15m"},
      {"kural_tipi": "15m_profesjonel", "label": "15m Profesjonel Momentum (Esnetilmiş 8 Şart)", "period": "15m"},
      {"kural_tipi": "acil_15_dk", "label": "acil 15 dk yetiş (Esnetilmiş Sprint)", "period": "15m"},
      {"kural_tipi": "super_fisher_15", "label": "Süper Fisher 15", "period": "15m"},
      {"kural_tipi": "1h_dalga_gorsel", "label": "1 Saatlik (Dalga Marj + RSI > 50 + +DI > 25 + HMA20)", "period": "1h"},
  ]

  for strat in aktif_stratejiler:
    kural_tipi = strat["kural_tipi"]
    label = strat["label"]
    period = strat["period"]

    if kural_tipi not in tum_hafiza:
      tum_hafiza[kural_tipi] = {}
    kural_hafizasi = tum_hafiza[kural_tipi]

    print(f"\n--> Taranıyor: {label} ({period}) | Toplam Hisse: {len(STOCKS)}")

    for ticker in STOCKS:
      clean_ticker = ticker.strip()
      try:
        df = yf.download(
            clean_ticker, period="1mo", interval=period, progress=False
        )
        time.sleep(0.2)

        if df.empty or len(df) < 40:
          continue

        if isinstance(df.columns, pd.MultiIndex):
          df.columns = df.columns.get_level_values(0)

        close = df["Close"]
        high = df["High"]
        low = df["Low"]
        volume = df["Volume"]

        # --- ORTAK İNDİKATÖRLER ---
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

        # --- BOMBA 15 KURAL SETİ (Orijinal) ---
        if kural_tipi == "15m_klasik":
          bar_sayisi = 6
          recent_df = df.iloc[-(bar_sayisi + 1) : -1]
          ort_high = recent_df["High"].mean()
          ort_low = recent_df["Low"].mean()
          ort_close = recent_df["Close"].mean()

          pivot = (ort_high + ort_low + ort_close) / 3
          birinci_dalga_marji = pivot * 1.0023

          sma20 = close.rolling(20).mean()
          bb_middle = sma20.iloc[-1]

          rvol = volume / volume.rolling(20).mean()
          rvol_curr = rvol.iloc[-1]

          prev_close = close.iloc[-2]
          kapanis_teyit = (prev_close <= birinci_dalga_marji) and (
              close_curr > birinci_dalga_marji
          )

          if (
              kapanis_teyit
              and (close_curr > bb_middle)
              and (mfi_curr > 60)
              and (cmf_curr > -0.20)
              and (rsi_curr > 50)
              and (rvol_curr > 0.6)
          ):
            sinyal_var = True

        # --- 15M PROFESYONEL MOMENTUM KURAL SETİ (Esnetilmiş) ---
        elif kural_tipi == "15m_profesjonel":
          sart_wave = check_wave_margins(df, lookback=5)
          sart_vol_growth = volume.iloc[-1] > volume.iloc[-2]
          
          rvol = volume / volume.rolling(20).mean()
          sart_rvol = rvol.iloc[-1] > 1.0
          
          hma20 = calculate_hma(close, 20)
          sart_hma = close_curr > hma20.iloc[-1]
          
          sma20 = close.rolling(20).mean()
          sart_bb = close_curr >= sma20.iloc[-1]
          
          sart_mfi = mfi_curr > 25
          sart_pid = plus_di_curr > 15
          sart_rsi = rsi_curr > 45

          if (
              sart_wave
              and sart_vol_growth
              and sart_rvol
              and sart_hma
              and sart_bb
              and sart_mfi
              and sart_pid
              and sart_rsi
          ):
            sinyal_var = True

        # --- ACİL 15 DK YETİŞ ---
        elif kural_tipi == "acil_15_dk":
          rvol_curr = volume.iloc[-1] / (volume.rolling(20).mean().iloc[-1] + 1e-10)
          hacim_patlamasi = rvol_curr >= 0.6
          
          hma20 = calculate_hma(close, 20)
          hma20_curr = hma20.iloc[-1]
          
          sart_hma = close_curr > hma20_curr
          sart_mfi = mfi_curr > 60
          sart_rsi = rsi_curr > 45

          if hacim_patlamasi and sart_hma and sart_mfi and sart_rsi:
            sinyal_var = True

        # --- SÜPER FISHER 15 ---
        elif kural_tipi == "super_fisher_15":
          rvol_curr = volume.iloc[-1] / (volume.rolling(20).mean().iloc[-1] + 1e-10)
          sart_rvol = rvol_curr >= 0.6

          strend_line = calculate_strend(df, period=10, multiplier=3)
          sart_strend = close_curr > strend_line.iloc[-1]

          hma20 = calculate_hma(close, 20)
          sart_hma = close_curr > hma20.iloc[-1]

          fish, trg = calculate_fisher(df, length=9)
          fish_curr = fish.iloc[-1]
          trg_curr = trg.iloc[-1]
          fish_prev = fish.iloc[-2]
          trg_prev = trg.iloc[-2]

          sart_fisher = (fish_curr > trg_curr) or ((fish_prev <= trg_prev) and (fish_curr > trg_curr))
          sart_mfi = mfi_curr > 45
          sart_di = plus_di_curr > minus_di_curr

          if sart_rvol and sart_strend and sart_hma and sart_fisher and sart_mfi and sart_di:
            sinyal_var = True

        # --- 1H DALGA MARJLI KURAL SETİ ---
        elif kural_tipi == "1h_dalga_gorsel":
          hma20 = calculate_hma(close, 20)
          hma20_curr = hma20.iloc[-1]
          wave_breakout = check_wave_margins(df, lookback=3)

          if (
              (close_curr > hma20_curr)
              and (rsi_curr > 50)
              and (plus_di_curr > 25)
              and wave_breakout
          ):
            sinyal_var = True

        if sinyal_var:
          son_gonderim = kural_hafizasi.get(clean_ticker, 0)
          if simdi_epoch - son_gonderim > COOLDOWN_SECONDS:
            temiz_isim = clean_ticker.replace(".IS", "")
            zaman_str = datetime.now(TZ_TR).strftime("%H:%M")

            ilk_destek, ilk_direnc = hesapla_fibonacci_destek_direnc(df)
            rvol_curr = volume.iloc[-1] / (volume.rolling(20).mean().iloc[-1] + 1e-10)

            baslik = f"BIST {label} Sinyal"
            mesaj = (
                f"🚀 *BIST {label} Sinyal* ({zaman_str})\n• Hisse:"
                f" `🟦 {temiz_isim} 🟦` | Fiyat: {close_curr:.2f}\n• MFI: {mfi_curr:.1f}"
                f" | RSI: {rsi_curr:.1f} | RVOL:"
                f" {rvol_curr:.2f}\n• 🟢 İlk Destek:"
                f" {ilk_destek:.2f}\n• 🔴 İlk Direnç: {ilk_direnc:.2f}"
            )

            send_ntfy(mesaj, baslik)

            kural_hafizasi[clean_ticker] = simdi_epoch
            hafiza_kaydet(tum_hafiza)

      except Exception as e:
        print(f"Hata oluştu ({clean_ticker}): {e}")
        continue

  print("\nTüm Stratejilerin Tarama Turu Başarıyla Tamamlandı.")


if __name__ == "__main__":
  run_scanner()
