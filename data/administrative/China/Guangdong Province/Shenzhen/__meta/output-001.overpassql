// Important note: SubArea: China/Guangdong Province/Shenzhen
[out:json][timeout:30000];
area["name:en"="Shenzhen"]->.searchArea;
(
  relation["boundary"="administrative"]["admin_level"=6](area.searchArea);
);
out geom;
