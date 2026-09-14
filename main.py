import yfinance as yf
import pandas as pd
import pandas_ta as ta
import requests
import urllib.parse
import time

PHONE_NUMBER = "905462848792"
API_KEY = "3477940"

def whatsapp_mesaj_gonder(mesaj):
    try:
        encoded_msg = urllib.parse.quote(mesaj)
        url = f"https://api.callmebot.com/whatsapp.php?phone={PHONE_NUMBER}&text={encoded_msg}&apikey={API_KEY}"
        requests.get(url, timeout=10)
    except Exception as e:
        print(f"Hata oluştu: {e}")

# TÜM BIST HİSSELERİ (Tüm Alfabeye Göre Alfabetik)
bist_hisseleri = [
    "AAVST.IS", "A1CAP.IS", "ACSEL.IS", "ADEL.IS", "ADESE.IS", "AGHOL.IS", "AGROT.IS", "AHGAZ.IS", "AKBNK.IS", "AKCNS.IS",
    "AKFGY.IS", "AKFYE.IS", "AKMGY.IS", "AKSA.IS", "AKSEN.IS", "AKSGY.IS", "AKSUE.IS", "AKTVF.IS", "ALARK.IS", "ALBRK.IS",
    "ALCAR.IS", "ALCTL.IS", "ALFAS.IS", "ALGYO.IS", "ALKA.IS", "ALKIM.IS", "ALTNY.IS", "ALMAD.IS", "ALVES.IS", "ANELE.IS",
    "ANGEN.IS", "ANHYT.IS", "ANSGR.IS", "ARASE.IS", "ARCLK.IS", "ARDYZ.IS", "ARENA.IS", "ARSAN.IS", "ARTMS.IS", "ASELS.IS",
    "ASGYO.IS", "ASTOR.IS", "ASUZU.IS", "ATAGY.IS", "ATATP.IS", "ATEKS.IS", "ATSYH.IS", "AVOD.IS", "AVPGY.IS", "AVTUR.IS",
    "AYCES.IS", "AYDEM.IS", "AYGAZ.IS", "AZTEK.IS", "BAGFS.IS", "BAKAB.IS", "BALAT.IS", "BANVT.IS", "BARMA.IS", "BASGZ.IS",
    "BAYRK.IS", "BEGYO.IS", "BERA.IS", "BEYAZ.IS", "BFREN.IS", "BIENP.IS", "BIGCH.IS", "BIMAS.IS", "BIOEN.IS", "BIZIM.IS",
    "BJKAS.IS", "BLCYT.IS", "BNTAS.IS", "BOBET.IS", "BORLS.IS", "BOSSA.IS", "BRCVN.IS", "BRISA.IS", "BRKO.IS", "BRKSN.IS",
    "BRMEN.IS", "BRSAN.IS", "BRYAT.IS", "BSOKE.IS", "BTCIM.IS", "BUCIM.IS", "BURCE.IS", "BURVA.IS", "BVSAN.IS", "BYDNR.IS",
    "CANTE.IS", "CATES.IS", "CCOLA.IS", "CELHA.IS", "CEMAS.IS", "CEMTS.IS", "CMBTN.IS", "CMENT.IS", "CONSE.IS", "COSMO.IS",
    "CRDFA.IS", "CRFSA.IS", "CUSAN.IS", "CVKMD.IS", "CWENE.IS", "DAGI.IS", "DAPGM.IS", "DARDL.IS", "DGATE.IS", "DGGYO.IS",
    "DITAS.IS", "DMRGD.IS", "DMSAS.IS", "DOAS.IS", "DOBUR.IS", "DOCO.IS", "DOHOL.IS", "DOKTA.IS", "DURDO.IS", "DYOBY.IS",
    "DZGYO.IS", "EBEBK.IS", "ECILC.IS", "ECZYT.IS", "EDATA.IS", "EDIP.IS", "EGEEN.IS", "EGGUB.IS", "EGPRO.IS", "EGSER.IS",
    "EKGYO.IS", "EKIZ.IS", "EKLTV.IS", "ELITE.IS", "EMKEL.IS", "ENJSA.IS", "ENKAI.IS", "ENTRA.IS", "EPLAS.IS", "ERBOS.IS",
    "EREGL.IS", "ERSU.IS", "ESCAR.IS", "ESEN.IS", "ETILR.IS", "EUPWR.IS", "EUREK.IS", "EYGYO.IS", "FORMT.IS", "FORTE.IS",
    "FRIGO.IS", "FROTO.IS", "FZLGY.IS", "GARAN.IS", "GARFA.IS", "GEDIK.IS", "GEDZA.IS", "GENIL.IS", "GENTAS.IS", "GESAN.IS",
    "GIPTA.IS", "GLBMD.IS", "GLCVY.IS", "YATAS.IS", "GLYHO.IS", "GMTAS.IS", "GOKNR.IS", "GOLTS.IS", "GOODY.IS", "GOZDE.IS",
    "GRNYO.IS", "GRSEL.IS", "GSDHO.IS", "GSDEVR.IS", "GSDDE.IS", "GUBRF.IS", "GWIND.IS", "GZNMI.IS", "HALKB.IS", "HATEK.IS",
    "HEKTS.IS", "HKTM.IS", "HLGYO.IS", "HUBVC.IS", "HUNER.IS", "HURGZ.IS", "ICUGS.IS", "IDGYO.IS", "IEYHO.IS", "IHAAS.IS",
    "IHEVA.IS", "IHGZT.IS", "IHLAS.IS", "IHLGM.IS", "IHYAY.IS", "IMASM.IS", "INDES.IS", "INFO.IS", "INGRM.IS", "INTEM.IS",
    "INVEO.IS", "INVES.IS", "IPEKE.IS", "ISATR.IS", "ISBTR.IS", "ISCTR.IS", "ISCUR.IS", "ISDMR.IS", "ISFIN.IS", "ISGSY.IS",
    "ISGYO.IS", "ISKPL.IS", "ISMEN.IS", "ISSEN.IS", "ITEKS.IS", "IYYU.IS", "IZINV.IS", "IZMDC.IS", "JANTS.IS", "KAFEIN.IS",
    "KLSER.IS", "KAMWE.IS", "KAPLM.IS", "KAREL.IS", "KARSN.IS", "KARTN.IS", "KATMR.IS", "KAYSE.IS", "KCAER.IS", "KCHOL.IS",
    "KENT.IS", "KRVGD.IS", "KBORU.IS", "KGYO.IS", "KIMMR.IS", "KLGYO.IS", "KLMSN.IS", "KLSYN.IS", "KMPUR.IS", "KNFRT.IS",
    "KONTR.IS", "KONYE.IS", "KORDS.IS", "KOZAA.IS", "KOZAL.IS", "KRDMA.IS", "KRDMB.IS", "KRDMD.IS", "KRONT.IS", "KRPLS.IS",
    "KRTEK.IS", "KSTUR.IS", "KTLEV.IS", "KTVKY.IS", "KUYAŞ.IS", "KZBGY.IS", "KZGYO.IS", "LIDER.IS", "LIDFA.IS", "LINK.IS",
    "LKMNH.IS", "LMKDC.IS", "LUKSK.IS", "MAALT.IS", "MACKO.IS", "MAKIM.IS", "MAKTK.IS", "MANAS.IS", "MARKA.IS", "MARTI.IS",
    "MAVI.IS", "MEDTR.IS", "MEGAP.IS", "MEGMT.IS", "MEPET.IS", "MERCN.IS", "MERIT.IS", "MERKO.IS", "METRO.IS", "METUR.IS",
    "MGROS.IS", "MHRGY.IS", "MIATK.IS", "MMPCT.IS", "MOBTL.IS", "MNDRS.IS", "MNDTR.IS", "MOBTL.IS", "MOGAN.IS", "MPARK.IS",
    "MRGYO.IS", "MRSHL.IS", "MSGYO.IS", "MTRKS.IS", "MTRYO.IS", "MZHLD.IS", "NATEN.IS", "NETAS.IS", "NIBAS.IS", "NTGAZ.IS",
    "NTHOL.IS", "NUGYO.IS", "NUHCM.IS", "OBAMS.IS", "OBASE.IS", "ODAS.IS", "OFSYM.IS", "ONCSM.IS", "ORCA.IS", "ORGE.IS",
    "ORMA.IS", "OSMEN.IS", "OSTIM.IS", "OTKAR.IS", "OTTO.IS", "OYAKC.IS", "OYYAT.IS", "OZATD.IS", "OZGYO.IS", "OZKGY.IS",
    "OZRDN.IS", "OZSUB.IS", "PAGYO.IS", "PAMEL.IS", "PAPIL.IS", "PARSN.IS", "PASEU.IS", "PATS.IS", "PENGD.IS", "PENTAS.IS",
    "PETKM.IS", "PETUN.IS", "PGSUS.IS", "PINAR.IS", "PKART.IS", "PKENT.IS", "PLTUR.IS", "PNLSN.IS", "PNSUT.IS", "POLHO.IS",
    "POLTK.IS", "PRDGS.IS", "PRKAB.IS", "PRKME.IS", "PRZMA.IS", "PSDTC.IS", "PSGYO.IS", "QUAGR.IS", "RALYH.IS", "RAYSG.IS",
    "REEDR.IS", "RNPOL.IS", "RODRG.IS", "ROYAL.IS", "RTALB.IS", "RUBNS.IS", "RYGYO.IS", "RYSAS.IS", "SAHOL.IS", "SAMAT.IS",
    "SANEL.IS", "SANFM.IS", "SANGS.IS", "SANFO.IS", "SANKO.IS", "SARKY.IS", "SASA.IS", "SAYAS.IS", "SDTTR.IS", "SEGMN.IS",
    "SEKFK.IS", "SEKUR.IS", "SELEC.IS", "SELVA.IS", "SEYKM.IS", "SILVR.IS", "SISE.IS", "SKBNK.IS", "SKTAS.IS", "SKYMD.IS",
    "SMART.IS", "SMRTG.IS", "SNAAM.IS", "SNICA.IS", "SNKRN.IS", "SNPAM.IS", "SODSN.IS", "SOKM.IS", "SONME.IS", "SRVGY.IS",
    "SUMAS.IS", "SUNTK.IS", "SURGY.IS", "SUWEN.IS", "TABGD.IS", "TAKST.IS", "TARKM.IS", "TATEN.IS", "TATGD.IS", "TAVHL.IS",
    "TBORG.IS", "TCELL.IS", "TDGYO.IS", "TEKTN.IS", "TERA.IS", "TETMT.IS", "TEZOL.IS", "TGSAS.IS", "THYAO.IS", "TKFEN.IS",
    "TKNSA.IS", "TLMAN.IS", "TMPOL.IS", "TMSN.IS", "TNZTP.IS", "TOASO.IS", "TRCAS.IS", "TRGYO.IS", "TRILC.IS", "TSKB.IS", "TSPOR.IS",
    "TTKOM.IS", "TTRAK.IS", "TUCLK.IS", "TUPRS.IS", "TURSG.IS", "UFUK.IS", "ULAS.IS", "ULKER.IS", "ULUFA.IS", "ULUSE.IS",
    "ULUUN.IS", "UNLU.IS", "USAK.IS", "VAKBN.IS", "VAKFN.IS", "VAKKO.IS", "VANGD.IS", "VBTYZ.IS", "VERTU.IS", "VERUS.IS",
    "VESBE.IS", "VESTL.IS", "VKFYO.IS", "VKGYO.IS", "VKING.IS", "YAPRK.IS", "YATAS.IS", "YAYLA.IS", "YEOTK.IS", "YGGYO.IS",
    "YGYO.IS", "YKBNK.IS", "YONGA.IS", "YOTAS.IS", "YUNSA.IS", "YYLGD.IS", "ZEDUR.IS", "ZELVE.IS", "ZOREN.IS", "ZRGYO.IS"
]

bist_hisseleri = sorted(list(set(bist_hisseleri)))
bulunan = 0

print(f"🔍 Toplam {len(bist_hisseleri)} BIST hissesi MFI 65 ve MFI 70 için taranıyor...\n")

for ticker in bist_hisseleri:
    try:
        time.sleep(0.15)
        df = yf.download(ticker, period="60d", interval="1h", progress=False)
        if df.empty or len(df) < 25: 
            continue
        
        df_4h = df.resample('4h').agg({
            'Open': 'first', 'High': 'max', 'Low': 'min', 'Close': 'last', 'Volume': 'sum'
        }).dropna()

        if isinstance(df_4h.columns, pd.MultiIndex):
            df_4h.columns = df_4h.columns.get_level_values(0)

        if len(df_4h) < 20: 
            continue

        df_4h['CMF'] = ta.cmf(df_4h['High'], df_4h['Low'], df_4h['Close'], df_4h['Volume'], length=20)
        df_4h['MFI'] = ta.mfi(df_4h['High'], df_4h['Low'], df_4h['Close'], df_4h['Volume'], length=14)
        df_4h['RSI'] = ta.rsi(df_4h['Close'], length=14)
        
        dmi = ta.dmi(df_4h['High'], df_4h['Low'], df_4h['Close'], length=14)
        df_4h['DMP'] = dmi['DMP_14']

        dmp_bugun = df_4h['DMP'].iloc[-1]
        rsi_bugun = df_4h['RSI'].iloc[-1]
        cmf_bugun = df_4h['CMF'].iloc[-1]

        mfi_onceki = df_4h['MFI'].iloc[-2]
        mfi_bugun = df_4h['MFI'].iloc[-1]

        # KESİŞİM ŞARTLARI
        mfi_65_kesim = (mfi_onceki <= 65) and (mfi_bugun > 65)
        mfi_70_kesim = (mfi_onceki <= 70) and (mfi_bugun > 70)

        artida_dmi = dmp_bugun > 40
        rsi_guclu = rsi_bugun > 50
        cmf_filtre = cmf_bugun > -0.20

        # Eğer diğer tüm kriterler sağlanıyorsa ve MFI 65 veya 70 kesilmişse:
        if (mfi_65_kesim or mfi_70_kesim) and artida_dmi and rsi_guclu and cmf_filtre:
            bulunan += 1
            hisse_adi = ticker.replace(".IS", "")
            
            # Sinyal seviyesini belirleme
            seviye = "MFI 70 (Güçlü)" if mfi_70_kesim else "MFI 65"
            
            bildirim = (
                f"🚀 {seviye} YUKARI KESİM SİNYALİ!\n\n"
                f"📈 Hisse: #{hisse_adi}\n"
                f"⏰ Periyot: 4 Saatlik\n"
                f"🔥 MFI Kesişimi: {mfi_onceki:.1f} ➔ {mfi_bugun:.1f}\n"
                f"⚡ +DI: {dmp_bugun:.1f} (>40)\n"
                f"📊 RSI: {rsi_bugun:.1f} (>50)\n"
                f"💰 CMF: {cmf_bugun:.2f} (>-0.20)"
            )
            whatsapp_mesaj_gonder(bildirim)
            print(f"✅ SİNYAL GÖNDERİLDİ ({seviye}): {hisse_adi}")

    except Exception:
        continue

print("\n--- TARAMA TAMAMLANDI ---")
if bulunan == 0:
    print("❌ Belirlenen şartlara uyan hisse bulunamadı.")
