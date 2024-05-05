[out:json][timeout:30000];
area["name:en"="Fukuoka"]->.outer;
area["name:en"="Chuo Ward"]->.inner;
(
  nwr["building"="church"](area.inner)(area.outer);
);
out geom;
