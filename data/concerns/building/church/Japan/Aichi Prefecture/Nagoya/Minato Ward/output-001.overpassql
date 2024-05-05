[out:json][timeout:30000];
area["name:en"="Nagoya"]->.outer;
area["name:en"="Minato Ward"]->.inner;
(
  nwr["building"="church"](area.inner)(area.outer);
);
out geom;
