from datetime import datetime, timedelta
import json
import os
import threading
import time
import urllib.request
import pandas as pd
import pytz
import yfinance as yf
from flask import Flask

app = Flask(__name__)

# Ayarlar
NTFY_TOPIC = "borsa_senet"
HAFIZA_DOSYASI = "hafiza_sunucu15.json"
COOLDOWN_SURESI_SAAT = 1  # Aynı hisse için tekrar bildirim aralığı
TZ_TR = pytz.timezone("Europe/Istanbul")

# BIST TÜM HİSSELER LİSTESİ (Eksiksiz Tam Liste)
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


def indikatorleri_hesapla(df):
  delta = df["Close"].diff()
  gain = (delta.where(delta > 0, 0) * df["Volume"]).rolling(14).sum()
  loss = (-delta.where(delta < 0, 0) * df["Volume"]).rolling(14).sum()
  rs = gain / loss
  df["MFI"] = 100 - (100 / (1 + rs))

  delta_rsi = df["Close"].diff()
  gain_rsi = delta_rsi.where(delta_rsi > 0, 0).rolling(14).mean()
  loss_rsi = (-delta_rsi.where(delta_rsi < 0, 0)).rolling(14).mean()
  rs_rsi = gain_rsi / loss_rsi
  df["RSI"] = 100 - (100 / (1 + rs_rsi))

  mf_multiplier = (
      (df["Close"] - df["Low"]) - (df["High"] - df["Close"])
  ) / (df["High"] - df["Low"])
  mf_multiplier = mf_multiplier.fillna(0)
  mf_volume = mf_multiplier * df["Volume"]
  df["CMF"] = mf_volume.rolling(20).sum() / df["Volume"].rolling(20).sum()

  high_diff = df["High"].diff()
  low_diff = -df["Low"].diff()
  plus_dm = high_diff.where((high_diff > low_diff) & (high_diff > 0), 0)
  tr1 = df["High"] - df["Low"]
  tr2 = (df["High"] - df["Close"].shift()).abs()
  tr3 = (df["Low"] - df["Close"].shift()).abs()
  tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
  atr = tr.rolling(14).mean()
  plus_di = 100 * (plus_dm.rolling(14).mean() / atr)
  df["+DI"] = plus_di

  return df


def piyasalari_tara():
  simdi = datetime.now(TZ_TR)
  print(f"Tarama başladı: {simdi}")
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

      fiyat = float(son["Close"])
      mfi = float(son["MFI"])
      rsi = float(son["RSI"])
      cmf = float(son["CMF"])
      plus_di = float(son["+DI"])

      kosul = (mfi > 70) and (rsi > 50) and (cmf > 0) and (plus_di > 30)

      if kosul:
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
              f"Fiyat: {fiyat:.2f}\n"
              f"MFI: {mfi:.1f} | RSI: {rsi:.1f}\n"
              f"CMF: {cmf:.2f} | +DI: {plus_di:.1f}"
          )
          baslik = f"🚀 Süper 15dk Sinyali: {hisse_adi}"
          bildirim_gonder(mesaj, baslik)

          hafiza[hisse_adi] = simdi.isoformat()
          hafizaya_kaydet(hafiza)

          time.sleep(0.2)

    except Exception as e:
      continue

  print(f"Tarama bitti: {datetime.now(TZ_TR)}")


def arka_plan_dongusu():
  while True:
    piyasalari_tara()
    time.sleep(900)


@app.route("/")
def ana_sayfa():
  threading.Thread(target=piyasalari_tara).start()
  return "BIST 15DK Sinyal Sunucusu Aktif ve Çalışıyor!"


if __name__ == "__main__":
  t = threading.Thread(target=arka_plan_dongusu)
  t.daemon = True
  t.start()

  app.run(host="0.0.0.0", port=5000)
