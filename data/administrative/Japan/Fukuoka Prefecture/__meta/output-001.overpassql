// Important note: SubArea: Japan/Fukuoka Prefecture
[out:json][timeout:30000];
area["name:en"="Fukuoka Prefecture"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=7](area.searchArea);
);
out meta;
