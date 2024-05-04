[out:json][timeout:30000];
area["name:en"="Kyoto"]->.searchArea;
(
  nwr["historic"="castle"](area.searchArea);
);
out geom;
