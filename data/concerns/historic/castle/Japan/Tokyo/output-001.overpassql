[out:json][timeout:30];
area["name:en"="Tokyo"]->.searchArea;
(
  nwr["historic"="castle"](area.searchArea);
);
out geom;
