[out:json][timeout:30000];
area["name:en"="Tokyo"]->.searchArea;
(
  nwr["heritage"](area.searchArea);
);
out geom;
