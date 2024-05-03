[out:json][timeout:30000];
area["name:en"="Guangdong Province"]->.searchArea;
(
  nwr["office"="diplomatic"](area.searchArea);
);
out geom;
