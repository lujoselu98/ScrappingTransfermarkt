if __name__ == '__main__':
    with open('Raw_All_Players_Data_Links.txt', 'r') as f:
        lines = f.readlines()

    profile_links = [line.split('->')[1].strip() for line in lines]
    profile_links = list(dict.fromkeys(profile_links))
    ids = [profile_link.split('/')[-1] for profile_link in profile_links]
    values_link = [link.replace('profil', 'marktwertverlauf')  for link in profile_links]
    cups_link = [link.replace('profil', 'erfolge')  for link in profile_links]
    with open('data/urls.txt', 'w') as f:
        for id, profile_link, value_link, cup_link in zip(ids, profile_links, values_link, cups_link):
            f.write(f"{id}\n")
            f.write(f"{profile_link}\n")
            f.write(f"{value_link}\n")
            f.write(f"{cup_link}\n")
            f.write("\n")
