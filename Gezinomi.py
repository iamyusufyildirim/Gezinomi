                                        #########################################################################
                                        # Kural Tabanlı Sınıflandırma ile Potansiyel Müşteri Getirisi Hesaplama #
                                        #########################################################################

#      +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#      +                                                UYGULAMA ÖNCESİ                                                          +
#      +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#      +                                                                                                                         +
#      +                                                                                                                         +
#      +         SaleId   SaleDate CheckInDate       Price     ConceptName  SaleCityName     CInDay  SaleCheckInDayDiff Seasons  +
#      +  0      415122 2022-12-03  2022-12-03   79.304029    Herşey Dahil      Antalya   Saturday                   0     Low   +
#      +  1      415103 2022-12-03  2022-12-03   45.970696  Yarım Pansiyon      Antalya   Saturday                   0     Low   +
#      +  2      404034 2022-09-12  2022-09-13   77.838828    Herşey Dahil      Antalya    Tuesday                   1    High   +
#      +  3      415094 2022-12-03  2022-12-10  222.710623  Yarım Pansiyon        İzmir   Saturday                   7     Low   +
#      +  4      414951 2022-12-01  2022-12-03  140.476190  Yarım Pansiyon        İzmir   Saturday                   2     Low   +
#      +                                                                                                                         +
#      +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#     +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#     +                     UYGULAMA SONRASI                    +
#     +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#     +                                                         +
#     +        SALES_LEVEL_BASED         SEGMENT     Price      +
#     +  0   GIRNE_HERŞEY DAHIL_HIGH        A        103.94     +
#     +  1   GIRNE_HERŞEY DAHIL_LOW         A        90.94      +
#     +  2   İZMİR_YARIM_PANSIYON_HIGH      A        87.66      +
#     +  3   DIĞER_HERŞEY DAHIL_LOW         A        87.31      +
#     +  4   DIĞER_HERŞEY DAHIL_HIGH        A        83.79      +
#     +                                                         +
#     +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


# Gerekli kütüphane importları ve bazı görsel ayarlamaları yapıyoruz
import pandas as pd
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.float_format", lambda x : "%.2f" % x)

# İlgili veri setini projemize dahil ediyoruz
def load_dataset():
    data = pd.read_excel("data_sets/miuul_gezinomi.xlsx")
    return data

df = load_dataset()


# Veri setini tanımak adına check_df fonkdiyonunu tanımlıyoruz.
def check_df(dataframe, head=10):
    """
    Veri setindeki gözlem birimi, boyut bilgisi, değişken isimleri
    gibi veri seti hakkındaki genel resmi verir.

    Parameters
    ----------
    dataframe : dataframe
                Bilgisi istenilen veri seti

    head : int
           Kaç satır gözlem birimi istenildiği bilgisi

    """
    print("\n###################################")
    print(f"----> İlk {head} Gözlem Birimi <----")
    print("###################################")
    print(dataframe.head(head))

    print("\n###################################")
    print("-----> Veri Seti Boyut Bilgisi <-----")
    print("###################################")
    print(dataframe.shape)

    print("\n###################################")
    print("--------> Değişken İsimleri <--------")
    print("###################################")
    print(dataframe.columns)

    print("\n###################################")
    print("-------> Eksik Değer Var mı? <-------")
    print("###################################")
    print(dataframe.isnull().values.any())

    print("\n###################################")
    print("-----> Betimsel İstatistikler <------")
    print("###################################")
    print(dataframe.describe().T)

    print("\n###################################")
    print("---> Veri Seti Hakkında Bilgiler <---")
    print("###################################")
    print(dataframe.info())


check_df(dataframe=df)


# veri setindeki eksik değerleri tablo formatında gösterecek bir fonksiyon tanımlıyoruz.
def na_table(dataframe):
    na_columns = [col for col in dataframe.columns if dataframe[col].isnull().sum() > 0]
    missing_values = (dataframe[na_columns].isnull().sum()).sort_values(ascending=False)
    ratio = (dataframe[na_columns].isnull().sum() / dataframe.shape[0] * 100).sort_values(ascending=False)
    table = pd.concat([missing_values, ratio], axis=1, keys=["Değer", "%"])
    print(table)

na_table(dataframe=df)


# Eksik değerlerin Price değişkenin de olması ilgili hesaplamaların yapılmasında bozukluklara yol açacağından ötürü temizliyoruz.
df.dropna(inplace=True)


# Veri seti her satış işleminde oluşan kayıtlardan meydana gelmektedir. Bunun anlamı tablo tekilleştirilmemiştir.
# Diğer bir ifade ile belirli demografik özelliklere sahip bir kullanıcı birden fazla kez alışveriş yapmış olabilir.
# value_counts() fonksiyonu ile birden fazla satış kaydı olup olmadığını sorguluyoruz.
df.value_counts()


"""
Bu kod parçacığı, verileri belirli sütunlara göre gruplara ayırır, grupların ortalamasını hesaplar ve sonucu ortalamaya göre sıralar.
Veriyi "SaleCityName", "ConceptName", "Seasons" kırılımında Price değişkeninin ortalamasına göre sıralıyoruz.
Bu işlem ile benzer özelliklere sahip olan müşterileri aynı grupta toplamış oluyoruz.
Bu durum, groupby işleminden sonra DataFrame'in boyutunun düşmesi, gruplama işlemi sırasında bazı satırların birleştirilmesi veya özetlenmesi nedeniyle olabilir.
groupby işlemi, orijinal DataFrame'deki benzer değerlere sahip satırları gruplara ayırır ve bu gruplar üzerinde bir toplama işlemi
veya başka bir özetleme işlemi gerçekleştirir. Bu özetleme işlemi sonucunda, grupların sayısı orijinal DataFrame'deki satır sayısından daha az olabilir. 
"""
df = df.groupby(["SaleCityName", "ConceptName", "Seasons"]).agg({"Price":"mean"}).sort_values(by="Price", ascending=False)
df.reset_index(inplace=True)



# Seviye tabanlı müşterileri (Persona) tanımlıyoruz.
df["Sales_Level_Based"] = [row[0] + "_" +
                           row[1] + "_" +
                           row[2] for row in df.values]



# Personaları Price değişkenine göre 4 farklı segmente ayırıyoruz.
df["Segment"] = pd.qcut(df["Price"], 4, labels=["D", "C", "B", "A"])


# Gereksiz değişkenleri veri setinden çıkartalım.
df = df[["Sales_Level_Based", "Segment", "Price"]]


# Çıktının daha güzel olması adına değişken ve gözlem birimlerini büyük harfle dönüştrümeyi tercih ediyorum.
df.columns = [col.upper() for col in df.columns]
df["SALES_LEVEL_BASED"] = [row.upper() for row in df["SALES_LEVEL_BASED"]]




# Antalya'da her şey dahil konseptinde, yüksek sezonda tatil yapmak isteyen bir müşterinin ne kadar gelir kazandırması beklenir?
new_user = "ANTALYA_HERŞEY DAHIL_HIGH"
df[df["SALES_LEVEL_BASED"] == new_user]

# Girne'de yarım pansiyon bir otele düşük sezon bir tatilde giden bir tatilci ne kadar kazandırır?
new_user = "GIRNE_YARIM PANSIYON_LOW"
df[df["SALES_LEVEL_BASED"] == new_user]


