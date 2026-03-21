[out:json][timeout:30];
area["name:en"="Naka Ward"]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["leisure"~"playground"](area.inner)(area.outer);
);
out geom;
