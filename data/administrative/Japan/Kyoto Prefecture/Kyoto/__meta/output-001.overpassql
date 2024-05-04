// Important note: SubArea: Japan/Kyoto Prefecture/Kyoto
[out:json][timeout:30000];
area["name:en"="Kyoto"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=8](area.searchArea);
);
out meta;
