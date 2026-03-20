[out:json][timeout:30];
area["name:en"="Tokyo"]->.searchArea;
(
  nwr["heritage"](area.searchArea);
);
out geom;
