[out:json][timeout:30000];
area["name:en"="Tokyo"]->.searchArea;
(
  relation["boundary"="administrative"]["name:en"="Taito"](area.searchArea);
);
out geom;
