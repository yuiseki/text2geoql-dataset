// Important note: SubArea: Taiwan/Taoyuan City
[out:json][timeout:30];
area["name:en"="Taoyuan City"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=7](area.searchArea);
);
out meta;
