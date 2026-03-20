[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Isogo Ward"]->.inner;
(
  nwr["leisure"="park"](area.inner)(area.outer);
);
out geom;
