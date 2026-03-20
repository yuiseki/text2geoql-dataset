[out:json][timeout:30];
area["name:en"="Guangdong Province"]->.searchArea;
(
  nwr["office"="diplomatic"](area.searchArea);
);
out geom;
