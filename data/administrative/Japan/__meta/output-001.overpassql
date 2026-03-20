// Important note: SubArea: Japan
[out:json][timeout:30];
area["name:en"="Japan"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=4](area.searchArea);
);
out meta;
