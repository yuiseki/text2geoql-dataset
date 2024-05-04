// Important note: SubArea: Japan/Kyoto Prefecture
[out:json][timeout:30000];
area["name:en"="Kyoto Prefecture"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=7](area.searchArea);
);
out meta;
