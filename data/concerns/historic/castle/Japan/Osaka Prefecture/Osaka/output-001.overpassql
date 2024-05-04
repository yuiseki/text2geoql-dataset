[out:json][timeout:30000];
area["name:en"="Osaka"]->.searchArea;
(
  nwr["historic"="castle"](area.searchArea);
);
out geom;
