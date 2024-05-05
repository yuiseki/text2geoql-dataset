[out:json][timeout:30000];
area["name:en"="Fukuoka"]->.outer;
area["name:en"="Minami Ward"]->.inner;
(
  nwr["building"="church"](area.inner)(area.outer);
);
out geom;
