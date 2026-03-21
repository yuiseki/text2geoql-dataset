[out:json][timeout:30];
area["name:en"="Naka Ward"]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["cuisine"~"korean"](area.inner)(area.outer);
);
out geom;
