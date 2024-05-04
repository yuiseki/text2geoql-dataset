// Important note: SubArea: Japan/Shizuoka Prefecture
[out:json][timeout:30000];
area["name:en"="Shizuoka Prefecture"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=7](area.searchArea);
);
out meta;
