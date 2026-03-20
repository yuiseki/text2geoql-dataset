[out:json][timeout:30];
area["name:en"="Yokohama"]->.searchArea;
(
  nwr["historic"="castle"](area.searchArea);
);
out geom;
