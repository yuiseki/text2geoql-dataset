[out:json][timeout:30000];
area["name:en"="Municipality of Prizren"]->.searchArea;
(
  nwr["historic"="castle"](area.searchArea);
);
out geom;
