[out:json][timeout:30000];
area["name:en"="Tokyo"]->.searchArea;
(
  nwr["office"="diplomatic"](area.searchArea);
);
out geom;
