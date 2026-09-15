import requests
import yfinance as yf
import pandas as pd
import time
   from datetime import datetime
import pytz

# Türkiye saatine göre saat kontrolü
tr_tz = pytz.timezone('Europe/Istanbul')
simdiki_saat = datetime.now(tr_tz).hour

if simdiki_saat < 9 or simdiki_saat >= 19:
    print("Mesai saatleri dışındayız (09:00 - 19:00 harici), tarama durduruldu.")
    exit()                    
# BIST Tüm Hisseler (Yüzlerce hisse kapsayan kapsamlı liste)
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
    "CVKMD.IS", "CWENE.IS", "CにいIS", "DAGI.IS", "DAPGM.IS", "DARDL.IS", "DENGE.IS", "DERHL.IS", "DERIM.IS", "DESA.IS",
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
    "KLSER.IS", "KLSYN.IS", "KMPUR.IS", "KNFRT.IS", "kontr.IS", "KONYA.IS", "KOPOL.IS", "KORDS.IS", "KOTON.IS", "KOZAA.IS",
    "KOZAL.IS", "KRDMD.IS", "KRGYO.IS", "KRONT.IS", "KRPLS.IS", "KRSTL.IS", "KRTEK.IS", "KZBGY.IS", "KZYGZ.IS", "LIDER.IS",
    "LIDFA.IS", "LKMNH.IS", "LMKDC.IS", "LOGO.IS", "LUKSK.IS", "MAALT.IS", "MAKIM.IS", "MAKTK.IS", "MANAS.IS", "MARKA.IS",
    "MARTI.IS", "MAVI.IS", "MEDTR.IS", "MEGAP.IS", "MEKAG.IS", "MEPET.IS", "MERCN.IS", "MERKO.IS", "METUR.IS", "MGROS.IS",
    "MIATK.IS", "MMCAS.IS", "MNDRS.IS", "MNDTR.IS", "MOBTL.IS", "MPARK.IS", "MRGYO.IS", "	MTRKS.IS", "	MTRYO.IS", "	MZHLD.IS",
    "NATEN.IS", "NETAS.IS", "NIBAS.IS", "NTHOL.IS", "NUGYO.IS", "NUHCM.IS", "OBAMS.IS", "OBASE.IS", "ODAS.IS", "OFSYM.IS",
    "ONCSM.IS", "ORCAY.IS", "OYYAT.IS", "OZAKD.IS", "OZGYO.IS", "OZKGY.IS", "OZLTM.IS", "OZRDN.IS", "PAKRD.IS", "PAMEL.IS",
    "PAPIL.IS", "PARSN.IS", "PASEU.IS", "PCILT.IS", "PEKGY.IS", "PENGD.IS", "PENTA.IS", "PETKM.IS", "PETUN.IS", "PGSUS.IS",
    "PINSU.IS", "PKART.IS", "PKENT.IS", "PNSUT.IS", "POLHO.IS", "POLTK.IS", "PRDGS.IS", "PRKME.IS", "PRKAB.IS", "PSGYO.IS",
    "QNBFB.IS", "QNBFL.IS", "QUAGR.IS", "RALYH.IS", "REEDR.IS", "RNPOL.IS", "RODRG.IS", "ROYAL.IS", "RTALB.IS", "RUBNS.IS",
    "RYGYO.IS", "RYSAS.IS", "SAFKR.IS", "SAHOL.IS", "	SASA.IS", "	SAYAS.IS", "	SDTTR.IS", "	SEGFO.IS", "	SEGYO.IS",
    "SEKFK.IS", "SEKUR.IS", "SELEC.IS", "SELVA.IS", "SEYKM.IS", "SILVR.IS", "SISE.IS", "SKBNK.IS", "SKTAS.IS", "SMART.IS",
    "SMRTG.IS", "SNGYO.IS", "SNICA.IS", "SNPAM.IS", "SODSN.IS", "SOKM.IS", "SONME.IS", "SRVGY.IS", "SUMAS.IS", "SUNTK.IS",
    "SUWEN.IS", "	TABGD.IS", "	TARKM.IS", "	TATEN.IS", "	TATGD.IS", "	TAVHL.IS", "	TBORG.IS", "	TCELL.IS", "	TCKRC.IS",
    "TDGYO.IS", "TEKTU.IS", "TETMT.IS", "TEZOL.IS", "TGSAS.IS", "THYAO.IS", "	TKFEN.IS", "	TKNSA.IS", "	TMPOL.IS", "TMSN.IS",
    "	TOASO.IS", "	TRCAS.IS", "	TRGYO.IS", "	TRMET.IS", "	TSKB.IS", "	TSPOR.IS", "	TTKOM.IS", "	TTRAK.IS", "	TUCLK.IS",
    "	TUPRS.IS", "	Turek.IS", "	TURSG.IS", "	UFUK.IS", "	ULAS.IS", "	ULUFA.IS", "	ULKER.IS", "	ULUUN.IS", "	VAKBN.IS",
    "	VAKFN.IS", "	VAKGY.IS", "	VBTYZ.IS", "	VERTU.IS", "	VERUS.IS", "	VESBE.IS", "	VESTL.IS", "	VKFYO.IS", "	VKGYO.IS",
    "	VKING.IS", "	YAPRK.IS", "	YATAS.IS", "	YAYLA.IS", "	YBTAS.IS", "	YEOTK.IS", "	YESIL.IS", "	YGGYO.IS", "	YIGIT.IS",
    "	YKBNK.IS", "	YKSL.IS", "	YUNSA.IS", "	YYAPI.IS", "	ZEDUR.IS", "	ZOREN.IS", "	ZRGYO.IS"
]

PHONE = "905462848792"
API_KEY = "3477940"

def send_whatsapp(message):
    url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE}&text={requests.utils.quote(message)}&apikey={API_KEY}"
    try:
        res = requests.get(url, timeout=10)
        print(f"WhatsApp Yanıtı: {res.status_code}")
    except Exception as e:
        print(f"Mesaj Hatası: {e}")

def run_scanner():
    print(f"BIST Geniş Tarama Başlatıldı... Toplam Hisse: {len(STOCKS)}")
    matched = []

    for ticker in STOCKS:
        clean_ticker = ticker.strip()
        try:
            df = yf.download(clean_ticker, period="1mo", interval="4h", progress=False)
            if df.empty or len(df) < 20:
                continue

            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            close = df['Close']
            high = df['High']
            low = df['Low']
            volume = df['Volume']

            # RSI (14)
            delta = close.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

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

            # Son Değerler
            mfi_curr = mfi.iloc[-1]
            mfi_prev = mfi.iloc[-2]
            rsi_curr = rsi.iloc[-1]
            plus_di_curr = plus_di.iloc[-1]
            cmf_curr = cmf.iloc[-1]

            # Koşullar: MFI 65 yukarı kesişim, +DI > 30, RSI > 50, CMF > -0.20
            if (mfi_prev < 65 and mfi_curr >= 65) and (plus_di_curr > 30) and (rsi_curr > 50) and (cmf_curr > -0.20):
                matched.append(clean_ticker.replace(".IS", ""))

        except Exception as e:
            continue

    if matched:
        send_whatsapp(f"🚀 BIST Sinyal (Tümü): {', '.join(matched)}")
    else:
        print("Tüm hisseler tarandı, uyan hisse bulunamadı.")

if __name__ == "__main__":
    run_scanner()

