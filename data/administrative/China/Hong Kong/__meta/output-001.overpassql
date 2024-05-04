// Important note: SubArea: China/Hong Kong
[out:json][timeout:30000];
area["name:en"="Hong Kong"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=6](area.searchArea);
);
out meta;
