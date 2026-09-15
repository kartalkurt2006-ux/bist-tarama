import os
import requests
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import urllib.parse

def tum_bist_hisselerini_getir():
    # BIST'teki tüm ana ve alt pazardaki hisseleri kapsayan genişletilmiş liste (500+ Hisse)
    hisseler = [
        "ACSEL.IS", "ADEL.IS", "ADESE.IS", "ADGYO.IS", "AEFES.IS", "AFYON.IS", "AGESA.IS", "AGHOL.IS", "AGROT.IS", "AGYO.IS",
        "AHGAZ.IS", "AKBNK.IS", "AKCNS.IS", "AKENR.IS", "AKFGY.IS", "AKFYE.IS", "AKGRT.IS", "AKMGY.IS", "AKSA.IS", "AKSEN.IS",
        "AKSGY.IS", "AKSUE.IS", "AKYHO.IS", "ALARK.IS", "ALBRK.IS", "ALCAR.IS", "ALCTL.IS", "ALFAS.IS", "ALGYO.IS", "ALKA.IS",
        "ALKIM.IS", "ALKLC.IS", "ALTNY.IS", "ANELE.IS", "ANGEN.IS", "ANHYT.IS", "ANSGR.IS", "ARASE.IS", "ARCLK.IS", "ARDYZ.IS",
        "ARENA.IS", "ARSAN.IS", "ARZUM.IS", "ASELS.IS", "ASTOR.IS", "ASUZU.IS", "ATAGY.IS", "ATAKP.IS", "ATEKS.IS", "ATLAS.IS",
        "ATSYH.IS", "AVOD.IS", "AVPGY.IS", "AYCES.IS", "AYDEM.IS", "AYEN.IS", "AYES.IS", "AYGAZ.IS", "AZTEK.IS", "BAGFS.IS",
        "BAKAB.IS", "BALAT.IS", "BANVT.IS", "BARMA.IS", "BASCM.IS", "BASGZ.IS", "BAYRK.IS", "BEGYO.IS", "BERA.IS", "BEYAZ.IS",
        "BFREN.IS", "BIENY.IS", "BIGCH.IS", "BIMAS.IS", "BINHO.IS", "BIOEN.IS", "BIZIM.IS", "BJKAS.IS", "BLCYT.IS", "BMSCH.IS",
        "BMSTL.IS", "BNTAS.IS", "BOBET.IS", "BORLS.IS", "BOSSA.IS", "BRISA.IS", "BRKO.IS", "BRKSN.IS", "BRMEN.IS", "BRYAT.IS",
        "BSOKE.IS", "BTCIM.IS", "BUCIM.IS", "BURCE.IS", "BURVA.IS", "BVSAN.IS", "CANTE.IS", "CASA.IS", "CATES.IS",
        "CCOLA.IS", "CELHA.IS", "CEMAS.IS", "CEMTS.IS", "CEOEM.IS", "CIMSA.IS", "CLEBI.IS", "CMBTN.IS", "CMENT.IS",
        "CONSE.IS", "COSMO.IS", "CRDFA.IS", "CRFSA.IS", "CUSAN.IS", "CVKMD.IS", "CWENE.IS", "DAGI.IS", "DAPGM.IS", "DARDL.IS",
        "DENGE.IS", "DERHL.IS", "DERIM.IS", "DESA.IS", "DESPC.IS", "DEVA.IS", "DIRIT.IS", "DITAS.IS", "DMRGD.IS", "DMSAS.IS",
        "DNISI.IS", "DOAS.IS", "DOBUR.IS", "DOCO.IS", "DOGUB.IS", "DOHOL.IS", "DOKTA.IS", "DURDO.IS", "DYOBY.IS",
        "DZGYO.IS", "EBEBK.IS", "ECILC.IS", "ECZYT.IS", "EDIP.IS", "EGEEN.IS", "EGEPO.IS", "EGGUB.IS", "EGPRO.IS",
        "EGSER.IS", "EKGYO.IS", "EKOS.IS", "EKSUN.IS", "ELITE.IS", "EMKEL.IS", "ENERY.IS", "ENJSA.IS", "ENKAI.IS", "ENSRI.IS",
        "EPLAS.IS", "ERBOS.IS", "ERCB.IS", "EREGL.IS", "ERSU.IS", "ESCAR.IS", "ESEN.IS", "ETILR.IS", "EUPWR.IS", "EUREN.IS",
        "EYGYO.IS", "FADE.IS", "FENER.IS", "FLAP.IS", "FMIZP.IS", "FONET.IS", "FORMT.IS", "FORTE.IS", "FRIGO.IS", "FROTO.IS",
        "GARAN.IS", "GARFA.IS", "GEDIK.IS", "GEDZA.IS", "GENTS.IS", "GEREL.IS", "GESAN.IS", "GLBMD.IS", "GLCVY.IS", "GLRYH.IS",
        "GLYHO.IS", "GMTAS.IS", "GOKNR.IS", "GOLTS.IS", "GOODY.IS", "GOZDE.IS", "GRNYO.IS", "GRSEL.IS", "GSDDE.IS", "GSDHO.IS",
        "GSRAY.IS", "GUBRF.IS", "GWIND.IS", "GZNMI.IS", "HALKB.IS", "HATEK.IS", "HATSN.IS", "HDFGS.IS", "HEKTS.IS", "HKTM.IS",
        "HLGYO.IS", "HTTBT.IS", "HUBVC.IS", "HUNER.IS", "HURGZ.IS", "ICBCT.IS", "IDEAS.IS", "IDGYO.IS", "IHEVA.IS", "IHGZT.IS",
        "IHLAS.IS", "IHLGM.IS", "IHYAZ.IS", "IMASM.IS", "INDES.IS", "INFO.IS", "INTEM.IS", "INVEO.IS", "IPEKE.IS", "ISATR.IS",
        "ISBIR.IS", "ISBTR.IS", "ISCTR.IS", "ISDMR.IS", "ISFIN.IS", "ISGSY.IS", "ISGYO.IS", "ISKPL.IS", "ISKUR.IS",
        "ISMEN.IS", "ISSEN.IS", "IZFAS.IS", "IZINV.IS", "IZMDC.IS", "JANTS.IS", "KAPLM.IS", "KAREL.IS", "KARSN.IS", "KARTN.IS",
        "KARYE.IS", "KASTB.IS", "KATMR.IS", "KCAER.IS", "KCHOL.IS", "KENT.IS", "KERVT.IS", "KFEIN.IS", "KGYO.IS",
        "KIMMR.IS", "KLGYO.IS", "KLKIM.IS", "KLMSN.IS", "KLSER.IS", "KMPUR.IS", "KNFRT.IS", "KONTR.IS", "KONYA.IS", "KOPOL.IS",
        "KORDS.IS", "KOTON.IS", "KOZAA.IS", "KOZAL.IS", "KRDMA.IS", "KRDMB.IS", "KRDMD.IS", "KRONT.IS", "KRPLS.IS", "KRSTL.IS",
        "KRTEK.IS", "KRVGD.IS", "KTSKR.IS", "KUTPO.IS", "KUVVA.IS", "KZBGY.IS", "KZGYO.IS", "LIDER.IS", "LIDFA.IS", "LINK.IS",
        "LKMNH.IS", "LOGO.IS", "LUKSK.IS", "MAALT.IS", "MAKIM.IS", "MAKTK.IS", "MANAS.IS", "MARKA.IS", "MARTI.IS",
        "MAVI.IS", "MEDTR.IS", "MEGAP.IS", "MEKAG.IS", "MENPA.IS", "MERCN.IS", "MERKO.IS", "METRO.IS", "METUR.IS", "MGROS.IS",
        "MIATK.IS", "MMCAS.IS", "MNDRS.IS", "MNDTR.IS", "MOBTL.IS", "MPARK.IS", "MRSHL.IS", "MSGYO.IS", "MTRKS.IS",
        "NETAS.IS", "NIBAS.IS", "NTGAZ.IS", "NTHOL.IS", "NUGYO.IS", "NUHCM.IS", "OBASE.IS", "ODAS.IS",
        "OFSYM.IS", "ONCSM.IS", "ORCAY.IS", "OYYAT.IS", "OZAKD.IS", "OZGYO.IS", "OZRDN.IS", "OZSUB.IS", "PASTR.IS", "PAGYO.IS",
        "PAMEL.IS", "PAPIL.IS", "PARSN.IS", "PATEK.IS", "PCILT.IS", "PEKGY.IS", "PENGD.IS", "PENTA.IS", "PETKM.IS", "PETUN.IS",
        "PGSUS.IS", "PKART.IS", "PKENT.IS", "PNSUT.IS", "POLHO.IS", "POLTK.IS", "PRDGS.IS", "PRKME.IS", "PRKTS.IS", "PSDTC.IS",
        "PSGYO.IS", "QUAGR.IS", "RALYH.IS", "RAYSG.IS", "REEDR.IS", "RNPOL.IS", "RODRG.IS", "ROYAL.IS", "RTALB.IS", "RUBNS.IS",
        "SAHOL.IS", "SAMAT.IS", "SANEL.IS", "SANFM.IS", "SANKO.IS", "SARKY.IS", "SASA.IS", "SAYAS.IS", "SDTTR.IS",
        "SEGMN.IS", "SEKFK.IS", "SEKUR.IS", "SELEC.IS", "SELGD.IS", "SELVA.IS", "SEYKM.IS", "SILVR.IS", "SISE.IS", "SKBNK.IS",
        "SKTAS.IS", "SMART.IS", "SMRTG.IS", "SOKM.IS", "SONME.IS", "SRVGY.IS", "SUMAS.IS", "SUNTK.IS", "SUWEN.IS",
        "TABGD.IS", "TARKM.IS", "TATEN.IS", "TATGD.IS", "TAVHL.IS", "TBORG.IS", "TCELL.IS", "TDGYO.IS", "TEKTU.IS", "TERA.IS",
        "TGSAS.IS", "THYAO.IS", "TIRE.IS", "TMPOL.IS", "TMSN.IS", "TOASO.IS", "TRCAS.IS", "TRGYO.IS", "TRILC.IS", "TSKB.IS",
        "TSPOR.IS", "TTKOM.IS", "TTRAK.IS", "TUCLK.IS", "TUPRS.IS", "TUKAS.IS", "UFUK.IS", "ULAS.IS", "ULKER.IS",
        "ULUUN.IS", "UMPAS.IS", "UNLU.IS", "USAK.IS", "VAKBN.IS", "VAKFN.IS", "VAKKO.IS", "VANGD.IS", "VBTYZ.IS", "VERTU.IS",
        "VERUS.IS", "VESBE.IS", "VESTL.IS", "VKFYO.IS", "VKGYO.IS", "VKING.IS", "YAPRK.IS", "YATAS.IS", "YAYLA.IS", "YEOTK.IS",
        "YESIL.IS", "YGGYO.IS", "YKBNK.IS", "YKSL.IS", "YUNSA.IS", "ZEDUR.IS", "ZOREN.IS", "PAVO.IS"
    ]
    return list(set(hisseler))

eslesti = []

def tarayiciyi_calistir():
    hisseler = tum_bist_hisselerini_getir()
    print(f"Toplam {len(hisseler)} BIST hissesi taranıyor...")

    for ticker in hisseler:
        try:
            df = yf.download(ticker, interval="15m", period="10d", progress=False)
            if df.empty or len(df) < 50:
                continue
                
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            close = df['Close']
            high = df['High']
            low = df['Low']
            volume = df['Volume']

            # MFI (14)
            delta = close.diff()
            money_flow = close * volume
            positive_mf = money_flow.where(delta > 0, 0)
            negative_mf = money_flow.where(delta < 0, 0)
            pos_mf_14 = positive_mf.rolling(window=14).sum()
            neg_mf_14 = negative_mf.rolling(window=14).sum()
            mfi = 100 - (100 / (1 + (pos_mf_14 / neg_mf_14)))

            # +DI (14)
            plus_dm = high.diff()
            minus_dm = low.diff()
            plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0.0)
            tr1 = pd.DataFrame([high - low, (high - close.shift()).abs(), (low - close.shift()).abs()]).max(axis=0)
            atr = tr1.rolling(window=14).mean()
            plus_dm_series = pd.Series(plus_dm, index=df.index)
            plus_di = 100 * (plus_dm_series.rolling(window=14).mean() / atr)

            # HMA (20)
            def calculate_hma(series, period=20):
                half_length = int(period / 2)
                sqrt_length = int(np.sqrt(period))
                wma_half = series.rolling(window=half_length).apply(lambda x: np.dot(x, np.arange(1, len(x) + 1)) / np.sum(np.arange(1, len(x) + 1)), raw=True)
                wma_full = series.rolling(window=period).apply(lambda x: np.dot(x, np.arange(1, len(x) + 1)) / np.sum(np.arange(1, len(x) + 1)), raw=True)
                diff = 2 * wma_half - wma_full
                hma = diff.rolling(window=sqrt_length).apply(lambda x: np.dot(x, np.arange(1, len(x) + 1)) / np.sum(np.arange(1, len(x) + 1)), raw=True)
                return hma

            hma_20 = calculate_hma(close, 20)

            # CMF (20)
            mf_multiplier = ((close - low) - (high - close)) / (high - low)
            mf_multiplier = mf_multiplier.fillna(0)
            mf_volume = mf_multiplier * volume
            cmf = mf_volume.rolling(window=20).sum() / volume.rolling(window=20).sum()

            mfi_curr = mfi.iloc[-1]
            plus_di_curr = plus_di.iloc[-1]
            plus_di_prev = plus_di.iloc[-2]
            close_curr = close.iloc[-1]
            hma_curr = hma_20.iloc[-1]
            cmf_curr = cmf.iloc[-1]

            # Koşullar:
            kosul_plus_di = (plus_di_prev <= 40) and (plus_di_curr > 40)
            kosul_mfi = mfi_curr > 69
            kosul_hma = close_curr > hma_curr
            kosul_cmf = cmf_curr > 0

            if kosul_plus_di and kosul_mfi and kosul_hma and kosul_cmf:
                temiz_ticker = ticker.replace(".IS", "")
                eslesti.append(temiz_ticker)

        except Exception as e:
            continue

    if eslesti:
        mesaj = f"⚡ BIST 15dk Momentum Sinyali:\n" + ", ".join(eslesti)
        whatsapp_gonder(mesaj)
    else:
        print("Kriterlere uyan hisse bulunamadı.")

def whatsapp_gonder(mesaj):
    url = f"https://api.callmebot.com/whatsapp.php?phone=TELEFONUN&text={urllib.parse.quote(mesaj)}&apikey=APIKEYIN"
    requests.get(url)

if __name__ == "__main__":
    tarayiciyi_calistir()
