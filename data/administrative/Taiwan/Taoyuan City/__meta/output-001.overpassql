// Important note: SubArea: Taiwan/Taoyuan City
[out:json][timeout:30000];
area["name:en"="Taoyuan City"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=7](area.searchArea);
);
out meta;
