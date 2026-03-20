[out:json][timeout:30];
area["name:en"="Nagoya"]->.searchArea;
(
  nwr["historic"="castle"](area.searchArea);
);
out geom;
