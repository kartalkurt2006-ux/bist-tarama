from datetime import datetime, timedelta, time
import json
import os
import threading
import time as t_mod
import urllib.request
import pandas as pd
import pytz
import yfinance as yf
from flask import Flask

app = Flask(__name__)

# ==============================================================================
# SUNUCU15.PY - 4 MADDELİK SİSTEM ARTILARI VE ÖZELLİKLERİ:
# 1. 15 Dakikalık Periyot & Zaman Kontrolü: 15m barlar ile nokta atışı tarama, 
#    hafta sonu ve mesai saatleri dışını filtreleme.
# 2. Akıllı Cooldown (Hafıza) Mekanizması: Aynı hisseye 1 saat içinde tekrar 
#    bildirim gitmesini engellemek için hafiza_sunucu15.json desteği.
# 3. Thread Güvenliği (Lock): Manuel tarama ile arka plan döngüsünün 
#    çakışmasını önleyen kilit mekanizması.
# 4. Gelişmiş Filtre Kombinasyonu: TDSeq dip teyidi, Hull 20, CMF, DI+ ve 
#    Hacim Patlaması filtrelerinin tam uyumu.
# ==============================================================================

NTFY_TOPIC = "borsa_senet"
HAFIZA_DOSYASI = "hafiza_sunucu15.json"
COOLDOWN_SURESI_SAAT = 1
TZ_TR = pytz.timezone("Europe/Istanbul")

# Çakışmayı önlemek için İşlem Kilidi (Lock)
tarama_kilit = threading.Lock()

# BIST TÜM HİSSELER LİSTESİ (Yan yana düzenli dizi formatı)
BIST_HISSELERI = [
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
    "YGGYO.IS", "YIGIT.IS", "YKBNK.IS", "YKSL.IS", "YUNSA.IS", "YYAPI.IS", "ZEDUR.IS", "ZOREN.IS", "ZRGYO.IS"
]


def hafizayi_oku():
  if os.path.exists(HAFIZA_DOSYASI):
    try:
      with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
        return json.load(f)
    except:
      return {}
  return {}


def hafizaya_kaydet(hafiza):
  try:
    with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
      json.dump(hafiza, f, ensure_ascii=False, indent=4)
  except Exception as e:
    print(f"Hafıza kayıt hatası: {e}")


def bildirim_gonder(mesaj, baslik="Borsa Sinyali"):
  try:
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    data = mesaj.encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Title": baslik.encode("utf-8"),
            "Priority": "urgent",
            "Tags": "chart_with_upwards_trend,rotating_light,rocket",
        },
    )
    urllib.request.urlopen(req)
  except Exception as e:
    print(f"Bildirim hatası: {e}")


def wma(series, period):
  weights = pd.Series(range(1, period + 1))
  return series.rolling(period).apply(
      lambda x: (x * weights).sum() / weights.sum(), raw=True
  )


def hull_moving_average(series, period=20):
  half_period = int(period / 2)
  sqrt_period = int(pd.np.sqrt(period))
  wma_half = wma(series, half_period)
  wma_full = wma(series, period)
  diff = 2 * wma_half - wma_full
  return wma(diff, sqrt_period)


def td_seq_alis_kurulumu_kontrol(df):
  if len(df) < 15:
    return False
  close = df["Close"]
  earlier_close = close.shift(4)
  condition = close < earlier_close
  recent_cond = condition.iloc[-9:]
  return recent_cond.all()


def indikatorleri_hesapla(df):
  period_cmf = 20
  mf_multiplier = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / (
      df["High"] - df["Low"] + 1e-9
  )
  mf_volume = mf_multiplier * df["Volume"]
  df["CMF"] = mf_volume.rolling(period_cmf).sum() / df["Volume"].rolling(
      period_cmf
  ).sum()

  period_di = 14
  up_move = df["High"].diff()
  down_move = df["Low"].diff()
  plus_dm = pd.Series(
      [
          up if (up > down and up > 0) else 0
          for up, down in zip(up_move, down_move)
      ],
      index=df.index,
  )
  true_range = pd.Series(
      [
          max(h - l, abs(h - c_prev), abs(l - c_prev))
          for h, l, c_prev in zip(
              df["High"], df["Low"], df["Close"].shift(1)
          )
      ],
      index=df.index,
  )
  tr_smoothed = true_range.rolling(period_di).sum()
  plus_dm_smoothed = plus_dm.rolling(period_di).sum()
  df["+DI"] = (plus_dm_smoothed / (tr_smoothed + 1e-9)) * 100

  df["Hull_20"] = hull_moving_average(df["Close"], period=20)

  ema12 = df["Close"].ewm(span=12, adjust=False).mean()
  ema26 = df["Close"].ewm(span=26, adjust=False).mean()
  df["Weighted_MACD"] = ema12 - ema26
  df["MACD_Signal"] = df["Weighted_MACD"].ewm(span=9, adjust=False).mean()

  return df


def piyasalari_tara(manuel_tetikleme=False):
  if not tarama_kilit.acquire(blocking=False):
    print("Zaten devam eden bir tarama var, bu istek atlandı.")
    return

  try:
    simdi = datetime.now(TZ_TR)

    if not manuel_tetikleme:
      if simdi.weekday() >= 5:
        print(f"Hafta sonu olduğu için otomatik tarama atlandı: {simdi}")
        return

      anlik_zaman = simdi.time()
      if not (time(9, 0) <= anlik_zaman <= time(19, 30)):
        print(f"Çalışma saatleri dışındayız (09:00 - 19:30): {simdi}")
        return

    print(
        f"15 Dakikalık Veri Taraması Başladı (Manuel: {manuel_tetikleme}):"
        f" {simdi}"
    )
    hafiza = hafizayi_oku()

    for hisse in BIST_HISSELERI:
      try:
        df = yf.download(hisse, period="5d", interval="15m", progress=False)
        if df.empty or len(df) < 30:
          continue

        if isinstance(df.columns, pd.MultiIndex):
          df.columns = df.columns.get_level_values(0)

        df = indikatorleri_hesapla(df)

        son = df.iloc[-1]
        onceki = df.iloc[-2]

        fiyat = float(son["Close"])
        bir_onceki_fiyat = float(onceki["Close"])
        son_hacim = float(son["Volume"])
        ortalama_hacim = float(df["Volume"].iloc[-21:-1].mean())

        plus_di = float(son["+DI"])
        cmf = float(son["CMF"])
        hull = float(son["Hull_20"])
        w_macd = float(son["Weighted_MACD"])
        w_signal = float(son["MACD_Signal"])

        td_dip_sarti = td_seq_alis_kurulumu_kontrol(df)
        kosul_di = plus_di > 20
        kosul_cmf = cmf > 0
        kosul_hull = hull < fiyat
        kosul_osillator = w_macd >= w_signal

        fiyat_degisim = (
            (fiyat - bir_onceki_fiyat) / bir_onceki_fiyat
        ) * 100
        kosul_hacim_fiyat = (son_hacim > (ortalama_hacim * 1.5)) and (
            fiyat_degisim >= 1.5
        )

        if (
            td_dip_sarti
            and kosul_di
            and kosul_cmf
            and kosul_hull
            and kosul_osillator
            and kosul_hacim_fiyat
        ):
          hisse_adi = hisse.replace(".IS", "")

          son_gonderim_zamanı = hafiza.get(hisse_adi)
          gonderebilir = True
          if son_gonderim_zamanı:
            gecen_sure = simdi - datetime.fromisoformat(son_gonderim_zamanı)
            if gecen_sure < timedelta(hours=COOLDOWN_SURESI_SAAT):
              gonderebilir = False

          if gonderebilir:
            mesaj = (
                f"Saat: {simdi.strftime('%H:%M')}\n"
                f"Fiyat: {fiyat:.2f} TL (%%{fiyat_degisim:.2f})\n"
                f"DI+ ({plus_di:.1f}) > 20 | CMF ({cmf:.2f}) > 0\n"
                f"Hull 20 & Hacim Patlaması Onaylandı!"
            )
            baslik = f"🚀 15dk Tabandan Fırlama: {hisse_adi}"
            bildirim_gonder(mesaj, baslik)

            hafiza[hisse_adi] = simdi.isoformat()
            hafizaya_kaydet(hafiza)

            t_mod.sleep(0.2)

      except Exception as e:
        continue

    print(f"Tarama bitti: {datetime.now(TZ_TR)}")
  finally:
    tarama_kilit.release()


def arka_plan_dongusu():
  while True:
    piyasalari_tara(manuel_tetikleme=False)
    t_mod.sleep(900)


@app.route("/")
def ana_sayfa():
  return "BIST 15dk Tabandan Fırlama Sinyal Sunucusu Aktif ve Çalışıyor!"


@app.route("/tara")
def manuel_tara():
  threading.Thread(
      target=piyasalari_tara, kwargs={"manuel_tetikleme": True}
  ).start()
  return "Manuel tarama başlatıldı! Sinyaller ntfy'a gelecektir."


if __name__ == "__main__":
  t = threading.Thread(target=arka_plan_dongusu)
  t.daemon = True
  t.start()

  app.run(host="0.0.0.0", port=5000)
