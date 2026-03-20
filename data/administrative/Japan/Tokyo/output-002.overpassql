[out:json][timeout:30];
area["name:en"="Japan"]->.searchArea;
(
  relation["boundary"="administrative"]["name:en"="Tokyo"](area.searchArea);
);
out geom;
