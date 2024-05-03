// Important note: SubArea: South Korea/Seoul
[out:json][timeout:30000];
area["name:en"="Seoul"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=6](area.searchArea);
);
out meta;
