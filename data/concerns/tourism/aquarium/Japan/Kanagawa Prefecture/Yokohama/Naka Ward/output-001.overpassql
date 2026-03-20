[out:json][timeout:30];
area["name:en"="Yokohama"]->.outer;
area["name:en"="Naka Ward"]->.inner;
(
  nwr["tourism"="aquarium"](area.inner)(area.outer);
);
out geom;
