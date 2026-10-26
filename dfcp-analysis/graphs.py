
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# Klasor yollarimiz
BASE_DIR = Path(__file__).resolve().parent
CSV_DIR = BASE_DIR / "csv"
GRAPH_DIR = BASE_DIR / "graphs"

# graphs klasoru yoksa olustur
GRAPH_DIR.mkdir(exist_ok=True)

# Grafik gorunumu
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["font.size"] = 10


def read_view(name):
    """Athena'dan indirilen CSV dosyasini okur."""
    file_path = CSV_DIR / f"{name}.csv"

    if not file_path.exists():
        print(f"Dosya bulunamadi: {file_path.name}")
        return None

    df = pd.read_csv(file_path)

    if df.empty:
        print(f"CSV bos: {file_path.name}")
        return None

    return df


def save_graph(name):
    """Aktif grafigi PNG olarak kaydeder."""
    plt.tight_layout()
    output = GRAPH_DIR / f"{name}.png"
    plt.savefig(output, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Olusturuldu: {output.name}")


def add_date(df):
    """Yil, ay, gun alanlarini tarihe donusturur."""
    df = df.copy()

    df["date"] = pd.to_datetime(
        df["year"].astype(str) + "-"
        + df["month"].astype(str).str.zfill(2) + "-"
        + df["day"].astype(str).str.zfill(2)
    )

    return df.sort_values("date")


# 1. GUNLUK HABER SAYISI
def graph_daily_news():
    df = read_view("vw_daily_news")
    if df is None:
        return

    df = add_date(df)

    plt.figure()
    plt.plot(
        df["date"],
        df["record_count"],
        marker="o",
        label="Toplam kayit"
    )
    plt.plot(
        df["date"],
        df["distinct_url_count"],
        marker="o",
        label="Benzersiz URL"
    )

    plt.title("Gunluk Haber Analizi - Eylul/Ekim 2026")
    plt.xlabel("Tarih")
    plt.ylabel("Haber sayisi")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.xticks(rotation=45)

    save_graph("01_gunluk_haber")


# 2. KATEGORI DAGILIMI
def graph_categories():
    df = read_view("vw_category_distribution")
    if df is None:
        return

    df = df.sort_values("record_count")

    plt.figure()
    plt.barh(df["category"], df["record_count"])
    plt.title("Kategori Bazinda Haber Dagilimi")
    plt.xlabel("Toplam haber kaydi")
    plt.ylabel("Kategori")

    save_graph("02_kategori_dagilimi")

# 4. GUNLUK KATEGORI DEGISIMI

def graph_daily_category():
    df = read_view("vw_daily_category")
    if df is None:
        return

    df = add_date(df)

    # Her kategori icin gunluk benzersiz URL sayisi
    pivot = df.pivot_table(
        index="date",
        columns="category",
        values="distinct_url_count",
        aggfunc="sum",
        fill_value=0
    )

    categories = list(pivot.columns)

    import math

    ncols = 2
    nrows = math.ceil(len(categories) / ncols)

    fig, axes = plt.subplots(
        nrows=nrows,
        ncols=ncols,
        figsize=(16, 4 * nrows),
        squeeze=False
    )

    axes = axes.flatten()

    for i, category in enumerate(categories):
        ax = axes[i]

        ax.plot(
            pivot.index,
            pivot[category],
            marker="o",
            markersize=3
        )

        ax.set_title(category)
        ax.set_xlabel("Tarih")
        ax.set_ylabel("Benzersiz URL Sayisi")
        ax.grid(alpha=0.3)
        ax.tick_params(axis="x", rotation=45)

    # Kullanilmayan panelleri gizle
    for i in range(len(categories), len(axes)):
        axes[i].set_visible(False)

    fig.suptitle(
        "Eylul-Ekim 2026: Kategori Bazinda Gunluk Benzersiz Haber Sayisi",
        fontsize=16
    )

    fig.tight_layout(rect=[0, 0, 1, 0.97])

    output = GRAPH_DIR / "04_kategoriler_ayri_paneller.png"

    fig.savefig(
        output,
        dpi=300,
        bbox_inches="tight"
    )

    plt.close(fig)

    print(f"Olusturuldu: {output.name}")


# 7. KAYNAK CESITLILIGI
def graph_source_diversity():
    df = read_view("vw_source_diversity")
    if df is None:
        return

    df = df.sort_values("distinct_sources")

    plt.figure()
    plt.barh(df["category"], df["distinct_sources"])
    plt.title("Kategori Bazinda Farkli Haber Kaynaklari")
    plt.xlabel("Benzersiz kaynak sayisi")
    plt.ylabel("Kategori")

    save_graph("07_kaynak_cesitliligi")




# TUM GRAFIKLERI CALISTIR
def main():
    graph_daily_news()
    graph_categories()
    graph_daily_category()
    graph_source_diversity()

    print("\nGrafik olusturma islemi tamamlandi.")


if __name__ == "__main__":
    main()
