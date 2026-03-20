[out:json][timeout:30];
area["name:en"="Fukuoka Prefecture"]->.searchArea;
(
  nwr["historic"="castle"](area.searchArea);
);
out geom;
