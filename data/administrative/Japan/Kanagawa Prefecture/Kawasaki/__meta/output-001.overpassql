// Important note: SubArea: Japan/Kanagawa Prefecture/Kawasaki
[out:json][timeout:30000];
area["name:en"="Kawasaki"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=8](area.searchArea);
);
out meta;
