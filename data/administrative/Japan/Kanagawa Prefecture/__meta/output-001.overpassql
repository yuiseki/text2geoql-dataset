// Important note: SubArea: Japan/Kanagawa Prefecture
[out:json][timeout:30000];
area["name:en"="Kanagawa Prefecture"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=7](area.searchArea);
);
out meta;
