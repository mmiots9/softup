import re
import json
import requests
from bs4 import BeautifulSoup

# TODO: CRAN function
# TODO: bioconductor function
# other function
# TODO: github function


def pypi_search(package_name: str) -> tuple[str, bool]:
    URL = f'https://pypi.org/project/{package_name}/#history'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, "html.parser")
    release_versions = soup.find_all("p", class_ = "release__version")
    latest_version = [r.text.strip() for r in release_versions][0]
    stable = False if "pre-release" in latest_version else True
    latest_version = re.sub(r'\n.*', '', latest_version)
    link = f'https://pypi.org/project/{package_name}/{latest_version}/'
    return (latest_version, stable, link)


def cran_search(package_name: str) -> tuple[str, bool]:
    URL = f'https://cran.r-project.org/web/packages/{package_name}/index.html'
    page = requests.get(URL)
    if page.status_code != 200:
        raise IndexError
    soup = BeautifulSoup(page.content, "html.parser")
    latest_version = soup.find("td", string= lambda text: text == "Version:").parent.find_all("td")[1].text
    stable = False if "pre-release" in latest_version else True
    return (latest_version, stable, URL)



def bioconductor_search(package_name: str) -> tuple[str, bool]:
    URL = f'https://www.bioconductor.org/packages/release/bioc/html/{package_name}.html'
    page = requests.get(URL)
    if page.status_code != 200:
        raise IndexError
    soup = BeautifulSoup(page.content, "html.parser")
    latest_version = soup.find("td", string= lambda text: text == "Version").parent.find_all("td")[1].text
    stable = False if "pre-release" in latest_version else True
    return (latest_version, stable, URL)


def main(packages_dict: dict) -> None:
    source_dict = {"pypi": pypi_search, 
                   "cran": cran_search,
                   "bioconductor": bioconductor_search}
    update_dict = {}
    error_list = []
    for package, p_dict in packages_dict.items():
        try:
            latest_v, stable, link = source_dict[p_dict.get("source")](package)
        except IndexError:
            print(f"No info found for package {package}") # TODO: transform to log
            error_list.append(package)
            continue
        if not stable and (p_dict.get("pre-release", "") != latest_v):
            p_dict["pre-release"] = latest_v
            p_dict['link'] = link
            update_dict[package] = {"stable": False}
            print(f'Pre-release {latest_v} found for {package}') # TODO: transform to log
            continue
        if p_dict.get("stable", "") != latest_v:
            p_dict["stable"] = latest_v
            p_dict['link'] = link
            update_dict[package] = {"stable": False}
            print(f'Stable release {latest_v} found for {package}') # TODO: transform to log
            continue

        print(f'No new versions found for {package}') # TODO: transform to log

    # TODO: send mail
    # TODO: update file

if __name__ == '__main__':
    with open("packages.json", "r") as pf:
        packages_dict = json.load(pf)
    main(packages_dict)

