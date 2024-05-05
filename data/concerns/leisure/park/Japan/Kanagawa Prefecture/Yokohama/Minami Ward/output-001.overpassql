[out:json][timeout:30000];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Minami Ward"]->.inner;
(
  nwr["leisure"="park"](area.inner)(area.outer);
);
out geom;
