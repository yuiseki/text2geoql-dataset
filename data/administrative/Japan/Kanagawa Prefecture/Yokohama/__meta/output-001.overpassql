// Important note: SubArea: Japan/Kanagawa Prefecture/Yokohama
[out:json][timeout:30000];
area["name:en"="Yokohama"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=8](area.searchArea);
);
out geom;
