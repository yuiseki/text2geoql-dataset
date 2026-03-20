[out:json][timeout:30];
area["name:en"="Tokyo"]->.searchArea;
(
  nwr["tourism"="aquarium"](area.searchArea);
);
out geom;
