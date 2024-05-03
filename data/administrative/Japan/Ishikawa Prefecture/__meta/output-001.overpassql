// Important note: SubArea: Japan/Ishikawa Prefecture
[out:json][timeout:30000];
area["name:en"="Ishikawa Prefecture"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=7](area.searchArea);
);
out meta;
