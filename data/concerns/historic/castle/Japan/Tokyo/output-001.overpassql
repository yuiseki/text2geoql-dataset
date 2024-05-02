[out:json][timeout:30000];
area["name:en"="Tokyo"]->.searchArea;
(
  nwr["historic"="castle"](area.searchArea);
);
out geom;
