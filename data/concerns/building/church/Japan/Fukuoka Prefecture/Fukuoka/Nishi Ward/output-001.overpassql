[out:json][timeout:30];
area["name:en"="Fukuoka"]->.outer;
area["name:en"="Nishi Ward"]->.inner;
(
  nwr["building"="church"](area.inner)(area.outer);
);
out geom;
