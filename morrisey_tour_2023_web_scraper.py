import requests
from datetime import datetime
from bs4 import BeautifulSoup


def extract_show_info(show_text: str):
    show_text = show_text.removesuffix("post-show")
    show_date = datetime.strptime(show_text[show_text.find("(") + 1:show_text.find(")")],
                                  "%B %d, %Y").strftime("%Y-%m-%d")
    show_text = show_text[: show_text.find("(")]
    show_city = show_text.split(sep=" - ")[0].strip()
    show_venue = show_text.split(sep=" - ")[1].strip()
    print(show_date, show_city, show_venue)
    return show_date, show_city, show_venue


def extract_songs(raw_setlist):
    raw_setlist = raw_setlist.replace("/", "\n")
    setlist = []
    for song in raw_setlist.splitlines():
        song = song.strip()
        if song != "":
            print(song)
            setlist.append(song)
    return setlist


def is_live_debut(setlist):
    live_debut_list = []
    for song in setlist:
        if song.endswith("(live debut)"):
            live_debut_list.append("Live debut")
        else:
            live_debut_list.append("")
    return live_debut_list


def scrape_morrissey_tour_info_from_urls(urls):
    csv = "show_date,show_city,show_venue,song_num,song,live_debut\n"
    for url in urls:
        page = requests.get(url)
        soup = BeautifulSoup(page.text, "html.parser")
        links = soup.find_all("a", string="Info")
        for link in links:
            show_url = link.get("href")
            show_page = requests.get(show_url)
            show_soup = BeautifulSoup(show_page.text, "html.parser")

            show_title = show_soup.find("h1", class_="p-title-value").text
            setlist_text = show_soup.body.find(
                string="Setlist:"
            ).next_element.next_element.next_element.next_element.text

            show_date, show_city, show_venue = extract_show_info(show_title)
            extracted_songs = extract_songs(setlist_text)
            live_debut = is_live_debut(extracted_songs)

            for idx, (song, debut) in enumerate(zip(extracted_songs, live_debut)):
                song = song.removesuffix("(live debut)")
                csv += f"{show_date},\"{show_city}\",\"{show_venue}\",{idx + 1},\"{song}\",\"{debut}\"\n"
    return csv


def run():
    URLS = ["https://www.morrissey-solo.com/tour/2023/",
            "https://www.morrissey-solo.com/tour/#archive"]
    with open("morrissey_tour_2023.csv", "w") as f:
        setlist_ = scrape_morrissey_tour_info_from_urls(URLS)
        f.write(setlist_)
    print(">>> end of process")


if __name__ == '__main__':
    run()