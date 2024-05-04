// Important note: SubArea: Japan/Aichi Prefecture/Nagoya
[out:json][timeout:30000];
area["name:en"="Nagoya"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=8](area.searchArea);
);
out meta;
