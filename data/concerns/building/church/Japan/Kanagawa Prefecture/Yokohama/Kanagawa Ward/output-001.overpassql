[out:json][timeout:30000];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Kanagawa Ward"]->.inner;
(
  nwr["building"="church"](area.outer);
);
out geom;
