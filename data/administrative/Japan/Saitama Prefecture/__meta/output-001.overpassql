// Important note: SubArea: Japan/Saitama Prefecture
[out:json][timeout:30];
area["name:en"="Saitama Prefecture"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=7](area.searchArea);
);
out meta;
