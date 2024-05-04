[out:json][timeout:30000];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Chikusa Ward"]->.inner;
(
  nwr["building"="church"](area.outer);
);
out geom;
